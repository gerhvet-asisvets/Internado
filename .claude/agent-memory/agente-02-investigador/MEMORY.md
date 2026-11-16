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

- FAO, Manual on meat inspection for developing countries (1994): texto completo en HTML por capítulos (carpeta t0756e en fao.org/4). Caps. 1 (ante y post mortem, incluidas aves) y 7 (enfermedades de las aves) traen hallazgos, criterio de dictamen y diferenciales por enfermedad. Útil como referencia técnica rotulada.
- eCFR 9 CFR 381.83 a 381.93 (disposición post mortem de aves) se lee por la API del versionador sección a sección. Ojo: 381.87 (2023) permite recortar tumores; la norma nacional de aves exige decomiso total de neoplasias. Señalar siempre la divergencia.
- OMSA, Manual Terrestre 3.3.4 (influenza aviar) se descarga en PDF; los capítulos del Código Terrestre y otros capítulos del Manual devolvieron 403.
- E-utilities (efetch) para títulos y autores: tomar el DOI solo de PubmedData/ArticleIdList. El selector genérico devuelve DOI de las referencias citadas. Cotejar autores en el registro; no completarlos de memoria. Si la herramienta PubMed da límite de tasa, usar E-utilities con pausas.
- Diagramas: Pillow con fuentes Carlito da PNG legibles; dibujar primero los conectores y luego las cajas, y calcular la altura de cada fila con la caja más alta de la fila para evitar solapes.

## Bloqueos conocidos
- Boletines epidemiológicos del MINSA: el CDN se redirige a sí mismo (bucle 301). La copia de archive.org corta la conexión. Faltan por probar SIRVETA (OPS/PANAFTOSA), LILACS y SciELO.
- PubMed no tiene estudios de prevalencia de patógenos en carne en Panamá. La búsqueda devuelve falsos positivos por el serovar Salmonella Panama.
- Siguen faltando el límite nacional de nitrito, la temperatura de canal y la norma nacional de aves.
- PubMed sigue sin datos de Salmonella, Campylobacter ni decomisos avícolas en Panamá. Costa Rica sirvió como dato regional (Salmonella Infantis en pollo; Campylobacter resistente a quinolonas).
- El PDF de las directrices Codex CXG 78-2011 por el proxy de fao.org devuelve JavaScript, no el PDF.

## Lecciones de ACT-2026-002 (manual de inspección avícola)
- Integrar solo las normas del dossier aprobado de AGENTE_06 y releer en el OCR los artículos con cifras. Cuando un hallazgo no está nombrado en la lista legal de decomisos, marcar la correspondencia como INTERPRETACION.
- En la matriz de peligros, la inspección oficial no entra en el árbol P1-P4 del operador (si entra, aparecen celdas no binarias).
- Repetir al inicio del material las reservas de interpretación del dossier y el aviso de que el dictamen es del MV oficial.
