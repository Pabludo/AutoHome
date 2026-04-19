# Configuración AutoHome - Guía Completa

## Requisitos Previos

- Python 3.12+
- Git
- Credenciales de:
  - Idealista (email/password del propietario)
  - Clientify API Token
  - Inmovilla (API URL + Token, opcional si usas CSV)

## 1. Instalación Rápida

### Windows (PowerShell)
```powershell
# Clonar repositorio
git clone https://github.com/Pabludo/AutoHome.git
cd AutoHome

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
playwright install chromium
pip install -e .

# Configurar credenciales
cp .env.example .env
# ↓ Editar .env con tus credenciales
```

### macOS / Linux
```bash
git clone https://github.com/Pabludo/AutoHome.git
cd AutoHome
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pip install -e .
cp .env.example .env
# Editar .env
```

## 2. Variables de Entorno (.env)

```env
# === Credenciales Idealista ===
# Email de la cuenta propietaria de los inmuebles
IDEALISTA_EMAIL=tu-email@ejemplo.com

# Contraseña para login automático
IDEALISTA_PASSWORD=tu-contraseña

# === Token API Clientify ===
# Obtener en: Clientify → Configuración → Integraciones → API
CLIENTIFY_API_TOKEN=tu-token-aqui
CLIENTIFY_BASE_URL=https://api.clientify.net/v1

# === API Inmovilla (opcional) ===
# Si tu plan incluye módulo API REST activado
INMOVILLA_API_URL=https://tu-instancia.inmovilla.com/api
INMOVILLA_API_TOKEN=tu-token-inmovilla

# Alternativa: usar CSV exports en data/imports/

# === Base de Datos ===
# SQLite (local, desarrollo):
DATABASE_URL=sqlite:///data/autohome.db

# PostgreSQL (producción):
# DATABASE_URL=postgresql://usuario:pass@host:5432/autohome

# === Configuración del Pipeline ===
# Repetir scraping cada N horas
PIPELINE_INTERVAL_HOURS=6

# Delays aleatorios entre requests a Idealista (segundos)
SCRAPER_DELAY_MIN_SECONDS=2
SCRAPER_DELAY_MAX_SECONDS=5

# Máximo de inmuebles por sesión de scraping
SCRAPER_MAX_PROPERTIES_PER_SESSION=20

# === Logging ===
LOG_LEVEL=INFO
# Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 3. Verificar Conectividad

```bash
# Test de conexiones a todas las APIs externas
autohome check-connections

# Output esperado:
# Service                 Status           Details
# ────────────────────────────────────────────────────
# Clientify API           ✓ Connected      API token valid
# Inmovilla API           ✓ Connected      API accessible
# Idealista (Playwright)  ✓ Browser OK     Page loaded: Idealista
```

Si alguno falla:
- **Clientify**: Verifica que CLIENTIFY_API_TOKEN sea válido y no esté expirado
- **Inmovilla**: Confirma que INMOVILLA_API_URL y token son correctos, o usa CSV
- **Idealista**: Revisa que no haya cambios en el HTML (selectores pueden necesitar ajuste)

## 4. Configurar Reglas de Negocio

Edita `rules/example_rules.yaml`:

```yaml
rules:
  # Inmueble con mucho interés → crear deal HIGH en Clientify
  - name: high_interest
    type: threshold
    conditions:
      - metric: visits
        operator: ">="
        value: 1000
      - metric: email_contacts
        operator: ">="
        value: 10
    operator: AND
    action: notify_high_interest
    priority: high
    enabled: true

  # Muy poco interés → sugerir ajuste de precio
  - name: low_interest
    type: threshold
    conditions:
      - metric: visits
        operator: "<"
        value: 100
    action: suggest_price_reduction
    priority: medium
    enabled: true
```

**Métricas disponibles:**
- `visits` — Número total de visitas
- `email_contacts` — Contactos por email
- `phone_contacts` — Contactos por teléfono
- `favorites` — Guardados como favorito

**Operadores:**
- `>=`, `<=`, `>`, `<`, `==`, `!=`

**Acciones disponibles:**
- `notify_high_interest` — Crear deal HIGH en Clientify
- `suggest_price_reduction` — Añadir nota, sugerir rebaja
- `recommend_reactivation` — Inmueble inactivo, recomendar reactivación
- `attach_resources` — Adjuntar videos/PDFs desde carpeta resources/

## 5. Ejecutar el Pipeline

### Manual (una sola ejecución):
```bash
# Ejecutar todo el flujo una vez
autohome run-pipeline

# Usar verbose para ver detalles
autohome run-pipeline --verbose
```

### Automático (cada 6 horas - en desarrollo):
```bash
# Próximamente: scheduler integrado
# Por ahora: usar Task Scheduler de Windows o cron en Linux

# Windows Task Scheduler:
# Crear tarea programada:
# Acción: C:\Projects\AutoHome\.venv\Scripts\python.exe
# Argumentos: -m autohome.cli run-pipeline
# Programar: cada 6 horas
```

## 6. Monitoreo y Logs

Los logs se guardan en `logs/` (cuando se implemente DB):

```bash
# Ver logs en tiempo real (desarrollo)
tail -f logs/autohome.log  # macOS/Linux
Get-Content -Path logs\autohome.log -Wait  # Windows
```

**Monitorar en base de datos:**
```sql
SELECT * FROM action_history 
WHERE executed_at > NOW() - INTERVAL 1 HOUR
ORDER BY executed_at DESC;
```

## 7. Casos de Uso Comunes

### Inmuebles en Venta Rápida
```yaml
- name: rapid_sale
  conditions:
    - metric: visits
      operator: ">="
      value: 2000
    - metric: email_contacts
      operator: ">="
      value: 50
  action: notify_high_interest
  priority: critical
```

### Propiedades Estancadas
```yaml
- name: stale_property
  conditions:
    - metric: visits
      operator: "<"
      value: 10
    - metric: email_contacts
      operator: "=="
      value: 0
  action: recommend_reactivation
  priority: high
```

### Portfolio Diverso (Multi-Tecnología)
Si tienes PV + PT + CT, las etiquetas de irradiancia cambian automáticamente:
- **PV**: "Irradiance – GTI"
- **PT/CT**: "Irradiance – DNI"

## 8. Troubleshooting

### "403 Forbidden" en Idealista
→ El scraper puede estar bloqueado. Soluciones:
1. Aumentar delays: `SCRAPER_DELAY_MIN_SECONDS=10`
2. Usar modo headful (visible): cambios en código
3. Rotar credenciales / usar nuevo IP

### "ModuleNotFoundError: autohome"
```bash
# Reinstalar en modo editable
pip install -e .
```

### Tests fallando
```bash
# Ejecutar con output verboso
python -m pytest tests/ -vv -s

# Test específico
python -m pytest tests/test_agents/test_condition_engine.py::test_high_interest_rule_triggers -v
```

### Lint errors
```bash
# Verificar
ruff check src/

# Arreglar automáticamente
ruff check src/ --fix
```

## 9. Próximos Pasos

- [ ] **Semana 1**: Configurar credenciales y verificar conectividad
- [ ] **Semana 2**: Test scraping real contra Idealista, ajustar selectores
- [ ] **Semana 3**: Conectar Clientify y crear primeras tarjetas de prueba
- [ ] **Semana 4**: Implementar scheduling automático
- [ ] **Mes 2**: Dashboard básico, monitoreo, migración a PostgreSQL
- [ ] **Mes 3**: Producción en Azure/AWS, soporte multi-agencia

## 10. Soporte

- **Documentación técnica**: `/docs/`
- **Análisis de viabilidad**: `/docs/VIABILITY_ANALYSIS.md`
- **Referencia de APIs**: `/docs/API_NOTES.md`
- **Issues en GitHub**: Reporta bugs y solicita features

---

**¿Necesitas ayuda?** Abre un issue en GitHub o consulta la documentación en `/docs/`.
