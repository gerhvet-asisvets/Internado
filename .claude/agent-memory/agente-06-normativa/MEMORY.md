# Memoria de proyecto — AGENTE_06_NORMATIVA

Sin enlaces de Drive, IDs ni datos personales: este archivo está en un repositorio público.

## Fuentes que funcionan
- Infojurídica (Procuraduría de la Administración): la ficha `norma_screen.php?numsec=N` responde con curl e incluye fecha, Gaceta, vigencia y referencias posteriores.
- El buscador `busq_norma` (POST con `ajax=1`) devuelve 0 resultados aunque se le pasen filtros. Localizar la norma por numsec: los numsec son correlativos por fecha de Gaceta. Se prueban valores cercanos a una norma de fecha conocida, se ajusta el rango y luego se recorre en paralelo (unas 120 fichas en menos de 1 minuto).
- numsec útiles (públicos): DE 352/2001 = 31951; DE 81/2003 = 32977; Ley 430/2024 = 62157; DE 8/2026 = 66980; DE 99/2022 = 58917; DE 71/2023 = 61653; DE 6/2024 = 61658.
- Gacetas en `gacetas.procuraduria-admon.gob.pa/<num>_<año>.pdf`. Hay fallos de DNS transitorios: reintentar 2 o 3 veces.
- eCFR: la API versioner exige `--compressed` y una fecha de versión igual o anterior a `up_to_date_as_of` (ver `titles.json`).

## Técnicas
- OCR: `pdftoppm -r 200 -gray` y luego `tesseract -l spa`, siempre con `OMP_THREAD_LIMIT=1` y xargs -P4 (unos 3 s por página). Sin limitar los hilos se bloquea.
- Antes de pasar el OCR, comprobar si la Gaceta tiene capa de texto (pdftotext): la Ley 430 y la G.O. 24411 la tienen.
- El OCR pierde las letras y números de las listas: contar los numerales en el texto o en la imagen y decirlo en el informe.
- Las firmas se confirman renderizando la página a 70 ppp y mirando la imagen.

## Errores que hay que evitar (vistos en ACT-2026-001)
- Al resumir una falta, conservar su finalidad u objeto: DE 8/2026 art. 125 num. 3 lit. a dice "para obtener autorización"; la información errónea en la inspección es falta leve (num. 1 lit. e).
- No fechar la competencia de la DINACAVV en el DE 8/2026: viene de la Ley 430/2024.
- DE 71 art. 20: la etiqueta lleva la fecha de empaque, no la de sacrificio (esta va en el documento del distribuidor, art. 36).
- Derogación de artículos modificatorios (DE 8/2026 art. 126 sobre DE 81/2003 arts. 10 y 11): la ficha del DE 352 en Infojurídica no la refleja. Consultar siempre las dos fichas y presentar el efecto como INTERPRETACION.
- Los materiales que circulan sin el expositor (trípticos) deben repetir la reserva de "pendiente de criterio jurídico".
