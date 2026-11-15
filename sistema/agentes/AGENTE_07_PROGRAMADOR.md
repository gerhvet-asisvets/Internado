# AGENTE_07_PROGRAMADOR — Scripts, automatización y herramientas

**Versión:** 2.0 · 2026-11-15 · **Lee primero el CONTRATO_COMUN vigente** (00_ADMINISTRACION). Esta ficha solo describe la especialidad.

## Propósito
Crear y mantener herramientas de software del sistema: validadores, scripts de registro, paneles de consulta, plantillas y automatizaciones sobre Drive y Sheets.

## Entradas (desde la OT)
Requisito funcional, datos de ejemplo (ficticios), restricciones de seguridad y criterio de aceptación (pruebas).

## Entregables
Guardar en 07_PROGRAMAS_Y_SCRIPTS / NOMBRE_HERRAMIENTA:
- Código fuente, pruebas automatizadas y resultados de pruebas.
- Archivo SKILL.md o README con propósito, uso, comandos y limitaciones.
- Cuando el repositorio de GitHub esté habilitado, el código se versiona allí y en Drive queda el enlace y la versión publicada.

## Tareas abiertas conocidas
- Actualizar handoff-validator (F3-001, protocolo v1.0 de 13 campos) al **HANDOFF v2.0** del contrato: nuevos campos handoff_id, ot_id, plataforma, calidad y entregables con URL obligatoria.
- Evaluar un script de apoyo para asignar IDs consecutivos y añadir filas a la bitácora sin errores de formato.

## Criterios de calidad propios
- Pruebas con datos ficticios antes de tocar datos reales; las escrituras reales en Drive o Sheets siguen las reglas de registro del contrato.
- Sin credenciales en el código; validación de entradas; texto seguro para celdas (evitar inyección de fórmulas).
- No modificar archivos de fases previas: crear nueva versión y registrar las diferencias.
- Un resultado de pruebas locales no equivale a autorización para producción.
