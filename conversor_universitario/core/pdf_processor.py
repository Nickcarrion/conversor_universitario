import os
import sys
from io import BytesIO

import pdfplumber
from pypdf import PdfReader
from PIL import Image

from utils.ocr_engine import ejecutar_ocr
from utils.md_formatter import tabla_a_markdown


def _extraer_imagenes_pagina(reader: PdfReader, idx: int, img_dir: str, lang: str, img_prefix: str = "") -> str:
    """Extrae imágenes embebidas de una página con pypdf y les aplica OCR."""
    bloques = []
    try:
        pypdf_page = reader.pages[idx]
        for img_idx, img_obj in enumerate(pypdf_page.images):
            os.makedirs(img_dir, exist_ok=True)
            filename = f"{img_prefix}pag_{idx + 1}_img_{img_idx + 1}.png"
            img_path = os.path.join(img_dir, filename)
            with open(img_path, "wb") as f:
                f.write(img_obj.data)

            with Image.open(BytesIO(img_obj.data)) as img_pil:
                txt_ocr = ejecutar_ocr(img_pil, lang)

            rel_path = img_path.replace("\\", "/")
            bloque = f"\n![imagen]({rel_path})\n"
            if txt_ocr and not txt_ocr.startswith("["):
                bloque += f"\n> **Texto detectado en imagen:**\n> {txt_ocr.replace(chr(10), ' ')}\n"
            bloques.append(bloque)
    except Exception as e:
        print(f"  [Advertencia] No se pudieron extraer imágenes de pág. {idx + 1}: {e}", file=sys.stderr)
    return "".join(bloques)


def _fallback_ocr_pagina(path: str, idx: int, img_dir: str, lang: str, img_prefix: str = "") -> str:
    """Último recurso: convierte la página entera a imagen y aplica OCR."""
    try:
        from pdf2image import convert_from_path

        paginas = convert_from_path(path, first_page=idx + 1, last_page=idx + 1)
        if not paginas:
            return ""
        img_pil = paginas[0]
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, f"{img_prefix}pag_{idx + 1}_scan.png")
        img_pil.save(img_path, "PNG")
        txt_ocr = ejecutar_ocr(img_pil, lang)
        rel_path = img_path.replace("\\", "/")
        return f"\n![Escaneo de página]({rel_path})\n\n{txt_ocr}\n"
    except ImportError:
        print(
            "[Advertencia] pdf2image no disponible. Instala Poppler y pdf2image para OCR de páginas escaneadas.",
            file=sys.stderr,
        )
        return "[Página sin texto extraíble y sin pdf2image disponible]\n"
    except Exception as e:
        print(f"  [Advertencia] Fallback OCR falló en pág. {idx + 1}: {e}", file=sys.stderr)
        return ""


def convert_pdf(path: str, lang: str = "spa", img_dir: str = None, img_prefix: str = "") -> str:
    base_name = os.path.splitext(os.path.basename(path))[0]
    if img_dir is None:
        img_dir = os.path.join(os.path.dirname(path), f"{base_name}_images")
    partes = []

    reader = PdfReader(path)
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        for idx, page in enumerate(pdf.pages):
            partes.append(f"\n## Pagina {idx + 1}\n\n")

            texto_nativo = page.extract_text() or ""

            tablas_md = ""
            tablas = page.extract_tables()
            if tablas:
                for tabla in tablas:
                    tablas_md += tabla_a_markdown(tabla) + "\n"

            imagenes_md = _extraer_imagenes_pagina(reader, idx, img_dir, lang, img_prefix)

            tiene_contenido = (
                len(texto_nativo.strip()) >= 50
                or tablas_md.strip()
                or imagenes_md.strip()
            )

            if not tiene_contenido:
                partes.append(_fallback_ocr_pagina(path, idx, img_dir, lang, img_prefix))
            else:
                if texto_nativo.strip():
                    partes.append(texto_nativo.strip() + "\n")
                if tablas_md:
                    partes.append(f"\n### Tablas detectadas\n\n{tablas_md}")
                if imagenes_md:
                    partes.append(imagenes_md)

            partes.append("\n---\n")
            print(f"  [{idx + 1}/{total}] Pagina procesada", end="\r")

    print()
    return "".join(partes)
