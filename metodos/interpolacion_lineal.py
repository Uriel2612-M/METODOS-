# metodos/interpolacion_lineal.py
import math


def calcular_tabla_interpolacion_lineal(a, b, f_a, f_b, x, valor_real=None):
    """
    Calcula el paso a paso de la Interpolación Lineal entre dos puntos.

    Fórmula (apunte):  g(x) = [ (f(b) - f(a)) / (b - a) ] * (x - a) + f(a)
    Error (opcional):  Є = | f(x) - g(x) | = | valor real - valor calculado |

    Args:
        a (float): Extremo inferior conocido.
        b (float): Extremo superior conocido.
        f_a (float): Valor de la función en a, f(a).
        f_b (float): Valor de la función en b, f(b).
        x (float): Punto donde se quiere estimar el valor.
        valor_real (float, opcional): f(x) exacto. Si se da, se calcula el margen de error Є.

    Returns:
        dict con la misma forma que bisectriz.py:
            {"estado": "exito" | "error_intervalo" | "error_datos: ...",
             "iteraciones": [ {paso, descripcion, formula, valor}, ... ],
             "resultado": g(x),
             "error": Є o None}
        Aquí cada "iteración" es un paso del procedimiento, ya que el método no es iterativo.
    """

    # 1. Validación inicial
    try:
        a, b, f_a, f_b, x = float(a), float(b), float(f_a), float(f_b), float(x)
        if valor_real is not None:
            valor_real = float(valor_real)
    except (TypeError, ValueError) as e:
        return {"estado": f"error_datos: {e}", "iteraciones": [], "resultado": None, "error": None}

    # a = b haría dividir entre cero; x fuera de [a, b] sería extrapolación, no interpolación
    if a == b or not (min(a, b) <= x <= max(a, b)):
        return {"estado": "error_intervalo", "iteraciones": [], "resultado": None, "error": None}

    # 2. Pasos del procedimiento
    diferencia_x = b - a                      # b - a
    diferencia_y = f_b - f_a                  # f(b) - f(a)
    pendiente = diferencia_y / diferencia_x   # (f(b) - f(a)) / (b - a)
    avance = x - a                            # x - a
    g_x = pendiente * avance + f_a            # g(x)

    pasos = [
        ("Diferencia en x", "b - a", diferencia_x),
        ("Diferencia en y", "f(b) - f(a)", diferencia_y),
        ("Pendiente", "(f(b) - f(a)) / (b - a)", pendiente),
        ("Avance desde a", "x - a", avance),
        ("Valor interpolado g(x)", "pendiente * (x - a) + f(a)", g_x),
    ]

    error = None
    if valor_real is not None:
        error = abs(valor_real - g_x)
        pasos.append(("Margen de error Є", "|f(x) - g(x)|", error))

    # 3. Guardar los datos de cada paso (mismo estilo de redondeo que bisectriz.py)
    iteraciones = [
        {"paso": i, "descripcion": desc, "formula": formula, "valor": round(valor, 6)}
        for i, (desc, formula, valor) in enumerate(pasos, start=1)
    ]

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "resultado": round(g_x, 6),
        "error": round(error, 6) if error is not None else None,
    }


# =====================================================================
# PRUEBA INDEPENDIENTE
# =====================================================================
if __name__ == "__main__":
    # Ejemplo del apunte: estimar Ln 3 con intervalos [2, 5] y luego [2, 4]
    casos = [("a) Ln 2 y Ln 5", 2, 5), ("b) Ln 2 y Ln 4", 2, 4)]

    print("--- INICIANDO PRUEBA DE INTERPOLACIÓN LINEAL (Ln 3) ---")
    for nombre, a, b in casos:
        resultado = calcular_tabla_interpolacion_lineal(
            a=a, b=b, f_a=math.log(a), f_b=math.log(b), x=3, valor_real=math.log(3)
        )
        print(f"\nCaso {nombre}")
        if resultado["estado"] == "exito":
            print(f"{'Paso':<5} | {'Descripción':<26} | {'Fórmula':<28} | {'Valor'}")
            print("-" * 80)
            for fila in resultado["iteraciones"]:
                print(f"{fila['paso']:<5} | {fila['descripcion']:<26} | {fila['formula']:<28} | {fila['valor']}")
            print(f"g(3) = {resultado['resultado']}   Є = {resultado['error']}")
        else:
            print(f"Falla detectada: {resultado['estado']}")