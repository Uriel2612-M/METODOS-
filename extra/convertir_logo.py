import os
from PIL import Image

carpeta = os.path.dirname(os.path.abspath(__file__))
entrada = os.path.join(carpeta, "logoMN.png")
salida = os.path.join(carpeta, "icono.ico")

Image.open(entrada).save(
    salida,
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
)
print("Listo:", salida)