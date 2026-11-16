---
name: investigacion-sanitaria
description: Procedimiento de AGENTE_02 para investigaciones de salud pública veterinaria, inocuidad, zoonosis y epidemiología con matrices, diagramas, fuentes verificadas y síntesis para charla.
user-invocable: false
---

# Investigación sanitaria — v1.1

## Procedimiento
1. Pregunta de investigación, alcance, público y finalidad, según la OT.
2. Estrategia de búsqueda registrada:
   - PubMed (herramientas PubMed), Codex, FAO/OMS, FSIS/USDA (Federal Register, eCFR), OMSA;
   - MINSA y la región (OPS, CDC).
   - Anotar fecha y términos de búsqueda.
3. Leer el texto completo cuando sea posible. Si solo se leyó el resumen, declararlo: el Coordinador baja c2 cuando no se dice.
4. Producir:
   - informe completo;
   - anexos reales (matriz en Google Sheet, diagramas en PNG o PDF);
   - síntesis para charla: 10 ideas con su fuente y preguntas con respuesta.
5. Marcar las citas normativas decisivas para que AGENTE_06 las verifique.

## Checklist
- [ ] Matriz de peligros biológicos, químicos y físicos por etapa del proceso, con su medida de control.
- [ ] Los PCC y límites críticos citan su fuente y advierten que no son universales.
- [ ] Datos de Panamá y la región, o DATO_FALTANTE explícito.
- [ ] Nivel de evidencia indicado; correlación distinguida de causalidad.
- [ ] Cada estudio citado se coteja con su título en PubMed (organismo, matriz y país), no solo con las cifras. Si el resumen no da la dirección de un efecto o la unidad de una concentración, no se afirman o se marcan como no verificables.
- [ ] Matriz de peligros: P1 a P4 respondidas solo con Sí o No (si depende del diseño, una fila por escenario); pestaña de criterios de probabilidad, severidad y significancia; lista de peligros contrastada con la lista legal mínima (DE 352/2001 art. 4, incluidos vidrio y plástico) y con la inspección post mortem si hay sacrificio.

## Lecciones
- **ACT-2026-001:**
  - Los boletines de ETA del MINSA entran en un bucle de redirecciones. Intentar los boletines epidemiológicos en PDF o los informes de la OPS.
  - Faltan datos de prevalencia de patógenos en carne en Panamá.
  - Los apéndices de FSIS no se abrieron; el Federal Register y el eCFR sí funcionan.
  - **FSIS 2021 (Apéndices A y B):** cambiaron los parámetros de las opciones heredadas. La opción 1.2 de enfriamiento exige de 120 a 80 °F en 1 h o menos, además de 120 a 55 °F en 6 h. Citar siempre la opción con todos sus parámetros, leyendo el texto completo del 86 FR 71007 en govinfo. El eCFR se lee por la API del versionador (`www.ecfr.gov/api/versioner/v1/full/AAAA-MM-DD/title-9.xml?section=X`, con `curl --compressed`).
  - Un criterio de adulteración (por ejemplo, FDA CPG 555.425, de 7 a 25 mm) no es un límite crítico ni la sensibilidad de un detector de metales. El límite del PCC de detección de metales son los patrones de prueba validados para el equipo y el producto.
