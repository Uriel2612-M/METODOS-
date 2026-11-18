"""
Verificación de los motores de Mínimos Cuadrados e Integración (ZERO LIMIT).

Ejecutar desde la raíz del proyecto:
    python documentacion/verificacion_minimos_integracion.py

No modifica ningún archivo. Comprueba:
  1. Línea Recta con los datos del PDF LíneaRecta.pdf (a1, a0 y g(1.1)).
  2. Cuadrática con los datos de N3_10 (x0 del libro: 1,26571).
  3. Integración contra los ejemplos de los PDF y del libro.
  4. Newton-Cotes exacta para polinomios de grado <= n (n = 2 a 10).
  5. Flujo de la Etapa 3: cada problema jugable se resuelve paso a paso con respuestas correctas.
"""
import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from logica.gestor_metodos import cargar_metodos, MOTORES_PASOS  # noqa: E402
from logica.gestor_desafio import GestorDesafio  # noqa: E402

cargar_metodos()
fallos = []


def comprobar(nombre, obtenido, esperado, margen=2e-4):
    ok = abs(obtenido - esperado) <= margen
    print(f"[{'OK' if ok else 'FALLO'}] {nombre}: obtenido={obtenido:.6f} esperado={esperado:.6f}")
    if not ok:
        fallos.append(nombre)


def ultimo(metodo, problema):
    return MOTORES_PASOS[metodo](problema)[-1]["valor"]


# 1) Línea Recta (LíneaRecta.pdf)
xi = [1.1, 1.9, 2.4, 4.8, 5.1, 10.5]
yi = [2.5, 2.7, 3.7, 5.2, 6.0, 8.3]
base = {"datos_base": {"xi": xi, "yi": yi}, "resultado_final": "a1"}
comprobar("Línea Recta a1", ultimo("MINIMOS_CUADRADOS_LINEAL", base), 0.633695)
comprobar("Línea Recta a0", ultimo("MINIMOS_CUADRADOS_LINEAL", {**base, "resultado_final": "a0"}), 2.008444)
comprobar("Línea Recta g(1.1)", ultimo("MINIMOS_CUADRADOS_LINEAL",
          {"datos_base": {"xi": xi, "yi": yi}, "resultado_final": "g(x)",
           "parametros_fijos": {"x_interpolar": 1.1}}), 2.705508)

# 2) Cuadrática del libro (problema 9.4): x0 = 1,26571
t = [0.0, 1.0, 2.0, 3.0, 4.0]
x = [1.1, 0.3, -6.5, -21.0, -39.0]
comprobar("Cuadrática libro 9.4 x0", ultimo("MINIMOS_CUADRADOS_CUADRATICA",
          {"datos_base": {"xi": t, "yi": x}, "resultado_final": "a0"}), 1.26571)

# 3) Integración
f_sq = "1 - x**2"
def integral(metodo, fun, a, b, n):
    return ultimo(metodo, {"funcion_python": fun, "parametros_fijos": {"a": a, "b": b, "n": n}})

comprobar("Trapecio n=4 (RTMN.pdf)", integral("TRAPECIO", f_sq, 0, 1, 4), 0.65625)
comprobar("Simpson 1/3 n=4 (R1tercioSimpson.pdf)", integral("SIMPSON_1_3", f_sq, 0, 1, 4), 2 / 3)
comprobar("Simpson 3/8 n=6", integral("SIMPSON_3_8", f_sq, 0, 1, 6), 2 / 3)
comprobar("Newton-Cotes n=4 (TNewtonCotesAyC.pdf)", integral("NEWTON_COTES_CERRADAS", f_sq, 0, 1, 4), 2 / 3)
comprobar("Simpson 1/3 libro 6.3 (23,8104)",
          integral("SIMPSON_1_3", "math.sqrt(1 + math.cos(x)**2)", 0, 20, 4), 23.8104)

# 4) Newton-Cotes exacta para x^3 con n = 2..10 (la tabla corregida debe cumplirlo)
for n in range(2, 11):
    comprobar(f"Newton-Cotes exacta x^3, n={n}", integral("NEWTON_COTES_CERRADAS", "x**3", 0, 2, n), 4.0)

# 5) Flujo de la Etapa 3 con respuestas correctas
random.seed(12345)
for _ in range(40):
    g = GestorDesafio()
    g.en_juego = True
    for _ in range(12):
        if not g.preparar_etapa_3():
            break
        pid = g.problema_actual_n3["id"]
        ok = True
        for paso in iter(lambda: g.paso_etapa_3_actual(), None):
            if not g.verificar_respuesta_etapa_3(paso["valor"])[0]:
                ok = False
                break
        if not ok:
            fallos.append(f"Etapa 3 {pid}")
            print(f"[FALLO] Etapa 3: {pid} no se resuelve con respuestas correctas")
print("[OK] Etapa 3: 40 corridas con respuestas correctas (ver mensajes de fallo si los hay)")

print()
if fallos:
    print(f"RESULTADO: {len(fallos)} comprobaciones fallaron: {fallos}")
    sys.exit(1)
print("RESULTADO: todas las comprobaciones pasaron")
