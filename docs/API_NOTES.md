# API Notes — Endpoints Reales Verificados

## Inmovilla REST API

**Base URL:** `https://procesos.inmovilla.com/api/v1`
**Auth:** `Token: {INMOVILLA_API_TOKEN}` header
**Docs:** `https://procesos.apinmo.com/api/v1/apidoc/`
**Rate limits:** clientes 20/min, propiedades 10/min, enums 2/min
**Estado:** ✅ Verificado — 10,705 propiedades

### Endpoints usados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/propiedades/listado?page=N` | Listar propiedades (paginado) |
| GET | `/propiedades/{cod_ofer}` | Detalle completo de propiedad |
| GET | `/propiedades/{cod_ofer}/extrainfo` | publishinfo (portales), leads |
| GET | `/propietarios/{keycli}` | Datos del propietario |
| GET | `/clientes/buscar?nombre=X` | Buscar clientes |

### Campos clave del inmueble

```
cod_ofer, ref, precio, precioinmo, m_cons, habitaciones, banyos,
latitud, longitud, referenciacol (= ref Idealista), keycli (ID propietario),
nodisponible, prospecto, fechaact
```

### publishinfo → Idealista URL

```python
extrainfo["publishinfo"]  # list[dict] por portal
# Cada entry: {"idealista": {"state", "publication_url", "quality_percentage"}}
# Fallback: referenciacol → https://www.idealista.com/inmueble/{referenciacol}/
```

---

## Idealista (Web Scraping)

**No hay API oficial para estadísticas.**
**Método:** Playwright (Chromium headless) con login de propietario/agencia
**Estado:** ✅ Verificado — property 28751504: 303 visits, 15 emails, 32 favorites

### Flujo de autenticación

1. Navegar a `https://www.idealista.com/login`
2. Rellenar email → submit → rellenar password → submit (2 pasos)
3. Manejar posibles CAPTCHAs

### Datos extraídos

| Métrica | Selector | Ejemplo |
|---------|----------|---------|
| Visitas | `#stats-ondemand` inner text parsing | 303 |
| Contactos email | idem | 15 |
| Favoritos | idem | 32 |
| Contactos teléfono | idem | null (no siempre disponible) |

### Mitigaciones anti-bot

- Delays aleatorios 3-7 seg entre navegaciones
- Scroll para trigger de lazy-load en `#stats-ondemand`
- Máximo 10 propiedades por sesión (configurable)

---

## Clientify REST API

**Base URL:** `https://api.clientify.net/v1`
**Auth:** `Authorization: Token {CLIENTIFY_API_TOKEN}`
**Docs:** `https://developers.clientify.com`
**Estado:** ✅ Verificado — 10,002 contactos, 2 pipelines

### Endpoints usados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/contacts/?query=email` | Buscar contacto por email |
| POST | `/deals/` | Crear deal/oportunidad |
| PATCH | `/deals/{id}/` | Actualizar deal (mover stage) |
| POST | `/contacts/{id}/notes/` | Añadir nota a contacto |
| GET | `/deals/pipelines/` | Listar pipelines |

### Estructura de un deal

```json
{
  "name": "Inmueble Calle Example 123",
  "contact": 12345,
  "pipeline": 1,
  "pipeline_stage": "new",
  "amount": 250000,
  "custom_fields": {
    "idealista_url": "https://idealista.com/inmueble/123456",
    "visits": 1619,
    "email_contacts": 11,
    "favorites": 88
  }
}
```

---

## Casafari REST API

**Base URL:** `https://api.casafari.com`
**Auth:** JWT — `POST /login` → `access_token` / `refresh_token`
**Docs:** `https://docs.api.casafari.com/`
**Estado:** ⏸ Conector implementado, pendiente credenciales plan API

### Endpoints implementados en conector

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/login` | Login → access_token + refresh_token |
| GET | `/refresh-token` | Renovar access_token (Bearer refresh_token) |
| POST | `/api/v1/references/locations` | Resolver nombre de ubicación → location_id |
| POST | `/api/v1/properties/search` | Buscar propiedades (activas, vendidas, etc.) |
| GET | `/api/v1/properties/search/{id}` | Detalle con historial de precios |
| POST | `/api/v1/comparables/search` | Comparables + estadísticas + precios estimados |
| POST | `/api/v1/valuation/comparables-prices` | Valoración: fast_sell, fair_market, out_of_market |
| GET | `/api/v1/listing-alerts/feeds` | Feeds de alertas configurados |
| POST | `/api/v1/listing-alerts/search` | Buscar alertas (new, price_up, price_down, sold) |

### Market Analytics API (endpoints adicionales)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/market-analytics-api/analysis` | Análisis de mercado por zona |
| POST | `/market-analytics-api/distributions/properties` | Distribución de propiedades + cuartiles |
| POST | `/market-analytics-api/distributions/prices` | Distribución por rangos de precio |
| POST | `/market-analytics-api/distributions/bedrooms` | Distribución por habitaciones |
| POST | `/market-analytics-api/distributions/time-on-market` | Distribución de tiempo en mercado |
| POST | `/market-analytics-api/time-series` | Series temporales (avg_price, sold, price_up/down) |

### Datos relevantes para AutoHome

- **Bajadas de precio:** `alert_subtypes: ["price_down"]` en listing-alerts
- **Multiagencia:** `listings[]` en property detail → varias agencias por inmueble
- **Valoración:** `estimated_prices.fair_market_price` vs precio de venta en Inmovilla
- **Tiempo en mercado:** `days_on_market` por propiedad
- **Historial de precios:** `sale_price_history[]`, `rent_price_history[]`
# API Integration Notes

## Clientify API

### Base URL
```
https://api.clientify.net/v1/
```

### Authentication
```
Authorization: Token <API_TOKEN>
```
Token obtained from: Clientify → Settings → Integrations → API

### Key Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts/` | List contacts (paginated) |
| POST | `/contacts/` | Create contact |
| GET | `/contacts/{id}/` | Get contact detail |
| PATCH | `/contacts/{id}/` | Update contact |
| GET | `/deals/` | List deals |
| POST | `/deals/` | Create deal |
| PATCH | `/deals/{id}/` | Update deal (move stage) |
| GET | `/pipelines/` | List pipelines |
| GET | `/pipelines/{id}/stages/` | List pipeline stages |
| POST | `/contacts/{id}/notes/` | Add note to contact |

### Rate Limits
- Standard plan: ~60 requests/minute
- Implement throttling at connector level

### Example: Create Deal
```python
{
    "name": "Inmueble Calle Example 123",
    "contact": 12345,
    "pipeline": 1,
    "pipeline_stage": "new",
    "expected_close_date": "2026-06-01",
    "amount": 250000,
    "custom_fields": {
        "idealista_url": "https://idealista.com/inmueble/123456",
        "last_visits": 1619,
        "last_contacts": 11,
        "trend": "rising"
    }
}
```

---

## Inmovilla API

### Access
- Requires API REST module activated in the Inmovilla plan
- Documentation provided by Inmovilla support on activation
- Typically REST with token authentication

### Expected Endpoints (to confirm)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/properties/` | List properties |
| GET | `/prospects/` | List prospects/leads |
| GET | `/prospects/{id}/` | Prospect detail (includes portal URLs) |
| GET | `/contacts/` | Contact information |

### Key Data We Need
- Prospect list with status
- Associated Idealista URL per property
- Client contact details (name, email, phone)
- Property status (active/sold/withdrawn)

### Fallback if no API
1. CSV/Excel export from Inmovilla panel
2. Place exports in `data/imports/` folder
3. Script parses and loads into local DB

---

## Idealista (Scraping)

### No API Available
- Statistics visible only to authenticated property owners/agents
- Access via Playwright browser automation

### Target Data Points
| Metric | Location | Selector (to discover) |
|--------|----------|----------------------|
| Total visits | Statistics panel | TBD - needs live inspection |
| Email contacts | Statistics panel | TBD |
| Favorites | Statistics panel | TBD |
| Last updated | Statistics panel | TBD |
| Phone contacts | Statistics panel | TBD |

### Authentication Flow
1. Navigate to `idealista.com/login`
2. Fill email + password
3. Handle potential CAPTCHA / 2FA
4. Navigate to property statistics URL
5. Extract metrics from DOM
6. Store with timestamp

### Anti-Detection Measures
- Random delays: 2-5 seconds between actions
- Human-like mouse movements (optional)
- Realistic viewport size (1920x1080)
- Standard User-Agent strings
- Cookie persistence between sessions
- Max 20-30 properties per session
