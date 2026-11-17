import os

# Raíz del proyecto = carpeta que contiene main.py (un nivel arriba de /utilidades)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_RECURSOS = os.path.join(RAIZ_PROYECTO, "recursos")


def ruta_recurso(nombre_archivo):
    """Ruta absoluta de un archivo de /recursos, sin importar desde dónde se ejecute el programa."""
    return os.path.join(CARPETA_RECURSOS, nombre_archivo)


def mensaje_no_encontrado(nombre_archivo):
    """Texto de error que dice qué ruta se buscó y qué archivos hay realmente en /recursos."""
    texto = f"Error: No se encontró {nombre_archivo}\n  Se buscó en: {ruta_recurso(nombre_archivo)}"
    if os.path.isdir(CARPETA_RECURSOS):
        existentes = ", ".join(sorted(os.listdir(CARPETA_RECURSOS))) or "(carpeta vacía)"
        texto += f"\n  Archivos en recursos/: {existentes}"
    else:
        texto += f"\n  La carpeta recursos/ no existe en: {RAIZ_PROYECTO}"
    return texto