"""
REGLA DE SIMPSON 1/3  (método: SIMPSON_1_3)
Fuente: R1tercioSimpson.pdf (OneDrive_1_18-11-2026.zip)

    h = (b - a) / n            (n siempre par)
    I = (h/3) · [ f(a) + 4·Σ f(x impares) + 2·Σ f(x pares interiores) + f(b) ]
"""
import math

from logica.gestor_metodos import registrar_metodo, parametros


@registrar_metodo("SIMPSON_1_3")
def pasos_simpson_1_3(problema):
    p = parametros(problema)
    a, b, n = float(p["a"]), float(p["b"]), int(p["n"])
    if n < 2 or n % 2 != 0:
        raise ValueError("Simpson 1/3 requiere un número par de intervalos")
    f = lambda x: eval(problema["funcion_python"], {"math": math}, {"x": x})

    h = (b - a) / n
    suma_impares = sum(f(a + i * h) for i in range(1, n, 2))
    suma_pares = sum(f(a + i * h) for i in range(2, n, 2))
    resultado = (h / 3) * (f(a) + 4 * suma_impares + 2 * suma_pares + f(b))

    return [
        {"corto": "h", "etiqueta": "Tamaño de paso h",
         "formula": "h = (b - a) / n", "valor": round(h, 6)},
        {"corto": "suma impares", "etiqueta": "Suma de f(xi) con i impar",
         "formula": "f(x1) + f(x3) + ... + f(x(n-1))", "valor": round(suma_impares, 6)},
        {"corto": "suma pares", "etiqueta": "Suma de f(xi) con i par interior",
         "formula": "f(x2) + f(x4) + ... + f(x(n-2))", "valor": round(suma_pares, 6)},
        {"corto": "I", "etiqueta": "Integral aproximada",
         "formula": "I = (h/3)[f(a) + 4·impares + 2·pares + f(b)]", "valor": round(resultado, 6)},
    ]
