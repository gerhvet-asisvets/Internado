# Memoria de AGENTE_03_AGENDA

## Lecciones (OT-2026-010, rotación de planta)
- Calcular días hábiles y semanas con `date` en Bash; no a mano.
- Antes de crear un evento, list_events con margen de una semana antes y después del periodo, timeZone America/Panama: detecta duplicados y bloques personales recurrentes (p. ej. estudio nocturno y dominical) que solo chocan según el horario.
- Evento de día completo: create_event con allDay true, startTime 'AAAA-MM-DD', endTime = día siguiente al último (fin exclusivo), notificationLevel NONE y sin attendees. La respuesta trae start.date y end.date para verificarlo.
- Comprobar feriados nacionales del periodo (p. ej. 28 de noviembre) y si caen en día hábil; marcar como INTERPRETACION si no hay fuente oficial abierta.
- Datos que siempre faltan en un cambio de planta: horario, dirección, contacto en planta, planta anterior, requisitos de ingreso (indumentaria, carné de salud), entregas finales y actividades concretas.
- Revisar en ACTIVIDADES las actividades en_curso cuya fecha ya pasó: suelen no tener fecha real de presentación y chocan con la rotación.
- read_file_content muestra escapes de markdown (barras invertidas, asteriscos en tablas) que no están en el Doc; verificar con download_file_content en text/plain.
- En markdown para Doc, los saltos de línea simples se unen en un párrafo: usar línea en blanco o lista.
- Subir YAML: escribir en el scratchpad, validar con python yaml, sha256sum y base64Content 'sha256:<hex>:<ruta>' con disableConversionToGoogleType true.
