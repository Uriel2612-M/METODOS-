# metodos/runge_kutta_orden_superior.py
import math
from logica.gestor_metodos import registrar_metodo, parametros


def _evaluar_funcion_2do_orden(funcion, y, z, t):
    """Evalúa y'' = f(y, y', t), aceptando z, yp, u o v para representar y'."""
    if callable(funcion):
        return float(funcion(y, z, t))

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
        "z": float(z),
        "yp": float(z),
        "u": float(z),
        "v": float(z),
        "t": float(t),
        "x": float(t),
    }
    return float(eval(funcion, entorno_seguro, {}))


def calcular_tabla_runge_kutta_orden_superior(funcion, y0, z0, t0=0.0, h=0.2, pasos=1, valor_real=None):
    """
    Runge-Kutta de 4° orden para EDO de 2° orden: y'' = f(y, y', t).
    Sustitución: y' = z  ->  z' = f(y, z, t).

    Fórmulas por paso:
        k1 = h * z_n                                  | m1 = h * f(y_n, z_n, t_n)
        k2 = h * (z_n + m1/2)                         | m2 = h * f(y_n + k1/2, z_n + m1/2, t_n + h/2)
        k3 = h * (z_n + m2/2)                         | m3 = h * f(y_n + k2/2, z_n + m2/2, t_n + h/2)
        k4 = h * (z_n + m3)                           | m4 = h * f(y_n + k3, z_n + m3, t_n + h)
        y_(n+1) = y_n + (1/6)*(k1 + 2*k2 + 2*k3 + k4)
        z_(n+1) = z_n + (1/6)*(m1 + 2*m2 + 2*m3 + m4)
    """
    try:
        y0 = float(y0)
        z0 = float(z0)
        t0 = float(t0)
        h = float(h)
        pasos = int(pasos)
        if valor_real is not None:
            valor_real = float(valor_real)
    except (TypeError, ValueError) as e:
        return {"estado": f"error_datos: {e}", "iteraciones": [], "resultado": None, "error": None}

    if not funcion or (isinstance(funcion, str) and not funcion.strip()):
        return {"estado": "error_datos: la función f(y, y', t) está vacía", "iteraciones": [], "resultado": None, "error": None}
    if h <= 0:
        return {"estado": "error_datos: el tamaño de paso h debe ser mayor que cero", "iteraciones": [], "resultado": None, "error": None}
    if pasos < 1:
        return {"estado": "error_datos: se requiere al menos 1 paso", "iteraciones": [], "resultado": None, "error": None}

    iteraciones = []
    t_actual = t0
    y_actual = y0
    z_actual = z0
    y_siguiente = y0
    z_siguiente = z0

    try:
        for i in range(1, pasos + 1):
            t_siguiente = t_actual + h

            k1 = h * z_actual
            m1 = h * _evaluar_funcion_2do_orden(funcion, y_actual, z_actual, t_actual)

            k2 = h * (z_actual + m1 / 2.0)
            m2 = h * _evaluar_funcion_2do_orden(funcion, y_actual + k1 / 2.0, z_actual + m1 / 2.0, t_actual + h / 2.0)

            k3 = h * (z_actual + m2 / 2.0)
            m3 = h * _evaluar_funcion_2do_orden(funcion, y_actual + k2 / 2.0, z_actual + m2 / 2.0, t_actual + h / 2.0)

            k4 = h * (z_actual + m3)
            m4 = h * _evaluar_funcion_2do_orden(funcion, y_actual + k3, z_actual + m3, t_actual + h)

            y_siguiente = y_actual + (1.0 / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            z_siguiente = z_actual + (1.0 / 6.0) * (m1 + 2.0 * m2 + 2.0 * m3 + m4)

            iteraciones.append({
                "iteracion": i,
                "t": round(t_actual, 6),
                "y": round(y_actual, 6),
                "z": round(z_actual, 6),
                "k1": round(k1, 6), "m1": round(m1, 6),
                "k2": round(k2, 6), "m2": round(m2, 6),
                "k3": round(k3, 6), "m3": round(m3, 6),
                "k4": round(k4, 6), "m4": round(m4, 6),
                "t_siguiente": round(t_siguiente, 6),
                "y_siguiente": round(y_siguiente, 6),
                "z_siguiente": round(z_siguiente, 6),
            })

            t_actual = t_siguiente
            y_actual = y_siguiente
            z_actual = z_siguiente

    except Exception as e:
        return {"estado": f"error_calculo: {e}", "iteraciones": iteraciones, "resultado": None, "error": None}

    error = abs(valor_real - y_siguiente) if valor_real is not None else None

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "resultado": round(y_siguiente, 6),
        "resultado_derivada": round(z_siguiente, 6),
        "error": round(error, 6) if error is not None else None,
    }


@registrar_metodo("RUNGE_KUTTA_ORDEN_SUPERIOR")
def pasos_runge_kutta_orden_superior(problema):
    p = parametros(problema)
    z0 = p.get("z0", p.get("yp0", p.get("y_prima_0", 0.0)))
    res = calcular_tabla_runge_kutta_orden_superior(
        problema["funcion_python"],
        p["y0"],
        z0,
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
            {"corto": f"k1 (p{i})", "etiqueta": f"Paso {i}: k1 para y",
             "formula": "k1 = h · z_n", "valor": f["k1"]},
            {"corto": f"m1 (p{i})", "etiqueta": f"Paso {i}: m1 para y' (z)",
             "formula": "m1 = h · f(y_n, z_n, t_n)", "valor": f["m1"]},
            {"corto": f"k2 (p{i})", "etiqueta": f"Paso {i}: k2 para y",
             "formula": "k2 = h · (z_n + m1/2)", "valor": f["k2"]},
            {"corto": f"m2 (p{i})", "etiqueta": f"Paso {i}: m2 para y' (z)",
             "formula": "m2 = h · f(y_n + k1/2, z_n + m1/2, t_n + h/2)", "valor": f["m2"]},
            {"corto": f"k3 (p{i})", "etiqueta": f"Paso {i}: k3 para y",
             "formula": "k3 = h · (z_n + m2/2)", "valor": f["k3"]},
            {"corto": f"m3 (p{i})", "etiqueta": f"Paso {i}: m3 para y' (z)",
             "formula": "m3 = h · f(y_n + k2/2, z_n + m2/2, t_n + h/2)", "valor": f["m3"]},
            {"corto": f"k4 (p{i})", "etiqueta": f"Paso {i}: k4 para y",
             "formula": "k4 = h · (z_n + m3)", "valor": f["k4"]},
            {"corto": f"m4 (p{i})", "etiqueta": f"Paso {i}: m4 para y' (z)",
             "formula": "m4 = h · f(y_n + k3, z_n + m3, t_n + h)", "valor": f["m4"]},
            {"corto": f"z{i} (y'{i})", "etiqueta": f"Paso {i}: derivada y' en t = {f['t_siguiente']}",
             "formula": "z_(n+1) = z_n + (1/6)·(m1 + 2·m2 + 2·m3 + m4)", "valor": f["z_siguiente"]},
            {"corto": f"y{i}", "etiqueta": f"Paso {i}: valor y en t = {f['t_siguiente']}",
             "formula": "y_(n+1) = y_n + (1/6)·(k1 + 2·k2 + 2·k3 + k4)", "valor": f["y_siguiente"]},
        ])
    return pasos