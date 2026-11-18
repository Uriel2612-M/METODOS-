"""
MÍNIMOS CUADRADOS  (Nivel 3 - Ordinario)
========================================
Motores basados en los PDF del proyecto:
  - TMínimosCuadrados.pdf         : idea general (curva que minimiza la dispersión)
  - LíneaRecta.pdf                : n·a0 + Σx·a1 = Σy ; Σx·a0 + Σx²·a1 = Σxy, resuelto por eliminación
  - CuadráticaCúbica.pdf          : ecuaciones normales cuadrática y cúbica
  - LinealCuadráticaFunción.pdf   : ecuaciones normales con función f(x)

Nombres de método (deben coincidir con "metodos_viables" del JSON):
  MINIMOS_CUADRADOS_LINEAL              -> Línea Recta            g(x) = a0 + a1·x
  MINIMOS_CUADRADOS_CUADRATICA          -> Cuadrática             g(x) = a0 + a1·x + a2·x²
  MINIMOS_CUADRADOS_CUBICA              -> Cúbica                 g(x) = a0 + a1·x + a2·x² + a3·x³
  MINIMOS_CUADRADOS_LINEAL_FUNCION      -> Lineal con Función     g(x) = a0 + a1·x + a2·f(x)
  MINIMOS_CUADRADOS_CUADRATICA_FUNCION  -> Cuadrática con Función g(x) = a0 + a1·x + a2·x² + a3·f(x)

Procedimiento (igual al PDF):
  1) Sumatorias: n, Σx, Σx², ..., Σy, Σxy, ...  (la matriz es simétrica: cada suma se calcula una vez)
  2) Eliminación: se multiplica una ecuación por un factor y se suma a la siguiente
  3) Sustitución hacia atrás: se obtienen los coeficientes empezando por el último
  4) Resultado final: g(x) en el punto x a predecir, o el coeficiente indicado en
     "resultado_final" del problema (obligatorio; por ejemplo "a1" o "g(x)").

Margen de error: no se fija aquí. Se usa el margen por defecto del motor (0.0002),
porque los PDF no indican otro.
"""
import math

from logica.gestor_metodos import registrar_metodo, parametros

# Cada término de la base se describe como (exponente de x, exponente de f(x))
TERMINOS = {
    "1": (0, 0),
    "x": (1, 0),
    "x2": (2, 0),
    "x3": (3, 0),
    "f": (0, 1),
}

# Base de cada modelo, en el orden de los coeficientes a0, a1, a2, ...
MODELOS = {
    "MINIMOS_CUADRADOS_LINEAL": ["1", "x"],
    "MINIMOS_CUADRADOS_CUADRATICA": ["1", "x", "x2"],
    "MINIMOS_CUADRADOS_CUBICA": ["1", "x", "x2", "x3"],
    "MINIMOS_CUADRADOS_LINEAL_FUNCION": ["1", "x", "f"],
    "MINIMOS_CUADRADOS_CUADRATICA_FUNCION": ["1", "x", "x2", "f"],
}

_SUPERINDICES = {2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶"}


def _sup(k):
    return _SUPERINDICES.get(k, f"^{k}")


def _etiqueta(p, q):
    """Parte literal de una sumatoria: '' para n, 'x', 'x²', 'f(x)', 'xf(x)', 'f(x)²'..."""
    texto = ""
    if p:
        texto += "x" + ("" if p == 1 else _sup(p))
    if q:
        texto += "f(x)" + ("" if q == 1 else _sup(q))
    return texto


def _nombre_sumatoria(p, q, con_y=False):
    """Nombre como en los PDF: n, Σx, Σx², Σy, Σxy, Σf(x), Σf(x)y ..."""
    literal = _etiqueta(p, q)
    if con_y:
        return "Σ" + literal + "y"
    if not literal:
        return "n"
    return "Σ" + literal


def _expresion_sumatoria(p, q, con_y=False):
    partes = []
    if p:
        partes.append("xi" + ("" if p == 1 else _sup(p)))
    if q:
        partes.append("f(xi)" + ("" if q == 1 else _sup(q)))
    if con_y:
        partes.append("yi")
    return "·".join(partes) if partes else "1"


def _evaluar_f(problema, x):
    return eval(problema["funcion_python"], {"math": math}, {"x": x})


def _sumar(xs, ys, fs, p, q, con_y=False):
    total = 0.0
    for x, y, fx in zip(xs, ys, fs):
        termino = (x ** p) * (fx ** q)
        if con_y:
            termino *= y
        total += termino
    return total


def _paso_sumatoria(p, q, valor, con_y=False):
    nombre = _nombre_sumatoria(p, q, con_y)
    return {
        "corto": nombre,
        "etiqueta": f"Sumatoria {nombre}",
        "formula": f"{nombre} = Σ {_expresion_sumatoria(p, q, con_y)}",
        "valor": round(valor, 6),
    }


def _texto_termino(nombre_termino):
    return {"1": "", "x": "x", "x2": "x²", "x3": "x³", "f": "f(x)"}[nombre_termino]


def _ajustar(problema, nombre_modelo):
    datos = parametros(problema)
    xs = [float(v) for v in datos["xi"]]
    ys = [float(v) for v in datos["yi"]]
    if len(xs) != len(ys):
        raise ValueError("xi y yi tienen distinto tamaño")

    nombres_base = MODELOS[nombre_modelo]
    terminos = [TERMINOS[t] for t in nombres_base]
    m = len(terminos)
    if len(xs) < m:
        raise ValueError("No hay suficientes puntos para este modelo")

    usa_f = any(q for _, q in terminos)
    fs = [float(_evaluar_f(problema, x)) for x in xs] if usa_f else [1.0] * len(xs)

    pasos = []

    # ---------------- 1) Sumatorias y ecuaciones normales ----------------
    M = [[0.0] * m for _ in range(m)]
    b = [0.0] * m
    ya_registradas = set()
    for i in range(m):
        for j in range(i, m):
            p = terminos[i][0] + terminos[j][0]
            q = terminos[i][1] + terminos[j][1]
            valor = _sumar(xs, ys, fs, p, q)
            M[i][j] = M[j][i] = valor
            if (p, q) not in ya_registradas:
                ya_registradas.add((p, q))
                pasos.append(_paso_sumatoria(p, q, valor))
        p, q = terminos[i]
        b[i] = _sumar(xs, ys, fs, p, q, con_y=True)
        pasos.append(_paso_sumatoria(p, q, b[i], con_y=True))

    # ---------------- 2) Eliminación (como en LíneaRecta.pdf) ----------------
    A = [fila[:] for fila in M]
    c = b[:]
    for k in range(m - 1):
        if abs(A[k][k]) < 1e-12:
            raise ValueError("Pivote nulo: el sistema no tiene solución única")
        for i in range(k + 1, m):
            factor = -A[i][k] / A[k][k]
            pasos.append({
                "corto": f"factor E{i + 1}",
                "etiqueta": f"Factor para eliminar a{k} de la ecuación {i + 1}",
                "formula": f"factor = -({A[i][k]:.6g}) / ({A[k][k]:.6g})",
                "valor": round(factor, 6),
            })
            for j in range(k, m):
                A[i][j] += factor * A[k][j]
            c[i] += factor * c[k]
            pasos.append({
                "corto": f"E{i + 1}: a{k + 1}",
                "etiqueta": f"Coeficiente de a{k + 1} en la ecuación {i + 1}",
                "formula": f"E{i + 1}' = E{i + 1} + factor · E{k + 1}",
                "valor": round(A[i][k + 1], 6),
            })
            pasos.append({
                "corto": f"E{i + 1}: término",
                "etiqueta": f"Término independiente de la ecuación {i + 1}",
                "formula": f"E{i + 1}' = E{i + 1} + factor · E{k + 1}",
                "valor": round(c[i], 6),
            })

    # ---------------- 3) Sustitución hacia atrás ----------------
    resultado = problema.get("resultado_final")
    if resultado is None:
        # Sin "resultado_final" el motor no sabe qué pedir al jugador; el problema se descarta.
        raise ValueError("El problema no define resultado_final")
    if resultado == "g(x)":
        r = 0
    elif resultado.startswith("a") and resultado[1:].isdigit():
        r = int(resultado[1:])
    else:
        raise ValueError(f"resultado_final no válido: {resultado}")
    if r >= m:
        raise ValueError(f"resultado_final {resultado} fuera de rango para este modelo")

    coef = [None] * m
    for k in range(m - 1, r - 1, -1):
        if abs(A[k][k]) < 1e-12:
            raise ValueError("Pivote nulo en sustitución hacia atrás")
        suma = sum(A[k][j] * coef[j] for j in range(k + 1, m))
        coef[k] = (c[k] - suma) / A[k][k]
        pasos.append({
            "corto": f"a{k}",
            "etiqueta": f"Coeficiente a{k}",
            "formula": f"a{k} = (término{k + 1} - Σ A·a) / {A[k][k]:.6g}",
            "valor": round(coef[k], 6),
        })

    # ---------------- 4) Resultado final: g(x) en el punto pedido ----------------
    if resultado == "g(x)":
        x_pred = datos.get("x_interpolar")
        if x_pred is None:
            raise ValueError("Falta el punto x a predecir")
        x_pred = float(x_pred)
        f_pred = float(_evaluar_f(problema, x_pred)) if usa_f else 1.0
        g = sum(coef[i] * (x_pred ** terminos[i][0]) * (f_pred ** terminos[i][1]) for i in range(m))

        partes = []
        for i, nombre_termino in enumerate(nombres_base):
            texto = _texto_termino(nombre_termino)
            partes.append(f"a{i}" + ("" if not texto else "·" + texto))
        pasos.append({
            "corto": "g(x)",
            "etiqueta": f"Valor ajustado g({x_pred})",
            "formula": "g(x) = " + " + ".join(partes),
            "valor": round(g, 6),
        })

    return pasos


@registrar_metodo("MINIMOS_CUADRADOS_LINEAL")
def pasos_minimos_cuadrados_lineal(problema):
    return _ajustar(problema, "MINIMOS_CUADRADOS_LINEAL")


@registrar_metodo("MINIMOS_CUADRADOS_CUADRATICA")
def pasos_minimos_cuadrados_cuadratica(problema):
    return _ajustar(problema, "MINIMOS_CUADRADOS_CUADRATICA")


@registrar_metodo("MINIMOS_CUADRADOS_CUBICA")
def pasos_minimos_cuadrados_cubica(problema):
    return _ajustar(problema, "MINIMOS_CUADRADOS_CUBICA")


@registrar_metodo("MINIMOS_CUADRADOS_LINEAL_FUNCION")
def pasos_minimos_cuadrados_lineal_funcion(problema):
    return _ajustar(problema, "MINIMOS_CUADRADOS_LINEAL_FUNCION")


@registrar_metodo("MINIMOS_CUADRADOS_CUADRATICA_FUNCION")
def pasos_minimos_cuadrados_cuadratica_funcion(problema):
    return _ajustar(problema, "MINIMOS_CUADRADOS_CUADRATICA_FUNCION")
