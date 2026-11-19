# metodos/runge_kutta_4.py
import math
from logica.gestor_metodos import registrar_metodo, parametros


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
        "x": float(t),
    }
    return float(eval(funcion, entorno_seguro, {}))


def calcular_tabla_runge_kutta_4(funcion, y0, t0=0.0, h=0.2, pasos=2, valor_real=None):
    """
    Método de Runge-Kutta de 4° orden clásico (Regla 1/3 de Simpson).

    Fórmulas:
        k1      = h * f(y_n, t_n)
        k2      = h * f(y_n + k1 / 2, t_n + h / 2)
        k3      = h * f(y_n + k2 / 2, t_n + h / 2)
        k4      = h * f(y_n + k3, t_n + h)
        y_(n+1) = y_n + (1 / 6) * (k1 + 2*k2 + 2*k3 + k4)
    """
    try:
        y0 = float(y0)
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

    iteraciones = []
    t_actual = t0
    y_actual = y0
    y_siguiente = y0

    try:
        for i in range(1, pasos + 1):
            t_siguiente = t_actual + h

            k1 = h * _evaluar_funcion(funcion, y_actual, t_actual)
            k2 = h * _evaluar_funcion(funcion, y_actual + k1 / 2.0, t_actual + h / 2.0)
            k3 = h * _evaluar_funcion(funcion, y_actual + k2 / 2.0, t_actual + h / 2.0)
            k4 = h * _evaluar_funcion(funcion, y_actual + k3, t_actual + h)
            y_siguiente = y_actual + (1.0 / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

            iteraciones.append({
                "iteracion": i,
                "t": round(t_actual, 6),
                "y": round(y_actual, 6),
                "k1": round(k1, 6),
                "k2": round(k2, 6),
                "k3": round(k3, 6),
                "k4": round(k4, 6),
                "t_siguiente": round(t_siguiente, 6),
                "y_siguiente": round(y_siguiente, 6),
            })

            t_actual = t_siguiente
            y_actual = y_siguiente

    except Exception as e:
        return {"estado": f"error_calculo: {e}", "iteraciones": iteraciones, "resultado": None, "error": None}

    error = abs(valor_real - y_siguiente) if valor_real is not None else None

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "resultado": round(y_siguiente, 6),
        "error": round(error, 6) if error is not None else None,
    }


@registrar_metodo("RUNGE_KUTTA_4")
def pasos_runge_kutta_4(problema):
    p = parametros(problema)
    res = calcular_tabla_runge_kutta_4(
        problema["funcion_python"],
        p["y0"],
        t0=p.get("t0", 0.0),
        h=p.get("h", 0.2),
        pasos=int(p.get("pasos", 1)),
    )
    if res["estado"] != "exito":
        return []

    pasos = []
    for f in res["iteraciones"]:
        i = f["iteracion"]
        pasos.extend([
            {"corto": f"k1 (p{i})", "etiqueta": f"Paso {i}: pendiente k1",
             "formula": "k1 = h · f(y_n, t_n)", "valor": f["k1"]},
            {"corto": f"k2 (p{i})", "etiqueta": f"Paso {i}: pendiente k2",
             "formula": "k2 = h · f(y_n + k1/2, t_n + h/2)", "valor": f["k2"]},
            {"corto": f"k3 (p{i})", "etiqueta": f"Paso {i}: pendiente k3",
             "formula": "k3 = h · f(y_n + k2/2, t_n + h/2)", "valor": f["k3"]},
            {"corto": f"k4 (p{i})", "etiqueta": f"Paso {i}: pendiente k4",
             "formula": "k4 = h · f(y_n + k3, t_n + h)", "valor": f["k4"]},
            {"corto": f"y{i}", "etiqueta": f"Paso {i}: valor en t = {f['t_siguiente']}",
             "formula": "y_(n+1) = y_n + (1/6)·(k1 + 2·k2 + 2·k3 + k4)", "valor": f["y_siguiente"]},
        ])
    return pasos