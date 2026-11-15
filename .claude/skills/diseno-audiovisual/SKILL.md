---
name: diseno-audiovisual
description: Procedimiento de AGENTE_08 para producir diapositivas diseñadas (pptx a Google Slides), trípticos A4 de 6 paneles (HTML a PDF), infografías y piezas de audio o video, siempre editables y en PDF.
user-invocable: false
---

# Diseño audiovisual — v1.0

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
- **Audio:** herramientas ElevenLabs, si están conectadas. El conector restringido no genera video ni imagen.

## Checklist
- [ ] Ningún dato que no esté en los HANDOFF aprobados.
- [ ] Contraste suficiente, 24 pt mínimo en diapositivas y 9 pt en impresos. Cualquier excepción, por ejemplo los pies de fuente, va declarada.
- [ ] Espacio reservado para los logotipos MINSA y DINACAVV, sin reproducirlos.
- [ ] Hoja de créditos con el origen y la licencia de cada imagen e ícono.
- [ ] Revisar visualmente la conversión a Google Slides, no solo el texto. Una captura con Playwright del PDF sirve como referencia.

## Lecciones
- **ACT-2026-001:**
  - Los rótulos abreviados restaron coherencia (c4): usar los términos exactos del documento de apoyo.
  - La conversión a Slides no se revisó visualmente: añadir una captura de verificación.
