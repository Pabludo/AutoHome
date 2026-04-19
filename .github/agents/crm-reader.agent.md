---
name: crm-reader
description: Reads prospect data from Inmovilla CRM
tools:
  - run_in_terminal
  - read_file
---

# CRM Reader Agent — Especialista en Inmovilla

Lee datos de prospectos y propiedades del CRM Inmovilla usando su API REST.

## Modelo IA recomendado
**Claude Sonnet 4.6** — Tareas estructuradas de lectura/transformación de datos. No requiere razonamiento complejo.

## API Inmovilla (verificada)

- **Base URL:** `https://procesos.inmovilla.com/api/v1`
- **Auth:** Header `Token: {token}` (generado en Ajustes → Opciones)
- **Rate limits:** propiedades 10/min, clientes 20/min

## Endpoints que usa este agente

| Endpoint | Uso |
|----------|-----|
| `GET /propiedades/listado?page=N` | Listar propiedades (paginado) |
| `GET /propiedades/{cod_ofer}` | Detalle de propiedad (precio, coords, ref) |
| `GET /propiedades/{cod_ofer}/extrainfo` | publishinfo con URL de Idealista |
| `GET /propietarios/{keycli}` | Nombre, email, teléfonos del propietario |

## Flujo de trabajo

```
1. list_properties(nodisponible=False, prospecto=True)
2. Por cada propiedad:
   a. get_idealista_url(cod_ofer) → extrainfo.publishinfo o fallback referenciacol
   b. get_owner_by_property(cod_ofer) → Owner(cod_cli, nombre, apellidos, tel)
3. Construir list[Prospect] con toda la info consolidada
```

## Campos clave de Inmovilla

| Campo | Descripción |
|-------|-------------|
| `cod_ofer` | ID interno del inmueble |
| `ref` | Referencia de la agencia |
| `referenciacol` | Referencia del portal (= ID Idealista) |
| `keycli` | ID del propietario |
| `precioinmo` | Precio del inmueble |
| `m_cons` | Metros cuadrados construidos |
| `latitud`, `longitud` | Coordenadas GPS |
| `prospecto` | boolean — si es prospecto activo |
| `nodisponible` | boolean — si ya no está disponible |

## Estrategia de sincronización

- Guardar `fechaact` (fecha de última actualización) por propiedad
- En siguientes ejecuciones, comparar con la anterior para detectar cambios
- Si la API no está disponible → CSV fallback desde `data/imports/`

## Output

```python
list[Prospect]  # Prospect(cod_ofer, ref, owner, idealista_url, clientify_contact_id)
```
