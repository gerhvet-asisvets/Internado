---
name: diseno-audiovisual
description: Procedimiento de AGENTE_08 para producir diapositivas diseñadas (pptx a Google Slides), trípticos A4 de 6 paneles (HTML a PDF), infografías y piezas de audio o video, siempre editables y en PDF.
user-invocable: false
---

# Diseño audiovisual — v1.1

## Flujo técnico que funcionó (ACT-2026-001)
- **Diapositivas:**
  1. Generarlas con python-pptx (`pip install python-pptx` si hace falta).
  2. Subirlas a Drive con `contentMimeType: application/vnd.openxmlformats-officedocument.presentationml.presentation`; se convierten a Google Slides.
  3. Exportar además un PDF de referencia.
- **Tríptico:**
  1. Maqueta HTML/CSS con página A4 horizontal y 3 columnas por cara.
  2. Convertirla a PDF y PNG con Playwright y Chromium (ya instalados).
  3. Hacer un Google Doc editable con el texto de cada panel.
- **Subida de binarios:** `base64Content` = `sha256:<hex>:<ruta absoluta>` y `disableConversionToGoogleType: true`. Límite de unos 3 MB por archivo; comprimir las imágenes si hace falta.
- **Verificación de la conversión a Google Slides:**
  1. Exportar el Slides con `download_file_content` (`exportMimeType` application/pdf, y también el .pptx).
  2. Renderizar con `pdftoppm -r 60` y montar con PIL una comparación lado a lado con el PDF de referencia.
  3. Auditar el .pptx exportado con python-pptx: listar los runs de menos de 24 pt o con una fuente distinta de la declarada, y comprobar que hay notas en cada diapositiva.
  4. Subir una hoja de contactos PNG como captura de verificación.
- **Audio:** herramientas ElevenLabs, si están conectadas. El conector restringido no genera video ni imagen.

## Checklist
- [ ] Ningún dato que no esté en los HANDOFF aprobados.
- [ ] Contraste suficiente, 24 pt mínimo en diapositivas y 9 pt en impresos. Cualquier excepción, por ejemplo los pies de fuente, va declarada.
- [ ] Espacio reservado para los logotipos MINSA y DINACAVV, sin reproducirlos.
- [ ] Hoja de créditos con el origen y la licencia de cada imagen e ícono.
- [ ] Revisar visualmente la conversión a Google Slides, no solo el texto (procedimiento de verificación de arriba).
- [ ] Cada rótulo conserva los calificativos que el público verifica (vigente, firmado, deficiente, justificado, uno mismo). Si no cabe a 24 pt, se rediseña la forma; no se recorta el texto.
- [ ] Los ejemplos ficticios ilustran exactamente las reglas que enuncia la diapositiva.
- [ ] Impresos: 3 mm de sangrado si hay fondo a sangre; solapa interior 2-3 mm más corta en plegado en rodillo; fuentes incrustadas como TrueType u OpenType (no Type 3) y declaradas con @font-face en la maqueta HTML.

## Lecciones
- **ACT-2026-001:**
  - Los rótulos abreviados restaron coherencia (c4): usar los términos exactos del documento de apoyo.
  - La conversión a Slides no se revisó visualmente: añadir una captura de verificación.
