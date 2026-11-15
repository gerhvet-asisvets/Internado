---
name: contrato-comun
description: Reglas comunes obligatorias del sistema de agentes Internado MINSA–DINACAVV (ciclo de sesión, bitácora, HANDOFF, permisos, IDs, evaluación). Cargar antes de cualquier trabajo del sistema.
user-invocable: false
---

# Contrato común (resumen operativo)

El texto completo y vigente está en `sistema/CONTRATO_COMUN.md`, y su copia en Drive (00_ADMINISTRACION/CONTRATO_COMUN_vX) es la que trae los enlaces. **Léelo completo si tienes cualquier duda.** Si este resumen y el contrato se contradicen, prevalece el contrato.

## Ciclo de sesión
1. Confirmar la versión vigente en BITACORA_AGENTES / VERSIONES_SISTEMA.
2. Registrar inicio_sesion en BITACORA.
3. Leer la OT, sus entradas y la bitácora de la actividad.
4. Pasar la OT a en_curso.
5. Producir el trabajo completo.
6. Guardarlo en la carpeta propia, en la subcarpeta `ACT-AAAA-NNN_TITULO_CORTO`.
7. Guardar el HANDOFF (.yaml) en 09_ARCHIVO_HISTORICO/HANDOFF.
8. Añadir la fila en HANDOFFS.
9. Pasar la OT a entregada, con salida_urls y handoff_id.
10. Registrar cierre_sesion.

## Reglas que no se rompen
- **Leer y modificar, nunca borrar.** Toda modificación lleva su fila en BITACORA (valor_anterior y valor_nuevo).
- Las filas de BITACORA solo se añaden; nunca se editan.
- Todo HANDOFF va al Coordinador. **Solo el Coordinador evalúa y transfiere.**
- Nunca afirmar que algo quedó registrado o guardado sin la confirmación de la herramienta. Si falla, se registra `accion = error`.
- Separar HECHO_VERIFICADO, INTERPRETACION, HIPOTESIS y DATO_FALTANTE. No inventar fuentes, artículos ni cifras.
- L3 (borrar, compartir, publicar, cambiar permisos o el contrato) requiere aprobación del SUPERVISOR.
- El repositorio es público: no escribir en él enlaces de Drive, IDs ni datos personales.

## HANDOFF v2.1
Es el formato v2.0 más un campo opcional `propuesta_skill`. Plantilla: `sistema/plantillas/HANDOFF_v2.1.yaml`.

```yaml
propuesta_skill:
  - skill: 'normativa-panama'       # o 'nueva:<nombre>'
    tipo: 'leccion|procedimiento|checklist|nueva_skill'
    texto: 'Texto exacto a añadir o cambiar'
    motivo: ''
    evidencia: ''                   # OT o fila BIT donde se observó
```

## Herramientas de Drive (lecciones técnicas)
- **Google Doc:** create_file con `contentMimeType: text/markdown` (se convierte solo). Evitar negritas dentro de tablas.
- **YAML y binarios:** `disableConversionToGoogleType: true`. Para subir un archivo local se usa `base64Content` = `sha256:<hex>:<ruta absoluta>`.
- **Límite de carga:** unos 3 MB por archivo. Un archivo mayor no se sube: se deja su enlace oficial y se registra el error.
- Las herramientas de Drive no editan el contenido de un archivo existente. Una corrección es una versión nueva, y la anterior se mueve a VERSIONES_ANTERIORES.
- **Sheets:** append_values para añadir filas; update_values en celdas concretas, leyendo antes de escribir.
