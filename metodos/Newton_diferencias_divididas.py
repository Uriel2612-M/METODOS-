# metodos/newton_diferencias_divididas.py


def calcular_tabla_newton_dif_divididas(xi, yi, x, valor_real=None):
    """
    Calcula el paso a paso de Newton con Diferencias Divididas (intervalos no uniformes).

    Fórmula (apunte):
        g(x) = D0 + D1(x - x1) + D2(x - x1)(x - x2) + D3(x - x1)(x - x2)(x - x3) + ...
    Diferencias divididas:
        D_k^j = ( D_(k-1)^(j+1) - D_(k-1)^j ) / ( x_(j+k) - x_j )
        (numerador: resta de dos diferencias de orden k-1;
         denominador: resta de los dos valores x no comunes)

    Args:
        xi (list[float]): Abscisas de los puntos conocidos (distintas entre sí, en el orden dado).
        yi (list[float]): Ordenadas de los puntos conocidos (mismo tamaño que xi).
        x (float): Punto donde se quiere estimar el valor.
        valor_real (float, opcional): f(x) exacto. Si se da, se calcula el margen de error Є.

    Returns:
        dict con la misma forma que bisectriz.py:
            {"estado": "exito" | "error_intervalo" | "error_datos: ...",
             "iteraciones": [ {iteracion, coeficiente, producto, termino, acumulado}, ... ],
             "tabla_diferencias": [ [y_i], [D1_j], [D2_j], ... ]   (columna k = orden k),
             "resultado": g(x),
             "error": Є o None}
        Cada "iteración" es un término de la fórmula de Newton (D_k multiplicado por su producto);
        el método no es iterativo. "tabla_diferencias" sirve para dibujar la tabla del apunte.
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
    if len(set(xi)) != len(xi):
        # Dos x iguales harían dividir entre cero en el denominador
        return _falla("error_datos: hay valores de xi repetidos")

    # x fuera del rango de los datos sería extrapolación, no interpolación
    if not (min(xi) <= x <= max(xi)):
        return _falla("error_intervalo")

    n = len(xi)

    # 2. Tabla de diferencias divididas: columna 0 = y, columna k = diferencias de orden k
    tabla = [yi[:]]
    for k in range(1, n):
        previa = tabla[k - 1]
        columna = [(previa[j + 1] - previa[j]) / (xi[j + k] - xi[j]) for j in range(n - k)]
        tabla.append(columna)

    # 3. Construcción de g(x) término por término
    iteraciones = []
    g_x = 0.0
    producto = 1.0

    for k in range(n):
        coeficiente = tabla[k][0]        # D_k (primera fila de cada columna)
        if k > 0:
            producto *= (x - xi[k - 1])  # (x - x1)(x - x2)...(x - xk)
        termino = coeficiente * producto
        g_x += termino

        # 4. Guardar los datos de esta iteración (mismo estilo de redondeo que bisectriz.py)
        iteraciones.append({
            "iteracion": k + 1,
            "coeficiente": round(coeficiente, 6),
            "producto": round(producto, 6),
            "termino": round(termino, 6),
            "acumulado": round(g_x, 6),
        })

    error = abs(valor_real - g_x) if valor_real is not None else None

    return {
        "estado": "exito",
        "iteraciones": iteraciones,
        "tabla_diferencias": [[round(v, 6) for v in col] for col in tabla],
        "resultado": round(g_x, 6),
        "error": round(error, 6) if error is not None else None,
    }


def _falla(estado):
    return {"estado": estado, "iteraciones": [], "tabla_diferencias": [], "resultado": None, "error": None}


# =====================================================================
# PRUEBA INDEPENDIENTE
# =====================================================================
if __name__ == "__main__":
    # Ejemplo del apunte: encontrar g(x) para x = 7 (intervalos no uniformes)
    xi = [7.3, 6.5, 6.1]
    yi = [-0.28, -1.35, -1.96]
    x = 7

    print("--- INICIANDO PRUEBA DE NEWTON CON DIFERENCIAS DIVIDIDAS ---")
    resultado = calcular_tabla_newton_dif_divididas(xi, yi, x)

    if resultado["estado"] == "exito":
        print("Tabla de diferencias divididas:")
        for k, columna in enumerate(resultado["tabla_diferencias"]):
            etiqueta = "y (D0)" if k == 0 else f"D{k}"
            print(f"  {etiqueta:<7}: {columna}")

        print(f"\nTérminos de g({x}):")
        print(f"{'k':<3} | {'Coeficiente':<12} | {'Producto':<10} | {'Término':<10} | {'Acumulado'}")
        print("-" * 60)
        for fila in resultado["iteraciones"]:
            print(f"{fila['iteracion']:<3} | {fila['coeficiente']:<12} | {fila['producto']:<10} | {fila['termino']:<10} | {fila['acumulado']}")
        print(f"\ng({x}) = {resultado['resultado']}")
    else:
        print(f"Falla detectada: {resultado['estado']}")