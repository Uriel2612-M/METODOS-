"""
REGLA DE SIMPSON 3/8  (método: SIMPSON_3_8)
Fuente: R3octavosSimpson.pdf (OneDrive_1_18-11-2026.zip)

    h = (b - a) / n            (n múltiplo de 3)
    I = (3h/8) · [ f(a) + 3·Σ f(xi) con i no múltiplo de 3 + 2·Σ f(xi) con i múltiplo de 3 + f(b) ]
"""
import math

from logica.gestor_metodos import registrar_metodo, parametros


@registrar_metodo("SIMPSON_3_8")
def pasos_simpson_3_8(problema):
    p = parametros(problema)
    a, b, n = float(p["a"]), float(p["b"]), int(p["n"])
    if n < 3 or n % 3 != 0:
        raise ValueError("Simpson 3/8 requiere un número de intervalos múltiplo de 3")
    f = lambda x: eval(problema["funcion_python"], {"math": math}, {"x": x})

    h = (b - a) / n
    suma_no_m3 = sum(f(a + i * h) for i in range(1, n) if i % 3 != 0)
    suma_m3 = sum(f(a + i * h) for i in range(3, n, 3))
    resultado = (3 * h / 8) * (f(a) + 3 * suma_no_m3 + 2 * suma_m3 + f(b))

    return [
        {"corto": "h", "etiqueta": "Tamaño de paso h",
         "formula": "h = (b - a) / n", "valor": round(h, 6)},
        {"corto": "suma no múltiplos de 3", "etiqueta": "Suma de f(xi) con i no múltiplo de 3",
         "formula": "f(x1) + f(x2) + f(x4) + f(x5) + ...", "valor": round(suma_no_m3, 6)},
        {"corto": "suma múltiplos de 3", "etiqueta": "Suma de f(xi) con i múltiplo de 3 interior",
         "formula": "f(x3) + f(x6) + ... ", "valor": round(suma_m3, 6)},
        {"corto": "I", "etiqueta": "Integral aproximada",
         "formula": "I = (3h/8)[f(a) + 3·no_múltiplos + 2·múltiplos + f(b)]", "valor": round(resultado, 6)},
    ]
