# Registro de cambios del sistema

## 2.6 — 2026-11-15
- **Skill nueva lectura-ejecucion-6h v1.0** (OT-2026-016, HO-2026-012, aprobada por el SUPERVISOR, A1): procedimiento del Coordinador para el ciclo programado de lectura de COLA_TAREAS a las 00, 06, 12 y 18 h (America/Panama), con despacho solo desde el hilo principal, lock con lease en la pestaña CICLOS, dry-run, límites por ciclo e informe. Se añade al campo `skills:` de agente-00-coordinador.
- coordinacion-internado: sección 5 bis, que remite al ciclo programado.
- Herramienta nueva `herramientas/lectura-6h` v0.1.0: planificador determinista sin credenciales y 48 pruebas (P01-P12 y S01-S06) con datos ficticios.
- Estructura de la bitácora: pestaña CICLOS (solo de anexado) y fila PER-2026-005 LECTURA_6H en PERMISOS (fase 1: solo_lectura durante 7 días).
- CONTRATO_COMUN sin cambios (sigue en 2.2).

## 2.5 — 2026-11-15
- **normativa-panama v1.2**, con las 3 propuestas de HO-2026-013 (OT-2026-013) aprobadas por el SUPERVISOR: búsqueda en Infojurídica por Gaceta, autoridad o número; revisar "DEROGADO POR" en la norma antigua antes de declarar que no existe norma, y regla de adopción de RTCA; checklist de competencias DINACAVV/MIDA, emergencias zoosanitarias vigentes y no dividir PDF con pdfunite. Lección: el DE 147/2022 es la norma nacional de aves.
- La propuesta de lectura cada 6 horas (OT-2026-016) pasa a numerarse 2.6.
- CONTRATO_COMUN sin cambios (sigue en 2.2).

## 2.4 — 2026-11-15
- **charlas-educativas v1.2**, con las 2 propuestas de HO-2026-010 (OT-2026-011) aprobadas por el SUPERVISOR: en charlas de 30 minutos o menos, cuestionario de 6 preguntas como máximo y ejercicio exprés dentro de la duración; extensión del documento de apoyo medida en el PDF exportado, con los anexos de control declarados aparte.
- CONTRATO_COMUN sin cambios (sigue en 2.2).

## 2.3 — 2026-11-15
- **Skills v1.1 con las 16 propuestas aprobadas por el SUPERVISOR**, surgidas de las revisiones independientes de ACT-2026-001 (OT-2026-006 a 009) y de OT-2026-010.
- normativa-panama: búsqueda por numsec cuando el buscador de Infojurídica falla; consulta de ambas fichas ante derogaciones de decretos modificatorios; conservar los requisitos del literal al resumir faltas; OCR con hilos limitados.
- investigacion-sanitaria: cotejo del título de cada estudio; opciones FSIS 2021 con todos sus parámetros y lectura del eCFR por API; criterio de adulteración no es límite crítico; checklist de la matriz de peligros.
- charlas-educativas: tiempos como bloques propios que no superan la duración pedida; reparto de claves del cuestionario; comprobación de cifras técnicas en el texto primario; contenidos operativos para inspectores y control de calidad.
- diseno-audiovisual: procedimiento de verificación de la conversión a Slides; rótulos sin recortes, ejemplos fieles a la regla y preparación para imprenta.
- agenda-personal: checklist de rotación o cambio de planta.
- contrato-comun (skill): cómo verificar un Doc creado desde markdown. El documento CONTRATO_COMUN no cambia (sigue en 2.2).

## 2.2 — 2026-11-15
- **Corrección de la falla de ACT-2026-001.** El Coordinador había corrido como subagente en segundo plano, sin la herramienta Agent, así que ejecutó los roles él mismo y se autoevaluó.
- El Coordinador pasa a ser el hilo principal de cada sesión del repositorio (`.claude/settings.json`) y solo gestiona.
- Los 8 especialistas quedan definidos como subagentes (`.claude/agents/`), cada uno con `contrato-comun`, su skill de especialidad y memoria de proyecto. Se despachan en primer plano.
- Skills nuevas: contrato-comun, coordinacion-internado, normativa-panama, investigacion-sanitaria, charlas-educativas, diseno-audiovisual, agenda-personal, asistencias-entregas, tareas-personales, programacion-herramientas. Las cuatro primeras de especialidad parten con las lecciones de ACT-2026-001.
- HANDOFF v2.1: campo opcional `propuesta_skill`.
- Contrato: activación con subagentes (sección 2), regla de independencia de la evaluación (sección 9), especialización por skills y memoria (sección 12).

## 2.1 — 2026-11-15
- El repositorio pasa a ser la fuente versionada del sistema: los cambios al contrato y a las fichas se hacen primero aquí y después se publican en Drive (contrato, sección 12).
- Regla nueva de privacidad: el repositorio es público; no se publican enlaces de Drive, datos personales ni productos (contrato, sección 11).
- Fichas de agentes sin cambios (2.0).

## 2.0 — 2026-11-15
- Contrato común único (`sistema/CONTRATO_COMUN.md`) que reemplaza INSTRUCCIONES_MAESTRAS v1.0, PROTOCOLO_INTERCAMBIO v1.0 y el contrato copiado en cada ficha.
- Comunicación entre sesiones mediante la hoja BITACORA_AGENTES (pestañas BITACORA, COLA_TAREAS, HANDOFFS, EVALUACIONES, PERMISOS, VERSIONES_SISTEMA, CATALOGOS) y archivos HANDOFF en Drive. Solo el Coordinador transfiere resultados.
- Se elimina la prohibición de escribir en Drive/Sheets; registrar es obligatorio. Leer y modificar, nunca borrar; toda modificación queda en BITACORA.
- Coordinador con procedimientos de gestión y rúbrica de evaluación (5 criterios, 0–10).
- Nuevo AGENTE_08_AUDIOVISUAL.
- AGENTE_01 entrega obligatoriamente un documento de apoyo de lectura previa; AGENTE_02 entrega informe completo con anexos reales.
- Nombres de carpetas alineados con Drive; nueva carpeta 10_AUDIOVISUALES.
- HANDOFF v2.0 (añade handoff_id, ot_id, plataforma, calidad; entregables con URL obligatoria).

## 1.0 — 2026-11-10
- Versión inicial: 8 sesiones especializadas en ChatGPT con traspaso manual de HANDOFF v1.0 (13 campos).
- Validador HANDOFF v1.0 (F3-001, 24/24 pruebas).
