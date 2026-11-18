"""
REGISTRO DE MÉTODOS "PASO A PASO"
=================================
Aquí se conectan los métodos numéricos nuevos (Trapecio, Simpson, Mínimos Cuadrados,
Euler, Runge-Kutta, Falsa Posición, Jacobi, etc.) SIN tocar el resto del juego.

Para agregar un método basta con crear UN archivo en la carpeta /metodos/ y decorar
una función con @registrar_metodo("NOMBRE"). El juego detecta el archivo solo.
El NOMBRE debe ser el mismo que aparece en "metodos_viables" del JSON
(por ejemplo "TRAPECIO", "SIMPSON_1_3", "RUNGE_KUTTA_4").

La función recibe el problema ya instanciado (con sus números aleatorios) y devuelve
la LISTA DE PASOS que el jugador debe ir respondiendo. Cada paso es un diccionario:

    {
      "corto":    "h",                          # nombre breve de lo que se pide (obligatorio)
      "etiqueta": "Tamaño de paso h",           # descripción del paso
      "formula":  "h = (b - a) / n",            # solo se muestra en Modo Práctica
      "valor":    0.25,                         # respuesta correcta (número, obligatorio)
      "margen":   0.0002,                       # opcional: error permitido en ESTE paso
    }

El ÚLTIMO paso debe ser el resultado final del método.
Si algo sale mal (datos inválidos, división entre cero...) levanta una excepción
o devuelve una lista vacía: el juego simplemente descarta ese problema.

EJEMPLO COMPLETO  (archivo metodos/trapecio.py)
-----------------------------------------------
    import math
    from logica.gestor_metodos import registrar_metodo, parametros

    @registrar_metodo("TRAPECIO")
    def pasos_trapecio(problema):
        p = parametros(problema)                  # a, b, n ... ya combinados
        a, b, n = p["a"], p["b"], int(p["n"])
        f = lambda x: eval(problema["funcion_python"], {"math": math}, {"x": x})

        h = (b - a) / n
        suma_interior = sum(f(a + i * h) for i in range(1, n))
        resultado = (h / 2) * (f(a) + 2 * suma_interior + f(b))

        return [
            {"corto": "h", "etiqueta": "Tamaño de paso h",
             "formula": "h = (b - a) / n", "valor": round(h, 6)},
            {"corto": "suma", "etiqueta": "Suma de f(xi) interiores",
             "formula": "f(x1) + ... + f(x(n-1))", "valor": round(suma_interior, 6)},
            {"corto": "I", "etiqueta": "Integral aproximada",
             "formula": "I = (h/2)[f(a) + 2·suma + f(b)]", "valor": round(resultado, 6)},
        ]

Con eso el método ya funciona en el Modo Práctica y en la Etapa 3 del Modo Desafío.
"""
import importlib
import pkgutil

# nombre del método -> función(problema) -> lista de pasos
MOTORES_PASOS = {}


def registrar_metodo(nombre):
    """Decorador: registra la función como motor del método `nombre`."""
    def decorador(funcion):
        MOTORES_PASOS[nombre] = funcion
        return funcion
    return decorador


def metodo_registrado(nombre):
    return nombre in MOTORES_PASOS


def parametros(problema):
    """
    Junta en un solo diccionario todos los datos numéricos de un problema instanciado:
    valores_iniciales + parametros_fijos + datos_base (xi, yi, t0, h, ...).
    """
    datos = {}
    datos.update(problema.get("valores_iniciales", {}))
    datos.update(problema.get("parametros_fijos", {}))
    datos.update(problema.get("datos_base", {}))
    return datos


def cargar_metodos():
    """
    Importa todos los archivos de /metodos para que sus @registrar_metodo se ejecuten.
    Si un archivo está roto, se avisa en consola y se sigue con los demás
    (un compañero con un error no tumba todo el juego).
    """
    import metodos
    for modulo in pkgutil.iter_modules(metodos.__path__):
        try:
            importlib.import_module(f"metodos.{modulo.name}")
        except Exception as error:
            print(f"[gestor_metodos] No se pudo cargar metodos/{modulo.name}.py -> {error!r}")