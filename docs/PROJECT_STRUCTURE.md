# Project Structure

```
AutoHome/
├── .github/
│   ├── agents/                    # Agent definitions (Copilot-style)
│   │   ├── scraper.agent.md       # Idealista scraping agent
│   │   ├── crm-reader.agent.md    # Inmovilla CRM reader agent
│   │   ├── condition-engine.agent.md  # Rule evaluation agent
│   │   ├── action-dispatcher.agent.md # Clientify action agent
│   │   ├── orchestrator.agent.md  # Main pipeline orchestrator
│   │   └── planner.agent.md       # Planning and analysis agent
│   └── workflows/
│       └── daily-pipeline.yml     # Scheduled execution (future)
├── docs/
│   ├── VIABILITY_ANALYSIS.md      # Full viability study
│   ├── PROJECT_STRUCTURE.md       # This file
│   └── API_NOTES.md               # API integration notes
├── src/
│   └── AutoHome/
│       ├── __init__.py
│       ├── cli.py                 # CLI entry point
│       ├── config.py              # Settings (Pydantic)
│       ├── agents/                # Agent implementations
│       │   ├── __init__.py
│       │   ├── base.py            # Base agent class
│       │   ├── scraper.py         # Idealista scraper
│       │   ├── crm_reader.py      # Inmovilla integration
│       │   ├── condition_engine.py    # Rule engine
│       │   └── action_dispatcher.py   # Clientify actions
│       ├── connectors/            # External service connectors
│       │   ├── __init__.py
│       │   ├── idealista.py       # Playwright-based scraper
│       │   ├── inmovilla.py       # Inmovilla API client
│       │   └── clientify.py       # Clientify API client
│       ├── models/                # Data models
│       │   ├── __init__.py
│       │   ├── property.py        # Property/metrics models
│       │   ├── prospect.py        # Prospect/contact models
│       │   ├── rule.py            # Condition rules models
│       │   └── action.py          # Action/event models
│       ├── db/                    # Database layer
│       │   ├── __init__.py
│       │   ├── engine.py          # DB connection
│       │   ├── repositories.py    # Data access layer
│       │   └── migrations/        # Schema migrations
│       └── utils/                 # Shared utilities
│           ├── __init__.py
│           ├── logging.py
│           └── retry.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_connectors/
│   │   ├── test_idealista.py
│   │   ├── test_inmovilla.py
│   │   └── test_clientify.py
│   ├── test_agents/
│   │   └── test_condition_engine.py
│   └── test_models/
│       └── test_rules.py
├── resources/                     # Media resources for mailings (future)
│   └── .gitkeep
├── rules/                         # Rule definitions (YAML)
│   └── example_rules.yaml
├── .env.example                   # Environment variables template
├── .gitignore
├── pyproject.toml                 # Project config + dependencies
├── requirements.txt               # Pinned dependencies
└── README.md
```
