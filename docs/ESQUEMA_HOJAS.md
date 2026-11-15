# Esquema de las hojas de cálculo

## BITACORA_AGENTES_MINSA_2026_2027 (Drive: 09_ARCHIVO_HISTORICO)

Zona horaria de la hoja: America/Panama. Las listas desplegables leen la pestaña CATALOGOS.

| Pestaña | Columnas |
|---|---|
| BITACORA | registro_id, fecha_hora, agente, plataforma, actividad_id, ot_id, accion, recurso, recurso_url, detalle, valor_anterior, valor_nuevo, autorizado_por |
| COLA_TAREAS | ot_id, actividad_id, asignado_a, creado_por, fecha_creacion, descripcion, entradas_urls, criterios_aceptacion, prioridad, fecha_limite, estado, salida_urls, handoff_id, evaluacion_id, ultima_actualizacion |
| HANDOFFS | handoff_id, fecha_hora, origen, destino, plataforma, actividad_id, ot_id, archivo_url, estado, transferido_a_ot, observacion |
| EVALUACIONES | evaluacion_id, fecha_hora, ot_id, handoff_id, agente_evaluado, c1_completitud, c2_fuentes, c3_profundidad, c4_coherencia, c5_trazabilidad, puntaje_total, dictamen, observaciones, siguiente_paso, aprobacion_supervisor |
| PERMISOS | permiso_id, agente, recurso, nivel, alcance, otorgado_por, fecha, vigencia, estado |
| VERSIONES_SISTEMA | version, fecha, archivo, archivo_url, cambio, autorizado_por |
| CATALOGOS | agentes, plataformas, acciones, estados_ot, estados_handoff, dictamen, niveles_permiso |

### Catálogos
- **agentes:** SUPERVISOR, AGENTE_00_COORDINADOR … AGENTE_08_AUDIOVISUAL
- **plataformas:** Claude, ChatGPT, manual
- **acciones:** inicio_sesion, lectura, creacion, modificacion, entrega, evaluacion, transferencia, aprobacion, permiso, cambio_sistema, error, registro_pendiente, cierre_sesion
- **estados_ot:** pendiente_aprobacion, asignada, en_curso, entregada, en_evaluacion, aprobada, requiere_correccion, bloqueada, cerrada, cancelada
- **estados_handoff:** recibido, en_evaluacion, aprobado, requiere_correccion, transferido, archivado
- **dictamen:** aprobado, requiere_correccion, rechazado
- **niveles_permiso:** L0_redactar_analizar, L1_leer, L2_crear_y_modificar_con_registro, L3_accion_aprobada_por_supervisor

## CONTROL_INTERNO_MINSA_2026_2027 (Drive: carpeta raíz)

| Pestaña | Columnas |
|---|---|
| ACTIVIDADES | actividad_id, fecha, tipo, titulo, area, estado, evidencia_url, ultima_revision |
| TAREAS | tarea_id, actividad_id, titulo, prioridad, fecha_limite, estado, evidencia_url |
| ASISTENCIA_PERSONAL | actividad_id, fecha, asistencia, evidencia_url, observacion |
| ENTREGAS_PERSONALES | entrega_id, actividad_id, nombre, vencimiento, estado, archivo_url, confirmado_por |
| FUENTES_NORMATIVAS | documento_id, entidad, titulo, numero, fecha_emision, articulo, enlace_oficial, vigencia_verificada, fecha_consulta |
| PRODUCTOS | producto_id, actividad_id, tipo, titulo, version, archivo_url, revision |
| BITACORA_CAMBIOS | Histórico v1.0, cerrado desde 2026-11-15 (los registros continúan en BITACORA_AGENTES) |
