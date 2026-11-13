import json
import os

class GestorManual:
    @staticmethod
    def obtener_todas_las_fichas():
        """Lee y devuelve todas las fichas técnicas del manual."""
        ruta = os.path.join("recursos", "manual_ingeniero.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("metodos", [])
        except FileNotFoundError:
            print("Error: Base de datos del manual no encontrada.")
            return []