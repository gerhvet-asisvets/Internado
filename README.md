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
CLAUDE.md                      Reglas del repositorio (privacidad, flujo de cambios)
.claude/settings.json          La sesión principal arranca como el Coordinador
.claude/agents/                Subagentes: coordinador y 8 especialistas
.claude/skills/                Skills: contrato-comun, coordinacion-internado y una por especialidad
.claude/agent-memory/          Memoria de cada especialista (se crea al trabajar)
sistema/
  CONTRATO_COMUN.md            Reglas comunes únicas
  agentes/AGENTE_00..08.md     Fichas de especialidad (también en Drive para ChatGPT)
  plantillas/HANDOFF_v2.1.yaml
herramientas/handoff-validator Validador de HANDOFF (v1.0; migración a v2.1: OT-2026-005)
docs/ESQUEMA_HOJAS.md
CHANGELOG.md
```

## Cómo se usa

- **Claude Code:** abre una sesión en este repositorio y pide la tarea. El Coordinador planifica, te pide aprobación y despacha a los especialistas como subagentes. Cada uno trabaja con su skill, guarda los productos y el HANDOFF en Drive y deja todo registrado en la bitácora.
- **ChatGPT:** abre la conversación del agente y escribe *"Revisa tu cola de tareas"*. El agente lee el contrato, su ficha y su skill desde este repositorio público.

## Cómo se especializan los agentes

Cada especialista anota en su memoria lo que aprende en cada orden de trabajo y propone mejoras a su skill en el HANDOFF (`propuesta_skill`). El Coordinador las filtra, tú las apruebas y quedan integradas en la skill con su versión y su entrada en `CHANGELOG.md`.

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
