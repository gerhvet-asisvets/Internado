# Memoria de proyecto: AGENTE_01_CHARLAS

## Lecciones de revisión (OT de revisión independiente de la charla HACCP, nov 2026)
- Fallo recurrente de los tiempos: el cuestionario PRE y el POST se meten dentro de otros bloques y el ejercicio queda "opcional" fuera de la duración pedida. Hay que sumar cada bloque por separado (PRE, exposición, preguntas, POST, ejercicio) y usar el mismo número de minutos en el guion, las diapositivas y el cuestionario.
- Al cerrar un cuestionario, revisar cómo se reparten las claves. Una versión anterior tenía las 8 respuestas en "b".
- Unificar los conteos entre documentos (número de no conformidades del ejercicio, minutos del ejercicio).
- Toda cifra de 9 CFR, FSIS o FDA se comprueba en el texto primario, con el subapartado y el tipo de producto. Ejemplo: nitrito en tocino, 120 ppm inyectado o por inmersión y 200 ppm solo curado en seco (9 CFR 424.22(b)).
- Para inspectores y control de calidad, añadir: cómo redactar la no conformidad (requisito, evidencia, hallazgo), regla de muestreo de registros, criterios para aceptar una validación, competencia del equipo HACCP y diferencia de roles entre el auditor interno y el inspector oficial. Al menos la mitad del tiempo, para el bloque operativo.
- Comprobar que una norma por especie (DE 71/2023 y DE 6/2024, carne fresca) se aplica de verdad al tipo de planta del caso (por ejemplo, embutidos) antes de citarla como fundamento.

## Fuentes y bloqueos técnicos
- ecfr.gov redirige a una página de desbloqueo desde el entorno; Cornell LII (law.cornell.edu/cfr/text/9/...) sirve como espejo legible.
- El PDF del Codex CXC 1-1969 en openknowledge.fao.org devuelve 403; la numeración de secciones queda sin verificar.
- El conteo de páginas de un Google Doc no sale con read_file_content. Hay que estimarlo por palabras (unas 500 a 550 por página A4 en prosa) y declararlo como estimación.

## Lecciones de producción (OT de la charla HACCP v1.1, nov 2026)
- Extensión real: un Google Doc creado desde markdown con muchas tablas se infla (unas 150 palabras por página en tablas). La primera carga del documento de apoyo dio 34 páginas. Lo que funcionó: pandoc a .docx, formato con python-docx (A4, márgenes de 2 cm, Arial 10, tablas a 8,5 con interlineado 1), subirlo convertido a Google Doc y medir las páginas exportando a PDF con pdfinfo. Medir antes de subir con soffice --headless --convert-to pdf (da un número parecido; Drive dio 2 páginas más).
- Subir archivos locales a Drive: usar la referencia sha256:<hex>:<ruta> en base64Content; no hace falta pegar el texto. Comprobar después el contenido exportando a text/plain.
- Si una carga sale mal: no se borra. Renombrarla con un sufijo y moverla a VERSIONES_ANTERIORES con update_file, y registrarla en BITACORA.
- Cuadre de 30 minutos que funcionó: apertura 1, PRE 3, contexto 5, operativo 10, ejercicio exprés 5, cierre 1, preguntas 2, POST 3. Cuestionario de 6 preguntas (30 s cada una), todas de aplicación; ejercicio exprés con una sola tarea (redactar una no conformidad) y ejercicio completo como material opcional declarado.
- Para comprobar el reparto de claves, escribirlo en la hoja del expositor (letra y porcentaje) en el momento de redactar.
- Cifras técnicas: Cornell LII (9 CFR) y govinfo (Federal Register en HTML) se leen bien desde el entorno con curl más un extractor de texto.
- La sesión puede cortarse por el límite de uso: dejar los borradores en el scratchpad antes de subir nada y, al retomar, buscar en la carpeta los archivos _v1.x ya creados para no duplicarlos.
