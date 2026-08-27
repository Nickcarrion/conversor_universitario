import sys
import pytesseract
from PIL import Image

_disponible = None  # None = sin comprobar


def _tesseract_disponible() -> bool:
    global _disponible
    if _disponible is None:
        try:
            pytesseract.get_tesseract_version()
            _disponible = True
        except Exception:
            print(
                "\n[Advertencia] Tesseract no encontrado. OCR desactivado.\n"
                "  Instala con: winget install UB-Mannheim.TesseractOCR\n",
                file=sys.stderr,
            )
            _disponible = False
    return _disponible


def ejecutar_ocr(imagen_pil: Image.Image, lang: str = "spa") -> str:
    if not _tesseract_disponible():
        return "[OCR no disponible: Tesseract no instalado]"
    try:
        # Tesseract no acepta modos raros (P, CMYK, LA, 1): normalizar a RGB
        if imagen_pil.mode not in ("RGB", "L"):
            imagen_pil = imagen_pil.convert("RGB")
        return pytesseract.image_to_string(imagen_pil, lang=lang).strip()
    except Exception as e:
        print(f"[Advertencia] Error de OCR: {e}", file=sys.stderr)
        return f"[Error de OCR: {e}]"
