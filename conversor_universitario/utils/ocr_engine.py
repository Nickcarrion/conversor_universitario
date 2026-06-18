import sys
import pytesseract
from PIL import Image

_tesseract_warned = False


def ejecutar_ocr(imagen_pil: Image.Image, lang: str = "spa") -> str:
    global _tesseract_warned
    try:
        texto = pytesseract.image_to_string(imagen_pil, lang=lang)
        return texto.strip()
    except pytesseract.TesseractNotFoundError:
        if not _tesseract_warned:
            print(
                "\n[Advertencia] Tesseract no encontrado. OCR desactivado.\n"
                "  Instala con: winget install UB-Mannheim.TesseractOCR\n",
                file=sys.stderr,
            )
            _tesseract_warned = True
        return "[OCR no disponible: Tesseract no instalado]"
    except Exception as e:
        print(f"[Advertencia] Error de OCR: {e}", file=sys.stderr)
        return f"[Error de OCR: {e}]"
