---
name: diseno-audiovisual
description: Procedimiento de AGENTE_08 para producir diapositivas diseñadas (pptx a Google Slides), trípticos A4 de 6 paneles (HTML a PDF), infografías y piezas de audio o video, siempre editables y en PDF.
user-invocable: false
---

# Diseño audiovisual — v1.2

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
- **Tríptico para imprenta (OT-2026-012):** usar fuentes TrueType (.ttf), no OpenType CFF (.otf): Chromium incrusta las .otf como Type 3 y las .ttf como CID TrueType. Crear un subconjunto con pyftsubset (fonttools), incrustarlo en base64 en @font-face para que la maqueta sea portable, generar página de 303 x 216 mm (3 mm de sangrado) y fijar TrimBox y BleedBox con pypdf. Comprobar con pdffonts. Playwright está instalado para Node, no para Python.
- **Rótulos a 24 pt sin recortes (OT-2026-012):** antes de guardar el .pptx, medir cada caja con PIL ImageFont y LiberationSans (métricas de Arial), con ajuste por palabras y alto de línea 1,2 veces el cuerpo, y avisar de toda caja que no quepa. Comprobar con un script que cada palabra del texto aprobado aparece en su diapositiva.
- **Cambio puntual sobre una versión aprobada (OT-2026-017):**
  1. Regenerar la versión anterior con el mismo script y comprobar que el .pptx sale idéntico parte a parte.
  2. Aplicar solo el cambio pedido.
  3. Comparar las partes del paquete (solo deben diferir slideN.xml y notesSlideN.xml de las diapositivas cambiadas), el texto, las notas, la geometría y los píxeles de las exportaciones PDF de Slides de ambas versiones.
  4. Subir una captura lado a lado de las diapositivas cambiadas. Las marcas de verificación se dibujan como forma libre, no con glifos.
- **Material derivado de documentos aprobados (OT-2026-015):** generar el contenido desde una lista estructurada en la que cada afirmación lleva su sección de origen y uno o más fragmentos literales de la fuente. Un validador busca cada fragmento en el texto exportado de la fuente (text/plain, espacios normalizados) y otro comprueba en el pdftotext del PDF que los bloques copiados aparecen completos. La tabla de fidelidad se genera desde la misma lista, no a mano.
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
- [ ] En la exportación de Google Slides, ninguna unidad (°C, %, mm) queda partida al final de línea: Slides corta después de "°" aunque haya espacio de no separación. Si ocurre, mover el salto (párrafo propio o ancho de caja distinto), no cambiar el texto aprobado.
- [ ] Impresos A4 de varias páginas en HTML: SVG a 1 unidad = 1 px CSS, sin escalar, con texto de 12 px o más y cajas con altura calculada según sus líneas; antes de exportar, medir con Chromium elementos más anchos que la página y textos de menos de 9 pt (deben ser 0); revisar todas las páginas con pdftoppm a 40-80 ppp buscando páginas casi vacías y rótulos superpuestos; la versión de 1-2 páginas se comprueba con pdfinfo.
- [ ] Esquemas anatómicos sin fotografías: SVG propios con rótulos literales del documento aprobado, marca "esquema no a escala; posición aproximada" y declaración en la tabla de fidelidad de que la disposición es del diseñador.

## Lecciones
- **ACT-2026-001:**
  - Los rótulos abreviados restaron coherencia (c4): usar los términos exactos del documento de apoyo.
  - La conversión a Slides no se revisó visualmente: añadir una captura de verificación.
  - **D8 (OT-2026-012 y 017):** si una nota visual pide marcar como cumplido algo que el ejemplo no permite afirmar, se señala el riesgo al Coordinador y se aplica la decisión del SUPERVISOR. Mientras no la haya, se marca "por comprobar" y se declara la adaptación en el HANDOFF. En D8 el SUPERVISOR pidió las casillas en verde y se aplicó así (v1.2).
