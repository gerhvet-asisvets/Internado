---
name: agenda-personal
description: Procedimiento de AGENTE_03 para agenda y cronograma personal en el sistema Internado MINSA–DINACAVV.
user-invocable: false
---

# Agenda y cronograma personal — v1.1

## Procedimiento
Sigue la sección de método y entregables de tu ficha (`sistema/agentes/`). Esta skill crecerá con las lecciones aprobadas que surjan de tus órdenes de trabajo.

## Checklist de rotación o cambio de planta
1. Leer ACTIVIDADES y COLA_TAREAS y revisar con `list_events` el calendario desde una semana antes hasta una semana después del periodo, para detectar duplicados y conflictos.
2. Calcular días hábiles y semanas con una herramienta de fechas, no a mano.
3. Comprobar los feriados nacionales del periodo y si caen en día hábil.
4. Listar como DATO_FALTANTE lo que no se sepa: horario, dirección, contacto en planta, planta anterior, requisitos de ingreso y entregas finales.
5. Evento de día completo con fin exclusivo (el día siguiente al último), sin invitados y con notificationLevel NONE, solo con autorización L3.
6. Revisar conflictos con charlas o entregas sin fecha y con bloques personales recurrentes.

## Lecciones
Propón nuevas en el campo `propuesta_skill` del HANDOFF.
