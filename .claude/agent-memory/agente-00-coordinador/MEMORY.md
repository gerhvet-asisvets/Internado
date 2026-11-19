# Memoria del Coordinador

## Tarea programada de lectura 6h (2026-11-16)
- create_trigger desde la sesión no guarda conectores (parámetro no disponible en la organización) ni el repositorio como fuente: la sesión disparada arranca sin Drive/Sheets y sin repo. El supervisor los añade editando la tarea en claude.ai; después, "ejecutar ahora" sirve de prueba.
- La sesión disparada con repo carga el coordinador, los agentes y la skill, y tiene Agent. Coste observado: unos 1,5 USD por ciclo en solo lectura.
- Colisión de IDs de BITACORA entre el ciclo programado y la sesión del Coordinador: usar bloques distintos (el ciclo continúa la serie 00xx; la sesión interactiva usa un bloque reservado).
- Un subagente lanzado aunque sea "en primer plano" corre async; un límite de uso lo corta y se reanuda con SendMessage, revisando antes qué archivos ya creó.
