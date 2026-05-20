"""
hiring.cafe job scraper using Playwright.
Navigates the site like a real user and supports filters.

Install dependencies:
    pip install playwright
    playwright install chromium
"""

import json
import time
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp


# ---------------------------------------------------------------------------
# Filter config
# ---------------------------------------------------------------------------

@dataclass
class JobFilters:
    """
    All filters are optional. Set only the ones you want.

    workplace:   "remote" | "hybrid" | "onsite"
    commitment:  "full_time" | "part_time" | "contract" | "internship"
    seniority:   "no_experience" | "entry" | "mid" | "senior" | "lead" | "executive"
    location:    country/city string shown in the location filter (e.g. "United States")
    """
    workplace:  Optional[str] = None
    commitment: Optional[str] = None
    seniority:  Optional[str] = None
    location:   Optional[str] = None


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

def scrape_hiring_cafe(
    search_term: str,
    filters: Optional[JobFilters] = None,
    max_jobs: int = 50,
    headless: bool = True,
) -> list[dict]:
    """
    Scrape job listings from hiring.cafe.

    Args:
        search_term: Keyword/title to search (e.g. "Python Developer")
        filters:     Optional JobFilters instance
        max_jobs:    Stop after collecting this many jobs
        headless:    Set False to watch the browser in action

    Returns:
        List of job dicts
    """
    filters = filters or JobFilters()
    jobs: list[dict] = []

    sb = sb_cdp.Chrome()
    endpoint_url = sb.get_endpoint_url()

    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False,
        #                             proxy={"server": ""})
        # context = browser.new_context(
        #     user_agent=(
        #         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #         "AppleWebKit/537.36 (KHTML, like Gecko) "
        #         "Chrome/120.0.0.0 Safari/537.36"
        #     ),
        #     viewport={"width": 1280, "height": 900},
        # )
        # page = context.new_page()
        browser = p.chromium.connect_over_cdp(endpoint_url)
        page = browser.contexts[0].pages[0]

        # ---- 1. Open site ------------------------------------------------
        print("Opening hiring.cafe ...")
        page.goto("https://hiring.cafe", wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(2000)

        # ---- 2. Type search term ----------------------------------------
        print(f"Searching for: {search_term}")
        _search(page, search_term)

        # ---- 3. Apply filters -------------------------------------------
        if any(v is not None for v in asdict(filters).values()):
            print("Applying filters ...")
            _apply_filters(page, filters)

        # ---- 4. Scrape results ------------------------------------------
        print("Scraping job listings ...")
        jobs = _scrape_jobs(page, max_jobs)

        browser.close()

    return jobs


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _search(page: Page, term: str) -> None:
    """Type into the search box and submit."""
    # Try common search input selectors
    selectors = [
        'input[placeholder*="Search"]',
        'input[placeholder*="search"]',
        'input[type="search"]',
        'input[type="text"]',
    ]
    for sel in selectors:
        try:
            page.wait_for_selector(sel, timeout=5000)
            page.fill(sel, term)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)
            return
        except PlaywrightTimeout:
            continue

    raise RuntimeError("Could not find the search input on hiring.cafe")


def _click_filter_option(page: Page, label_text: str) -> bool:
    """
    Look for a button/checkbox/label whose visible text matches label_text
    (case-insensitive). Returns True if clicked.
    """
    # Normalise the label for flexible matching
    needle = label_text.lower().replace("_", " ")

    # Try buttons and clickable labels
    for selector in ["button", "label", "[role='option']", "[role='checkbox']", "li"]:
        elements = page.query_selector_all(selector)
        for el in elements:
            try:
                text = (el.inner_text() or "").strip().lower()
                if needle in text or text in needle:
                    el.click()
                    page.wait_for_timeout(800)
                    return True
            except Exception:
                continue
    return False


def _apply_filters(page: Page, filters: JobFilters) -> None:
    """
    Intercept API calls to inject filter params, OR attempt UI-based clicking.
    hiring.cafe stores filters in the URL / query params after interaction.
    We try to click filter chips/dropdowns; fall back to URL params.
    """
    filter_map = {
        "workplace":  {
            "remote":    ["remote", "work from home"],
            "hybrid":    ["hybrid"],
            "onsite":    ["onsite", "on-site", "office"],
        },
        "commitment": {
            "full_time":  ["full time", "full-time"],
            "part_time":  ["part time", "part-time"],
            "contract":   ["contract", "freelance"],
            "internship": ["internship", "intern"],
        },
        "seniority": {
            "no_experience": ["no experience"],
            "entry":         ["entry", "junior"],
            "mid":           ["mid", "middle"],
            "senior":        ["senior"],
            "lead":          ["lead"],
            "executive":     ["executive", "director", "vp", "c-level"],
        },
    }

    def try_filter(category: str, value: str) -> None:
        candidates = filter_map.get(category, {}).get(value, [value])
        # First try to open a dropdown/panel for this category
        for panel_label in [category, category.replace("_", " ")]:
            _click_filter_option(page, panel_label)

        for label in candidates:
            if _click_filter_option(page, label):
                print(f"  ✔ Applied {category} = {value}")
                return
        print(f"  ⚠ Could not find UI element for {category} = {value}")

    if filters.workplace:
        try_filter("workplace", filters.workplace)
    if filters.commitment:
        try_filter("commitment", filters.commitment)
    if filters.seniority:
        try_filter("seniority", filters.seniority)
    if filters.location:
        _click_filter_option(page, filters.location)

    page.wait_for_timeout(2000)  # Let results refresh


def _scrape_jobs(page: Page, max_jobs: int) -> list[dict]:
    """
    Scroll through results, extract job cards, and paginate if needed.
    Falls back to intercepting XHR data if card parsing returns nothing.
    """
    jobs: list[dict] = []
    seen_ids: set = set()

    # Wait for at least one job card to appear
    card_selectors = [
        "article",
        "[data-testid='job-card']",
        ".job-card",
        ".job-listing",
        "[class*='JobCard']",
        "[class*='job-card']",
        "[class*='jobCard']",
    ]

    card_sel = None
    for sel in card_selectors:
        try:
            page.wait_for_selector(sel, timeout=8000)
            card_sel = sel
            break
        except PlaywrightTimeout:
            continue

    if not card_sel:
        print("Warning: could not detect job card elements; attempting JS extraction.")
        return _extract_via_js(page, max_jobs)

    prev_count = 0
    stall_count = 0

    while len(jobs) < max_jobs:
        cards = page.query_selector_all(card_sel)
        for card in cards:
            if len(jobs) >= max_jobs:
                break
            job = _parse_card(card)
            uid = job.get("title", "") + job.get("company", "") + job.get("location", "")
            if uid and uid not in seen_ids:
                seen_ids.add(uid)
                jobs.append(job)

        # Scroll to load more
        page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        page.wait_for_timeout(1500)

        # Detect end of results
        if len(jobs) == prev_count:
            stall_count += 1
            if stall_count >= 3:
                print("No new jobs loading — reached end of results.")
                break
        else:
            stall_count = 0
        prev_count = len(jobs)
        print(f"  Collected {len(jobs)} jobs so far ...")

    return jobs


def _parse_card(card) -> dict:
    """Extract fields from a single job card element."""
    def safe_text(sel: str) -> str:
        try:
            el = card.query_selector(sel)
            return el.inner_text().strip() if el else ""
        except Exception:
            return ""

    def safe_attr(sel: str, attr: str) -> str:
        try:
            el = card.query_selector(sel)
            return (el.get_attribute(attr) or "").strip() if el else ""
        except Exception:
            return ""

    # Grab all visible text lines to mine if specific selectors fail
    try:
        full_text = card.inner_text()
        lines = [l.strip() for l in full_text.splitlines() if l.strip()]
    except Exception:
        lines = []

    title    = safe_text("h2") or safe_text("h3") or (lines[0] if lines else "")
    company  = safe_text("[class*='company']") or safe_text("[class*='Company']") or (lines[1] if len(lines) > 1 else "")
    location = safe_text("[class*='location']") or safe_text("[class*='Location']") or ""
    salary   = safe_text("[class*='salary']") or safe_text("[class*='Salary']") or ""
    apply_url = (
        safe_attr("a[href*='apply']", "href")
        or safe_attr("a", "href")
        or ""
    )
    posted   = safe_text("[class*='date']") or safe_text("[class*='Date']") or safe_text("time") or ""

    # Pick out tags / badges (remote, seniority, etc.)
    tags: list[str] = []
    for badge_sel in ["[class*='badge']", "[class*='tag']", "[class*='pill']", "[class*='chip']"]:
        badge_els = card.query_selector_all(badge_sel)
        for b in badge_els:
            try:
                t = b.inner_text().strip()
                if t:
                    tags.append(t)
            except Exception:
                pass

    return {
        "title":    title,
        "company":  company,
        "location": location,
        "salary":   salary,
        "posted":   posted,
        "tags":     list(set(tags)),
        "apply_url": apply_url,
    }


def _extract_via_js(page: Page, max_jobs: int) -> list[dict]:
    """Last-resort: pull raw text from the DOM and heuristically parse jobs."""
    print("Attempting JS-based extraction ...")
    raw = page.evaluate("""
        () => {
            const cards = document.querySelectorAll('article, [class*="job"], [class*="card"]');
            return Array.from(cards).slice(0, 200).map(c => c.innerText);
        }
    """)
    jobs = []
    for text in raw[:max_jobs]:
        lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
        if lines:
            jobs.append({
                "title":    lines[0] if lines else "",
                "company":  lines[1] if len(lines) > 1 else "",
                "location": lines[2] if len(lines) > 2 else "",
                "raw_text": " | ".join(lines[:6]),
            })
    return jobs


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    print("=== hiring.cafe Playwright Scraper ===\n")
    search_term = input("Search term (e.g. 'Python Developer'): ").strip()

    # --- Filter prompts ---
    print("\nFilters (press Enter to skip any):")

    def ask(prompt, options):
        print(f"  {prompt} [{', '.join(options)}]: ", end="")
        val = input().strip().lower().replace(" ", "_")
        return val if val in options else None

    workplace  = ask("Workplace type", ["remote", "hybrid", "onsite"])
    commitment = ask("Commitment",     ["full_time", "part_time", "contract", "internship"])
    seniority  = ask("Seniority",      ["no_experience", "entry", "mid", "senior", "lead", "executive"])

    print("  Location (e.g. 'United States', or press Enter to skip): ", end="")
    location = input().strip() or None

    filters = JobFilters(
        workplace=workplace,
        commitment=commitment,
        seniority=seniority,
        location=location,
    )

    max_jobs = 50
    print(f"\nMax jobs to scrape (default 50): ", end="")
    try:
        val = input().strip()
        if val:
            max_jobs = int(val)
    except ValueError:
        pass

    headless_input = input("Run headless? [Y/n]: ").strip().lower()
    headless = headless_input != "n"

    # --- Run ---
    jobs = scrape_hiring_cafe(search_term, filters, max_jobs=max_jobs, headless=headless)

    print(f"\n✅ Scraped {len(jobs)} jobs.")

    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}] {job.get('title')} @ {job.get('company')}")
        print(f"    Location : {job.get('location')}")
        print(f"    Salary   : {job.get('salary')}")
        print(f"    Tags     : {', '.join(job.get('tags', []))}")
        print(f"    Posted   : {job.get('posted')}")
        print(f"    Apply    : {job.get('apply_url')}")

    out_file = f"{search_term.replace(' ', '_')}_jobs.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to {out_file}")


if __name__ == "__main__":
    main()
