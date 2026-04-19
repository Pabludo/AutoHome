# Getting Started with AutoHome

Welcome to AutoHome — Real Estate Metrics Automation Platform.

## Quick Setup

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Pabludo/AutoHome.git
cd AutoHome
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
playwright install chromium
pip install -e .
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env and fill in:
# - IDEALISTA_EMAIL / IDEALISTA_PASSWORD
# - CLIENTIFY_API_TOKEN
# - INMOVILLA_API_URL / INMOVILLA_API_TOKEN (optional if using CSV import)
```

### 3. Test Connectivity
```bash
python -m autohome.cli check-connections
```

This will verify:
- ✅ Clientify API access
- ✅ Inmovilla API access (if configured)
- ✅ Playwright browser launch

## Project Structure

- **`src/autohome/agents/`** — 6 autonomous agents for the pipeline
  - `scraper.py` — Idealista property metrics scraper
  - `crm_reader.py` — Inmovilla prospect data reader
  - `condition_engine.py` — Rule evaluation engine
  - `action_dispatcher.py` — Clientify action executor
  - `orchestrator.agent.md` — Pipeline orchestration spec
  
- **`src/autohome/connectors/`** — External API clients
  - `idealista.py` — Playwright-based web scraper
  - `clientify.py` — Clientify REST API
  - `inmovilla.py` — Inmovilla REST API

- **`src/autohome/models/`** — Pydantic data models
  - Property metrics, prospects, rules, actions

- **`rules/`** — YAML condition definitions
  - `example_rules.yaml` → customize to your needs

- **`tests/`** — Unit tests (pytest + asyncio)

- **`docs/`** — Documentation
  - `VIABILITY_ANALYSIS.md` — Full project analysis
  - `PROJECT_STRUCTURE.md` — Directory layout
  - `API_NOTES.md` — API endpoint reference

## Development

### Run Tests
```bash
python -m pytest tests/ -v
```

### Lint Code
```bash
ruff check src/ tests/
ruff check src/ tests/ --fix  # Auto-fix
```

### Test Scraping
```bash
python -m autohome.cli scrape-test "https://www.idealista.com/inmueble/111029821/"
```

## Architecture

```
Inmovilla (Prospects) 
    ↓
CRM Reader Agent
    ↓
[Property URLs]
    ↓
Scraper Agent (Playwright)
    ↓
[Metrics: visits, contacts, favorites]
    ↓
Condition Engine
    ↓
[Triggered Rules]
    ↓
Action Dispatcher
    ↓
Clientify (Create deals, add notes, trigger automations)
```

## Next Steps

**Phase 1** (MVP):
- [ ] Test Idealista scraper with real credentials
- [ ] Confirm Inmovilla API endpoints or switch to CSV import
- [ ] Implement database persistence (SQLite)
- [ ] Add manual schedule execution (APScheduler)

**Phase 2** (Automation):
- [ ] Scheduled execution (cron / APScheduler)
- [ ] Trend-based rules
- [ ] Resource attachment system
- [ ] Error alerting (email/Slack)

**Phase 3** (Production):
- [ ] PostgreSQL migration
- [ ] Server deployment (Azure/AWS)
- [ ] Monitoring & logging
- [ ] Multi-agency support

## Troubleshooting

**ModuleNotFoundError: No module named 'autohome'**
```bash
pip install -e .
```

**Playwright headless browser issues**
```bash
playwright install chromium
# Or use headful mode for debugging:
# Set HEADFUL=1 in .env
```

**429 Too Many Requests (Idealista)**
- Increase delay between requests in `.env`:
  ```
  SCRAPER_DELAY_MIN_SECONDS=5
  SCRAPER_DELAY_MAX_SECONDS=10
  ```

## Data Protection & Compliance

- All personal data is stored with encryption intent (pending DB layer)
- Property statistics are public (owner's own listings)
- Prospect contact data: only with documented consent
- Implement: right to access, deletion, data export per GDPR

## Support

See `/docs` for detailed analysis and design notes.

---

**Project Status**: Phase 0 (Foundation) ✅ Complete
- [x] Project structure
- [x] Agent definitions  
- [x] Connector stubs
- [x] CLI & tests
- [x] Documentation
- [ ] Connectivity tests (manual)
- [ ] Phase 1 implementation
