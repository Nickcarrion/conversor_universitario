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
