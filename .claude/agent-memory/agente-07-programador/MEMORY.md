# Memoria de proyecto — AGENTE_07_PROGRAMADOR

Sin enlaces de Drive, IDs ni datos personales: este archivo está en un repositorio público.

## Entorno (comprobado en OT-2026-016)
- Las sesiones corren en Claude Code en la nube, en un contenedor efímero. Los subagentes tienen CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1: no pueden lanzar otros. Solo el hilo principal tiene Agent (se ve en get_session, lista de herramientas).
- El reloj del contenedor está en UTC. Para cualquier fecha de la bitácora usar `TZ=America/Panama date '+%Y-%m-%d %H:%M'`. Otras sesiones han anotado la hora UTC como hora de Panamá: no fiarse del orden horario de las filas antiguas.
- Herramientas de solo lectura útiles: list_triggers, get_environment, get_session y read_documentation (servidor claude-code-remote). Nunca create_trigger, update_trigger ni fire_trigger sin L3.
- Las tareas programadas en la nube clonan la rama POR DEFECTO, abren una sesión nueva en modo auto, y su prompt no vale como consentimiento. Las creadas por MCP quedan sin conectores si no se pasan explícitos. Sin solapamiento documentado: hace falta un lock propio.
- Documentación pública útil: code.claude.com/docs/en/routines.md, claude-code-on-the-web y settings.md (sección "Settings in cloud sessions"). Las páginas grandes se cortan: usar grep sobre el resultado guardado.

## Técnicas que funcionaron
- Trabajar en una rama sin tocar el checkout compartido: `git worktree add -b <rama> <ruta aparte> HEAD`. El Coordinador y otros subagentes usan el checkout principal al mismo tiempo.
- Subir a Drive por referencia (sha256:<hex>:<ruta>) solo funciona desde el directorio de trabajo o el scratchpad. Copiar antes al scratchpad lo que esté en un worktree. Comparar fileSize con `wc -c`.
- Los Docs creados desde markdown muestran fileSize "1": verificar exportando a text/plain.
- Planificador determinista en Python sin credenciales: el Coordinador lee las hojas con los conectores, guarda la instantánea JSON en el scratchpad y el script decide. Así no hay secretos en el código.
- Detector de IDs de Drive para las pruebas: token de 25 o más caracteres con al menos 3 dígitos, 3 mayúsculas y 3 minúsculas. Una regex simple da falsos positivos con nombres de funciones y valores de catálogo. No escribir un ID de ejemplo entero en el propio archivo de pruebas.
- En Sheets no hay comparar e intercambiar: un lock por registro solo de anexado (adquirir, latido, liberar), releer, y gana la primera fila activa.

## Errores que hay que evitar
- No dar por buena una prueba que pasa contra el reloj real: fijar `ahora` en las pruebas.
- `cmd | head -1` dentro de un bloque redirigido produce BrokenPipe: no truncar la salida que va a test_results.txt.
- Para validar un HANDOFF v2.1 usar `herramientas/handoff-validator/handoff_validator_v2.py` (OT-2026-005); la v1.0 rechaza los v2.1 y no se toca.

## Lecciones de OT-2026-005 (validador HANDOFF v2.1)
- Probar los catálogos contra 2-3 HANDOFF reales antes de fijarlos: los formatos de entregable de la plantilla (doc, slides, sheet, pdf, png, mp4, mp3) no cubren los reales (carpeta, py, md, txt, json, html, gs, js). Lo no cerrado en el contrato va como aviso con modo estricto opcional.
- En CATALOGOS el agente 04 se llama AGENTE_04_ASISTENCIAS (en v1.0 era AGENTE_04_ASISTENCIAS_ENTREGAS). actividad_id vacío es legítimo en OT de mantenimiento.
- download_file_content de Drive guarda el archivo en tool-results; copiarlo a un subdirectorio propio del scratchpad y leerlo con `python3 -I`. Nunca al repositorio.
- Los mensajes de error del validador nombran el campo, nunca el valor: así la salida se puede pegar en bitácora sin filtrar contenido.
- Si la OT pide commit en la rama actual, no sirve un worktree (la rama ya está en el checkout principal): añadir solo los archivos propios con `git add <rutas>` y comprobar `git status` limpio antes.
- La sesión se cortó por límite de uso a mitad de la OT: registrar en bitácora pronto (inicio y en_curso) permitió retomar sin duplicar filas.
