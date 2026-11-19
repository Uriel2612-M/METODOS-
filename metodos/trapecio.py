"""
REGLA DEL TRAPECIO  (método: TRAPECIO)
Fuente: RTMN.pdf (OneDrive_1_18-11-2026.zip)

    h = (b - a) / n
    I = (h/2) · [ f(a) + 2·Σ f(a + i·h)  (i = 1 .. n-1)  + f(b) ]
"""
import math

from logica.gestor_metodos import registrar_metodo, parametros


@registrar_metodo("TRAPECIO")
def pasos_trapecio(problema):
    p = parametros(problema)
    a, b, n = float(p["a"]), float(p["b"]), int(p["n"])
    if n < 1:
        raise ValueError("n debe ser mayor que cero")
    f = lambda x: eval(problema["funcion_python"], {"math": math}, {"x": x})

    h = (b - a) / n
    suma_interior = sum(f(a + i * h) for i in range(1, n))
    resultado = (h / 2) * (f(a) + 2 * suma_interior + f(b))

    return [
        {"corto": "h", "etiqueta": "Tamaño de paso h",
         "formula": "h = (b - a) / n", "valor": round(h, 6)},
        {"corto": "suma", "etiqueta": "Suma de f(xi) interiores",
         "formula": "f(x1) + ... + f(x(n-1))", "valor": round(suma_interior, 6)},
        {"corto": "I", "etiqueta": "Integral aproximada",
         "formula": "I = (h/2)[f(a) + 2·suma + f(b)]", "valor": round(resultado, 6)},
    ]
