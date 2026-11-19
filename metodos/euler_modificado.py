# metodos/euler_modificado.py
import math


def _evaluar_funcion(funcion, y, t):
    """Evalúa y' = f(y, t) aceptando tanto una expresión str del JSON como una función Python."""
    if callable(funcion):
        return float(funcion(y, t))

    entorno_seguro = {
        "__builtins__": None,
        "math": math,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "sqrt": math.sqrt,
        "abs": abs,
        "y": float(y),
        "t": float(t),
    }
    return float(eval(funcion, entorno_seguro, {}))


def calcular_tabla_euler_modificado(funcion, y0, y1, t0=0.0, h=0.2, pasos=2, valor_real=None):
    """
    Calcula el paso a paso del Método de Euler Modificado según el apunte de clase.

    Fórmula (apunte):  y'_1 = y_0 + (h / 2) * [ f(y_0, t_0) + f(y_1, t_1) ]
                       t_1  = t_0 + h
    Actualización entre iteraciones:
                       t_0 <- t_1,  t_1 <- t_0 + h,  y_0 <- y_1,  y_1 <- y'_1

    Args:
        funcion (str | callable): Ecuación diferencial despejada y' = f(y, t) (ej. "(5*y*t - 1) / 3").
        y0 (float): Primer valor inicial conocido en t0.
        y1 (float): Segundo valor inicial conocido en t1.
        t0 (float, opcional): Tiempo inicial. Por defecto 0.0.
        h (float, opcional): Tamaño de paso. Por defecto 0.2.
        pasos (int, opcional): Cantidad de iteraciones a calcular (ej. 2 para y'1 y y'2).
        valor_real (float, opcional): Solución analítica exacta en el último t para calcular error Є.

    Returns:
        dict con la misma estructura que lagrange.py:
            {"estado": "exito" | "error_datos: ..." | "error_calculo: ...",
             "iteraciones": [ {iteracion, t0, t1, y0, y1, f_y0_t0, f_y1_t1, y_prima}, ... ],
             "resultado": y'_n (última aproximación),
             "error": Є o None}
    """

    # 1. Validación inicial
    try:
        y0 = float(y0)
        y1 = float(y1)
        t0 = float(t0)
        h = float(h)
        pasos = int(pasos)
        if valor_real is not None:
            valor_real = float(valor_real)
    except (TypeError, ValueError) as e:
        return {"estado": f"error_datos: {e}", "iteraciones": [], "resultado": None, "error": None}

    if not funcion or (isinstance(funcion, str) and not funcion.strip()):
        return {"estado": "error_datos: la función f(y, t) está vacía", "iteraciones": [], "resultado": None, "error": None}
    if h <= 0:
        return {"estado": "error_datos: el tamaño de paso h debe ser mayor que cero", "iteraciones": [], "resultado": None, "error": None}
    if pasos < 1:
        return {"estado": "error_datos: se requiere al menos 1 paso", "iteraciones": [], "resultado": None, "error": None}

    # 2. Cálculo iterativo (regla trapezoidal con corrimiento de variables)
    iteraciones = []
    t_actual_0 = t0
    y_actual_0 = y0
    y_actual_1 = y1
    y_prima = y1

    try:
        for i in range(1, pasos + 1):
            t_actual_1 = t_actual_0 + h

            f_0 = _evaluar_funcion(funcion, y_actual_0, t_actual_0)
            f_1 = _evaluar_funcion(funcion, y_actual_1, t_actual_1)

            y_prima = y_actual_0 + (h / 2.0) * (f_0 + f_1)

            # 3. Guardar los datos de esta iteración (mismo redondeo a 6 decimales que lagrange.py)
            iteraciones.append({
                "iteracion": i,
                "t0": round(t_actual_0, 6),
                "t1": round(t_actual_1, 6),
                "y0": round(y_actual_0, 6),
                "y1": round(y_actual_1, 6),
                "f_y0_t0": round(f_0, 6),
                "f_y1_t1": round(f_1, 6),
                "y_prima": round(y_prima, 6),
            })

            # Corrimiento de valores para la siguiente iteración (y'2, y'3, ...)
            t_actual_0 = t_actual_1
            y_actual_0 = y_actual_1
            y_actual_1 = y_prima

    except Exception as e:
        return {"estado": f"error_calculo: {e}", "iteraciones": iteraciones, "resultado": None, "error": None}

    error = abs(valor_real - y_prima) if valor_real is not None else None

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "resultado": round(y_prima, 6),
        "error": round(error, 6) if error is not None else None,
    }

from logica.gestor_metodos import registrar_metodo, parametros


@registrar_metodo("EULER_MODIFICADO")
def pasos_euler_modificado(problema):
    p = parametros(problema)
    func = problema["funcion_python"]
    y0 = float(p["y0"])
    t0 = float(p.get("t0", 0.0))
    h = float(p.get("h", 0.2))
    num_pasos = int(p.get("pasos", 1))

    pasos = []
    y1 = p.get("y1")
    if y1 is None:
        # Predictor de Euler simple cuando el JSON solo da y0
        y1 = round(y0 + h * _evaluar_funcion(func, y0, t0), 6)
        pasos.append({
            "corto": "y1* (predictor)",
            "etiqueta": f"Predictor Euler en t1 = {round(t0 + h, 6)}",
            "formula": "y1* = y0 + h · f(y0, t0)",
            "valor": y1,
        })

    res = calcular_tabla_euler_modificado(func, y0, y1, t0=t0, h=h, pasos=num_pasos)
    if res["estado"] != "exito":
        return []

    for f in res["iteraciones"]:
        i = f["iteracion"]
        pasos.append({
            "corto": f"y'_{i}",
            "etiqueta": f"Paso {i} (t = {f['t1']}): aproximación corregida",
            "formula": "y'_i = y0 + (h/2)·[f(y0, t0) + f(y1, t1)]",
            "valor": f["y_prima"],
        })
    return pasos