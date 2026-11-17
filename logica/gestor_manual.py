import json
import os
from utilidades.rutas import ruta_recurso, mensaje_no_encontrado

class GestorManual:
    @staticmethod
    def obtener_todas_las_fichas():
        """Lee y devuelve todas las fichas técnicas del manual."""
        ruta = ruta_recurso("manual_ingeniero.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("metodos", [])
        except FileNotFoundError:
            print(mensaje_no_encontrado("manual_ingeniero.json"))
            return []