# Memoria de AGENTE_08_AUDIOVISUAL

## OT-2026-009 (revisión de diapositivas y tríptico, ACT-2026-001)

### Técnicas que funcionaron
- `download_file_content` guarda los binarios en disco y devuelve la ruta. Un Google Slides se exporta con `exportMimeType` `application/pdf` y también como `.pptx`; el `.pptx` sirve para auditar con python-pptx.
- Revisión visual: `pdftoppm -r 60` del PDF de Slides y del PDF de referencia, comparados lado a lado con PIL. Una hoja de contactos de 4x5 pesa menos de 1 MB y se sube sin problemas.
- Auditoría con python-pptx: listar los runs de menos de 24 pt o con una fuente distinta de la declarada, y comprobar que cada diapositiva tiene notas. Calibri o MS-PGothic en `pdffonts` pueden venir solo de las notas y del tema, así que hay que comprobarlo antes de reportarlo.
- `pdffonts` sobre el PDF del tríptico muestra si las fuentes quedaron como Type 3 (Chromium/Skia).
- Para rastrear la fidelidad hay que buscar cada dato en el documento de apoyo y también en la ficha normativa: algunos datos solo están en la ficha.

### Errores que hay que evitar
- Al recortar rótulos para llegar a 24 pt se pierden calificativos clave (deficiente, vigente, firmado). En D15 eso cambió el sentido de la falta grave.
- Un ejemplo ficticio tiene que ilustrar las mismas reglas que enuncia la diapositiva.
- Un impreso necesita sangrado de 3 mm si lleva fondo a sangre, una solapa 2-3 mm más corta en plegado en rodillo y la fuente embebida o declarada con @font-face.
- Contar dos veces las tablas de resumen antes de subir un Google Doc: el informe no se puede editar después y la corrección exige una versión nueva o una fe de erratas.

## OT-2026-012 (diapositivas y tríptico v1.1, ACT-2026-001)

### Técnicas que funcionaron
- Medir antes de guardar: PIL ImageFont con LiberationSans (métricas de Arial), ajuste de línea por palabras y alto de línea de 1,2 veces el cuerpo, con aviso por caja. Es algo conservador (Slides y LibreOffice usan unos 1,15) y evita recortar rótulos para llegar a 24 pt.
- Script de cobertura: cada palabra del texto aprobado de la estructura tiene que aparecer en su diapositiva. Detecta omisiones al instante.
- Cuando el texto aprobado no cabe a 24 pt: llevar las etiquetas a pestañas sobre el borde de la caja, poner a lo ancho las cajas de ejemplo, usar márgenes de 0,5 in en las diapositivas densas, poner el número de artículo en negrita al inicio del bloque y dejar los pies de dos líneas a 12 pt.
- Fijar en el tema del .pptx la fuente latina a Arial (reescribir ppt/theme/*.xml); así no aparece Calibri en la exportación.
- Evitar glifos que Arial no tiene (✗, ✓): LibreOffice los sustituye por otra fuente. Usar "X" o formas.
- Tríptico: las .ttf se incrustan como CID TrueType en Chromium y las .otf (CFF), como Inter, salen como Type 3. Carlito (OFL) con subconjunto de pyftsubset en base64 dentro de @font-face hace la maqueta portable. Página de 303 x 216 mm y TrimBox/BleedBox con pypdf.
- Playwright de Python no está instalado. El de Node funciona con executablePath de google-chrome. Medir el desborde de cada panel con scrollHeight - clientHeight.
- Generar las vistas PNG del tríptico desde el PDF con pdftoppm (sin la franja de la captura de pantalla).
- Hora: escribir siempre la hora de Panamá (TZ=America/Panama date). El reloj del contenedor está en UTC.

### Errores que hay que evitar
- Google Slides corta la línea después de "°" incluso con espacio de no separación ("4 °" / "C"). Solo se ve en la exportación de Slides, no en el PDF de LibreOffice. Verificar cada carga y, si ocurre, mover el salto de línea (párrafo propio o ancho distinto). Me costó dos recargas.
- Antes de subir otra carga, comprobar con search_files qué existe ya en la carpeta, para no duplicar después de una interrupción.
- Una nota visual que pide marcar en verde lo que el ejemplo no dice afirma de forma implícita algo no aprobado. Usar "por comprobar" y declararlo.

## OT-2026-017 (diapositivas v1.2, cambio puntual en una diapositiva, ACT-2026-001)

### Técnicas que funcionaron
- Cambio puntual sobre una versión aprobada: regenerar primero la versión anterior con su script y comprobar que el .pptx sale idéntico parte a parte (zipfile, comparar cada entrada). Luego aplicar solo el cambio y comprobar que solo difieren `slideN.xml` y `notesSlideN.xml`.
- Prueba de "el resto es idéntico": exportar a PDF el Slides anterior y el nuevo, `pdftoppm -r 60` y `ImageChops.difference(...).getbbox()` por página. `None` significa que no hay diferencia de píxeles; en la página cambiada, la caja delimita la zona exacta del cambio.
- El script de cobertura ampliado compara además, por diapositiva, el texto, las notas y la geometría de las formas entre dos .pptx exportados de Slides.
- Una marca de verificación dibujada con `build_freeform` (dos segmentos, línea blanca de 3 pt sobre un cuadrado verde) se conserva bien en Google Slides y evita glifos que Arial no tiene.
- Guardar los scripts de cada OT en la carpeta del scratchpad de esa OT: el de la OT anterior seguía allí y permitió reproducir la versión exacta.

### Errores que hay que evitar
- Si un cambio visual contradice la nota del expositor (por ejemplo, la nota dice "llevan '?'"), hay que ajustar la nota y declararlo como pendiente para el Coordinador, porque la OT puede pedir "sin cambios de texto".
- El handoff-validator del repositorio valida HANDOFF v1.0, no v2.1: no sirve para la v2.1 (OT-2026-005 pendiente). Basta con comprobar que el YAML se puede analizar.
