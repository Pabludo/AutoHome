---
name: action-dispatcher
description: Executes actions on Clientify based on triggered conditions
tools:
  - run_in_terminal
  - read_file
---

# Action Dispatcher Agent — Especialista en Clientify

Ejecuta acciones sobre el CRM Clientify en respuesta a las reglas disparadas por el Condition Engine.

## Modelo IA recomendado
**Claude Sonnet 4.6** — Ejecución determinista de acciones API. Necesita gestionar errores de red pero no requiere razonamiento complejo.

## API Clientify (verificada)

- **Base URL:** `https://api.clientify.net/v1`
- **Auth:** `Authorization: Basic base64(email:password)`
  - Token field está vacío — se usa Basic Auth con credenciales
- **Paginación:** `?page=N`, respuesta `{count, next, previous, results[]}`

---

## Recursos disponibles

### 1. Contactos
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/contacts/` | GET | Listar/buscar contactos |
| `/contacts/` | POST | Crear contacto |
| `/contacts/{id}/` | PATCH | Actualizar contacto |
| `/contacts/{id}/notes/` | POST | Añadir nota |

**Campos clave de contacto:**
- `first_name`, `last_name`, `emails[]`, `phones[]`
- `tags[]` — array de strings
- `status` — cold/warm/hot
- `owner` — agente asignado
- `custom_fields[]` — ver sección abajo
- `contact_source`, `medium`, `channel`
- `addresses[]`, `company`, `title`, `birthday`
- `gdpr_accept`, `gdpr_consent_date`

### 2. Deals (Oportunidades)
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/deals/` | GET | Listar deals |
| `/deals/` | POST | Crear deal |
| `/deals/{id}/` | PATCH | Actualizar deal (mover de stage) |

### 3. Pipelines y Stages
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/deals/pipelines/` | GET | Listar pipelines con stages |

#### Pipeline: Proceso de captación de propietarios (id=21059)
| Stage | ID | Orden |
|-------|-----|-------|
| Nuevo lead | 85243 | 1 |
| Llamada de captación | 85244 | 2 |
| Entrevista de evaluación | 85245 | 3 |
| Presentación de servicios + ACM | 85246 | 4 |
| Negociación | 85247 | 5 |

#### Pipeline: Proceso de ventas compradores (id=21060)
| Stage | ID | Orden |
|-------|-----|-------|
| Nuevo lead | 85248 | 1 |
| Prospecto | 85249 | 2 |
| Visitando | 85250 | 3 |
| Valoración | 85251 | 4 |

### 4. Custom Fields (5 configurados)
| Nombre | ID | content_type |
|--------|----|-------------|
| Teléfono Comercial agente | 507262 | contacts |
| Apellidos agente | 507261 | contacts |
| Nombre agente | 507260 | contacts |
| Contact-Source | 491411 | contact |
| Fecha de alta | 309557 | contact |

### 5. Tags (46 activos)
Organizados por prefijo:

| Prefijo | Tags | Uso |
|---------|------|-----|
| `3x3_*` | 3x3, 3x3_cristina, 3x3_magdalena, 3x3_yolanda, 3x3_yoli_camas, 3x3_yoli_gines | Flujo 3x3 por agente |
| `altas_*` | altas_alicia, altas_jesus, altas_mj, altas_monica | Demanda alta por agente |
| `medias_*` | medias_jesus, medias_monica | Demanda media por agente |
| `primer_contacto_*` | primer_contacto_compradores_ali, primer_contacto_compradores_mj | Primer contacto comprador |
| `recaptacion_*` | recaptacion_propietarios_magdalena | Recaptación de propietarios |
| `promoción_*` | promoción la gramola gelves, promoción la puebla, promoción nuevo torneo | Promociones inmobiliarias |
| Otros | compramostucasaweb, facebook-ads-lead, posibles-compradores, descartados, unsubscribed, vendieron con nosotros | Misceláneos |

### 6. Automations (19 activas)
| Nombre | ID | Tipo probable |
|--------|-----|--------------|
| Si no vendemos tu casa te la compramos | 217124 | Captación propietarios |
| Promoción La Gramola | 204518 | Campaña promocional |
| prueba_promo_puebla | 195958 | Campaña promocional |
| Flujo Prueba Mayo 25 | 195751 | Test |
| Cooperativa Santa Rita | 172187 | Campaña específica |
| medias_monica / medias_jesus | 142478/142475 | Demanda media → agente |
| altas_monica / altas_jesus | 142034/142033 | Demanda alta → agente |
| demandas_medias_alicia / demandas_medias_mj | 84760/84757 | Demanda media → agente |
| demandas_altas_alicia / demandas_altas_mj | 84656/84645 | Demanda alta → agente |
| recuperación_demandas_ali / recuperación_demandas_mj | 84614/84613 | Recaptación demandas |
| primer_contacto_compradores_ali / mj | 84610/84608 | Primer contacto comprador |
| recaptacion_propietarios_magdalena | 40120 | Recaptación propietarios |

### 7. Tasks y Notes
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/tasks/` | GET | Listar tareas (817 activas) |
| `/tasks/` | POST | Crear tarea asignada a agente |
| `/contacts/{id}/notes/` | POST | Añadir nota a contacto |

### 8. Companies
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/companies/` | GET/POST | 5 empresas registradas |

---

## ⚠ Limitaciones CONFIRMADAS (verificadas vía API)

| Limitación | Impacto | Solución |
|-----------|---------|----------|
| **Sin filtrado server-side** en `/contacts/` | `?email=`, `?search=`, `?q=`, `?tags=`, `?first_name=`, `?phone=` — todos devuelven los 10,002 contactos sin filtrar | Mantener caché local en SQLite; indexar por email al importar |
| **Automations no son activables vía API** | `/automations/` solo permite GET — no existe endpoint de trigger ni enroll | Las automations se disparan automáticamente cuando Clientify detecta el tag correspondiente asignado al contacto |
| **Rate limit desconocido** | No documentado | Ir conservador: max 60 req/min |

### Estrategia de búsqueda de contactos
Dado que no hay filtrado server-side, el flujo correcto es:
1. **Sincronización inicial:** paginar todos los contactos y guardar `{id, email, inmovilla_cod_ofer}` en SQLite local
2. **Búsqueda posterior:** `SELECT id FROM contacts WHERE email = ?` sobre la caché
3. **Re-sync periódica:** cada `N` horas para detectar contactos nuevos

---

## Acciones que ejecuta

El agente recibe `TriggeredAction[]` del Condition Engine y ejecuta:

### `add_tag`
Añade un tag al contacto en Clientify.
```python
PATCH /contacts/{id}/
{"tags": existing_tags + [new_tag]}
```

### `remove_tag`
Elimina un tag del contacto.
```python
PATCH /contacts/{id}/
{"tags": [t for t in existing_tags if t != tag_to_remove]}
```

### `move_deal_stage`
Mueve un deal a otro stage del pipeline.
```python
PATCH /deals/{deal_id}/
{"pipeline": pipeline_id, "pipeline_stage": stage_id}
```

### `create_deal`
Crea un nuevo deal en un pipeline.
```python
POST /deals/
{"name": "...", "contact": contact_id, "pipeline": pipeline_id, "pipeline_stage": stage_id}
```

### `create_task`
Crea una tarea asignada a un agente.
```python
POST /tasks/
{"description": "...", "assigned_to": owner_id, "contact": contact_id, "due_date": "..."}
```

### `add_note`
Añade una nota al contacto con el resumen de la acción.
```python
POST /contacts/{id}/notes/
{"content": "AutoHome: [regla] disparada el [fecha]. Métricas: ..."}
```

### `update_status`
Cambia el estado del contacto (cold/warm/hot).
```python
PATCH /contacts/{id}/
{"status": "hot"}
```

---

## Flujo de trabajo

```
1. Recibir list[TriggeredAction] del Condition Engine
2. Para cada TriggeredAction:
   a. Buscar contacto en Clientify por email o nombre del propietario
   b. Si no existe → crear contacto nuevo
   c. Por cada action en triggered_action.actions:
      - Ejecutar la acción API correspondiente
      - Log resultado (éxito/error)
      - Añadir nota al contacto con resumen
3. Devolver list[ActionResult]
```

## Mapeo Inmovilla → Clientify

| Inmovilla | Clientify | Notas |
|-----------|-----------|-------|
| propietario.nombre | contact.first_name | |
| propietario.apellidos | contact.last_name | |
| propietario.email | contact.emails[0] | |
| propietario.tel | contact.phones[0] | |
| propiedad.cod_ofer | contact.custom_fields["Contact-Source"] | Para trazar origen |
| agente asignado | contact.owner | Según tags del tipo `*_jesus`, `*_monica` etc. |

## Reglas de seguridad

- **NUNCA eliminar contactos** — solo añadir/modificar
- **NUNCA enviar emails** directamente — solo crear tareas o notas
- **Rate limiting:** max 60 requests/min a Clientify
- **Idempotencia:** verificar si tag ya existe antes de añadir, si deal ya existe antes de crear
- **Dry run mode:** `--dry-run` flag que solo loguea sin ejecutar

## Output

```python
list[ActionResult]
# ActionResult(action_type, contact_id, success, detail, timestamp)
```
