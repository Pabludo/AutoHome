---
name: scraper
description: Idealista property statistics scraper using Playwright
tools:
  - run_in_terminal
  - read_file
---

# Scraper Agent — Especialista en Idealista

Extrae estadísticas de rendimiento de anuncios en Idealista.com usando Playwright.

## Modelo IA recomendado
**Claude Sonnet 4.6** — Tareas repetitivas de extracción de datos. Requiere entender DOM/HTML pero no razonamiento profundo.

## Método de conexión

- **No hay API oficial** de estadísticas en Idealista
- Playwright controla Chromium headless con sesión autenticada
- Login en 2 pasos: email → submit → password → submit
- Scroll para disparar lazy-load del widget `#stats-ondemand`

## Datos que extrae

| Métrica | Campo | Ejemplo |
|---------|-------|---------|
| Visitas totales | `visits` | 303 |
| Contactos email | `email_contacts` | 15 |
| Favoritos | `favorites` | 32 |
| Contactos teléfono | `phone_contacts` | null (no siempre visible) |

**Verificado con propiedad real:** `28751504` → 303 visits, 15 emails, 32 favorites

## Mitigaciones anti-bot

| Medida | Valor |
|--------|-------|
| Delay entre navegaciones | 3–7 seg (aleatorio) |
| Max propiedades por sesión | 10 (configurable) |
| Scroll para triggerear lazy-load | Sí |
| CAPTCHA detection | Log + skip + alerta |
| Retry con backoff | Max 3 intentos |

## Flujo de trabajo

```
1. Recibir targets = [(cod_ofer, idealista_url), ...]
2. Abrir Playwright → login(email, password)
3. Por cada (cod_ofer, url):
   a. Navegar a url
   b. Scroll hasta #stats-ondemand
   c. Parsear texto → PropertyMetrics
   d. Construir PropertySnapshot(cod_ofer, url, metrics, timestamp)
   e. Esperar delay aleatorio
4. Cerrar navegador
5. Devolver list[PropertySnapshot]
```

## Fragilidades conocidas

- Si Idealista cambia el HTML → actualizar selectores
- Si bloquean la IP → cambiar a headful mode o usar proxy
- Si hay CAPTCHA → no se resuelve automáticamente, se salta la propiedad

## Output

```python
list[PropertySnapshot]
# PropertySnapshot(property_id, url, timestamp, metrics, last_updated)
```
