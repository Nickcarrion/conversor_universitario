import os
from datetime import datetime


def crear_frontmatter(filename: str) -> str:
    nombre_sin_ext = os.path.splitext(filename)[0]
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"---\n"
        f"archivo_original: {filename}\n"
        f"fecha_conversion: {fecha}\n"
        f"herramienta: Conversor Academico Markdown v2.0\n"
        f"---\n\n"
        f"# {nombre_sin_ext}\n\n"
    )


def crear_frontmatter_obsidian(filename: str, carpeta: str = "") -> str:
    """Propiedades YAML validas para Obsidian. Sin H1: el nombre de la nota es el titulo."""
    tipo = os.path.splitext(filename)[1][1:].lower()
    lineas = [
        "---",
        f'archivo_original: "{filename}"',
        f"tipo: {tipo}",
    ]
    if carpeta:
        lineas.append(f'curso: "{carpeta}"')
    lineas += [
        f"fecha_conversion: {datetime.now().strftime('%Y-%m-%d')}",
        "tags:",
        "  - conversion",
        f"  - {tipo}",
        "---",
        "",
        "",
    ]
    return "\n".join(lineas)


def tabla_a_markdown(filas: list) -> str:
    if not filas:
        return ""

    def limpiar_celda(c) -> str:
        if c is None:
            return ""
        return str(c).replace("\n", " ").replace("|", "\\|").strip()

    lineas = []
    encabezado = filas[0]
    lineas.append("| " + " | ".join(limpiar_celda(c) for c in encabezado) + " |")
    lineas.append("| " + " | ".join("---" for _ in encabezado) + " |")
    for fila in filas[1:]:
        # Pad filas cortas al ancho del encabezado
        fila_pad = list(fila) + [""] * (len(encabezado) - len(fila))
        lineas.append("| " + " | ".join(limpiar_celda(c) for c in fila_pad) + " |")
    return "\n".join(lineas) + "\n"
