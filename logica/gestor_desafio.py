import random

class GestorDesafio:
    def __init__(self):
        self.vidas_maximas = 3
        self.vidas = self.vidas_maximas
        self.tiempo_restante = 300  # 5 minutos en segundos
        self.etapa_actual = 1
        self.en_juego = False
        
        # Base temporal de preguntas para la Etapa 1 (Luego se migrará al JSON)
        self.banco_etapa_1 = [
            {
                "pregunta": "Identifique el método numérico cuya fórmula de aproximación es:\nx = a - f(a) * (b - a) / (f(b) - f(a))",
                "opciones": ["Bisectriz", "Falsa Posición", "Secante", "Newton-Raphson"],
                "correcta": "Falsa Posición"
            },
            {
                "pregunta": "Método que requiere transformar algebraicamente f(x) = 0 a la forma x = g(x) para iterar:",
                "opciones": ["Punto Fijo", "Lagrange", "Interpolación Lineal", "Bisectriz"],
                "correcta": "Punto Fijo"
            },
            {
                "pregunta": "El proceso iterativo se detiene cuando el error absoluto es menor o igual a:",
                "opciones": ["El límite b", "La derivada de f(x)", "La Tolerancia (ε)", "Cero exacto"],
                "correcta": "La Tolerancia (ε)"
            }
        ]
        self.pregunta_actual = None

    def iniciar_partida(self):
        self.vidas = self.vidas_maximas
        self.tiempo_restante = 300
        self.etapa_actual = 1
        self.en_juego = True

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
        self.pregunta_actual = random.choice(self.banco_etapa_1)
        # Mezclar opciones para que no siempre estén en el mismo orden
        opciones_mezcladas = self.pregunta_actual["opciones"].copy()
        random.shuffle(opciones_mezcladas)
        return self.pregunta_actual["pregunta"], opciones_mezcladas

    def verificar_respuesta_etapa_1(self, respuesta_jugador):
        if not self.pregunta_actual:
            return False
        return respuesta_jugador == self.pregunta_actual["correcta"]