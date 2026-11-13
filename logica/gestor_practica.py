from metodos.bisectriz import calcular_tabla_bisectriz

class GestorPractica:
    """Controla el estado de una sesión de práctica activa."""
    def __init__(self):
        self.problema_actual = None
        self.tabla_respuestas = []
        self.iteracion_actual = 0

    def inicializar_sesion(self, problema, metodo_seleccionado): 
        self.problema_actual = problema
        self.iteracion_actual = 0
        
        # Evaluamos el método que eligió el usuario
        if metodo_seleccionado == "BISECTRIZ":
            a = problema["valores_iniciales"]["a"]
            b = problema["valores_iniciales"]["b"]
            resultado = calcular_tabla_bisectriz(problema["funcion_python"], a, b, problema["tolerancia"])
            
            if resultado["estado"] == "exito":
                self.tabla_respuestas = resultado["iteraciones"]
                return True
                
        return False

    def verificar_respuesta(self, input_valor, margen=0.0001):
        """Verifica si la respuesta del usuario es correcta para el paso actual."""
        if self.iteracion_actual >= len(self.tabla_respuestas):
            return False, "Completado"

        valor_correcto = self.tabla_respuestas[self.iteracion_actual]["x_medio"]
        
        if abs(input_valor - valor_correcto) <= margen:
            self.iteracion_actual += 1
            return True, valor_correcto
        return False, None

    def obtener_datos_paso_actual(self):
        if self.iteracion_actual >= len(self.tabla_respuestas):
            return None
        return self.tabla_respuestas[self.iteracion_actual]