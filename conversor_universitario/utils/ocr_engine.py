import os
import shutil
import sys
from pathlib import Path

import pytesseract
from PIL import Image

_disponible = None  # None = sin comprobar


def _localizar_tesseract() -> None:
    """El instalador de Windows no agrega Tesseract al PATH: buscarlo a mano."""
    if shutil.which("tesseract"):
        return
    for ruta in (
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
    ):
        if ruta.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(ruta)
            return


def _localizar_tessdata() -> None:
    """spa.traineddata suele faltar en Program Files (sin permisos de escritura)."""
    local = Path.home() / ".tessdata"
    if (local / "spa.traineddata").is_file():
        os.environ.setdefault("TESSDATA_PREFIX", str(local))


_localizar_tesseract()
_localizar_tessdata()


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
    if not lang:  # lang=None -> modo Obsidian, sin OCR
        return ""
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
