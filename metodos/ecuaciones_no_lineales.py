# metodos/ecuaciones_no_lineales.py
import math


# ============================================================
#  ZERO LIMIT — Motores matemáticos: Ecuaciones No Lineales
#  Métodos: Bisección, Falsa Posición, Newton-Raphson,
#           Punto Fijo, Secante
#
#  Formato de retorno idéntico a bisectriz.py:
#    {"estado": "exito" | "error_intervalo" | "error_sintaxis: ..."
#               | "error_division_cero" | "no_converge",
#     "iteraciones": [...]}
#  REGLA: No importar CustomTkinter. Solo matemáticas.
# ============================================================

def _evaluar(funcion_str, x):
    """Evalúa una función dada como string con valor x."""
    return eval(funcion_str, {"__builtins__": {}}, {"math": math, "x": x})


# ------------------------------------------------------------
# FALSA POSICIÓN (Regula-Falsi)
# ------------------------------------------------------------
def calcular_tabla_falsa_posicion(funcion_str, a, b, tolerancia=0.001, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de Falsa Posición.
    Fórmula: x = a - f(a)*(b-a) / (f(b)-f(a))

    Args:
        funcion_str (str): La función a evaluar en formato Python (ej. "3*x**3 - 2*x - 3").
        a (float): Límite inferior del intervalo inicial.
        b (float): Límite superior del intervalo inicial.
        tolerancia (float): El error máximo permitido (ej. 0.001).
        max_iteraciones (int): Límite de seguridad para evitar bucles infinitos.

    Returns:
        dict:
            {"estado": "exito" | "error_intervalo" | "error_sintaxis: ..." 
                       | "error_division_cero" | "no_converge",
             "iteraciones": [
                 {"iteracion", "a", "b", "f_a", "f_b", "x_medio", "f_x_medio", "error"}, ...
             ]}
    """
    try:
        f_a = _evaluar(funcion_str, a)
        f_b = _evaluar(funcion_str, b)
    except Exception as e:
        return {"estado": f"error_sintaxis: {e}", "iteraciones": []}

    if f_a * f_b > 0:
        return {"estado": "error_intervalo", "iteraciones": []}

    iteraciones = []
    x_anterior = None
    paso = 1

    while paso <= max_iteraciones:
        denominador = f_b - f_a
        if denominador == 0:
            return {"estado": "error_division_cero", "iteraciones": iteraciones}

        x_medio = a - f_a * (b - a) / denominador
        f_x_medio = _evaluar(funcion_str, x_medio)

        error = abs(x_medio - x_anterior) if x_anterior is not None else None

        iteraciones.append({
            "iteracion":  paso,
            "a":          round(a, 6),
            "b":          round(b, 6),
            "f_a":        round(f_a, 6),
            "f_b":        round(f_b, 6),
            "x_medio":    round(x_medio, 6),
            "f_x_medio":  round(f_x_medio, 6),
            "error":      round(error, 6) if error is not None else None,
        })

        if error is not None and error <= tolerancia:
            return {"estado": "exito", "iteraciones": iteraciones}

        if f_x_medio == 0.0:
            return {"estado": "exito", "iteraciones": iteraciones}

        if f_a * f_x_medio < 0:
            b = x_medio
            f_b = f_x_medio
        else:
            a = x_medio
            f_a = f_x_medio

        x_anterior = x_medio
        paso += 1

    return {"estado": "no_converge", "iteraciones": iteraciones}


# ------------------------------------------------------------
# NEWTON-RAPHSON
# ------------------------------------------------------------
def calcular_tabla_newton_raphson(funcion_str, derivada_str, x0, tolerancia=0.001, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de Newton-Raphson.
    Fórmula: x_i+1 = x_i - f(x_i) / f'(x_i)

    Args:
        funcion_str (str): f(x) en formato Python (ej. "x**3 + 2*x**2 + 10*x - 20").
        derivada_str (str): f'(x) en formato Python (ej. "3*x**2 + 4*x + 10").
        x0 (float): Valor inicial.
        tolerancia (float): El error máximo permitido.
        max_iteraciones (int): Límite de seguridad.

    Returns:
        dict:
            {"estado": "exito" | "error_sintaxis: ..." | "error_division_cero" | "no_converge",
             "iteraciones": [
                 {"iteracion", "x_i", "f_xi", "f_prima_xi", "x_siguiente", "error"}, ...
             ]}
    """
    try:
        _evaluar(funcion_str, x0)
        _evaluar(derivada_str, x0)
    except Exception as e:
        return {"estado": f"error_sintaxis: {e}", "iteraciones": []}

    iteraciones = []
    x = x0

    for paso in range(1, max_iteraciones + 1):
        f_x  = _evaluar(funcion_str, x)
        fp_x = _evaluar(derivada_str, x)

        if fp_x == 0:
            return {"estado": "error_division_cero", "iteraciones": iteraciones}

        x_siguiente = x - f_x / fp_x
        error = abs(x_siguiente - x)

        iteraciones.append({
            "iteracion":    paso,
            "x_i":          round(x, 10),
            "f_xi":         round(f_x, 10),
            "f_prima_xi":   round(fp_x, 10),
            "x_siguiente":  round(x_siguiente, 10),
            "error":        round(error, 10),
        })

        x = x_siguiente

        if error <= tolerancia:
            return {"estado": "exito", "iteraciones": iteraciones}

    return {"estado": "no_converge", "iteraciones": iteraciones}


# ------------------------------------------------------------
# PUNTO FIJO (Sustituciones Sucesivas)
# ------------------------------------------------------------
def calcular_tabla_punto_fijo(g_str, x0, tolerancia=0.001, max_iteraciones=100):
    """
    Calcula la tabla completa de iteraciones para el Método de Punto Fijo.
    Transforma f(x)=0 a x = g(x) y aplica la fórmula: x_i+1 = g(x_i)

    Args:
        g_str (str): g(x) en formato Python (ej. "math.exp(-x)").
        x0 (float): Valor inicial.
        tolerancia (float): El error máximo permitido.
        max_iteraciones (int): Límite de seguridad (el método puede necesitar muchas iter.).

    Returns:
        dict:
            {"estado": "exito" | "error_sintaxis: ..." | "no_converge",
             "iteraciones": [
                 {"iteracion", "x_i", "g_xi", "error"}, ...
             ]}
    """
    try:
        _evaluar(g_str, x0)
    except Exception as e:
        return {"estado": f"error_sintaxis: {e}", "iteraciones": []}

    iteraciones = []
    x = x0

    for paso in range(1, max_iteraciones + 1):
        x_siguiente = _evaluar(g_str, x)
        error = abs(x_siguiente - x)

        iteraciones.append({
            "iteracion": paso,
            "x_i":       round(x, 10),
            "g_xi":      round(x_siguiente, 10),
            "error":     round(error, 10),
        })

        x = x_siguiente

        if error <= tolerancia:
            return {"estado": "exito", "iteraciones": iteraciones}

    return {"estado": "no_converge", "iteraciones": iteraciones}


# ------------------------------------------------------------
# SECANTE
# ------------------------------------------------------------
def calcular_tabla_secante(funcion_str, x0, x1, tolerancia=0.001, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de la Secante.
    Fórmula: x_i+1 = x_i+1 - f(x_i+1)*(x_i+1 - x_i) / (f(x_i+1) - f(x_i))

    Args:
        funcion_str (str): f(x) en formato Python (ej. "math.exp(-x) - x").
        x0 (float): Primer valor inicial.
        x1 (float): Segundo valor inicial.
        tolerancia (float): El error máximo permitido.
        max_iteraciones (int): Límite de seguridad.

    Returns:
        dict:
            {"estado": "exito" | "error_sintaxis: ..." | "error_division_cero" | "no_converge",
             "iteraciones": [
                 {"iteracion", "x_i", "f_xi", "error"}, ...
             ]}
    """
    try:
        f_x0 = _evaluar(funcion_str, x0)
        f_x1 = _evaluar(funcion_str, x1)
    except Exception as e:
        return {"estado": f"error_sintaxis: {e}", "iteraciones": []}

    iteraciones = []

    # Iteraciones 0 y 1 (valores iniciales)
    iteraciones.append({
        "iteracion": 0,
        "x_i":  round(x0, 10),
        "f_xi": round(f_x0, 10),
        "error": None,
    })
    iteraciones.append({
        "iteracion": 1,
        "x_i":  round(x1, 10),
        "f_xi": round(f_x1, 10),
        "error": round(abs(x1 - x0), 10),
    })

    for paso in range(2, max_iteraciones + 1):
        denominador = f_x1 - f_x0
        if denominador == 0:
            return {"estado": "error_division_cero", "iteraciones": iteraciones}

        x2  = x1 - f_x1 * (x1 - x0) / denominador
        f_x2 = _evaluar(funcion_str, x2)
        error = abs(x2 - x1)

        iteraciones.append({
            "iteracion": paso,
            "x_i":  round(x2, 10),
            "f_xi": round(f_x2, 10),
            "error": round(error, 10),
        })

        x0, f_x0 = x1, f_x1
        x1, f_x1 = x2, f_x2

        if error <= tolerancia:
            return {"estado": "exito", "iteraciones": iteraciones}

    return {"estado": "no_converge", "iteraciones": iteraciones}


# =====================================================================
# PRUEBA INDEPENDIENTE
# =====================================================================
import re
from logica.gestor_metodos import registrar_metodo, parametros


@registrar_metodo("FALSA_POSICION")
def pasos_falsa_posicion(problema):
    p = parametros(problema)
    tol = problema.get("tolerancia", 0.001)
    res = calcular_tabla_falsa_posicion(problema["funcion_python"], p["a"], p["b"], tol)
    if res["estado"] != "exito":
        return []
    return [
        {
            "corto": f"x{f['iteracion']}",
            "etiqueta": f"It {f['iteracion']} | a = {f['a']}, b = {f['b']}",
            "formula": "x = a - f(a)·(b - a) / (f(b) - f(a))",
            "valor": f["x_medio"],
        }
        for f in res["iteraciones"]
    ]


@registrar_metodo("NEWTON_RAPHSON")
def pasos_newton_raphson(problema):
    p = parametros(problema)
    tol = problema.get("tolerancia", 0.001)
    func = problema["funcion_python"]
    derivada = problema.get("derivada_python") or problema.get("derivada")
    if not derivada:
        # Respaldo numérico si el JSON no trae la derivada explícita
        f_mas = re.sub(r"\bx\b", "(x + 1e-6)", func)
        f_menos = re.sub(r"\bx\b", "(x - 1e-6)", func)
        derivada = f"(({f_mas}) - ({f_menos})) / 2e-6"

    res = calcular_tabla_newton_raphson(func, derivada, p["x0"], tol)
    if res["estado"] != "exito":
        return []
    return [
        {
            "corto": f"x{f['iteracion']}",
            "etiqueta": f"It {f['iteracion']} | x_actual = {round(f['x_i'], 6)}",
            "formula": "x(i+1) = x_i - f(x_i) / f'(x_i)",
            "valor": round(f["x_siguiente"], 6),
        }
        for f in res["iteraciones"]
    ]


@registrar_metodo("PUNTO_FIJO")
def pasos_punto_fijo(problema):
    p = parametros(problema)
    tol = problema.get("tolerancia", 0.001)
    g_str = problema.get("g_python") or problema.get("funcion_g") or problema["funcion_python"]
    res = calcular_tabla_punto_fijo(g_str, p["x0"], tol)
    if res["estado"] != "exito":
        return []
    return [
        {
            "corto": f"x{f['iteracion']}",
            "etiqueta": f"It {f['iteracion']} | x_actual = {round(f['x_i'], 6)}",
            "formula": "x(i+1) = g(x_i)",
            "valor": round(f["g_xi"], 6),
        }
        for f in res["iteraciones"]
    ]


@registrar_metodo("SECANTE")
def pasos_secante(problema):
    p = parametros(problema)
    tol = problema.get("tolerancia", 0.001)
    res = calcular_tabla_secante(problema["funcion_python"], p["x0"], p["x1"], tol)
    if res["estado"] != "exito":
        return []
    # Las iteraciones 0 y 1 son los valores iniciales x0 y x1; se pide desde la 2 en adelante
    iters = res["iteraciones"]
    pasos = []
    for idx in range(2, len(iters)):
        prev_2 = round(iters[idx - 2]["x_i"], 6)
        prev_1 = round(iters[idx - 1]["x_i"], 6)
        actual = iters[idx]
        pasos.append({
            "corto": f"x{actual['iteracion']}",
            "etiqueta": f"It {actual['iteracion'] - 1} | x(i-1) = {prev_2}, x(i) = {prev_1}",
            "formula": "x(i+1) = x(i) - f(x(i))·(x(i)-x(i-1)) / (f(x(i))-f(x(i-1)))",
            "valor": round(actual["x_i"], 6),
        })
    return pasos

if __name__ == "__main__":
    import math

    print("--- FALSA POSICIÓN: f(x) = 3x³ - 2x - 3, [1, 2] ---")
    r = calcular_tabla_falsa_posicion("3*x**3 - 2*x - 3", 1, 2, 0.001)
    print(f"Estado: {r['estado']}")
    print(f"{'It':<4} | {'a':<10} | {'b':<10} | {'x_medio':<12} | {'f_x_medio':<12} | {'Error'}")
    print("-" * 70)
    for f in r["iteraciones"]:
        err = str(f["error"]) if f["error"] is not None else "---"
        print(f"{f['iteracion']:<4} | {f['a']:<10} | {f['b']:<10} | {f['x_medio']:<12} | {f['f_x_medio']:<12} | {err}")

    print()
    print("--- NEWTON-RAPHSON: f(x) = x³+2x²+10x-20, x0=1 ---")
    r = calcular_tabla_newton_raphson("x**3 + 2*x**2 + 10*x - 20", "3*x**2 + 4*x + 10", 1.0, 0.001)
    print(f"Estado: {r['estado']}")
    for f in r["iteraciones"]:
        print(f"  {f}")

    print()
    print("--- PUNTO FIJO: g(x) = e^-x, x0=0 ---")
    r = calcular_tabla_punto_fijo("math.exp(-x)", 0.0, 0.001)
    print(f"Estado: {r['estado']} | Iteraciones: {len(r['iteraciones'])}")
    for f in r["iteraciones"][:5]:
        print(f"  {f}")

    print()
    print("--- SECANTE: f(x) = e^-x - x, x0=0, x1=1 ---")
    r = calcular_tabla_secante("math.exp(-x) - x", 0.0, 1.0, 0.001)
    print(f"Estado: {r['estado']}")
    for f in r["iteraciones"]:
        print(f"  {f}")
