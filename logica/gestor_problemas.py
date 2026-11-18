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
        elif tipo == "terminos_independientes":
            # Para Gauss-Seidel y Jacobi
            b1 = round(random.uniform(reglas["b1_min"], reglas["b1_max"]), 2)
            b2 = round(random.uniform(reglas["b2_min"], reglas["b2_max"]), 2)
            b3 = round(random.uniform(reglas["b3_min"], reglas["b3_max"]), 2)
            
            # Inyectamos los valores en la lista que espera el motor matemático
            p_instanciado["sistema"]["terminos_independientes"] = [b1, b2, b3]
            
            # Actualizamos el contexto visual para que el jugador vea los números reales
            p_instanciado["contexto"] = p_instanciado["contexto"].replace("B1", str(b1)).replace("B2", str(b2)).replace("B3", str(b3))

        elif tipo == "x_interpolar":
            # Para Interpolación Lineal básica
            x = round(random.uniform(reglas["x_min"], reglas["x_max"]), 2)
            
            if "parametros_fijos" not in p_instanciado: 
                p_instanciado["parametros_fijos"] = {}
                
            p_instanciado["parametros_fijos"]["x_interpolar"] = x
            p_instanciado["contexto"] += f"\n\nPunto a estimar: x = {x}"

        elif tipo == "yi_y_x_interpolar":
            # Para Lagrange y Newton (Diferencias Divididas, Adelante, Atrás)
            x = round(random.uniform(reglas["x_min"], reglas["x_max"]), 2)
            
            if "parametros_fijos" not in p_instanciado: 
                p_instanciado["parametros_fijos"] = {}
            p_instanciado["parametros_fijos"]["x_interpolar"] = x
            
            # Generar nuevos valores Y iterando la base y sumando/restando el delta
            yi_base = reglas["yi_base"]
            delta = reglas["yi_delta"]
            yi_nuevos = [round(y + random.uniform(-delta, delta), 2) for y in yi_base]
            
            # Inyectamos la nueva matriz Y
            if "datos_base" not in p_instanciado: 
                p_instanciado["datos_base"] = {}
            p_instanciado["datos_base"]["yi"] = yi_nuevos
            
            p_instanciado["contexto"] += f"\n\nNuevas lecturas de sensores (Y): {yi_nuevos}\nPunto a estimar: x = {x}"
            
        elif tipo == "yi_variable":
            # Para Mínimos Cuadrados
            yi_base = reglas["yi_base"]
            delta = reglas["yi_delta"]
            yi_nuevos = [round(y + random.uniform(-delta, delta), 2) for y in yi_base]
            
            if "datos_base" not in p_instanciado: 
                p_instanciado["datos_base"] = {}
            p_instanciado["datos_base"]["yi"] = yi_nuevos
            
            p_instanciado["contexto"] += f"\n\nNuevas lecturas de sensores (Y): {yi_nuevos}"
            
        elif tipo == "intervalo_y_n":
            # Para Trapecio (n variable)
            a = reglas["a_fijo"]
            b = reglas["b_fijo"]
            n = random.choice(reglas["opciones_n"])
            
            if "parametros_fijos" not in p_instanciado:
                p_instanciado["parametros_fijos"] = {}
            p_instanciado["parametros_fijos"]["a"] = a
            p_instanciado["parametros_fijos"]["b"] = b
            p_instanciado["parametros_fijos"]["n"] = n
            
            p_instanciado["contexto"] += f"\n\nIntervalo: [{a}, {b}] | Segmentos (n): {n}"
            
        elif tipo in ["intervalo_y_n_par", "intervalo_y_n_multiplo_3"]:
            # Para Simpson 1/3 y Simpson 3/8
            opcion = random.choice(reglas["opciones_parametros"])
            
            if "parametros_fijos" not in p_instanciado:
                p_instanciado["parametros_fijos"] = {}
            p_instanciado["parametros_fijos"]["a"] = opcion["a"]
            p_instanciado["parametros_fijos"]["b"] = opcion["b"]
            p_instanciado["parametros_fijos"]["n"] = opcion["n"]
            
            p_instanciado["contexto"] += f"\n\nIntervalo: [{opcion['a']}, {opcion['b']}] | Segmentos (n): {opcion['n']}"
            
        elif tipo == "y0_variable":
            # Para Euler y Runge-Kutta
            y0 = random.choice(reglas["opciones_y0"])
            
            if "parametros_fijos" not in p_instanciado:
                p_instanciado["parametros_fijos"] = {}
            p_instanciado["parametros_fijos"]["y0"] = y0
            
            p_instanciado["contexto"] += f"\n\nCondición inicial: y(0) = {y0}"

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
        ruta = ruta_recurso("banco_practica.json")
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
    
    @staticmethod
    def cargar_datos_nivel_2():
        # Actualizado con tu nuevo nombre de archivo
        ruta = ruta_recurso("banco_problemas_nivel2.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("problemas_nivel_2", [])
        except FileNotFoundError:
            print("Error: No se encontró banco_problemas_nivel2.json")
            return []
        
    @staticmethod
    def obtener_problema_aleatorio_nivel_2():
        """Devuelve un problema aleatorio instanciado del Nivel 2 (Medio Curso) para el Modo Desafío."""
        datos = GestorProblemas.cargar_datos_nivel_2()
        if not datos: return None
        plantilla = random.choice(datos)
        return GestorProblemas.instanciar_problema(plantilla)
    
    @staticmethod
    def cargar_datos_nivel_3():
        ruta = ruta_recurso("banco_problemas_nivel3.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos.get("problemas_nivel_3", [])
        except FileNotFoundError:
            print("Error: No se encontró banco_problemas_nivel3.json")
            return []
            
    @staticmethod
    def obtener_problema_aleatorio_nivel_3():
        """Devuelve un problema aleatorio instanciado del Nivel 3 (Ordinario) para el Modo Desafío."""
        datos = GestorProblemas.cargar_datos_nivel_3()
        if not datos: return None
        plantilla = random.choice(datos)
        return GestorProblemas.instanciar_problema(plantilla)
    
    @staticmethod
    def obtener_quiz_intermedio():
        """Carga y procesa dinámicamente un quiz de bonificación."""
        ruta = ruta_recurso("quizzes_lineales_intermedios_aleatorios.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                quizzes = datos.get("quizzes_rapidos", [])
        except FileNotFoundError:
            return None
            
        if not quizzes: return None
        
        quiz_plantilla = random.choice(quizzes)
        quiz = quiz_plantilla.copy()
        tipo_al = quiz["aleatorio"]["tipo"]
        
        # PROCESAMIENTO DINÁMICO SEGÚN EL TIPO DE QUIZ
        if tipo_al == "generacion_columna":
            n_ops = random.choice([3, 4])
            min_v = quiz["aleatorio"]["rango_valores"]["min"]
            max_v = quiz["aleatorio"]["rango_valores"]["max"]
            opciones = [round(random.uniform(min_v, max_v), 2) for _ in range(n_ops)]
            
            # Lógica: Seleccionar el mayor valor absoluto
            correcto = max(opciones, key=abs)
            
            quiz["opciones_pantalla"] = opciones
            quiz["respuesta_correcta"] = correcto
            quiz["texto_pregunta"] = f"{quiz['contexto']}\n\nColumna actual: {opciones}\n\n{quiz['pregunta']}"
            quiz["tipo_input"] = "botones"
            
        elif tipo_al == "variables_montante":
            rangos = quiz["aleatorio"]["rangos"]
            while True:
                p_ant = random.choice(rangos["PivoteAnterior"])
                p_act = random.choice(rangos["PivoteActual"])
                e_act = random.randint(rangos["ElementoActual"][0], rangos["ElementoActual"][1])
                f_piv = random.randint(rangos["FilaPivote"][0], rangos["FilaPivote"][1])
                c_piv = random.randint(rangos["ColumnaPivote"][0], rangos["ColumnaPivote"][1])
                
                # Restricción del motor: División exacta
                if (p_act * e_act - f_piv * c_piv) % p_ant == 0:
                    respuesta = (p_act * e_act - f_piv * c_piv) // p_ant
                    break
                    
            detalles = f"Pivote Anterior: {p_ant}\nPivote Actual: {p_act}\nElemento Actual: {e_act}\nFila Pivote: {f_piv}\nColumna Pivote: {c_piv}"
            quiz["texto_pregunta"] = f"{quiz['contexto']}\n\n{detalles}\n\n{quiz['pregunta']}"
            quiz["respuesta_correcta"] = str(respuesta)
            quiz["tipo_input"] = "texto"
            
        elif tipo_al == "seleccion_matriz":
            eleccion = random.choice(quiz["aleatorio"]["pool_opciones"])
            matriz_str = eleccion["matriz_display"]
            
            quiz["texto_pregunta"] = f"{quiz['contexto']}\n\n{matriz_str}\n\n{quiz['pregunta']}"
            quiz["opciones_pantalla"] = quiz["opciones_generales"]
            quiz["respuesta_correcta"] = eleccion["respuesta_correcta"]
            quiz["explicacion"] = eleccion["explicacion"]
            quiz["tipo_input"] = "botones"

        return quiz