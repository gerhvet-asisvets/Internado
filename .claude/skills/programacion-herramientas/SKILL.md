---
name: programacion-herramientas
description: Procedimiento de AGENTE_07 para scripts, validadores y herramientas del sistema en el sistema Internado MINSA–DINACAVV.
user-invocable: false
---

# Scripts, validadores y herramientas del sistema — v1.1

## Procedimiento
Sigue la sección de método y entregables de tu ficha (`sistema/agentes/`).
- **Validar todo HANDOFF antes de subirlo** (OT-2026-005): `python herramientas/handoff-validator/handoff_validator_v2.py HO-AAAA-NNN.yaml` desde el scratchpad. Si es rechazado, corregirlo antes de subir; anotar la `huella_sha256` en la fila de HANDOFFS. Los HANDOFF de Drive usados para pruebas se descargan solo al scratchpad y nunca se copian al repositorio.
- **Apps Script sin despliegue** (OT-2026-019): separar la lógica en funciones puras en Code.gs y en un bloque INICIO_PURO/FIN_PURO de JS.html; cargar Code.gs con `vm.runInContext` y mocks de SpreadsheetApp, PropertiesService, CacheService, LockService y Utilities; el mock de la hoja de solo lectura lanza un error ante cualquier escritura; fijar el reloj en el contexto; repetir la suite con TZ=UTC y con la zona del script; vista previa con `google.script.run` simulado y captura con Chrome sin cabeza a 390 px. En vm, los arrays y Date son de otro realm: comparar con `Array.from` u `Object.prototype.toString`, no con `deepStrictEqual` ni `instanceof`.

## Lecciones
- **Fórmulas en Sheets por la API** (OT-2026-019): con configuración regional es_ES (coma decimal), los argumentos se separan con punto y coma (`=COUNTIFS(A:A;1;B:B;"x")`); con comas dan #ERROR!, y las funciones de un solo argumento no lo delatan. Leer siempre con get_values después de escribir fórmulas.
- **Fechas desde Apps Script** (OT-2026-019): no usar `new Date(y, m-1, d)`, que depende de la zona del entorno. Para Panamá (UTC-5, sin horario de verano) usar `new Date(Date.UTC(y, m-1, d, 5))` y leer con `Utilities.formatDate(v, "America/Panama", "yyyy-MM-dd")`.
- **Catálogos de un validador** (OT-2026-005): probarlos contra 2-3 archivos reales antes de fijarlos. Lo que el contrato no cierra (por ejemplo, formatos de entregable) va como aviso, con un modo estricto opcional. Decisión del SUPERVISOR 2026-11-19: los formatos fuera de plantilla siguen como aviso.

## Tareas abiertas
Ninguna. OT-2026-005 (handoff-validator v2.1) cerrada el 2026-11-19.
