# AutoHome — Plataforma de Automatización Inmobiliaria

## Qué es

Pipeline automatizado que conecta el CRM de la agencia (Inmovilla) con portales de anuncios (Idealista), inteligencia de mercado (Casafari) y CRM comercial (Clientify). Detecta inmuebles con alto/bajo rendimiento y ejecuta acciones automáticas.

## Arquitectura

```
┌──────────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│  Inmovilla   │───>│   Scraper    │───>│   Condition   │───>│  Clientify  │
│  (Prospects) │    │  (Idealista) │    │   Engine      │    │  (Actions)  │
└──────────────┘    └──────────────┘    └───────────────┘    └─────────────┘
       │                   │                    │                    │
       │            ┌──────────────┐            │                    │
       │            │   Casafari   │────────────┘                    │
       │            │ (Valuation)  │                                 │
       │            └──────────────┘                                 │
       └────────────────────┬────────────────────────────────────────┘
                      ┌─────────────┐
                      │   SQLite DB  │
                      │  (metrics +  │
                      │   history)   │
                      └─────────────┘
```

## Flujo del pipeline

1. **CRM Reader** → Lee propiedades activas de Inmovilla, resuelve URLs de Idealista
2. **Scraper** → Abre Idealista con Playwright y extrae visitas, contactos, favoritos
3. **Casafari** *(pendiente credenciales API)* → Valoración de mercado, comparables, bajadas de precio
4. **Condition Engine** → Evalúa reglas YAML contra métricas recogidas
5. **Action Dispatcher** → Crea deals en Clientify, añade notas, sugiere acciones

## Conexiones externas

| Servicio | Tipo | Auth | Estado |
|----------|------|------|--------|
| Inmovilla | REST API (httpx async) | Token fijo | ✅ Operativo |
| Idealista | Web scraping (Playwright) | Login email/pass | ✅ Operativo |
| Clientify | REST API (httpx async) | Token Bearer | ✅ Operativo |
| Casafari | REST API (httpx async) | JWT email/pass | ⏸ Pendiente plan API |

## Tech Stack

- **Python 3.12+** — async-native
- **Playwright** — automación de navegador para Idealista
- **httpx** — cliente HTTP asíncrono para APIs REST
- **Pydantic** — validación de datos y configuración
- **APScheduler** — programación de tareas (por integrar)
- **SQLite → PostgreSQL** — persistencia (por implementar)

## Instalación rápida

```powershell
git clone https://github.com/Pabludo/AutoHome.git
cd AutoHome
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
pip install -e .
cp .env.example .env   # Rellenar credenciales
autohome check-connections
```

## Configuración (.env)

```env
IDEALISTA_EMAIL=...          IDEALISTA_PASSWORD=...
CLIENTIFY_API_TOKEN=...      CLIENTIFY_BASE_URL=https://api.clientify.net/v1
INMOVILLA_API_URL=...        INMOVILLA_API_TOKEN=...
CASAFARI_EMAIL=...           CASAFARI_PASSWORD=...
DATABASE_URL=sqlite:///data/autohome.db
PIPELINE_INTERVAL_HOURS=6
```

## Estructura del proyecto

```
src/autohome/
├── config.py              # Configuración centralizada (.env)
├── cli.py                 # Punto de entrada CLI (check-connections, scrape-test, run-pipeline)
├── connectors/            # Clientes de APIs externas
│   ├── inmovilla.py       #   REST API — propiedades, propietarios, URLs
│   ├── idealista.py       #   Playwright — estadísticas de anuncios
│   ├── clientify.py       #   REST API — deals, contactos, notas
│   └── casafari.py        #   REST API — valoraciones, comparables, alertas
├── agents/                # Lógica de negocio (pipeline)
│   ├── base.py            #   Clase abstracta con logging
│   ├── crm_reader.py      #   Lee prospectos activos de Inmovilla
│   ├── scraper.py         #   Extrae métricas de Idealista
│   ├── condition_engine.py #  Evalúa reglas YAML
│   └── action_dispatcher.py # Ejecuta acciones en Clientify
├── models/                # Modelos Pydantic
│   ├── property.py        #   Property, PropertyMetrics, PropertySnapshot
│   ├── prospect.py        #   Prospect, Owner
│   ├── rule.py            #   Rule, ThresholdCondition, TrendCondition
│   └── action.py          #   TriggeredAction, ActionResult
├── db/                    # Capa de persistencia (por implementar)
└── utils/
    └── retry.py           # Decorator retry con backoff exponencial
tests/                     # pytest + asyncio
rules/example_rules.yaml   # Reglas configurables del motor de condiciones
.github/agents/            # Definiciones de agentes Copilot (6 ficheros .agent.md)
docs/API_NOTES.md          # Referencia técnica de endpoints reales
```

## Comandos CLI

```bash
autohome check-connections    # Verifica conectividad con todos los servicios
autohome scrape-test <URL>    # Scrapea estadísticas de un inmueble en Idealista
autohome run-pipeline         # Ejecuta pipeline completo (por implementar)
```

## Tests y calidad

```bash
python -m pytest tests/ -v    # 2/2 tests passing
ruff check src/ tests/        # Lint limpio
```

## Pendiente

- [ ] Capa DB (SQLite) — persistencia de snapshots y histórico
- [ ] Pipeline CLI completo — orquestar CRM Reader → Scraper → Engine → Dispatcher
- [ ] Completar action handlers (suggest_price_reduction, recommend_reactivation)
- [ ] APScheduler — ejecución automática cada 6h
- [ ] TrendCondition — comparar métricas actuales vs históricas
- [ ] Casafari — activar cuando se obtengan credenciales API
