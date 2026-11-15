# Internado MINSA–DINACAVV 2026–2027 — Sistema de agentes

Fuente versionada del sistema de agentes que organiza el internado médico-veterinario (septiembre 2026 – agosto 2027). Funciona con **Claude y ChatGPT** a la vez: los agentes se comunican mediante una bitácora compartida en Google Sheets y archivos HANDOFF en Google Drive, coordinados por `AGENTE_00_COORDINADOR` bajo supervisión del interno.

## Qué hay aquí y qué no

| En este repositorio (público) | Solo en Google Drive / Sheets (privado) |
|---|---|
| Contrato común, fichas de agentes, plantillas, código y pruebas | Charlas, investigaciones, evidencias, normativa descargada, productos |
| Historial de versiones del sistema (`CHANGELOG.md`, commits) | Bitácora, cola de tareas, HANDOFF reales, evaluaciones |
| Esquema de las hojas | Enlaces e identificadores de Drive |

**No subir** enlaces de Drive, datos personales, evidencias, borradores ni credenciales.

## Estructura

```
sistema/
  CONTRATO_COMUN.md          Reglas comunes únicas (todos los agentes lo leen)
  agentes/AGENTE_00..08.md   Fichas de especialidad
  plantillas/HANDOFF_v2.0.yaml
herramientas/
  handoff-validator/         Validador de HANDOFF (v1.0; pendiente migrar a v2.0: OT-2026-005)
docs/
  ESQUEMA_HOJAS.md           Pestañas y columnas de la bitácora y del control interno
CHANGELOG.md
```

## Agentes

| Código | Especialidad |
|---|---|
| AGENTE_00_COORDINADOR | Gestiona, asigna, evalúa y transfiere resultados |
| AGENTE_01_CHARLAS | Charlas con documento de apoyo de lectura previa |
| AGENTE_02_INVESTIGADOR | Investigaciones completas con anexos |
| AGENTE_03_AGENDA | Agenda y cronograma personal |
| AGENTE_04_ASISTENCIAS | Asistencia y entregas personales |
| AGENTE_05_TAREAS | Tareas personales del interno |
| AGENTE_06_NORMATIVA | Normativa oficial verificada |
| AGENTE_07_PROGRAMADOR | Scripts y herramientas |
| AGENTE_08_AUDIOVISUAL | Diapositivas, trípticos, infografías, video y audio |

## Flujo de cambios del sistema

1. Proponer el cambio (HANDOFF tipo `recurso` al Coordinador).
2. Aprobación del supervisor.
3. Commit aquí con la nueva versión y entrada en `CHANGELOG.md`.
4. Publicar la misma versión en Drive (`00_ADMINISTRACION` o `01_AGENTES`), mover la anterior a `09_ARCHIVO_HISTORICO/VERSIONES_ANTERIORES` y registrar en `VERSIONES_SISTEMA` y `BITACORA`.

## Probar el validador

```
cd herramientas/handoff-validator
python -B -m unittest -v test_validator
```

Requiere Python 3 y PyYAML. Resultado esperado: 24/24.
