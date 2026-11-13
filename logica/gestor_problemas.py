import json
import os

class GestorProblemas:
    @staticmethod
    def obtener_problema(id_problema):
        """Busca y devuelve un problema específico desde el JSON."""
        ruta = os.path.join("recursos", "banco_problemas.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for p in datos.get("problemas_basicos", []):
                    if p["id"] == id_problema:
                        return p
        except FileNotFoundError:
            print("Error: No se encontró banco_problemas.json")
        return None

    @staticmethod
    def obtener_todos():
        """Devuelve la lista completa de problemas del banco."""
        ruta = os.path.join("recursos", "banco_problemas.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("problemas_basicos", [])
        except FileNotFoundError:
            print("Error: No se encontró banco_problemas.json")
            return []