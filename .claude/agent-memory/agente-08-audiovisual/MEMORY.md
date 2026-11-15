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
