import json
import os
import random
import copy
from utilidades.rutas import ruta_recurso, mensaje_no_encontrado
import math # Necesario para evaluar funciones matemáticas en el solucionario y gestor

class GestorProblemas:
    @staticmethod
    def cargar_datos_crudos():
        ruta = ruta_recurso("banco_problemas.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            print(mensaje_no_encontrado("banco_problemas.json"))
            return {"problemas_basicos": []}

    @staticmethod
    def instanciar_problema(problema_base):
        """Toma la plantilla del JSON y genera valores concretos según su tipo de aleatoriedad."""
        p_instanciado = copy.deepcopy(problema_base)
        
        if "aleatorio" not in p_instanciado:
            return p_instanciado

        reglas = p_instanciado["aleatorio"]
        tipo = reglas.get("tipo")

        if tipo == "intervalo_ab":
            if "opciones_intervalo" in reglas:
                opcion = random.choice(reglas["opciones_intervalo"])
            else:
                opcion = reglas
                
            a = round(random.uniform(opcion["a_min"], opcion["a_max"]), 2)
            b = round(random.uniform(opcion["b_min"], opcion["b_max"]), 2)
            
            if a > b: a, b = b, a
                
            p_instanciado["valores_iniciales"] = {"a": a, "b": b}
            p_instanciado["contexto"] = p_instanciado["contexto"] + f"\n\nIntervalo asignado: [{a}, {b}]"

        elif tipo == "valor_inicial":
            x0 = round(random.uniform(reglas["x0_min"], reglas["x0_max"]), 2)
            p_instanciado["valores_iniciales"] = {"x0": x0}
            p_instanciado["contexto"] = p_instanciado["contexto"] + f"\n\nValor inicial asignado: x0 = {x0}"
            
        elif tipo == "dos_valores_iniciales":
            x0 = round(random.uniform(reglas["x0_min"], reglas["x0_max"]), 2)
            x1 = round(random.uniform(reglas["x1_min"], reglas["x1_max"]), 2)
            p_instanciado["valores_iniciales"] = {"x0": x0, "x1": x1}
            p_instanciado["contexto"] = p_instanciado["contexto"] + f"\n\nValores iniciales asignados: x0 = {x0}, x1 = {x1}"

        elif tipo in ("x_interpolar", "yi_y_x_interpolar"):
            datos = p_instanciado["datos_base"]

            # Los yi se perturban respecto a los valores base (si el problema lo pide)
            if tipo == "yi_y_x_interpolar":
                delta = reglas["yi_delta"]
                datos["yi"] = [round(y + random.uniform(-delta, delta), 2) for y in reglas["yi_base"]]

            x = round(random.uniform(reglas["x_min"], reglas["x_max"]), 2)
            p_instanciado["valores_iniciales"] = {"x": x}

            xs = "   ".join(str(v) for v in datos["xi"])
            ys = "   ".join(str(v) for v in datos["yi"])
            p_instanciado["contexto"] = (p_instanciado["contexto"]
                                         + f"\n\nDatos:\n  xi:  {xs}\n  yi:  {ys}\nPunto a estimar: x = {x}")

        del p_instanciado["aleatorio"]
        return p_instanciado

    @staticmethod
    def obtener_problema_instanciado(id_problema):
        """Busca un problema específico por ID y lo devuelve instanciado con valores concretos."""
        datos = GestorProblemas.cargar_datos_crudos()
        for p in datos.get("problemas_basicos", []):
            if p["id"] == id_problema:
                return GestorProblemas.instanciar_problema(p)
        return None

    @staticmethod
    def obtener_todos_instanciados():
        """Devuelve una lista con todos los problemas, cada uno con valores aleatorios generados en el momento."""
        datos = GestorProblemas.cargar_datos_crudos()
        return [GestorProblemas.instanciar_problema(p) for p in datos.get("problemas_basicos", [])]
        
    @staticmethod
    def obtener_problema_aleatorio_por_metodo(metodo):
        """Devuelve un problema instanciado aleatorio que soporte el método solicitado."""
        datos = GestorProblemas.cargar_datos_crudos()
        candidatos = [p for p in datos.get("problemas_basicos", []) if metodo in p.get("metodos_viables", [])]
        if candidatos:
            plantilla = random.choice(candidatos)
            return GestorProblemas.instanciar_problema(plantilla)
        return None
    
    @staticmethod
    def obtener_todos_practica():
        """Lee el catálogo de problemas fijos para el Modo Práctica."""
        ruta = os.path.join("recursos", "banco_practica.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("problemas_practica", [])
        except FileNotFoundError:
            print("Error: No se encontró banco_practica.json")
            return []

    @staticmethod
    def obtener_problema_practica(id_problema):
        """Busca un problema específico dentro del banco de práctica."""
        for p in GestorProblemas.obtener_todos_practica():
            if p["id"] == id_problema:
                return p
        return None