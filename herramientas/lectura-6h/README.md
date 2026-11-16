# lectura-6h — planificador de la lectura de COLA_TAREAS cada 6 horas

**Estado: PROTOTIPO SIN DESPLEGAR. Programado y funcionando: NO.**
Origen: OT-2026-016, AGENTE_07_PROGRAMADOR, 2026-11-15. Versión 0.1.0.

## Qué es
Un planificador determinista que el Coordinador (hilo principal de Claude Code) ejecutaría en cada ciclo programado (00:00, 06:00, 12:00 y 18:00, America/Panama). Recibe una instantánea JSON de la hoja de bitácora y devuelve:

- la clasificación de cada OT (despachar, inspeccionar, evaluar, bloquear, aplazar o ignorar) con su motivo;
- el lock del ciclo (lease con caducidad) y la clave de despacho de cada OT, para no despachar dos veces;
- las filas de BITACORA y los eventos de CICLOS que el Coordinador escribiría;
- el informe del ciclo (JSON y markdown).

El script **no escribe en Google, no llama a la herramienta Agent y no evalúa**. Leer y escribir en Drive y Sheets lo hace el Coordinador con los conectores; despachar lo hace el hilo principal con Agent (los subagentes no pueden lanzar otros: `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`).

## Archivos
| Archivo | Contenido |
|---|---|
| `lectura_6h.py` | Planificador, lock, verificaciones e informe (solo biblioteca estándar, Python 3.9 o posterior) |
| `test_lectura_6h.py` | Pruebas P01-P12 de la solicitud técnica y S01-S06 de seguridad |
| `datos_ficticios/instantanea_ficticia.json` | 12 OT ficticias (OT-2099-*) que cubren todos los casos |
| `config.ejemplo.json` | Configuración de ejemplo (sin secretos). La real va fuera del repositorio: archivo en `LECTURA6H_CONFIG` o JSON en línea en la variable `LECTURA6H_CONFIG_JSON` del entorno de nube |
| `test_results.txt` | Resultado de la última ejecución de las pruebas |
| `(propuesta aplicada en el sistema 2.6)` | Diff propuesto (no aplicado) de la skill nueva lectura-ejecucion-6h, coordinacion-internado, agente-00-coordinador y CHANGELOG |

## Uso
```
python3 lectura_6h.py cron                      # expresión propuesta y próximos disparos
python3 lectura_6h.py planificar --snapshot instantanea.json --markdown
python3 lectura_6h.py planificar --snapshot instantanea.json --agent-disponible \
        --config "$LECTURA6H_CONFIG" --sesion "$CLAUDE_CODE_REMOTE_SESSION_ID"
python3 -m unittest -v test_lectura_6h
```
Sin `--agent-disponible`, ninguna OT se despacha: se bloquean y se avisa. Por defecto `dry_run` es `true`.

## Reglas que aplica
- **asignada / requiere_correccion:** se despachan solo si el asignado es un especialista del catálogo, tienen entradas y criterios, no dicen "pendiente de transferencia", cada OT citada en la descripción o en las entradas está aprobada o cerrada y su HANDOFF figura en entradas_urls, y no piden una acción L3 sin un permiso L3 específico (con el ot_id en el alcance) del SUPERVISOR.
- **en_curso:** solo se inspecciona: horas sin cambio, alerta de estancamiento o de marca de tiempo futura. Nunca se relanza.
- **pendiente_aprobacion:** nunca se ejecuta.
- **entregada:** pasa a evaluación por el Coordinador, que antes debe abrir todos los salida_urls y el HANDOFF (`verificar_evaluacion`) y comprobar que la entrega es del especialista (`verificar_entrega`).
- **Límites:** `max_trabajos_por_ciclo`, por prioridad (alta, media, baja), fecha límite y ot_id. `max_reintentos_despacho` para despachos sin efecto.
- **Interruptor:** una fila de PERMISOS con recurso `LECTURA_6H`, nivel L3 y otorgado_por SUPERVISOR. La última fila manda: `vigente` (dentro de su vigencia) activa el despacho, `parado` detiene el ciclo y cualquier otro valor deja el ciclo en solo lectura.

## Idempotencia (pestaña CICLOS propuesta, L3)
CICLOS es un registro **solo de anexado**, con los eventos `adquirir`, `latido`, `liberar` y `despacho`. El lock se deriva de él: un titular está activo mientras no haya `liberar` y su `lease_hasta` no haya pasado. Protocolo: leer, anexar `adquirir`, releer; gana la primera fila activa, y quien pierde anexa `liberar` con `perdido` y se retira. El evento `despacho` se anexa **antes** de llamar a Agent (escritura anticipada), con `clave_despacho = ot_id|estado|ultima_actualizacion`. Justo antes del despacho se relee la fila (`verificar_antes_de_despachar`). BITACORA nunca se usa como lock.

## Limitaciones
- Sheets no ofrece una operación atómica de comparar e intercambiar. La exclusión se apoya en el orden de las filas anexadas y en releer, lo que basta para un solo disparador cada 6 h, pero no es un lock distribuido fuerte.
- Las dependencias se deducen de las menciones OT-AAAA-NNN en el texto, porque la hoja no tiene columna de dependencias. Se propone añadir `depende_de` (L3).
- La detección de acciones L3 es por palabras clave y conservadora: ante la duda, bloquea.
- Las pruebas P02 (persistencia sin sesión), P05 (llamada real a Agent) y P12 (apagado del disparador real) no se pueden comprobar sin desplegar, y figuran como omitidas con su motivo.
