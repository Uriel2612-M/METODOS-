from metodos.bisectriz import calcular_tabla_bisectriz
from metodos.interpolacion_lineal import calcular_tabla_interpolacion_lineal
from metodos.lagrange import calcular_tabla_lagrange
from metodos.Newton_diferencias_divididas import calcular_tabla_newton_dif_divididas
from metodos.newton_adelante import calcular_tabla_newton_adelante
from metodos.newton_atras import calcular_tabla_newton_atras

# Métodos de interpolación que la práctica sabe resolver
METODOS_INTERPOLACION = (
    "INTERPOLACION_LINEAL", "LAGRANGE", "NEWTON_DIVIDIDAS", "NEWTON_ADELANTE", "NEWTON_ATRAS",
)

MARGEN_BISECTRIZ = 0.0001
MARGEN_INTERPOLACION = 0.0002  # "El margen de error permitido es de 2 diez milésimas" (apuntes)


class GestorPractica:
    """Controla el estado de una sesión de práctica activa."""
    def __init__(self):
        self.problema_actual = None
        self.metodo = None
        self.tabla_respuestas = []
        self.iteracion_actual = 0
        self.resultado_final = None

    def metodo_soportado(self, metodo):
        return metodo == "BISECTRIZ" or metodo in METODOS_INTERPOLACION

    def es_interpolacion(self):
        return self.metodo in METODOS_INTERPOLACION

    def inicializar_sesion(self, problema, metodo_seleccionado):
        self.problema_actual = problema
        self.metodo = metodo_seleccionado
        self.iteracion_actual = 0
        self.tabla_respuestas = []
        self.resultado_final = None

        if metodo_seleccionado == "BISECTRIZ":
            a = problema["valores_iniciales"]["a"]
            b = problema["valores_iniciales"]["b"]
            resultado = calcular_tabla_bisectriz(problema["funcion_python"], a, b, problema["tolerancia"])

            if resultado["estado"] == "exito":
                self.tabla_respuestas = resultado["iteraciones"]
                for fila in self.tabla_respuestas:
                    fila["valor"] = fila["x_medio"]   # lo que se le pide al jugador en cada paso
                return True
            return False

        if metodo_seleccionado in METODOS_INTERPOLACION:
            return self._inicializar_interpolacion(problema, metodo_seleccionado)

        return False

    # ------------------------------------------------------------------
    # INTERPOLACIÓN: se convierte el resultado del motor en una lista de pasos a responder
    # ------------------------------------------------------------------
    def _inicializar_interpolacion(self, problema, metodo):
        xi = problema["datos_base"]["xi"]
        yi = problema["datos_base"]["yi"]
        x = problema["valores_iniciales"]["x"]

        if metodo == "INTERPOLACION_LINEAL":
            res = calcular_tabla_interpolacion_lineal(xi[0], xi[1], yi[0], yi[1], x)
        elif metodo == "LAGRANGE":
            res = calcular_tabla_lagrange(xi, yi, x)
        elif metodo == "NEWTON_DIVIDIDAS":
            res = calcular_tabla_newton_dif_divididas(xi, yi, x)
        elif metodo == "NEWTON_ADELANTE":
            res = calcular_tabla_newton_adelante(xi, yi, x)
        else:
            res = calcular_tabla_newton_atras(xi, yi, x)

        if res["estado"] != "exito":
            return False

        constructores = {
            "INTERPOLACION_LINEAL": self._pasos_lineal,
            "LAGRANGE": self._pasos_lagrange,
            "NEWTON_DIVIDIDAS": self._pasos_dif_divididas,
            "NEWTON_ADELANTE": self._pasos_newton,
            "NEWTON_ATRAS": self._pasos_newton,
        }
        pasos = constructores[metodo](res, xi, yi)
        for n, paso in enumerate(pasos, start=1):
            paso["iteracion"] = n
            paso.setdefault("formula", "")

        self.tabla_respuestas = pasos
        self.resultado_final = res["resultado"]
        return True

    @staticmethod
    def _pasos_lineal(res, xi, yi):
        cortos = ["b - a", "f(b) - f(a)", "pendiente", "x - a", "g(x)"]
        return [{"corto": cortos[i], "etiqueta": f["descripcion"], "formula": f["formula"], "valor": f["valor"]}
                for i, f in enumerate(res["iteraciones"])]

    @staticmethod
    def _pasos_lagrange(res, xi, yi):
        pasos = []
        for f in res["iteraciones"]:
            i = f["iteracion"]
            pasos.append({
                "corto": f"y{i}·L{i}(x)",
                "etiqueta": f"Término {i}:  y{i} · L{i}(x)    (x{i} = {f['xi']},  y{i} = {f['yi']})",
                "formula": f"L{i}(x) = producto de (x - xj)/(x{i} - xj) para j distinto de {i}",
                "valor": f["termino"],
            })
        pasos.append({"corto": "g(x)", "etiqueta": "Valor interpolado g(x)",
                      "formula": "g(x) = suma de los términos anteriores", "valor": res["resultado"]})
        return pasos

    @staticmethod
    def _pasos_dif_divididas(res, xi, yi):
        pasos = []
        tabla = res["tabla_diferencias"]
        for k in range(1, len(tabla)):
            for j, valor in enumerate(tabla[k]):
                if k == 1:
                    formula = f"(y{j + 2} - y{j + 1}) / (x{j + 2} - x{j + 1})"
                else:
                    formula = f"(D{k - 1}_{j + 2} - D{k - 1}_{j + 1}) / (x{j + k + 1} - x{j + 1})"
                pasos.append({"corto": f"D{k}_{j + 1}",
                              "etiqueta": f"Diferencia dividida de orden {k}, fila {j + 1}",
                              "formula": formula, "valor": valor})
        pasos.append({"corto": "g(x)", "etiqueta": "Valor interpolado g(x)",
                      "formula": "g(x) = D0 + D1(x - x1) + D2(x - x1)(x - x2) + ...", "valor": res["resultado"]})
        return pasos

    def _pasos_newton(self, res, xi, yi):
        adelante = (self.metodo == "NEWTON_ADELANTE")
        simbolo = "Δ" if adelante else "∇"
        pasos = [{"corto": "h", "etiqueta": "Tamaño de intervalo h", "formula": "h = |x2 - x1|", "valor": res["h"]}]

        tabla = res["tabla_diferencias"]
        for k in range(1, len(tabla)):
            for j, valor in enumerate(tabla[k]):
                if k == 1:
                    formula = f"y{j + 2} - y{j + 1}"
                else:
                    formula = f"{simbolo}{k - 1}_{j + 2} - {simbolo}{k - 1}_{j + 1}"
                pasos.append({"corto": f"{simbolo}{k}_{j + 1}",
                              "etiqueta": f"Diferencia de orden {k}, fila {j + 1}",
                              "formula": formula, "valor": valor})

        if adelante:
            pasos.append({"corto": "s", "etiqueta": "Factor binomial s (coordenada local)",
                          "formula": "s = (x - x1) / h", "valor": res["s"]})
        else:
            pasos.append({"corto": "s", "etiqueta": "Factor binomial s (coordenada local, negativa)",
                          "formula": "s = (x - xn) / h", "valor": res["s"]})
        pasos.append({"corto": "g(x)", "etiqueta": "Valor interpolado g(x)",
                      "formula": ("g(x) = y1 + Δ1·s + Δ2·s(s-1)/2! + ..." if adelante
                                  else "g(x) = yn + ∇1·s + ∇2·s(s+1)/2! + ..."),
                      "valor": res["resultado"]})
        return pasos

    # ------------------------------------------------------------------
    def verificar_respuesta(self, input_valor, margen=None):
        """Verifica si la respuesta del usuario es correcta para el paso actual."""
        if self.iteracion_actual >= len(self.tabla_respuestas):
            return False, "Completado"

        if margen is None:
            margen = MARGEN_INTERPOLACION if self.es_interpolacion() else MARGEN_BISECTRIZ

        valor_correcto = self.tabla_respuestas[self.iteracion_actual]["valor"]

        if abs(input_valor - valor_correcto) <= margen:
            self.iteracion_actual += 1
            return True, valor_correcto
        return False, None

    def obtener_datos_paso_actual(self):
        if self.iteracion_actual >= len(self.tabla_respuestas):
            return None
        return self.tabla_respuestas[self.iteracion_actual]