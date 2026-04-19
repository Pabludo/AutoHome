# AutoHome - Real Estate Metrics Automation Platform

## Overview
Automated pipeline that reads property listing metrics from Idealista.com, evaluates configurable conditions, and triggers actions across CRM/marketing platforms (Inmovilla + Clientify).

## Architecture
```
┌──────────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│  Inmovilla   │───>│   Scraper    │───>│   Condition   │───>│  Clientify  │
│  (Prospects) │    │  (Idealista) │    │   Engine      │    │  (Actions)  │
└──────────────┘    └──────────────┘    └───────────────┘    └─────────────┘
       │                   │                    │                    │
       └───────────────────┴────────────────────┴────────────────────┘
                                    │
                              ┌─────────────┐
                              │   SQLite DB  │
                              │  (metrics +  │
                              │   history)   │
                              └─────────────┘
```

## Flow
1. **Inmovilla Agent** → Fetches prospects with Idealista URLs
2. **Scraper Agent** → Reads property statistics from Idealista (visits, contacts, favorites)
3. **Condition Engine** → Evaluates rules against metrics history
4. **Clientify Agent** → Creates/updates deals, triggers automations

## Tech Stack
- **Python 3.12+** — Core language
- **Playwright** — Browser automation for Idealista scraping
- **SQLite** → **PostgreSQL** — Data persistence (start local, scale later)
- **APScheduler** — Task scheduling
- **httpx** — Async HTTP client for APIs
- **Pydantic** — Data validation and settings

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
playwright install chromium
cp .env.example .env          # Fill in credentials
python -m AutoHome.cli check-connections
```

## Project Structure
See `docs/PROJECT_STRUCTURE.md` for full layout.
