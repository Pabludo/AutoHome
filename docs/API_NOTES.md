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
