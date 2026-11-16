import json
import os
import random

class GestorDesafio:
    def __init__(self):
        self.vidas_maximas = 3
        self.vidas = self.vidas_maximas
        self.tiempo_restante = 300  
        self.etapa_actual = 1
        self.en_juego = False
        
        # Variables de control de progresión
        self.preguntas_totales_etapa_1 = 7
        self.preguntas_respondidas = 0
        self.banco_etapa_1 = self.cargar_banco_preguntas()
        self.preguntas_disponibles = []
        self.pregunta_actual = None

    def cargar_banco_preguntas(self):
        ruta = os.path.join("recursos", "preguntas_teoricas.json")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                # Ahora buscamos la clave correcta del JSON de tu compañero
                return datos.get("preguntas", []) 
        except FileNotFoundError:
            print("Error: No se encontró preguntas_teoricas.json")
            return []

    def iniciar_partida(self):
        self.vidas = self.vidas_maximas
        self.tiempo_restante = 300
        self.etapa_actual = 1
        self.en_juego = True
        
        # Reiniciar control de preguntas
        self.preguntas_respondidas = 0
        # Seleccionar 7 preguntas al azar sin repetir
        if len(self.banco_etapa_1) >= self.preguntas_totales_etapa_1:
            self.preguntas_disponibles = random.sample(self.banco_etapa_1, self.preguntas_totales_etapa_1)
        else:
            self.preguntas_disponibles = self.banco_etapa_1.copy()
            random.shuffle(self.preguntas_disponibles)

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
        opciones_mezcladas = self.pregunta_actual["opciones"].copy()
        random.shuffle(opciones_mezcladas)
        return self.pregunta_actual["pregunta"], opciones_mezcladas

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