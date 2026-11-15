---
name: normativa-panama
description: Procedimiento de AGENTE_06 para identificar, verificar y citar por artículo la normativa sanitaria de Panamá (MINSA, DINACAVV, MIDA, APA/AUPSA) y separar las referencias internacionales (Codex, OMSA, FSIS).
user-invocable: false
---

# Normativa sanitaria de Panamá — v1.0

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
- El buscador de Infojurídica puede no responder. En ese caso, marcar la norma `pendiente_verificacion`; nunca suponer su vigencia.
- **Textos escaneados (OCR):** confirmar cada número de artículo en el encabezado del propio artículo antes de citarlo. Las firmas leídas por OCR quedan sin verificar.

## Checklist de entrega
- [ ] Cada norma lleva artículo, vigencia y fecha de consulta.
- [ ] Derogaciones verificadas dentro de la norma más reciente.
- [ ] Codex, FSIS y 9 CFR presentados como referencia técnica, no como obligación en Panamá.
- [ ] Las interpretaciones jurídicas están marcadas INTERPRETACION y recomiendan confirmar con asesoría legal.
- [ ] Copias oficiales de más de unos 3 MB: se deja el enlace y se registra el error.

## Lecciones
- **ACT-2026-001 (HACCP carnes):** el art. 126 del DE 8/2026 derogó los arts. 10 y 11 del DE 81/2003 (validación y auditoría HACCP anual). Vigente: inspección periódica según riesgo (DE 8/2026, art. 88). El DE 99/2022 está derogado íntegro. Siguen pendientes las modificatorias del DE 71/2023 y del DE 6/2024.
