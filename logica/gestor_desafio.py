import json
import os
import random
from utilidades.rutas import ruta_recurso, mensaje_no_encontrado
from logica.gestor_problemas import GestorProblemas
from logica.gestor_practica import GestorPractica

PROBLEMAS_TOTALES_ETAPA_3 = 1


class GestorDesafio:
    def __init__(self):
        self.vidas_maximas = 3
        self.vidas = self.vidas_maximas 
        self.etapa_actual = 1
        self.en_juego = False
        self.puntuacion = 0
        self.motor_matematico = GestorPractica()
        self.problema_actual_n2 = None
        self.metodo_actual_n2 = None
        self.problema_actual_n3 = None
        self.metodo_actual_n3 = None
        self.problemas_totales_etapa_3 = PROBLEMAS_TOTALES_ETAPA_3
        self.problemas_resueltos_etapa_3 = 0
        self.ids_usados_etapa_3 = []
        
        # Variables de control de progresión
        self.config_partida = {}
        self.preguntas_totales_etapa_1 = 7  # valor por defecto; se sobrescribe con el JSON
        self.preguntas_respondidas = 0
        self.banco_etapa_1 = self.cargar_banco_preguntas()
        self.preguntas_totales_etapa_1 = self.config_partida.get("preguntas_por_partida", 7)
        self.preguntas_disponibles = []
        self.pregunta_actual = None
        
    def sumar_puntos(self, cantidad):
        """Añade puntos al marcador del desafío."""
        self.puntuacion += cantidad

    def cargar_banco_preguntas(self):
        ruta = ruta_recurso("preguntas_teoricas.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.config_partida = datos.get("configuracion_partida", {})
                return datos.get("preguntas", [])
        except FileNotFoundError:
            print(mensaje_no_encontrado("preguntas_teoricas.json"))
            return []

    def iniciar_partida(self):
        self.vidas = self.vidas_maximas
        self.tiempo_restante = 900
        self.etapa_actual = 1
        self.en_juego = True
        
        # Reiniciar control de preguntas
        self.preguntas_respondidas = 0
        self.puntuacion = 0

        # Reiniciar control de la etapa 3
        self.problema_actual_n3 = None
        self.metodo_actual_n3 = None
        self.problemas_resueltos_etapa_3 = 0
        self.ids_usados_etapa_3 = []
        # Seleccionar 7 preguntas al azar sin repetir
        total = min(self.preguntas_totales_etapa_1, len(self.banco_etapa_1))
        self.preguntas_totales_etapa_1 = total
        if self.config_partida.get("mezclar_orden_preguntas", True):
            self.preguntas_disponibles = random.sample(self.banco_etapa_1, total)
        else:
            self.preguntas_disponibles = self.banco_etapa_1[:total]

    def restar_vida(self):
        self.vidas -= 1
        if self.vidas <= 0:
            self.en_juego = False
        return self.vidas

    def decrementar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
        if self.tiempo_restante <= 0:
            self.en_juego = False
        return self.tiempo_restante

    def formatear_tiempo(self):
        minutos = self.tiempo_restante // 60
        segundos = self.tiempo_restante % 60
        return f"{minutos:02d}:{segundos:02d}"

    def obtener_pregunta_etapa_1(self):
        if not self.preguntas_disponibles:
            return None, None
            
        self.pregunta_actual = self.preguntas_disponibles.pop(0)
        opciones = self.pregunta_actual["opciones"].copy()
        if self.config_partida.get("mezclar_opciones", True):
            random.shuffle(opciones)
        return self.pregunta_actual["pregunta"], opciones

    def obtener_metadatos_pregunta(self):
        """Categoría, dificultad y explicación de la pregunta en curso."""
        if not self.pregunta_actual:
            return {}
        return {
            "categoria": self.pregunta_actual.get("categoria", ""),
            "dificultad": self.pregunta_actual.get("dificultad", ""),
            "explicacion": self.pregunta_actual.get("explicacion", ""),
        }

    def verificar_respuesta_etapa_1(self, respuesta_jugador):
        if not self.pregunta_actual:
            return False
            
        letra_correcta = self.pregunta_actual["respuesta_correcta"] 
        mapa_indices = {"A": 0, "B": 1, "C": 2, "D": 3}
        indice_correcto = mapa_indices.get(letra_correcta)
        
        texto_correcto_original = self.pregunta_actual["opciones"][indice_correcto]
            
        es_correcta = (respuesta_jugador == texto_correcto_original)
        
        if es_correcta:
            self.preguntas_respondidas += 1
            
        return es_correcta
        
    def etapa_1_completada(self):
        return self.preguntas_respondidas >= self.preguntas_totales_etapa_1
    
    def preparar_etapa_2(self):
        """Obtiene un problema aleatorio de Nivel 2 y arranca el motor matemático"""
        exito = False
        intentos = 0
        
        # Bucle de seguridad: intenta generar problemas hasta que uno se resuelva correctamente
        while not exito and intentos < 10:
            self.problema_actual_n2 = GestorProblemas.obtener_problema_aleatorio_nivel_2()
            if not self.problema_actual_n2: 
                break
                
            self.metodo_actual_n2 = random.choice(self.problema_actual_n2["metodos_viables"])
            exito = self.motor_matematico.inicializar_sesion(self.problema_actual_n2, self.metodo_actual_n2)
            intentos += 1
    def verificar_respuesta_etapa_2(self, valor):
        # Usamos el motor matemático para validar el número
        correcto, valor_real = self.motor_matematico.verificar_respuesta(valor)
        return correcto, valor_real

    # ==========================================
    # ETAPA 3: SOBRECARGA DEL NÚCLEO (Nivel 3)
    # ==========================================
    def preparar_etapa_3(self):
        """
        Elige un problema de Nivel 3 cuyo método el motor YA sepa resolver y arranca la sesión.
        Los métodos que todavía no tienen lógica se saltan solos (ver logica/gestor_metodos.py).
        Devuelve True si hay un problema listo y False si no hay ninguno disponible.
        """
        plantillas = GestorProblemas.cargar_datos_nivel_3()
        random.shuffle(plantillas)

        for plantilla in plantillas:
            if plantilla.get("id") in self.ids_usados_etapa_3:
                continue
            metodos = list(plantilla.get("metodos_viables", []))
            random.shuffle(metodos)

            for metodo in metodos:
                if not self.motor_matematico.metodo_soportado(metodo):
                    continue
                problema = GestorProblemas.instanciar_problema(plantilla)
                if self.motor_matematico.inicializar_sesion(problema, metodo):
                    self.problema_actual_n3 = problema
                    self.metodo_actual_n3 = metodo
                    self.ids_usados_etapa_3.append(plantilla.get("id"))
                    return True

        self.problema_actual_n3 = None
        self.metodo_actual_n3 = None
        return False

    def metodos_pendientes_etapa_3(self):
        """Métodos de Nivel 3 que todavía no tienen motor (para avisar al equipo)."""
        pendientes = set()
        for plantilla in GestorProblemas.cargar_datos_nivel_3():
            for metodo in plantilla.get("metodos_viables", []):
                if not self.motor_matematico.metodo_soportado(metodo):
                    pendientes.add(metodo)
        return sorted(pendientes)

    def texto_problema_etapa_3(self):
        """Contexto del problema + los datos que el jugador necesita y el JSON no imprime."""
        problema = self.problema_actual_n3
        if not problema:
            return ""
        texto = problema.get("contexto", "")
        datos = problema.get("datos_base", {})

        # Mínimos cuadrados: el contexto solo trae las Y, faltan las X
        if "xi" in datos and "xi:" not in texto:
            texto += f"\nLecturas (X): {datos['xi']}"
        # Euler / Runge-Kutta: el paso h y t0 viven en datos_base y no se muestran
        if "h" in datos:
            texto += f"\nt0 = {datos.get('t0', 0)}  |  paso h = {datos['h']}"
        return texto

    def paso_etapa_3_actual(self):
        return self.motor_matematico.obtener_datos_paso_actual()

    def total_pasos_etapa_3(self):
        return len(self.motor_matematico.tabla_respuestas)

    def verificar_respuesta_etapa_3(self, valor):
        return self.motor_matematico.verificar_respuesta(valor)

    def registrar_problema_etapa_3_resuelto(self):
        """Suma un problema resuelto. Devuelve True si ya se completó la etapa 3 (victoria)."""
        self.problemas_resueltos_etapa_3 += 1
        return self.problemas_resueltos_etapa_3 >= self.problemas_totales_etapa_3