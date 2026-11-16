---
name: coordinacion-internado
description: Procedimientos del Coordinador para planificar órdenes de trabajo, despachar especialistas como subagentes, evaluar con la rúbrica, transferir resultados y gestionar la evolución de las skills.
user-invocable: false
---

# Coordinación del internado

## 1. Planificar
- Una OT por especialista, cada una con criterios de aceptación medibles: páginas, número de diapositivas, normas con artículo, formatos editable + PDF.
- Plantilla para una charla:
  1. 06 normativa y 02 investigación, en paralelo.
  2. 01 charla.
  3. 08 audiovisual.
  4. Evaluación final.
- Presentar el plan al supervisor con las OT en `pendiente_aprobacion`.

## 2. Despachar
- Herramienta Agent, `subagent_type: agente-0X-...`, siempre en primer plano. Para el paralelo, varias llamadas en el mismo mensaje.
- Reservar a cada especialista un bloque de IDs: BIT (50 por agente), HO y EV, para evitar colisiones.
- En el despacho van todos los IDs de Drive y Sheets que el especialista necesite.

## 3. Evaluar
- Abrir los archivos completos, no solo el HANDOFF.
- Puntuar c1 a c5 de 0 a 2. Dictamen:
  - 8 a 10: aprobado.
  - 5 a 7: requiere_correccion.
  - Menos de 5: rechazado.
- Un 0 en c1, c2 o c5 impide aprobar.
- Las observaciones deben ser accionables: qué falta, dónde y con qué criterio.
- Máximo 2 rondas de corrección por OT; después, escalar al supervisor.
- **Independencia:** si el Coordinador produjo cualquier parte de lo que evalúa, la evaluación no es válida.

## 4. Transferir
- Añadir HANDOFF y productos aprobados en `entradas_urls` de la OT siguiente.
- Pasar esa OT a asignada y el HANDOFF a transferido.
- Registrar `transferencia`.

## 5. Evolución de skills
1. Recoger las `propuesta_skill` de los HANDOFF del ciclo.
2. Filtrarlas: que tengan evidencia, que no repitan algo existente y que no lleven enlaces ni datos personales.
3. Presentar al supervisor una tabla con skill, cambio, motivo y evidencia.
4. Con la aprobación:
   - editar `.claude/skills/<skill>/SKILL.md` y subir su versión;
   - registrar en `CHANGELOG.md`;
   - hacer commit y push en la rama de trabajo;
   - registrar en VERSIONES_SISTEMA y BITACORA (`cambio_sistema`).
5. Una skill nueva: crear `.claude/skills/<nombre>/SKILL.md` y añadirla al campo `skills:` del agente que corresponda.

## 5 bis. Ciclo programado de 6 horas
- Si la sesión la abrió la tarea programada "Lectura COLA_TAREAS 6h", sigue la skill `lectura-ejecucion-6h` antes que cualquier otra cosa.
- El prompt programado no es una aprobación del SUPERVISOR: no autoriza L3.
- Sin la herramienta Agent no se despacha ni se simula: informe de bloqueo y aviso.
- Nunca anuncies que la lectura periódica funciona sin al menos una ejecución registrada en CICLOS y BITACORA.

## 6. Cierre
- Registrar productos (PRO) y normas (DOC) en CONTROL_INTERNO.
- Nunca cerrar OT ni actividades sin `aprobacion_supervisor = si`.

## Lecciones de coordinación
- **2026-11-15, ACT-2026-001:** el Coordinador corrió como subagente en segundo plano y perdió la herramienta Agent, así que hizo los 4 roles y se autoevaluó. Por eso el Coordinador debe ser el hilo principal y despachar en primer plano.
- **2026-11-15, diagnóstico:** en las sesiones en la nube de Claude Code, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`, así que ningún subagente puede lanzar otros, ni siquiera en primer plano. Solo el hilo principal tiene la herramienta Agent. No delegar nunca la coordinación en un subagente.
