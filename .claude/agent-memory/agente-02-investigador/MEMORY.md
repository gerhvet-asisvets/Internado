# Memoria de proyecto: AGENTE_02_INVESTIGADOR

## Lecciones de revisión (revisión independiente de la investigación HACCP en carnes, nov 2026)
- Errores que encontró la revisión en un informe "verificado", para no repetirlos:
  - Atribuir a Salmonella un estudio panameño que era de E. coli. Hay que leer el título completo en PubMed: el resumen del MCP puede perder los nombres en cursiva del organismo.
  - Poner en boca de la OMS patógenos que su hoja no nombra. Buscar la palabra exacta en el HTML.
  - Presentar las opciones FSIS antiguas sin los parámetros añadidos en 2021. Ejemplo: la opción 1.2 de enfriamiento exige de 120 a 80 °F en 1 h o menos, además de 120 a 55 °F en 6 h.
  - Usar el rango de 7 a 25 mm de la FDA CPG 555.425 como límite o como sensibilidad de un detector de metales. Es un criterio de adulteración.
  - Leer en un resumen efectos que no dice: dirección de un efecto, unidad de una concentración, "la intervención redujo" cuando solo se compara cuero con canal.
- En la matriz, P1 a P4 del árbol deben ser Sí o No. Si depende del diseño, se abre una fila por escenario. Añadir siempre una pestaña con la escala de probabilidad, severidad y significancia.
- Cotejar la matriz con la lista legal mínima de peligros del DE 352/2001 art. 4, que incluye vidrio y plástico. Si hay sacrificio, incluir la inspección post mortem.
- Las cifras nacionales (DE 71/2023, DE 6/2024 y DE 352/2001) estaban bien citadas. El riesgo estaba en las referencias de EE. UU. y en la literatura.

## Fuentes y técnicas que funcionaron
- eCFR: la API del versionador funciona con curl y respuesta comprimida (opción --compressed). La ruta es /api/versioner/v1/full/<fecha>/title-9.xml?section=<sección>. Sin esa opción devuelve un aviso de compresión.
- El Federal Register en govinfo (html) se descarga completo y sirve para las guías FSIS 2021.
- El PDF del Codex CXC 1-1969 (openknowledge.fao.org) se descargó con curl y se leyó con pdftotext.
- PubMed: con convert_article_ids solo salen los PMID que tienen PMC. Para los demás, usar lookup_article_by_citation (revista, año, volumen, primera página, autor) y luego get_article_metadata. Para el título exacto con cursivas, usar efetch de eutils.
- Gacetas de Panamá escaneadas: pdftoppm a 200 ppp y luego tesseract en español. Hay que fijar OMP_THREAD_LIMIT=1 y lanzar como máximo 4 procesos en paralelo; sin el límite de hilos, el OCR se bloquea por sobresuscripción.

## Bloqueos conocidos
- Boletines epidemiológicos del MINSA: el CDN se redirige a sí mismo (bucle 301). La copia de archive.org corta la conexión. Faltan por probar SIRVETA (OPS/PANAFTOSA), LILACS y SciELO.
- PubMed no tiene estudios de prevalencia de patógenos en carne en Panamá. La búsqueda devuelve falsos positivos por el serovar Salmonella Panama.
- Siguen faltando el límite nacional de nitrito, la temperatura de canal y la norma nacional de aves.
