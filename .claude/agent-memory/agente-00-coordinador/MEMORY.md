# Memoria del Coordinador

## Tarea programada de lectura 6h (2026-11-16)
- create_trigger desde la sesión no guarda conectores (parámetro no disponible en la organización) ni el repositorio como fuente: la sesión disparada arranca sin Drive/Sheets y sin repo. El supervisor los añade editando la tarea en claude.ai; después, "ejecutar ahora" sirve de prueba.
- La sesión disparada con repo carga el coordinador, los agentes y la skill, y tiene Agent. Coste observado: unos 1,5 USD por ciclo en solo lectura.
- Colisión de IDs de BITACORA entre el ciclo programado y la sesión del Coordinador: usar bloques distintos (el ciclo continúa la serie 00xx; la sesión interactiva usa un bloque reservado).
- Un subagente lanzado aunque sea "en primer plano" corre async; un límite de uso lo corta y se reanuda con SendMessage, revisando antes qué archivos ya creó.

## OT de app Apps Script (2026-11-16)
- AGENTE_07 en async (aunque se pidió primer plano) sí pudo ejecutar Node y Chrome local y subir binarios: unos 20 min y 107 llamadas para app + hoja + guía + 13 pruebas.
- Para evaluar código entregado en Drive: leer cada archivo con read_file_content (los escapes de markdown son del lector, no del archivo) y comprobar el modifiedTime del archivo de solo lectura frente a la hora de inicio del agente.
