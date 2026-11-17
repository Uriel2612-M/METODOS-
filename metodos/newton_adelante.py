# metodos/newton_adelante.py


def calcular_tabla_newton_adelante(xi, yi, x, valor_real=None, tol_h=1e-9):
    """
    Calcula el paso a paso de la Interpolación de Newton hacia Adelante (intervalos uniformes).

    Fórmula (apunte):
        g(x) = y1*C(s,0) + D1f(x1)*C(s,1) + D2f(x1)*C(s,2) + ...
        s = (x - x1) / h            (coordenada local, siempre positiva: izquierda a derecha)
        C(s,k) = s(s-1)(s-2)...(s-k+1) / k!
        Diferencias hacia adelante:  D^(k+1) f(x_i) = D^k f(x_(i+1)) - D^k f(x_i)
    Si los datos vienen de derecha a izquierda (x decreciente), se invierten x e y,
    tal como indica el apunte.

    Args:
        xi (list[float]): Abscisas con igual separación h.
        yi (list[float]): Ordenadas (mismo tamaño que xi).
        x (float): Punto donde se quiere estimar el valor.
        valor_real (float, opcional): f(x) exacto. Si se da, se calcula el margen de error Є.
        tol_h (float, opcional): tolerancia para decidir si la separación es uniforme.

    Returns:
        dict con la misma forma que bisectriz.py:
            {"estado": "exito" | "error_intervalo" | "error_no_uniforme" | "error_datos: ...",
             "iteraciones": [ {iteracion, delta, coef_binomial, termino, acumulado}, ... ],
             "tabla_diferencias": [ [y_i], [D1_i], [D2_i], ... ]   (columna k = orden k),
             "h": tamaño de intervalo, "s": factor binomial, "invertido": bool,
             "resultado": g(x),
             "error": Є o None}
        Cada "iteración" es un término de la fórmula (D^k f(x1) por C(s,k));
        el método no es iterativo.
    """

    # 1. Validación inicial
    try:
        xi = [float(v) for v in xi]
        yi = [float(v) for v in yi]
        x = float(x)
        if valor_real is not None:
            valor_real = float(valor_real)
    except (TypeError, ValueError) as e:
        return _falla(f"error_datos: {e}")

    if len(xi) != len(yi):
        return _falla("error_datos: xi y yi tienen distinto tamaño")
    if len(xi) < 2:
        return _falla("error_datos: se requieren al menos 2 puntos")

    # 2. Si los datos van de derecha a izquierda, se invierten x e y (el apunte pide s positivo)
    invertido = False
    if xi[1] < xi[0]:
        xi = xi[::-1]
        yi = yi[::-1]
        invertido = True

    # 3. ¿Intervalos uniformes?  h = |x(i+1) - x(i)| debe ser el mismo en toda la tabla
    pasos = [xi[i + 1] - xi[i] for i in range(len(xi) - 1)]
    h = pasos[0]
    if h <= 0:
        return _falla("error_datos: las abscisas deben ser distintas y estar ordenadas")
    if any(abs(p - h) > tol_h * max(1.0, abs(h)) for p in pasos):
        # Con intervalos no uniformes corresponde Newton con diferencias divididas o Lagrange
        return _falla("error_no_uniforme")

    # x fuera del rango de los datos sería extrapolación, no interpolación
    if not (xi[0] <= x <= xi[-1]):
        return _falla("error_intervalo")

    n = len(xi)

    # 4. Tabla de diferencias hacia adelante: columna 0 = y, columna k = diferencia de orden k
    tabla = [yi[:]]
    for k in range(1, n):
        previa = tabla[k - 1]
        tabla.append([previa[j + 1] - previa[j] for j in range(n - k)])

    # 5. Factor binomial s y construcción de g(x) término por término
    s = (x - xi[0]) / h
    iteraciones = []
    g_x = 0.0
    coef_binomial = 1.0  # C(s,0) = 1

    for k in range(n):
        if k > 0:
            coef_binomial *= (s - (k - 1)) / k  # C(s,k) = C(s,k-1) * (s - k + 1) / k
        delta = tabla[k][0]                     # D^k f(x1): primera fila de cada columna
        termino = delta * coef_binomial
        g_x += termino

        # 6. Guardar los datos de esta iteración (mismo estilo de redondeo que bisectriz.py)
        iteraciones.append({
            "iteracion": k + 1,
            "delta": round(delta, 6),
            "coef_binomial": round(coef_binomial, 6),
            "termino": round(termino, 6),
            "acumulado": round(g_x, 6),
        })

    error = abs(valor_real - g_x) if valor_real is not None else None

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "tabla_diferencias": [[round(v, 6) for v in col] for col in tabla],
        "h": round(h, 6),
        "s": round(s, 6),
        "invertido": invertido,
        "resultado": round(g_x, 6),
        "error": round(error, 6) if error is not None else None,
    }


def _falla(estado):
    return {"estado": estado, "iteraciones": [], "tabla_diferencias": [], "h": None, "s": None,
            "invertido": False, "resultado": None, "error": None}


# =====================================================================
# PRUEBA INDEPENDIENTE
# =====================================================================
if __name__ == "__main__":
    # Ejemplo del apunte: obtener g(x) para x = 3 (intervalos uniformes, h = 0.7)
    xi = [1.7, 2.4, 3.1]
    yi = [0.35, 0.87, 1.03]
    x = 3

    print("--- INICIANDO PRUEBA DE NEWTON HACIA ADELANTE ---")
    resultado = calcular_tabla_newton_adelante(xi, yi, x)

    if resultado["estado"] == "exito":
        print(f"h = {resultado['h']}   s = (x - x1)/h = {resultado['s']}")
        print("Tabla de diferencias hacia adelante:")
        for k, columna in enumerate(resultado["tabla_diferencias"]):
            etiqueta = "y (D0)" if k == 0 else f"D{k}"
            print(f"  {etiqueta:<7}: {columna}")

        print(f"\nTérminos de g({x}):")
        print(f"{'k':<3} | {'Delta':<10} | {'C(s,k)':<10} | {'Término':<10} | {'Acumulado'}")
        print("-" * 60)
        for fila in resultado["iteraciones"]:
            print(f"{fila['iteracion']:<3} | {fila['delta']:<10} | {fila['coef_binomial']:<10} | {fila['termino']:<10} | {fila['acumulado']}")
        print(f"\ng({x}) = {resultado['resultado']}")
    else:
        print(f"Falla detectada: {resultado['estado']}")