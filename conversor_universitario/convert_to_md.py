import os
import sys

from tqdm import tqdm

from utils.md_formatter import crear_frontmatter
from core.pdf_processor import convert_pdf
from core.pptx_processor import convert_pptx
from core.docx_processor import convert_docx
from core.xlsx_processor import convert_xlsx

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "data_extraida")
IMG_DIR  = os.path.join(OUT_DIR, "imagenes")

IDIOMA_OCR = "spa"  # Cambia a "eng", "spa+eng", etc. según necesites

# ============================================================================

EXTENSIONES = {
    ".pdf":  convert_pdf,
    ".pptx": convert_pptx,
    ".ppsx": convert_pptx,
    ".docx": convert_docx,
    ".xlsx": convert_xlsx,
}


def _md_name_from_path(file_path: str, data_dir: str, include_ext: bool = False) -> str:
    """Deriva el nombre del .md a partir de la ruta relativa dentro de data/.

    Ejemplo: data/Actividad 10 tarea/Archivo.pdf -> "Actividad 10 tarea - Archivo.md"
    Si include_ext=True: "Actividad 10 tarea - Archivo (pdf).md" (para resolver colisiones)
    """
    rel   = os.path.relpath(file_path, data_dir)
    parts = rel.replace("\\", "/").split("/")
    ext   = os.path.splitext(parts[-1])[1][1:].lower()
    stem  = os.path.splitext(parts[-1])[0]
    dirs  = parts[:-1]
    base  = " - ".join(dirs + [stem]) if dirs else stem
    if include_ext:
        return f"{base} ({ext}).md"
    return base + ".md"


def _resolver_nombres(lista: list, data_dir: str) -> dict:
    """Retorna {file_path: md_name} resolviendo colisiones añadiendo el tipo de archivo."""
    from collections import Counter
    base_names = [_md_name_from_path(p, data_dir) for p in lista]
    counts = Counter(base_names)
    result = {}
    for archivo, nombre in zip(lista, base_names):
        if counts[nombre] > 1:
            result[archivo] = _md_name_from_path(archivo, data_dir, include_ext=True)
        else:
            result[archivo] = nombre
    return result


def _img_prefix_from_path(file_path: str, data_dir: str) -> str:
    """Prefijo para nombrar imágenes, evitando colisiones entre archivos del mismo nombre."""
    rel   = os.path.relpath(file_path, data_dir)
    parts = rel.replace("\\", "/").split("/")
    stem  = os.path.splitext(parts[-1])[0]
    dirs  = parts[:-1]
    raw   = "_".join(dirs + [stem]) if dirs else stem
    return raw.replace(" ", "_") + "_"


def procesar_archivo(file_path: str, lang: str, out_dir: str, img_dir: str, data_dir: str, md_name: str) -> None:
    if not os.path.isfile(file_path):
        print(f"[!] No existe o no es un archivo: {file_path}", file=sys.stderr)
        return

    ext = os.path.splitext(file_path)[1].lower()
    conversor = EXTENSIONES.get(ext)
    if conversor is None:
        print(f"[!] Formato no soportado: {ext}  ({file_path})", file=sys.stderr)
        return

    out_path = os.path.join(out_dir, md_name)
    prefix   = _img_prefix_from_path(file_path, data_dir)

    print(f"\nProcesando: {os.path.relpath(file_path, data_dir)}")

    try:
        frontmatter = crear_frontmatter(os.path.basename(file_path))
        if ext in (".xlsx",):
            contenido = conversor(file_path)
        else:
            contenido = conversor(file_path, lang, img_dir=img_dir, img_prefix=prefix)

        # Convierte rutas absolutas de imágenes a relativas dentro de data_extraida/
        abs_img_prefix = img_dir.replace("\\", "/")
        contenido = contenido.replace(abs_img_prefix + "/", "imagenes/")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(frontmatter + contenido)

        print(f"OK -> {md_name}")

    except PermissionError:
        print(
            f"[!] El archivo esta protegido con contrasena o en uso: {file_path}",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"[!] Error procesando {file_path}: {e}", file=sys.stderr)
        raise


def descubrir_archivos(data_dir: str) -> list:
    """Busca recursivamente todos los archivos con extensión soportada en data_dir."""
    archivos = []
    for raiz, _, ficheros in os.walk(data_dir):
        for f in sorted(ficheros):
            if os.path.splitext(f)[1].lower() in EXTENSIONES:
                archivos.append(os.path.join(raiz, f))
    return archivos


def main() -> None:
    data_dir = os.path.abspath(DATA_DIR)
    out_dir  = os.path.abspath(OUT_DIR)
    img_dir  = os.path.abspath(IMG_DIR)

    if not os.path.isdir(data_dir):
        print(f"[!] No se encontro la carpeta de datos: {data_dir}", file=sys.stderr)
        sys.exit(1)

    lista = descubrir_archivos(data_dir)

    if not lista:
        print(f"No se encontraron archivos soportados en: {data_dir}", file=sys.stderr)
        sys.exit(1)

    nombres = _resolver_nombres(lista, data_dir)

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    print(f"Archivos encontrados: {len(lista)}\n")

    for archivo in tqdm(lista, desc="Progreso", unit="archivo"):
        procesar_archivo(archivo, IDIOMA_OCR, out_dir, img_dir, data_dir, nombres[archivo])

    print("\nConversion completada.")


if __name__ == "__main__":
    main()
