import os
import sys
from io import BytesIO

from docx import Document
from docx.oxml.ns import qn
from PIL import Image

from utils.ocr_engine import ejecutar_ocr
from utils.md_formatter import tabla_a_markdown

HEADING_MAP = {1: "#", 2: "##", 3: "###", 4: "####"}


def _nivel_heading(parrafo) -> int | None:
    estilo = parrafo.style.name if parrafo.style else ""
    if estilo.startswith("Heading "):
        try:
            return int(estilo.split(" ")[1])
        except ValueError:
            pass
    return None


def _extraer_hipervinculos(parrafo) -> str:
    """Combina texto plano e hipervínculos en formato Markdown."""
    partes = []
    for run in parrafo.runs:
        # Los hipervínculos están en el XML como w:hyperlink
        partes.append(run.text)

    # Buscar hipervínculos en el XML del párrafo
    for hlink in parrafo._p.findall(f".//{qn('w:hyperlink')}"):
        rId = hlink.get(f"{{{qn('r:id').split('}')[0][1:]}}}id") if False else None
        texto_link = "".join(r.text or "" for r in hlink.findall(f".//{qn('w:t')}"))
        if texto_link:
            partes.append(f"[{texto_link}]")

    return "".join(partes)


def _procesar_imagenes_parrafo(parrafo, doc, img_dir: str, img_counter: list, lang: str, img_prefix: str = "") -> str:
    """Extrae imágenes embebidas en un párrafo y retorna bloques Markdown con OCR."""
    bloques = []
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            pass  # Las relaciones se manejan por drawing

    # Buscar elementos drawing/inline (imágenes en línea)
    for drawing in parrafo._p.findall(f".//{qn('a:blip')}"):
        embed = drawing.get(f"{{{qn('r:embed').split('}')[0][1:]}}}embed") if False else drawing.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        if embed and embed in doc.part.rels:
            rel = doc.part.rels[embed]
            if "image" in rel.reltype:
                try:
                    img_bytes = rel.target_part.blob
                    img_counter[0] += 1
                    os.makedirs(img_dir, exist_ok=True)
                    ext = rel.target_part.content_type.split("/")[-1]
                    filename = f"{img_prefix}img_{img_counter[0]}.{ext}"
                    img_path = os.path.join(img_dir, filename)
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)
                    with Image.open(BytesIO(img_bytes)) as img_pil:
                        txt_ocr = ejecutar_ocr(img_pil, lang)
                    rel_path = img_path.replace("\\", "/")
                    bloque = f"\n![imagen]({rel_path})\n"
                    if txt_ocr and not txt_ocr.startswith("["):
                        bloque += f"\n> **OCR de imagen:** {txt_ocr.replace(chr(10), ' ')}\n"
                    bloques.append(bloque)
                except Exception as e:
                    print(f"  [Advertencia] No se pudo procesar imagen: {e}", file=sys.stderr)
    return "".join(bloques)


def convert_docx(path: str, lang: str = "spa", img_dir: str = None, img_prefix: str = "") -> str:
    base_name = os.path.splitext(os.path.basename(path))[0]
    if img_dir is None:
        img_dir = os.path.join(os.path.dirname(path), f"{base_name}_images")

    doc = Document(path)
    partes = []
    img_counter = [0]

    for elem in doc.element.body:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag == "p":
            from docx.text.paragraph import Paragraph
            parrafo = Paragraph(elem, doc)

            nivel = _nivel_heading(parrafo)
            texto = parrafo.text.strip()

            # Imágenes en este párrafo
            imagenes_md = _procesar_imagenes_parrafo(parrafo, doc, img_dir, img_counter, lang, img_prefix)
            if imagenes_md:
                partes.append(imagenes_md)

            if not texto:
                continue

            if nivel is not None:
                prefijo = HEADING_MAP.get(nivel, "####")
                partes.append(f"\n{prefijo} {texto}\n\n")
            elif parrafo.style and parrafo.style.name in ("List Bullet", "List Number"):
                partes.append(f"- {texto}\n")
            else:
                partes.append(f"{texto}\n")

        elif tag == "tbl":
            from docx.table import Table
            tabla = Table(elem, doc)
            filas = []
            for fila in tabla.rows:
                filas.append([celda.text for celda in fila.cells])
            if filas:
                partes.append("\n" + tabla_a_markdown(filas) + "\n")

    return "".join(partes)
