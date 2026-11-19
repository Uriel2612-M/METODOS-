"""
FÓRMULAS CERRADAS DE NEWTON-COTES  (método: NEWTON_COTES_CERRADAS)
Fuentes: TNewtonCotesAyC.pdf, RNewtonC-Cerradas.pdf y ConstantesN-CotesAC.pdf
         (OneDrive_1_18-11-2026.zip)

    h = (b - a) / n
    I = h · C_n · Σ w_i · f(x_i)        con x_i = a + i·h,  i = 0 .. n

Cada C_n = num/den y los pesos w_i salen de la tabla de constantes.

NOTA sobre la tabla del PDF: al comprobar que cada fila integra exactamente
polinomios de grado <= n (verificación hecha al revisar los PDF), se encontraron
dos errores de transcripción en el PDF, que aquí están corregidos:
  - n = 8: C_n = 4/14175 (el PDF dice 14/14175) y los pesos i=3 e i=5 son 10496 (el PDF dice 10946)
  - n = 9: el peso i=4 e i=5 es 5778 (el PDF dice 5788)
"""
import math

from logica.gestor_metodos import registrar_metodo, parametros

# n: (numerador de C_n, denominador de C_n, pesos w_0 ... w_n)
TABLA_CERRADAS = {
    1: (1, 2, [1, 1]),
    2: (1, 3, [1, 4, 1]),
    3: (3, 8, [1, 3, 3, 1]),
    4: (2, 45, [7, 32, 12, 32, 7]),
    5: (5, 288, [19, 75, 50, 50, 75, 19]),
    6: (1, 140, [41, 216, 27, 272, 27, 216, 41]),
    7: (7, 17280, [751, 3577, 1323, 2989, 2989, 1323, 3577, 751]),
    8: (4, 14175, [989, 5888, -928, 10496, -4540, 10496, -928, 5888, 989]),
    9: (9, 89600, [2857, 15741, 1080, 19344, 5778, 5778, 19344, 1080, 15741, 2857]),
    10: (5, 299376, [16067, 106300, -48525, 272400, -260550, 427368, -260550, 272400, -48525, 106300, 16067]),
}


@registrar_metodo("NEWTON_COTES_CERRADAS")
def pasos_newton_cotes_cerradas(problema):
    p = parametros(problema)
    a, b, n = float(p["a"]), float(p["b"]), int(p["n"])
    if n not in TABLA_CERRADAS:
        raise ValueError(f"n = {n} no está en la tabla de constantes cerradas (1 a 10)")
    num, den, pesos = TABLA_CERRADAS[n]
    f = lambda x: eval(problema["funcion_python"], {"math": math}, {"x": x})

    h = (b - a) / n
    suma_ponderada = sum(w * f(a + i * h) for i, w in enumerate(pesos))
    c_n = num / den
    resultado = h * c_n * suma_ponderada

    return [
        {"corto": "h", "etiqueta": "Tamaño de paso h",
         "formula": "h = (b - a) / n", "valor": round(h, 6)},
        {"corto": "C_n", "etiqueta": f"Constante C{n} de la tabla cerrada",
         "formula": f"C{n} = {num}/{den}", "valor": round(c_n, 6)},
        {"corto": "suma ponderada", "etiqueta": "Suma de w_i · f(x_i)",
         "formula": "Σ w_i · f(x_i)", "valor": round(suma_ponderada, 6)},
        {"corto": "I", "etiqueta": "Integral aproximada",
         "formula": "I = h · C_n · Σ w_i · f(x_i)", "valor": round(resultado, 6)},
    ]
