# metodos/ecuaciones_lineales.py
import math

# ============================================================
#  ZERO LIMIT — Motores matemáticos: Ecuaciones Lineales
#  Métodos: Gauss-Seidel, Jacobi
#
#  Formato de retorno idéntico a bisectriz.py:
#    {"estado": "exito" | "error_diagonal_cero: fila N"
#               | "no_converge",
#     "iteraciones": [...],
#     "diagonal_dominante": bool}
#  REGLA: No importar CustomTkinter. Solo matemáticas.
# ============================================================

def _verificar_diagonal_dominante(A):
    """
    Verifica si la matriz A es diagonal dominante.
    Condición: |a_ii| > suma de |a_ij| para j != i, en cada fila.
    """
    n = len(A)
    for i in range(n):
        if abs(A[i][i]) <= sum(abs(A[i][j]) for j in range(n) if j != i):
            return False
    return True


# ------------------------------------------------------------
# GAUSS-SEIDEL
# ------------------------------------------------------------
def calcular_tabla_gauss_seidel(A, b, x0=None, tolerancia=0.001, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de Gauss-Seidel.

    Usa los valores MÁS RECIENTES calculados en la misma iteración.
    Despeja cada variable de su propia ecuación y sustituye iterativamente.

    Args:
        A (list[list[float]]): Matriz de coeficientes n×n.
        b (list[float]): Vector de términos independientes.
        x0 (list[float]): Valores iniciales. Si es None, usa ceros.
        tolerancia (float): Criterio de paro: max|x_nuevo - x_anterior| <= tolerancia.
        max_iteraciones (int): Límite de seguridad.

    Returns:
        dict:
            {"estado": "exito" | "error_diagonal_cero: fila N" | "no_converge",
             "diagonal_dominante": bool,
             "iteraciones": [
                 {"iteracion": 0, "valores": [a0, b0, c0], "errores": ["-", "-", "-"]},
                 {"iteracion": 1, "valores": [a1, b1, c1], "errores": [ea1, eb1, ec1]},
                 ...
             ]}
    """
    n = len(A)

    for i in range(n):
        if A[i][i] == 0:
            return {
                "estado": f"error_diagonal_cero: fila {i + 1}",
                "diagonal_dominante": False,
                "iteraciones": [],
            }

    diagonal_ok = _verificar_diagonal_dominante(A)

    # Coeficientes despejados: x_i = C_i + sum(D_ij * x_j)
    C = [b[i] / A[i][i] for i in range(n)]
    D = [[(-A[i][j] / A[i][i]) if j != i else 0.0 for j in range(n)] for i in range(n)]

    x = x0[:] if x0 is not None else [0.0] * n
    iteraciones = []

    # Iteración 0: valores iniciales
    iteraciones.append({
        "iteracion": 0,
        "valores":   [round(v, 10) for v in x],
        "errores":   ["-"] * n,
    })

    for paso in range(1, max_iteraciones + 1):
        x_anterior = x[:]

        for i in range(n):
            # Gauss-Seidel: usa x ya actualizado en esta misma iteración
            x[i] = C[i] + sum(D[i][j] * x[j] for j in range(n))

        errores = [abs(x[i] - x_anterior[i]) for i in range(n)]

        iteraciones.append({
            "iteracion": paso,
            "valores":   [round(v, 10) for v in x],
            "errores":   [round(e, 10) for e in errores],
        })

        if max(errores) <= tolerancia:
            return {
                "estado": "exito",
                "diagonal_dominante": diagonal_ok,
                "iteraciones": iteraciones,
            }

    return {
        "estado": "no_converge",
        "diagonal_dominante": diagonal_ok,
        "iteraciones": iteraciones,
    }


# ------------------------------------------------------------
# JACOBI
# ------------------------------------------------------------
def calcular_tabla_jacobi(A, b, x0=None, tolerancia=0.001, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de Jacobi.

    Usa ÚNICAMENTE los valores de la iteración ANTERIOR para calcular
    todos los valores nuevos (a diferencia de Gauss-Seidel).

    Args:
        A (list[list[float]]): Matriz de coeficientes n×n.
        b (list[float]): Vector de términos independientes.
        x0 (list[float]): Valores iniciales. Si es None, usa unos.
        tolerancia (float): Criterio de paro: max|x_nuevo - x_anterior| <= tolerancia.
        max_iteraciones (int): Límite de seguridad.

    Returns:
        dict:
            {"estado": "exito" | "error_diagonal_cero: fila N" | "no_converge",
             "diagonal_dominante": bool,
             "iteraciones": [
                 {"iteracion": 0, "valores": [a0, b0, c0], "errores": ["-", "-", "-"]},
                 {"iteracion": 1, "valores": [a1, b1, c1], "errores": [ea1, eb1, ec1]},
                 ...
             ]}
    """
    n = len(A)

    for i in range(n):
        if A[i][i] == 0:
            return {
                "estado": f"error_diagonal_cero: fila {i + 1}",
                "diagonal_dominante": False,
                "iteraciones": [],
            }

    diagonal_ok = _verificar_diagonal_dominante(A)

    C = [b[i] / A[i][i] for i in range(n)]
    D = [[(-A[i][j] / A[i][i]) if j != i else 0.0 for j in range(n)] for i in range(n)]

    x = x0[:] if x0 is not None else [1.0] * n
    iteraciones = []

    # Iteración 0: valores iniciales
    iteraciones.append({
        "iteracion": 0,
        "valores":   [round(v, 10) for v in x],
        "errores":   ["-"] * n,
    })

    for paso in range(1, max_iteraciones + 1):
        x_anterior = x[:]

        # Jacobi: usa SOLO x_anterior para calcular todos los nuevos x al mismo tiempo
        x_nuevo = [
            C[i] + sum(D[i][j] * x_anterior[j] for j in range(n))
            for i in range(n)
        ]

        errores = [abs(x_nuevo[i] - x_anterior[i]) for i in range(n)]

        iteraciones.append({
            "iteracion": paso,
            "valores":   [round(v, 10) for v in x_nuevo],
            "errores":   [round(e, 10) for e in errores],
        })

        x = x_nuevo

        if max(errores) <= tolerancia:
            return {
                "estado": "exito",
                "diagonal_dominante": diagonal_ok,
                "iteraciones": iteraciones,
            }

    return {
        "estado": "no_converge",
        "diagonal_dominante": diagonal_ok,
        "iteraciones": iteraciones,
    }

from logica.gestor_metodos import registrar_metodo, parametros


def _construir_pasos_sistema(res, nombre_formula):
    if res["estado"] != "exito":
        return []
    pasos = []
    # Se salta la iteración 0 porque corresponde a los valores iniciales x0
    for fila in res["iteraciones"][1:]:
        it = fila["iteracion"]
        for j, val in enumerate(fila["valores"], start=1):
            pasos.append({
                "corto": f"x{j} (it {it})",
                "etiqueta": f"Iteración {it} — Variable x{j}",
                "formula": nombre_formula,
                "valor": round(val, 6),
            })
    return pasos


@registrar_metodo("GAUSS_SEIDEL")
def pasos_gauss_seidel(problema):
    p = parametros(problema)
    sis = problema.get("sistema", {})
    A = sis["coeficientes"]
    b = sis["terminos_independientes"]
    x0 = p.get("x0", sis.get("x0"))
    tol = problema.get("tolerancia", 0.001)
    res = calcular_tabla_gauss_seidel(A, b, x0, tol)
    return _construir_pasos_sistema(res, "Despeje usando los valores más recientes")


@registrar_metodo("JACOBI")
def pasos_jacobi(problema):
    p = parametros(problema)
    sis = problema.get("sistema", {})
    A = sis["coeficientes"]
    b = sis["terminos_independientes"]
    x0 = p.get("x0", sis.get("x0"))
    tol = problema.get("tolerancia", 0.001)
    res = calcular_tabla_jacobi(A, b, x0, tol)
    return _construir_pasos_sistema(res, "Despeje usando solo valores de la iteración anterior")

# =====================================================================
# PRUEBA INDEPENDIENTE
# =====================================================================
if __name__ == "__main__":
    A = [[3.0, -0.1, -0.2],
         [0.1,  7.0, -0.3],
         [0.3, -0.2, 10.0]]
    b = [7.85, -19.3, 71.4]

    print("--- GAUSS-SEIDEL: x0=[0,0,0] ---")
    r = calcular_tabla_gauss_seidel(A, b, [0.0, 0.0, 0.0], 0.001)
    print(f"Estado: {r['estado']} | Diagonal dominante: {r['diagonal_dominante']}")
    print(f"{'It':<4} | {'a':<14} | {'b':<14} | {'c':<14} | Errores")
    print("-" * 70)
    for f in r["iteraciones"]:
        vals = "  ".join(f"{v:<14}" for v in f["valores"])
        errs = "  ".join(str(e) for e in f["errores"])
        print(f"{f['iteracion']:<4} | {vals} | {errs}")

    print()
    print("--- JACOBI: x0=[1,1,1] ---")
    r = calcular_tabla_jacobi(A, b, [1.0, 1.0, 1.0], 0.001)
    print(f"Estado: {r['estado']} | Diagonal dominante: {r['diagonal_dominante']}")
    print(f"{'It':<4} | {'a':<14} | {'b':<14} | {'c':<14} | Errores")
    print("-" * 70)
    for f in r["iteraciones"]:
        vals = "  ".join(f"{v:<14}" for v in f["valores"])
        errs = "  ".join(str(e) for e in f["errores"])
        print(f"{f['iteracion']:<4} | {vals} | {errs}")
