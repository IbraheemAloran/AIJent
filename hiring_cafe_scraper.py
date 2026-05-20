"""
Scrape job postings from HiringCafe (https://hiring.cafe).

HiringCafe is a Next.js app. The public search API (/api/search-jobs) is
typically behind Cloudflare and blocks plain HTTP clients, so the most
reliable approach is to render the page with a real browser (Playwright)
and parse the rendered DOM.

Install:
    pip install playwright beautifulsoup4
    playwright install chromium

Usage:
    python hiring_cafe_scraper.py "AI Engineer" --max 25 --out jobs.json
"""

import argparse
import json
import re
import time
from urllib.parse import quote

from playwright.sync_api import sync_playwright


BASE = "https://hiring.cafe"


def build_url(query: str) -> str:
    state = json.dumps({"searchQuery": query}, separators=(",", ":"))
    return f"{BASE}/?searchState={quote(state)}"


def parse_card(text: str) -> dict:
    """Heuristically parse a HiringCafe card's innerText into fields."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out = {
        "posted": None, "title": None, "location": None, "salary": None,
        "workplace": None, "commitment": None, "company": None,
        "company_desc": None, "requirements": None, "skills": None,
    }
    if not lines:
        return out

    # First line is usually the posted age (e.g. "3mo", "1w", "6d")
    if re.match(r"^\d+\s*(mo|w|d|h|y)$", lines[0]):
        out["posted"] = lines.pop(0)

    if lines: out["title"] = lines.pop(0)
    if lines: out["location"] = lines.pop(0)

    # Optional salary line
    if lines and re.search(r"\$\d", lines[0]):
        out["salary"] = lines.pop(0)

    if lines and lines[0] in {"Remote", "Hybrid", "Onsite"}:
        out["workplace"] = lines.pop(0)
    if lines and lines[0] in {"Full Time", "Part Time", "Contract", "Internship", "Temporary"}:
        out["commitment"] = lines.pop(0)

    # Company line is "Company Name: short description"
    if lines and ":" in lines[0]:
        name, _, desc = lines.pop(0).partition(":")
        out["company"] = name.strip()
        out["company_desc"] = desc.strip()

    if lines: out["requirements"] = lines.pop(0)
    if lines: out["skills"] = lines.pop(0)
    return out


def scrape(query: str, max_jobs: int = 25, headless: bool = True) -> list[dict]:
    url = build_url(query)
    jobs: list[dict] = []
    seen: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"),
            viewport={"width": 1400, "height": 1000},
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_selector('a[href^="/viewjob/"]', timeout=30_000)

        last_count, stagnant = 0, 0
        while len(jobs) < max_jobs and stagnant < 4:
            cards = page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href^=\"/viewjob/\"]'))
                       .map(a => {
                         let el = a;
                         while (el.parentElement && el.innerText.length < 200) el = el.parentElement;
                         return { href: a.href, text: el ? el.innerText : a.innerText };
                       })"""
            )
            for c in cards:
                if c["href"] in seen:
                    continue
                seen.add(c["href"])
                rec = parse_card(c["text"])
                rec["url"] = c["href"]
                rec["job_id"] = c["href"].rsplit("/", 1)[-1]
                jobs.append(rec)
                if len(jobs) >= max_jobs:
                    break

            if len(jobs) == last_count:
                stagnant += 1
            else:
                stagnant = 0
            last_count = len(jobs)

            page.mouse.wheel(0, 4000)
            time.sleep(1.2)

        browser.close()
    return jobs[:max_jobs]


def main() -> None:
    # ap = argparse.ArgumentParser()
    # ap.add_argument("query", help="Search query, e.g. 'AI Engineer'")
    # ap.add_argument("--max", type=int, default=25, help="Max jobs to fetch")
    # ap.add_argument("--out", default="jobs.json", help="Output JSON path")
    # ap.add_argument("--headed", action="store_true", help="Show browser window")
    # args = ap.parse_args()

    # jobs = scrape("args.query", args.max, headless=not args.headed)
    jobs = scrape("machine learning engineer", 10, headless=False)
    # with open(args.out, "w") as f:
    #     json.dump(jobs, f, indent=2, ensure_ascii=False)
    # print(f"Saved {len(jobs)} jobs to {args.out}")
    with open("jobs.json", "w") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(jobs)} jobs to jobs.json")


if __name__ == "__main__":
    main()
