---
name: normativa-panama
description: Procedimiento de AGENTE_06 para identificar, verificar y citar por artículo la normativa sanitaria de Panamá (MINSA, DINACAVV, MIDA, APA/AUPSA) y separar las referencias internacionales (Codex, OMSA, FSIS).
user-invocable: false
---

# Normativa sanitaria de Panamá — v1.1

## Procedimiento
1. Listar las normas candidatas a partir de la OT y de las fichas previas, consultando CONTROL_INTERNO/FUENTES_NORMATIVAS para no duplicar.
2. Para cada norma, abrir el texto oficial y registrar:
   - entidad, tipo, número, fecha y Gaceta;
   - artículos pertinentes, con su número;
   - modificatorias y derogaciones;
   - vigencia y fecha de consulta.
3. Buscar las derogaciones posteriores dentro de las normas más recientes (por ejemplo, los artículos finales de "deroga"). Que una norma figure como vigente en un índice no basta.
4. Redactar la ficha normativa y el mensaje para el público, separando obligación legal de referencia técnica.
5. Proponer filas DOC para FUENTES_NORMATIVAS, sin repetir las ya registradas.

## Fuentes y accesos
- **gacetaoficial.gob.pa** bloquea el acceso automático (anti-bots). Usar las mismas Gacetas desde el repositorio de la Procuraduría de la Administración (infojuridica.procuraduria-admon.gob.pa), citando ambas.
- **Buscador de Infojurídica sin resultados:** localizar la ficha por su numsec en `norma_screen.php?numsec=N`. Los numsec son correlativos por fecha de Gaceta: probar valores cercanos a los de una norma de fecha conocida y ajustar hasta dar con el número de Gaceta. Citar el numsec hallado. Solo si así tampoco se encuentra, marcar la norma `pendiente_verificacion`; nunca suponer su vigencia.
- **Derogación de artículos de un decreto modificatorio:** consultar la ficha del modificatorio y la de la norma modificada, porque la afectación puede figurar solo en la primera. Explicar que no revive el texto original y marcar como INTERPRETACION, pendiente de asesoría legal, el efecto sobre la norma de base.
- **Textos escaneados (OCR):** confirmar cada número de artículo en el encabezado del propio artículo antes de citarlo. Las firmas leídas por OCR quedan sin verificar.
- **OCR de Gacetas:** `tesseract -l spa` con `OMP_THREAD_LIMIT=1` y varias páginas en paralelo (unos 3 s por página). Sin limitar los hilos, el OCR en paralelo se bloquea.

## Checklist de entrega
- [ ] Cada norma lleva artículo, vigencia y fecha de consulta.
- [ ] Derogaciones verificadas dentro de la norma más reciente.
- [ ] Codex, FSIS y 9 CFR presentados como referencia técnica, no como obligación en Panamá.
- [ ] Las interpretaciones jurídicas están marcadas INTERPRETACION y recomiendan confirmar con asesoría legal.
- [ ] Copias oficiales de más de unos 3 MB: se deja el enlace y se registra el error.
- [ ] Al resumir una falta para el público, se copian los requisitos del literal (finalidad, objeto) y no solo la conducta, y se comprueba que la misma conducta no figure también como falta leve. Ejemplo: DE 8/2026 art. 125 num. 3 lit. a ("para obtener autorización") frente a num. 1 lit. e.

## Lecciones
- **ACT-2026-001 (HACCP carnes):** el art. 126 del DE 8/2026 derogó los arts. 10 y 11 del DE 81/2003 (validación y auditoría HACCP anual). Vigente: inspección periódica según riesgo (DE 8/2026, art. 88). El DE 99/2022 está derogado íntegro. Infojurídica no registra modificatorias del DE 71/2023 ni del DE 6/2024 al 2026-11-15. La ficha del DE 352/2001 no refleja la derogación de 2026. La competencia de la DINACAVV viene de la Ley 430/2024.
