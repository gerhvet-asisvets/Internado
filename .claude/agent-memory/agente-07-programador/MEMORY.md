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
- Apps Script sin desplegar (OT-2026-019): cargar Code.gs en Node con `vm.runInContext` y mocks de SpreadsheetApp, PropertiesService, CacheService, LockService y Utilities. Parte pura del cliente entre marcas `INICIO_PURO`/`FIN_PURO` en JS.html. El mock de la hoja de solo lectura lanza un error ante cualquier escritura, y así se prueba "nunca escribir en X". Reloj fijo sustituyendo `hoyTexto_` en el contexto.
- Vista previa de una app de HtmlService: inyectar un `google.script.run` simulado con respuestas generadas por los mocks y capturar con `google-chrome --headless=new --window-size=390,1500 --virtual-time-budget=3000 --screenshot`. Chrome está instalado en el contenedor; Playwright no. Rotular la captura como PRUEBA con datos ficticios.
- IDs ficticios en las pruebas: solo minúsculas y guiones bajos, de 20 o más caracteres. Así pasan `extraerId_` y no los marca el detector de IDs.
- Implementación, autorización y uso compartido de una app web son L3: se entregan el código, una guía para el SUPERVISOR y las pruebas manuales marcadas como pendientes.

## Errores que hay que evitar
- Hojas en es_ES: en las fórmulas escritas por la API, el separador es `;`. Con `,` todas dan #ERROR! (las de un solo argumento no lo delatan). Leer siempre con get_values después de escribir.
- `new Date(y, m-1, d)` depende de la zona del proceso. Para Panamá, usar `new Date(Date.UTC(y, m-1, d, 5))`. Repetir las suites con TZ=UTC además de la zona del script.
- En `vm`, los arrays y Date del contexto son de otro realm: `assert.deepStrictEqual` e `instanceof` fallan. Usar `Array.from` u `Object.prototype.toString`.
- La prueba "el cliente no usa innerHTML" también falla si la palabra aparece en un comentario.
- No dar por buena una prueba que pasa contra el reloj real: fijar `ahora` en las pruebas.
- `cmd | head -1` dentro de un bloque redirigido produce BrokenPipe: no truncar la salida que va a test_results.txt.
- El handoff-validator del repositorio es v1.0 y rechaza los HANDOFF v2.1 (está pendiente la OT-2026-005); validar el v2.1 con yaml.safe_load más comprobaciones propias.
