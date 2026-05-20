# AIJent - AI-Powered Job Search Agent

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green)
![LangChain](https://img.shields.io/badge/LangChain-1.2+-orange)

An intelligent job search agent that uses AI embeddings and semantic matching to find the most relevant job opportunities based on your resume and preferences. AIJent leverages advanced NLP techniques, web scraping, and agentic workflows to streamline your job search process.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Design Patterns](#design-patterns)

## Overview

AIJent is an end-to-end AI job search system that automates the process of finding relevant job opportunities. It combines resume parsing, semantic embedding, intelligent filtering, and web scraping to deliver personalized job recommendations. The system is designed to be modular, scalable, and easy to extend with new data sources and matching algorithms.

### Problem Statement

Job searching is time-consuming and often yields irrelevant results. Traditional keyword-based search misses contextual understanding of both job requirements and candidate qualifications. AIJent solves this by using semantic similarity to match candidates with opportunities that truly align with their skills and experience.

### Key Benefits

- **Intelligent Matching**: Uses AI embeddings for semantic similarity matching, not just keyword search
- **Automated Resume Parsing**: Extracts structured data from resumes automatically
- **Customizable Filters**: Filter by location, experience level, company, commitment type, and more
- **Real-time Scraping**: Integrates with hiring.cafe for current job listings
- **User-Friendly Interface**: Web-based UI for easy interaction
- **API-First Design**: RESTful API for programmatic access

---

## Features

### Core Features

1. **Resume Upload & Parsing**
   - Upload PDF resumes
   - Automatic extraction of contact info, experience, education, skills, and projects
   - Structured JSON output for downstream processing
   - Support for various resume formats

2. **Job Scraping & Indexing**
   - Real-time scraping from hiring.cafe
   - Comprehensive filtering by:
     - Location (country, region, workplace type)
     - Experience level (entry, mid, senior)
     - Job title and description keywords
     - Commitment type (full-time, contract, etc.)
     - Company and industry
   - Full job description enrichment

3. **Semantic Job Matching**
   - Vector embedding of resume content using Google Generative AI
   - Vector embedding of job descriptions
   - Cosine similarity scoring for relevance ranking
   - Configurable similarity thresholds
   - Relevance-ranked job recommendations

4. **Job Search Agent**
   - LangChain-based agentic system
   - Multi-step reasoning and tool integration
   - Browser automation for advanced scraping
   - SQL database integration for job storage and retrieval

5. **Web Interface**
   - Gradio-based interactive UI
   - Resume upload functionality
   - Job recommendation display
   - Application tracking dashboard
   - Analytics and insights

---

## Tech Stack

### Core Framework & Language

| Component   | Version | Purpose                   |
| ----------- | ------- | ------------------------- |
| **Python**  | 3.12+   | Core programming language |
| **FastAPI** | 0.136+  | REST API framework        |
| **Gradio**  | 6.14+   | Web UI framework          |

### AI & Machine Learning

| Component                  | Version | Purpose                              |
| -------------------------- | ------- | ------------------------------------ |
| **LangChain**              | 1.2+    | AI agent framework and orchestration |
| **Google Generative AI**   | 2.0+    | LLM and embeddings                   |
| **LangChain Google GenAI** | 3.2+    | LangChain integration for Google AI  |
| **Ollama**                 | 0.6+    | Local LLM support                    |
| **LangChain Ollama**       | 1.1+    | Ollama integration                   |

### Data Processing & Parsing

| Component          | Version | Purpose                           |
| ------------------ | ------- | --------------------------------- |
| **BeautifulSoup4** | 4.14+   | HTML parsing for web scraping     |
| **PyMuPDF (fitz)** | 1.27+   | PDF parsing for resume extraction |
| **Pydantic**       | 2.13+   | Data validation and serialization |

### Web & Automation

| Component           | Version | Purpose                         |
| ------------------- | ------- | ------------------------------- |
| **Requests**        | 2.33+   | HTTP library for API calls      |
| **Playwright**      | 1.59+   | Browser automation for scraping |
| **Browser-Use**     | 0.5+    | High-level browser interaction  |
| **Browser-Use-SDK** | 3.5+    | Browser automation SDK          |

### Infrastructure & Utilities

| Component         | Version        | Purpose                                 |
| ----------------- | -------------- | --------------------------------------- |
| **Uvicorn**       | (via FastAPI)  | ASGI server                             |
| **NumPy**         | 2.4+           | Numerical computing (cosine similarity) |
| **python-dotenv** | (dependencies) | Environment variable management         |
| **Jupyter**       | 1.1+           | Notebook support                        |
| **IPykernel**     | 7.2+           | Jupyter kernel                          |

### Development & Testing

| Component        | Version | Purpose                            |
| ---------------- | ------- | ---------------------------------- |
| **LangSmith**    | 0.8+    | Monitoring and debugging LangChain |
| **MCP Adapters** | 0.2+    | Model Context Protocol integration |

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interfaces                             │
│  ┌──────────────────┐              ┌──────────────────┐          │
│  │   Gradio Web UI  │              │   FastAPI REST   │          │
│  │                  │              │   API (Port 8000)│          │
│  └────────┬─────────┘              └────────┬─────────┘          │
└───────────┼─────────────────────────────────┼──────────────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services Layer                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Resume Parser Service                                      │ │
│  │  • PDF to Text extraction (PyMuPDF)                        │ │
│  │  • LLM-based structured parsing (Google Generative AI)     │ │
│  │  • Pydantic validation                                     │ │
│  │  • JSON profile output                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Embedding Service                                          │ │
│  │  • Profile embedding (Google Embeddings API)               │ │
│  │  • Job description embedding                               │ │
│  │  • Cosine similarity computation (NumPy)                   │ │
│  │  • Threshold-based filtering (0.7 default)                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Job Scraper Service                                        │ │
│  │  • Web scraping (BeautifulSoup + Playwright)               │ │
│  │  • API integration (hiring.cafe)                           │ │
│  │  • Advanced filtering and query building                   │ │
│  │  • Pagination and rate limiting                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Job Search Agent (LangChain)                               │ │
│  │  • Multi-step reasoning                                    │ │
│  │  • Tool orchestration                                      │ │
│  │  • State management                                        │ │
│  │  • Error handling and retry logic                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SQL Agent Service                                          │ │
│  │  • Database query generation                               │ │
│  │  • Job storage and retrieval                               │ │
│  │  • Analytics computation                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data & Storage Layer                           │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │   profile.json   │  │ enriched_    │  │  SQL Database      │ │
│  │ (user profile)   │  │ jobs.json    │  │  (PostgreSQL/SQLite)
│  │                  │  │ (job listing)│  │                    │ │
│  └──────────────────┘  └──────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Resume Upload
     │
     ▼
PDF Parsing (PyMuPDF)
     │
     ▼
LLM Structured Extraction (Google Generative AI)
     │
     ▼
profile.json (stored)
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
Embedding Creation   User Profile
(Google Embeddings)
     │                 │
     └────────┬────────┘
              │
              ▼
         [Ready for Matching]
              │
              ├──────────────────────┐
              │                      │
              ▼                      ▼
         Job Scraping          Manual Job Input
         (hiring.cafe)
              │                      │
              └────────┬─────────────┘
                       │
                       ▼
              Job Description Cleaning
              (HTML to text)
                       │
                       ▼
              Job Embedding
              (Google Embeddings)
                       │
                       ▼
              Similarity Scoring
              (Cosine Similarity)
                       │
                       ▼
              Relevance Ranking
              (Filter by threshold)
                       │
                       ▼
         enriched_jobs.json (output)
                       │
                       ▼
          User Recommendations
```

### Component Interaction

1. **Resume Parser ↔ Embedder**: Resume text flows from parser to embedder for vectorization
2. **Job Scraper ↔ Embedder**: Job descriptions flow to embedder for vectorization
3. **Embedder ↔ Search Agent**: Similarity scores guide agent decision-making
4. **Search Agent ↔ SQL Agent**: SQL agent queries database for job storage
5. **All Services ↔ FastAPI**: REST endpoints expose all services

---



### Module Responsibilities

| Module               | Responsibility                                              |
| -------------------- | ----------------------------------------------------------- |
| **Resume_parser**    | Converts PDF resumes to structured, validated JSON profiles |
| **Embedder**         | Vectorizes text and computes semantic similarity scores     |
| **job_search_agent** | Discovers and enriches job listings from external sources   |
| **SQLAgent**         | Manages job storage, retrieval, and analytics queries       |
| **app_gradio**       | User-facing web interface for the entire system             |
| **main.py**          | REST API service for programmatic access                    |

---

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager
- Virtual environment tool (venv, conda, or poetry)
- Google API Key (for Generative AI and embeddings)
- Internet connection (for scraping and API calls)

### Step 1: Clone or Set Up Project

```bash
cd i:\Projects\AIJent\AIJent
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # macOS/Linux
```

### Step 3: Install Dependencies

```bash
pip install -e .
# or
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Local LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Database Configuration
DATABASE_URL=sqlite:///jobs.db
# or PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/aijent_db
```

### Step 5: Verify Installation

```bash
# Test imports
python -c "import langchain; import google.genai; print('All imports successful!')"

# Run a simple scrape test
python job_search_agent/job_scrape_mcp.py
```

---

## Configuration

### Scraper Filters

Modify `job_search_agent/job_scrape_mcp.py` to adjust search parameters:

```python
params = {
    "roleYoeRange": [0, 3],                    # Years of experience
    "seniorityLevel": ["Entry Level", "Mid Level"],
    "commitmentTypes": ["Full Time", "Contract"],
    "departments": ["Information Technology", "Software Development"],
    "jobTitleQuery": "(\"data scientist\" OR \"machine learning engineer\")",
    "searchQuery": "ai engineer",
    "locations": [                             # Geographic filters
        {
            "formatted_address": "United States",
            "workplace_types": ["Remote"]
        }
    ],
    "dateFetchedPastNDays": 61                 # Recently posted jobs
}
```

### Embedding Threshold

Adjust similarity matching threshold in `Embedder/embedding_mcp_server.py`:

```python
APPLY = 0.7  # Jobs with similarity >= 0.7 are recommended
```

Lower values = more jobs but less relevant
Higher values = fewer jobs but more relevant

### FastAPI Server Configuration

Modify `main.py`:

```python
uvicorn.run(
    "main:app",
    host="127.0.0.1",      # Listening address
    port=8000,             # Port number
    reload=True            # Auto-reload on code changes
)
```

---

## Usage

### 1. Via Gradio Web Interface

```bash
python app_gradio.py
```

Then visit `http://localhost:7860` in your browser.

### 2. Via REST API

Start the FastAPI server:

```bash
python main.py
```

Server runs on `http://127.0.0.1:8000`

#### Upload Resume

```bash
curl -X POST "http://127.0.0.1:8000/upload-resume" \
  -F "resume=@/path/to/resume.pdf"
```

### 3. Direct Python Usage

```python
from Resume_parser.parser_mcp_server import ResumeParser
from Embedder.embedding_mcp_server import embed_profile, similarity_score
from job_search_agent.job_scrape_mcp import scrape_jobs

# Parse resume
parser = ResumeParser()
profile = parser.parse("path/to/resume.pdf")

# Embed profile
embed_profile()

# Scrape jobs
scrape_jobs(max_jobs=10)

# Get matching jobs
import json
with open("enriched_jobs.json") as f:
    jobs = json.load(f)

for job in jobs:
    print(f"{job['title']} at {job['company']} - {job['location']}")
```

### 4. Via Jupyter Notebooks

Explore features interactively:

```bash
jupyter notebook playground.ipynb
```

---

## API Reference

### Resume Upload Endpoint

**POST** `/upload-resume`

Upload and parse a PDF resume.

**Parameters:**

- `resume` (file): PDF resume file

**Response:**

```json
{
  "Result": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "+1-555-0123",
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "years_of_exp": 5,
    "experience": [...],
    "education": [...],
    "projects": [...],
    "all_bullet_points_and_summary_and_skills": "..."
  }
}
```

### Health Check Endpoint

**GET** `/`

Check API status.

**Response:**

```json
{
  "Status": "200 OK"
}
```

---

## How It Works

### End-to-End Workflow

#### Phase 1: Resume Processing

1. User uploads PDF resume via UI or API
2. PyMuPDF extracts text from PDF
3. Google Generative AI (LLM) parses resume using prompt engineering
4. Output is validated against Pydantic models
5. Structured profile saved to `profile.json`

#### Phase 2: Profile Embedding

1. Resume profile text is combined: "first_name: John, skills: [Python, ML], experience: [...]"
2. Google Embeddings API converts text to 768-dimensional vector
3. Embedding stored in `profile.json`

#### Phase 3: Job Discovery

1. Scraper queries hiring.cafe API
2. Applies filters: location, experience level, job title, etc.
3. Constructs Next.js data URL with encoded search parameters
4. Fetches job listings in pages
5. For each job:
   - Extracts basic info (title, company, location, URL)
   - Fetches full HTML description
   - Cleans HTML (converts to plain text, formats lists)
   - Saves to temporary list

#### Phase 4: Job Embedding & Matching

1. All job descriptions embedded using Google Embeddings API
2. Cosine similarity computed between profile vector and each job vector
3. Jobs scored 0.0 - 1.0 (1.0 = perfect match)
4. Results filtered by threshold (default 0.7)
5. Top matches sorted by score
6. Output saved to `enriched_jobs.json`

#### Phase 5: Presentation

1. Results displayed via Gradio UI or API
2. User can review matches with relevance scores
3. Apply directly via link or save for later

### Semantic Matching Details

**Why Embeddings Over Keywords?**

Traditional approach:

```
Resume: "Python, AWS, Docker"
Job: "Requires Python and cloud technologies"
→ Keyword match missed "cloud" concept
```

Embedding approach:

```
Resume vector: [0.23, 0.45, -0.12, ...]
Job vector:    [0.21, 0.48, -0.10, ...]
Cosine similarity: 0.92 (high match!)
→ Semantic understanding captures relationship
```

**Vector Space:**

- Dimension: 768 (Google's embedding model)
- Similarity range: 0.0 (completely different) to 1.0 (identical)
- Threshold: 0.7 (default) - moderate relevance requirement

---

## Design Patterns

### 1. **Modular Service Architecture**

Each component (Resume Parser, Embedder, Job Scraper, SQL Agent) is independently deployable and testable.

### 2. **Pydantic Data Validation**

Strict schema enforcement ensures data integrity through the pipeline.

```python
class Profile(BaseModel):
    first_name: str
    email: str
    skills: List[str]
    # ... etc
```

### 3. **Agent-Based Orchestration**

LangChain agents coordinate multi-step workflows with tool composition.

### 4. **Lazy Loading & Caching**

Embeddings are cached in `profile.json` to avoid recomputation.

### 5. **Rate-Limited Scraping**

`time.sleep(1)` between requests respects server limits.

### 6. **Error Graceful Degradation**

If scraping fails, system continues with cached results.

### 7. **Separation of Concerns**

- Data parsing (Resume_parser)
- Vector operations (Embedder)
- Web scraping (job_search_agent)
- Database operations (SQLAgent)
- UI/API serving (app_gradio, main.py)

---

## Future Enhancements

- [ ] Multi-language resume support
- [ ] Real-time job update notifications
- [ ] Company research and culture fit scoring
- [ ] Interview prep recommendations
- [ ] Application tracking and follow-up management
- [ ] Salary negotiation insights
- [ ] Skill gap analysis with learning recommendations
- [ ] Integration with LinkedIn and Indeed
- [ ] Batch application automation
- [ ] Performance analytics dashboard

---

## Troubleshooting

### Issue: "No API key found"

**Solution:** Set `GOOGLE_API_KEY` environment variable in `.env` file.

### Issue: PDF parsing fails

**Solution:** Ensure PDF is text-based (not scanned image). Use OCR tools first if needed.

### Issue: Slow embedding computation

**Solution:** Increase batch size or use fewer job results. Consider local LLM via Ollama.

### Issue: No jobs found

**Solution:** Adjust search filters to be less restrictive. Check internet connection.

---

## Contributing

To extend AIJent:

1. Add new scraper in `job_search_agent/`
2. Create new LangChain tool in appropriate module
3. Update API endpoints in `main.py`
4. Add UI components in `app_gradio.py`
5. Write tests in `tests/` directory (create if needed)

---



**Last Updated:** May 2026
**Version:** 0.1.0
