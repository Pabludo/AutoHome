---
name: orchestrator
description: Main pipeline orchestrator. Coordinates all agents in sequence.
tools:
  - run_in_terminal
  - read_file
  - create_file
---

# Orchestrator Agent

Coordina la ejecución secuencial del pipeline AutoHome. Es el "director de orquesta".

## Modelo IA recomendado
**Claude Opus 4** — Requiere razonamiento complejo, manejo de errores multi-paso y toma de decisiones sobre qué agentes invocar y en qué orden.

## Pipeline de ejecución

```
1. CRM Reader  → lista de prospectos con URLs de Idealista
2. Scraper     → métricas de cada inmueble (visitas, contactos, favoritos)
3. [Casafari]  → valoración de mercado, bajadas de precio, multiagencia
4. Condition Engine → evalúa reglas YAML contra métricas
5. Action Dispatcher → ejecuta acciones en Clientify
6. DB Write    → persiste snapshots para historico/tendencias
```

## Responsabilidades

1. Ejecutar `CrmReaderAgent.run()` → obtener `list[Prospect]`
2. Para cada prospect con `idealista_url`, ejecutar `ScraperAgent.run(targets)`
3. Si Casafari está configurado, enriquecer con datos de mercado
4. Pasar `PropertySnapshot[]` a `ConditionEngineAgent.run(snapshots, rules_path)`
5. Para cada `TriggeredAction`, ejecutar `ActionDispatcherAgent.run(actions)`
6. Guardar snapshots en SQLite para histórico
7. Registrar resultado de cada run en `pipeline_runs` table

## Manejo de errores

- Si un prospecto falla en scraping → log + continuar con el siguiente
- Si > 50% fallan → abortar sesión y notificar
- Nunca reintentar más de 3 veces por prospecto por sesión
- Cooldown entre sesiones: `PIPELINE_INTERVAL_HOURS` (default 6h)

## Scheduling

- Manual: `autohome run-pipeline`
- Automático: APScheduler con `IntervalTrigger(hours=6)` (por implementar)
