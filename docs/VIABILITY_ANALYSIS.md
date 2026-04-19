# Análisis de Viabilidad — AutoHome

## 1. Lectura de Métricas de Idealista (Scraping)

### Situación
- Idealista **no ofrece API pública** para estadísticas de inmuebles.
- La web devuelve **HTTP 403** ante requests directos (Cloudflare + anti-bot).
- Las estadísticas (visitas, contactos por email, favoritos) **son visibles para el propietario/agencia** cuando están logueados en su panel.

### Viabilidad: ✅ VIABLE (con matices)

**Opción A — Playwright con sesión autenticada (RECOMENDADA)**
- Playwright controlando Chromium puede autenticarse en Idealista.
- Una vez logueado, navegar al panel de estadísticas de cada inmueble.
- Extraer datos del DOM directamente.
- **Ventaja**: Simula usuario real, esquiva la mayoría de protecciones.
- **Riesgo**: Idealista puede cambiar el HTML, requiere mantenimiento de selectores.
- **Mitigación**: Selectores robustos + alertas cuando falla el parsing.

**Opción B — MCP Browser Tools**
- Usar un MCP de navegador que inyecte código en una sesión abierta.
- Menos fiable para automatización desatendida.
- Útil como complemento para debugging.

**Opción C — Extensión de navegador + API local**
- Una extensión Chrome que lea las estadísticas y las envíe a un endpoint local.
- Más manual, no escala.

### Recomendación
Playwright **headless** con login automatizado. Las estadísticas son datos PROPIOS del usuario (sus inmuebles), por lo que no hay problema legal. Implementar:
- Retry con backoff exponencial
- Rotación de User-Agent
- Delays aleatorios entre requests (2-5 seg)
- Captcha detection + alerta manual

---

## 2. Integración con Clientify

### Situación
- Clientify tiene **API REST documentada** en `developers.clientify.com`.
- Autenticación via **API Token** (Bearer token en headers).
- Endpoints principales:
  - `GET/POST /v1/contacts/` — Gestión de contactos
  - `GET/POST /v1/deals/` — Gestión de oportunidades/tarjetas
  - `GET/POST /v1/companies/` — Empresas
  - Webhooks para eventos
  - Campos personalizados

### Viabilidad: ✅ TOTALMENTE VIABLE
- API madura con buena documentación.
- Permite crear deals/tarjetas programáticamente.
- Soporta campos custom para enriquecer con métricas.
- Permite asignar a pipelines y stages específicos.

### Lo que podremos hacer:
1. Buscar contacto por email/teléfono
2. Crear/actualizar deal con datos del inmueble
3. Mover deal entre stages del pipeline según condiciones
4. Adjuntar notas con historial de métricas
5. Triggear automaciones de email (workflows de Clientify)

---

## 3. Integración con Inmovilla

### Situación
- Inmovilla ofrece un **módulo API REST** (puede requerir activación en el plan).
- Endpoints para acceder a:
  - Inmuebles (con URLs de portales asociados como Idealista)
  - Contactos/Prospectos
  - Demandas
  - Agendas

### Viabilidad: ✅ VIABLE (pendiente confirmar módulo API activo)
- Si el plan incluye API REST: integración directa.
- Si no: alternativa via export XML/CSV periódico o scraping del panel.

### Lo que necesitamos de Inmovilla:
1. Listar prospectos activos
2. Obtener URL de Idealista asociada a cada prospecto
3. Obtener datos de contacto del cliente (nombre, email, teléfono)
4. Estado del proceso de venta

---

## 4. Tecnología Recomendada

### Lenguaje: **Python 3.12+**
**Razones:**
- Ecosystem maduro para scraping (Playwright, BeautifulSoup, Scrapy)
- Excelente para APIs REST (httpx, requests)
- Pydantic para validación de datos
- APScheduler / Celery para scheduling
- Fácil transición a Django/FastAPI si se necesita interfaz web
- Menor curva de aprendizaje que Node.js para este tipo de tareas

### ¿Por qué NO Node.js?
- Playwright existe para ambos, pero el ecosystem de data processing es más fuerte en Python
- Las integraciones con APIs son igual de sencillas, pero la manipulación de datos es más natural en Python
- NO necesitamos un servidor web real-time (donde Node brillaría)

### ¿Django?
- **NO para la fase inicial**. Django es un framework web completo, y este proyecto es un pipeline de datos.
- **SÍ en el futuro** si se necesita:
  - Dashboard web para visualizar métricas
  - Panel de administración para configurar reglas
  - Interfaz para gestionar los envíos
- Alternativa más ligera: **FastAPI** (async, más simple)

### Automatización: Scripts directos con scheduler
- No necesitamos n8n/Node-RED/Flow para la fase inicial
- `APScheduler` es suficiente para correr tareas periódicas
- Si crece la complejidad → migrar a Celery + Redis

---

## 5. Base de Datos

### Recomendación: **SQLite → PostgreSQL**

**Fase 1 (Local/MVP):**
- **SQLite** — 0 configuración, fichero local, suficiente para cientos de inmuebles.
- Almacenar:
  - Historial de métricas (timestamp + inmueble + visitas/contactos/favoritos)
  - Mapping prospecto → inmueble → contacto
  - Log de acciones ejecutadas
  - Configuración de reglas/condiciones

**Fase 2 (Producción):**
- Migrar a **PostgreSQL** cuando:
  - Necesitemos acceso concurrente
  - El volumen supere miles de registros/día
  - Despleguemos en servidor

**¿Por qué DB propia?**
- Las APIs externas tienen rate limits
- Necesitamos historial temporal de métricas (Idealista no lo da)
- Las condiciones necesitan comparar "métrica actual vs hace 7 días"
- Log de auditoría de qué acciones se lanzaron y cuándo

---

## 6. Infraestructura

### Fase 1: **100% Local**
- El proyecto corre en la máquina de desarrollo
- Script lanzado manualmente o via Task Scheduler de Windows
- SQLite local
- Sin costes de infraestructura

### Fase 2: **Servidor dedicado**
Cuando sea necesario:
- **Azure VM** (si ya tenéis cuenta Azure) — B2s (~15€/mes)
- **AWS Lightsail** — $10/mes
- O un **VPS simple** (Hetzner, DigitalOcean)
- Añadir: Docker compose + cron jobs
- PostgreSQL en el mismo servidor o managed

### ¿Cuándo migrar a servidor?
- Cuando necesitéis ejecución desatendida 24/7
- Cuando haya múltiples usuarios / agencias
- Cuando se integre dashboard web

---

## 7. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Idealista bloquea scraping | Media | Alto | User-agent rotation, delays, headful mode, IP rotation |
| Idealista cambia HTML | Alta | Medio | Selectores con fallback, tests E2E, alertas |
| Inmovilla sin API REST | Baja | Alto | Export CSV manual, scraping del panel |
| Rate limits de Clientify | Baja | Bajo | Queue con throttling |
| CAPTCHA en Idealista | Media | Alto | Detección + alerta + resolución manual |

---

## 8. Protección de Datos (GDPR/LOPD)

- ✅ Los datos de métricas de Idealista son del PROPIO usuario (sus inmuebles)
- ✅ Los prospectos han dado consentimiento (indicado por el usuario)
- ⚠️ Implementar:
  - Encriptación de datos personales en DB
  - Log de accesos
  - Mecanismo de borrado/exportación de datos (derecho al olvido)
  - Datos de acceso en variables de entorno, NUNCA en código

---

## 9. Conclusión

### El proyecto es **VIABLE** ✅

**Fortalezas:**
- Stack tecnológico probado (Python + Playwright + REST APIs)
- Flujo de datos claro: Inmovilla → Idealista → Condiciones → Clientify
- Escalable de local a cloud sin reescritura
- Sin dependencia de APIs propietarias complejas

**Debilidades:**
- Fragilidad del scraping de Idealista (principal riesgo)
- Dependencia de que Inmovilla tenga API activa

**Timeline estimado:**
- Fase 0 (Actual): Estructura + pruebas de conectividad → 1-2 semanas  
- Fase 1: MVP funcional (scraping + condiciones + Clientify) → 3-4 semanas
- Fase 2: Dashboard + scheduling automático → 2-3 semanas adicionales
