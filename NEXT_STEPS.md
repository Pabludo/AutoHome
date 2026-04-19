# NEXT STEPS — AutoHome Project

## 🎯 Objetivo Inmediato

Tu proyecto **AutoHome** está 100% configurado y desplegado en GitHub. Ahora necesitas prepararlo para la ejecución real.

## 📋 Checklist — Próximos Pasos

### 1️⃣ Acceso al Repositorio ✅ HECHO
- [x] Repositorio creado: https://github.com/Pabludo/AutoHome
- [x] Código pushado con 4 commits
- [x] Branch main es la rama principal
- [x] .gitignore correctamente configurado

**Tu URL del repo**: https://github.com/Pabludo/AutoHome

---

### 2️⃣ Clonar y Configurar Localmente (EN TU MÁQUINA)

```powershell
# En PowerShell, desde donde quieras tener el proyecto
git clone https://github.com/Pabludo/AutoHome.git
cd AutoHome

# Crear entorno virtual fresco
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar todas las dependencias
pip install -r requirements.txt
playwright install chromium
pip install -e .
```

---

### 3️⃣ Configurar Credenciales (.env)

```powershell
# Copiar template
cp .env.example .env

# Editar en tu editor favorito (VS Code, Notepad, etc.)
notepad .env
```

**Necesitas:**

```env
# Idealista — credenciales de propietario/agencia
IDEALISTA_EMAIL=tu-email@tudominio.com
IDEALISTA_PASSWORD=tu-contraseña

# Clientify — obtener en https://app.clientify.net → Configuración → API
CLIENTIFY_API_TOKEN=tu-token-aqui

# Inmovilla — opcional (o usar CSV en data/imports/)
INMOVILLA_API_URL=https://tu-instance.inmovilla.com/api
INMOVILLA_API_TOKEN=tu-token

# Mantener REST tal como está (base de datos local)
DATABASE_URL=sqlite:///data/autohome.db
```

---

### 4️⃣ Verificar que TODO Funciona

```powershell
# Test de conectividad con todas las APIs
autohome check-connections

# Deberías ver ✅ para cada servicio
```

**Resultado esperado:**
```
Service         Status                Details
─────────────────────────────────────────────────────
Clientify API   ✓ Connected          API token valid
Inmovilla API   ✓ Connected          API accessible
Idealista (PW)  ✓ Browser OK         Page loaded: Idealista
```

Si algo falla → consulta `/SETUP_ES.md` sección de troubleshooting.

---

### 5️⃣ Personalizar Reglas de Negocio

Edita **`rules/example_rules.yaml`** según tu lógica:

```yaml
rules:
  - name: "Mi Regla 1"
    conditions:
      - metric: visits
        operator: ">="
        value: 500
    action: notify_high_interest
    enabled: true
```

**Métricas disponibles:**
- `visits` — visitas totales
- `email_contacts` — contactos por email
- `phone_contacts` — contactos por teléfono
- `favorites` — guardados como favorito

---

### 6️⃣ Ejecución Manual del Pipeline

```powershell
# Ejecutar todo el flujo UNA VEZ
autohome run-pipeline

# O probar el scraper con una URL específica
autohome scrape-test "https://www.idealista.com/inmueble/XXXXXXX/"
```

---

### 7️⃣ Próximos Hitos (Roadmap)

#### Corto Plazo (Semana 1-2)
- [ ] Credenciales configuradas y testeadas
- [ ] ✅ check-connections funciona
- [ ] Primeras propiedades scrapeadas exitosamente
- [ ] Primeros deals creados en Clientify

#### Mediano Plazo (Semana 3-4)
- [ ] Implementar almacenamiento en SQLite
- [ ] Integrar APScheduler (ejecución automática cada 6h)
- [ ] Base de datos poblada con historial

#### Largo Plazo (Mes 2-3)
- [ ] Migración a PostgreSQL
- [ ] Despliegue en Azure/AWS
- [ ] Dashboard de métricas
- [ ] Notificaciones (email/Slack)

---

## 📚 Recursos

| Documento | Contenido | Idioma |
|-----------|----------|--------|
| `README.md` | Overview del proyecto | EN |
| `GETTING_STARTED.md` | Setup step-by-step | EN |
| `SETUP_ES.md` | Guía completa en español | ES |
| `docs/VIABILITY_ANALYSIS.md` | Análisis técnico completo | ES |
| `PROJECT_STATUS.md` | Estado actual del proyecto | EN |
| `docs/API_NOTES.md` | Referencias de APIs | EN |

---

## 🆘 Problemas Comunes

### "ModuleNotFoundError: No module named 'autohome'"
```powershell
pip install -e .
```

### "403 Forbidden" en Idealista
Aumenta los delays en `.env`:
```env
SCRAPER_DELAY_MIN_SECONDS=5
SCRAPER_DELAY_MAX_SECONDS=10
```

### Tests fallando
```powershell
python -m pytest tests/ -vv -s
```

### Lint errors
```powershell
ruff check src/ --fix
```

---

## 🚀 Deployment (Futuro)

Cuando estés listo para producción:

```powershell
# 1. Create Azure/AWS VM
# 2. Clone repo
# 3. Setup .env
# 4. Use Task Scheduler o cron:

# Windows Task Scheduler:
# Program: C:\path\to\AutoHome\.venv\Scripts\python.exe
# Arguments: -m autohome.cli run-pipeline
# Trigger: Daily at 00:00, repeat every 6 hours
```

---

## ✅ Summary

| Item | Status | Detalles |
|------|--------|----------|
| **Repo GitHub** | ✅ | https://github.com/Pabludo/AutoHome |
| **Código** | ✅ | 4 commits, todo sincronizado |
| **Documentación** | ✅ | EN + ES |
| **Environment** | ✅ | .venv creado, deps instaladas |
| **Conectores** | ✅ | Clientify, Inmovilla, Idealista (stubs) |
| **Tests** | ✅ | 2/2 pasando |
| **Lint** | ✅ | Limpio |
| **Credenciales** | ⏳ | Necesitas configurar .env |
| **Ejecución Real** | ⏳ | Lista para ejecutar |
| **Scheduling** | 🔜 | Phase 1 |
| **DB Persistence** | 🔜 | Phase 1 |

---

## 🎓 What Now?

1. **Lee** → SETUP_ES.md (configuración en español)
2. **Configura** → .env con tus credenciales
3. **Prueba** → `autohome check-connections`
4. **Personaliza** → rules/example_rules.yaml
5. **Ejecuta** → `autohome run-pipeline`

¡Tu plataforma está lista para despegar! 🚀

---

**Questions?** → Open an issue on https://github.com/Pabludo/AutoHome

**Last updated**: April 19, 2026
