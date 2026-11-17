# metodos/lagrange.py


def calcular_tabla_lagrange(xi, yi, x, valor_real=None):
    """
    Calcula el paso a paso de la Interpolación de Lagrange.

    Fórmula (apunte):  g(x) = SUMA_i  y_i * L_i(x)
                       L_i(x) = PRODUCTO_(j != i) (x - x_j) / (x_i - x_j)
    Se aplica a intervalos uniformes y no uniformes.

    Args:
        xi (list[float]): Abscisas de los puntos conocidos (deben ser distintas entre sí).
        yi (list[float]): Ordenadas de los puntos conocidos (mismo tamaño que xi).
        x (float): Punto donde se quiere estimar el valor.
        valor_real (float, opcional): f(x) exacto. Si se da, se calcula el margen de error Є.

    Returns:
        dict con la misma forma que bisectriz.py:
            {"estado": "exito" | "error_intervalo" | "error_datos: ...",
             "iteraciones": [ {iteracion, xi, yi, numerador, denominador, L_i, termino}, ... ],
             "resultado": g(x),
             "error": Є o None}
        Cada "iteración" es el término i de la suma (y_i * L_i(x)); el método no es iterativo.
    """

    # 1. Validación inicial
    try:
        xi = [float(v) for v in xi]
        yi = [float(v) for v in yi]
        x = float(x)
        if valor_real is not None:
            valor_real = float(valor_real)
    except (TypeError, ValueError) as e:
        return {"estado": f"error_datos: {e}", "iteraciones": [], "resultado": None, "error": None}

    if len(xi) != len(yi):
        return {"estado": "error_datos: xi y yi tienen distinto tamaño", "iteraciones": [], "resultado": None, "error": None}
    if len(xi) < 2:
        return {"estado": "error_datos: se requieren al menos 2 puntos", "iteraciones": [], "resultado": None, "error": None}
    if len(set(xi)) != len(xi):
        # Dos x iguales harían dividir entre cero en (x_i - x_j)
        return {"estado": "error_datos: hay valores de xi repetidos", "iteraciones": [], "resultado": None, "error": None}

    # x fuera del rango de los datos sería extrapolación, no interpolación
    if not (min(xi) <= x <= max(xi)):
        return {"estado": "error_intervalo", "iteraciones": [], "resultado": None, "error": None}

    # 2. Cálculo de cada término de la sumatoria
    iteraciones = []
    g_x = 0.0

    for i in range(len(xi)):
        numerador = 1.0
        denominador = 1.0
        for j in range(len(xi)):
            if j != i:
                numerador *= (x - xi[j])
                denominador *= (xi[i] - xi[j])

        L_i = numerador / denominador
        termino = yi[i] * L_i
        g_x += termino

        # 3. Guardar los datos de esta iteración (mismo estilo de redondeo que bisectriz.py)
        iteraciones.append({
            "iteracion": i + 1,
            "xi": round(xi[i], 6),
            "yi": round(yi[i], 6),
            "numerador": round(numerador, 6),
            "denominador": round(denominador, 6),
            "L_i": round(L_i, 6),
            "termino": round(termino, 6),
        })

    error = abs(valor_real - g_x) if valor_real is not None else None

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
    # Ejemplo del apunte: obtener g(x) para x = 2.4 con 5 puntos
    xi = [2.2, 2.5, 2.8, 3.1, 3.4]
    yi = [2.54, 2.82, 3.21, 3.32, 3.41]
    x = 2.4

    print("--- INICIANDO PRUEBA DEL MÉTODO DE LAGRANGE ---")
    resultado = calcular_tabla_lagrange(xi, yi, x)

    if resultado["estado"] == "exito":
        print(f"¡Cálculo exitoso! Tabla de términos para x = {x}:")
        print(f"{'i':<3} | {'xi':<6} | {'yi':<6} | {'Numerador':<11} | {'Denominador':<12} | {'L_i(x)':<10} | {'yi*L_i'}")
        print("-" * 80)
        for fila in resultado["iteraciones"]:
            print(f"{fila['iteracion']:<3} | {fila['xi']:<6} | {fila['yi']:<6} | {fila['numerador']:<11} | {fila['denominador']:<12} | {fila['L_i']:<10} | {fila['termino']}")
        print(f"\ng({x}) = {resultado['resultado']}")
    else:
        print(f"Falla detectada: {resultado['estado']}")