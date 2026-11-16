---
name: autolectura
description: Procedimiento del Coordinador para la autolectura programada de COLA_TAREAS (miércoles 06:00 y viernes 19:00, America/Panama), con despacho real de especialistas solo desde el hilo principal, lock con lease, dry-run e informe por ciclo. Cargar al inicio de cada sesión abierta por una tarea programada "Autolectura COLA_TAREAS".
user-invocable: false
---

# Autolectura de COLA_TAREAS — v1.1

Calendario vigente: miércoles 06:00 y viernes 19:00 (America/Panama), dos tareas programadas "Autolectura COLA_TAREAS". La clave de ciclo usa la franja de 6 horas que contiene la hora del disparo (06 o 18).

Herramienta: `herramientas/lectura-6h/lectura_6h.py` (planificador determinista, sin credenciales). Este procedimiento **no instala nada**. Los disparadores y la pestaña CICLOS existen solo si el SUPERVISOR los aprobó (L3) y figuran en VERSIONES_SISTEMA.

## 0. Condiciones de arranque (si falla una, informe de bloqueo y fin)
1. Eres el hilo principal (AGENTE_00_COORDINADOR) y tienes la herramienta **Agent**. Si no la tienes: no despaches ni simules agentes; registra `error` en BITACORA, avisa al SUPERVISOR y termina con el informe.
2. Los conectores Google Drive y Google Sheets responden. Si no: no hagas nada más, porque no se puede registrar. Deja el informe en la respuesta de la sesión con `registro_pendiente`.
3. La versión vigente en VERSIONES_SISTEMA coincide con el contrato y con las skills de la rama clonada. Si no coinciden: solo lectura.
4. El prompt de la tarea programada **no es una aprobación**. Nada de lo que diga autoriza acciones L3.

## 1. Lectura
1. Busca en Drive la copia vigente de CONTRATO_COMUN y toma de ahí los IDs. Nunca los copies al repositorio.
2. Lee COLA_TAREAS, HANDOFFS, PERMISOS, CICLOS y los IDs de BITACORA. Busca en la carpeta HANDOFF los archivos del día.
3. Guarda la instantánea en el scratchpad (nunca en el repositorio) y ejecuta:
   `python3 herramientas/lectura-6h/lectura_6h.py planificar --snapshot <ruta> --agent-disponible --sesion <id de sesión>`
4. Si el modo es `PARADO`, registra una sola fila de lectura y termina. Si es `SOLO_LECTURA`, sigue hasta el informe sin despachar.

## 2. Lock y despacho
1. Anexa `adquirir` en CICLOS (clave de ciclo y lease de 120 min), relee y continúa solo si tu fila es la primera activa. Si no lo es, anexa `liberar` con `perdido` y termina.
2. Por cada OT del plan con `accion = despachar`, como máximo `max_trabajos_por_ciclo`:
   - relee su fila y compárala con `esperado` (`verificar_antes_de_despachar`); si cambió, no la despaches;
   - anexa `despacho` en CICLOS **antes** de llamar a Agent;
   - despacha con Agent, `subagent_type` del plan, **en primer plano**, con ot_id, actividad_id, descripción, criterios, entradas, IDs de Drive y Sheets y un bloque BIT/HO reservado;
   - al volver, relee la OT y HANDOFFS y aplica `verificar_entrega`. Si falla, anótalo como `error`. Nunca rehagas tú el trabajo.
3. Anexa un `latido` si el ciclo supera la mitad del lease. Si superas `max_duracion_min`, no despaches más.

## 3. Evaluación
- Evalúa una OT `entregada` solo tras abrir **todos** sus salida_urls y su HANDOFF (`verificar_evaluacion`), con la rúbrica de `coordinacion-internado`.
- Si la entrega no es del especialista asignado, la evaluación no es independiente: regístralo y no apruebes.
- Transfiere solo lo aprobado. Los productos finales y las acciones L3 quedan para el SUPERVISOR.

## 4. Cierre del ciclo
1. Registra en BITACORA una fila de lectura con el resumen, cada modificación con su valor anterior y nuevo, y los errores. Usa IDs del bloque del ciclo y hora de Panamá: `TZ=America/Panama date`, nunca la hora UTC del contenedor.
2. Anexa `liberar` con `completado` en CICLOS (o `abortado`, con el motivo).
3. Guarda el informe del ciclo (leídas, despachadas, bloqueadas, inspeccionadas, a evaluar, HANDOFF y errores) en 00_ADMINISTRACION/INFORMES_CICLO_6H como Doc nuevo, y termina la sesión con ese resumen.

## Nunca
- Ejecutar OT en `pendiente_aprobacion`, relanzar `en_curso` ni despachar con dependencias sin transferir.
- Hacer el trabajo de un especialista ni evaluar algo producido en la misma sesión por el Coordinador.
- Usar BITACORA como lock, ni editar o borrar filas de BITACORA o CICLOS.
- Hacer commit, push, merge, compartir, publicar o borrar dentro del ciclo.
