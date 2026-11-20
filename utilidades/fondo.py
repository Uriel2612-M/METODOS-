"""
FONDO CON DISEÑO PARA LAS PANTALLAS DE ZERO LIMIT
=================================================
customtkinter no tiene transparencia real: un marco con fg_color="transparent" se pinta con el color
sólido de su contenedor. Por eso el diseño se pone DENTRO de cada pantalla: una imagen generada por código
(estilo terminal: lluvia de 0/1 y hexadecimal, pistas de circuito, fragmentos de código, regla en los bordes,
log de arranque y esquinas de "HUD") que se coloca
detrás de los demás widgets de la vista.

Uso (en el __init__ de cada vista, justo después de super().__init__):

    super().__init__(parent, fg_color=COLOR_FONDO)
    aplicar_fondo(self)

IMPORTANTE: el color de la vista debe ser COLOR_FONDO. Los widgets "transparent" que están encima toman ese
color, así que el centro de la imagen usa exactamente el mismo tono para que no se noten recuadros.

Si una vista borra todos sus hijos (for w in self.winfo_children(): w.destroy()), debe saltarse los que tengan
el atributo `es_fondo`, ver `limpiar_frame` en practica.py y desafio.py.
"""
import os
import random
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

COLOR_FONDO = "#070b08"
_RGB_FONDO = (7, 11, 8)
_VERDE = (0, 255, 0)

PASO_PUNTOS = 40            # separación de la malla de puntos
PASO_COLUMNA = 22          # separación entre columnas de "lluvia" de código
ALTO_CARACTER = 16

# Fragmentos de código que flotan tenues (relacionados con los métodos numéricos)
FRAGMENTOS = ["while (err > tol):", "x_new = x - f(x)/df(x)", "iter += 1", "return x", "f(x) == 0", "err < 1e-3",
              "h = (b - a) / n", "k1 = h * f(t, y)", "0x7FFE", "NULL", "[OK]", "jacobi(A, b)", "/* ZL */",
              "if f(a)*f(b) < 0:", "ZERO_LIMIT.exe", "0xDEADBEEF", "while True:", "sys.exit(0)", "&mut x"]

LOG_ARRANQUE = ["ZL//SYS  v1.0  [ONLINE]",
                "> nucleo numerico ........ OK",
                "> motores de metodos ..... OK"]
VOLCADO_HEX = ["0x0000  5A 45 52 4F 20 4C 49 4D  |ZERO LIM|",
               "0x0008  49 54 00 00 FF 7F 00 01  |IT......|",
               "0x0010  42 49 53 45 43 54 00 00  |BISECT..|"]

_cache = {}        # (ancho, alto) -> imagen PIL ya generada (se conservan las últimas pocas)
_fuentes = {}      # tamaño -> fuente


def _fuente(tamano):
    if tamano in _fuentes:
        return _fuentes[tamano]
    candidatas = ["C:/Windows/Fonts/consola.ttf", "consola.ttf", "DejaVuSansMono.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/System/Library/Fonts/Menlo.ttc"]
    fuente = None
    for ruta in candidatas:
        try:
            fuente = ImageFont.truetype(ruta, tamano)
            break
        except Exception:
            continue
    if fuente is None:
        try:
            fuente = ImageFont.load_default(tamano)
        except Exception:
            fuente = ImageFont.load_default()
    _fuentes[tamano] = fuente
    return fuente


def _cercania_al_borde(x, ancho):
    """0 en el centro horizontal, 1 en los bordes: el centro se deja limpio para que se lea el contenido."""
    return min(1.0, abs(x / ancho - 0.5) * 2)


def _lluvia_de_codigo(pincel, azar, ancho, alto):
    """Columnas verticales de 0/1 y hexadecimal, tipo terminal; más densas hacia los bordes."""
    fuente = _fuente(13)
    simbolos = "01" * 6 + "0123456789ABCDEF" + "ƒ∫Σ<>/{}"
    for x in range(8, ancho - 8, PASO_COLUMNA):
        borde = _cercania_al_borde(x, ancho)
        if azar.random() > 0.06 + 0.60 * borde ** 1.3:
            continue
        largo = azar.randint(6, 26)
        y0 = azar.randint(-largo * ALTO_CARACTER // 2, alto)
        for i in range(largo):
            y = y0 + i * ALTO_CARACTER
            if y < -ALTO_CARACTER or y > alto:
                continue
            avance = i / max(1, largo - 1)
            alfa = int(9 + 34 * avance ** 1.6)             # la cola se desvanece, la cabeza brilla
            color = (0, 255, 0, alfa)
            if i == largo - 1:
                color = (170, 255, 170, 80)                  # cabeza de la columna
            pincel.text((x, y), azar.choice(simbolos), font=fuente, fill=color)


def _trazas_de_circuito(pincel, azar, ancho, alto):
    """Pistas de circuito impreso (tramos rectos y diagonales a 45°) que entran desde los bordes."""
    def trazar(x, y, dx, dy, horizontal_primero, limite):
        puntos = [(x, y)]
        for _ in range(azar.randint(2, 4)):
            largo = azar.randint(30, 90)
            x, y = (x + dx * largo, y) if horizontal_primero else (x, y + dy * largo)
            puntos.append((x, y))
            largo = azar.randint(18, 55)
            giro = azar.choice([-1, 1])
            x, y = (x + dx * largo, y + giro * largo) if horizontal_primero else (x + giro * largo, y + dy * largo)
            puntos.append((x, y))
            if abs(x - puntos[0][0]) > limite and horizontal_primero:
                break
        pincel.line(puntos, fill=(0, 255, 0, 42), width=1, joint="curve")
        for (px, py) in puntos[1:-1:2]:
            pincel.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(0, 255, 0, 70))
        fx, fy = puntos[-1]
        pincel.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], outline=(0, 255, 0, 95), width=1)
        pincel.ellipse([fx - 1, fy - 1, fx + 1, fy + 1], fill=(0, 255, 0, 120))

    n_lados = max(4, alto // 90)
    for _ in range(n_lados):                                                  # desde el borde izquierdo
        trazar(0, azar.randint(40, alto - 40), 1, 1, True, ancho * 0.22)
    for _ in range(n_lados):                                                  # desde el borde derecho
        trazar(ancho, azar.randint(40, alto - 40), -1, 1, True, ancho * 0.22)
    for _ in range(max(2, ancho // 400)):                                     # desde abajo
        trazar(azar.randint(60, ancho - 60), alto, 1, -1, False, 0)


def _fragmentos_de_codigo(pincel, azar, ancho, alto):
    """Trozos de código sueltos, muy tenues, preferentemente hacia los bordes."""
    for _ in range(max(8, ancho * alto // 90000)):
        for _intento in range(12):
            x = azar.randint(20, max(21, ancho - 220))
            if azar.random() < 0.10 + 0.90 * _cercania_al_borde(x, ancho):
                y = azar.randint(20, alto - 30)
                pincel.text((x, y), azar.choice(FRAGMENTOS), font=_fuente(azar.choice([13, 15, 17])),
                            fill=(0, 255, 0, azar.randint(22, 42)))
                break


def _reglas_y_esquinas(pincel, ancho, alto):
    """Regla graduada en los bordes superior e izquierdo y esquinas tipo HUD."""
    verde = (0, 255, 0)
    fuente = _fuente(10)
    for x in range(70, ancho - 69, 10):
        largo = 9 if x % 100 == 0 else (6 if x % 50 == 0 else 3)
        pincel.line([(x, 0), (x, largo)], fill=verde + (55,), width=1)
        if x % 100 == 0:
            pincel.text((x + 3, 10), f"{x:04d}", font=fuente, fill=verde + (45,))
    for y in range(70, alto - 69, 10):
        largo = 9 if y % 100 == 0 else (6 if y % 50 == 0 else 3)
        pincel.line([(0, y), (largo, y)], fill=verde + (55,), width=1)
    m, largo, color = 10, 46, verde + (130,)
    for (x, y, sx, sy) in [(m, m, 1, 1), (ancho - m - 1, m, -1, 1), (m, alto - m - 1, 1, -1), (ancho - m - 1, alto - m - 1, -1, -1)]:
        pincel.line([(x, y), (x + sx * largo, y)], fill=color, width=2)
        pincel.line([(x, y), (x, y + sy * largo)], fill=color, width=2)


def _textos_de_esquina(pincel, ancho, alto):
    """Pequeño log de arranque (arriba a la izquierda) y volcado hexadecimal (abajo a la derecha)."""
    if ancho < 1340 or alto < 600:
        return          # en ventanas chicas taparía el contenido
    fuente = _fuente(11)
    for i, linea in enumerate(LOG_ARRANQUE):
        pincel.text((26, 16 + i * 14), linea, font=fuente, fill=(0, 255, 0, 90 if i else 140))
    for i, linea in enumerate(VOLCADO_HEX):
        pincel.text((ancho - 330, alto - 18 - (len(VOLCADO_HEX) - i) * 14), linea, font=fuente, fill=(0, 255, 0, 75))


def generar_fondo(ancho, alto):
    """Devuelve una imagen PIL (RGB) de ancho x alto con el diseño. Es determinista: siempre sale igual."""
    clave = (ancho, alto)
    if clave in _cache:
        return _cache[clave]

    # 1) Base: color plano con viñeta (solo se oscurece hacia los bordes; el centro queda igual a COLOR_FONDO)
    yy, xx = np.mgrid[0:alto, 0:ancho]
    d = np.sqrt(((xx / ancho) - 0.5) ** 2 + ((yy / alto) - 0.5) ** 2)
    viñeta = 1.0 - 0.55 * np.clip((d - 0.30) / 0.40, 0, 1)
    arr = np.empty((alto, ancho, 3), dtype=np.float32)
    arr[:] = np.array(_RGB_FONDO, dtype=np.float32)
    arr *= viñeta[..., None]

    # 2) Malla de puntos (en vez de líneas: se ve más "pantalla" y estorba menos al texto)
    for y in range(PASO_PUNTOS // 2, alto, PASO_PUNTOS):
        for x in range(PASO_PUNTOS // 2, ancho, PASO_PUNTOS):
            arr[y:y + 2, x:x + 2, :] = arr[y:y + 2, x:x + 2, :] * 0.65 + np.array(_VERDE) * 0.35 * 0.30
    imagen = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # 3) Capas de diseño (posiciones fijas gracias a la semilla)
    capa = Image.new("RGBA", imagen.size, (0, 0, 0, 0))
    pincel = ImageDraw.Draw(capa)
    azar = random.Random(2026)
    _trazas_de_circuito(pincel, azar, ancho, alto)
    _lluvia_de_codigo(pincel, azar, ancho, alto)
    _fragmentos_de_codigo(pincel, azar, ancho, alto)
    _reglas_y_esquinas(pincel, ancho, alto)
    _textos_de_esquina(pincel, ancho, alto)
    imagen = Image.alpha_composite(imagen, capa).convert("RGB")

    if len(_cache) >= 4:
        _cache.pop(next(iter(_cache)))
    _cache[clave] = imagen
    return imagen


def aplicar_fondo(vista):
    """Coloca el fondo detrás de todo lo que la vista dibuje. Llamar ANTES de crear los demás widgets."""
    etiqueta = tk.Label(vista, bd=0, highlightthickness=0, bg=COLOR_FONDO)
    etiqueta.es_fondo = True
    etiqueta.place(x=0, y=0, relwidth=1, relheight=1)
    estado = {"tam": None, "tarea": None}

    def dibujar():
        estado["tarea"] = None
        try:
            ancho, alto = etiqueta.winfo_width(), etiqueta.winfo_height()
            if ancho < 50 or alto < 50 or (ancho, alto) == estado["tam"]:
                return
            estado["tam"] = (ancho, alto)
            foto = ImageTk.PhotoImage(generar_fondo(ancho, alto))
            etiqueta.configure(image=foto)
            etiqueta.image = foto   # evita que Python libere la imagen
        except tk.TclError:
            pass  # la vista ya se destruyó

    def al_cambiar_tamano(_evento=None):
        if estado["tarea"]:
            etiqueta.after_cancel(estado["tarea"])
        # La primera vez se dibuja de inmediato; al arrastrar la ventana se espera a que se detenga
        estado["tarea"] = etiqueta.after(0 if estado["tam"] is None else 120, dibujar)

    etiqueta.bind("<Configure>", al_cambiar_tamano)
    return etiqueta