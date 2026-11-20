import customtkinter as ctk
from interfaces.menu import VistaMenu
from interfaces.practica import VistaPractica
from interfaces.manual import VistaManual
from interfaces.desafio import VistaDesafio
from utilidades.fondo import COLOR_FONDO

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

import os
import sys

def ruta_icono():
    # Dentro del .exe, PyInstaller descomprime los archivos en sys._MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "icono.ico")
    # Ejecutando con python main.py: el icono está en la carpeta extra
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra", "icono.ico")

class ZeroLimitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZERO LIMIT - Terminal de Diagnóstico")
        self.configure(fg_color=COLOR_FONDO)
        self.geometry("850x650")
        self.after(200, lambda: self.iconbitmap(ruta_icono()))
        self.contenedor_principal = ctk.CTkFrame(self, fg_color=COLOR_FONDO, corner_radius=0)
        self.contenedor_principal.pack(expand=True, fill="both")

        # Variables para el historial de navegación
        self.vista_actual = None
        self.historial = []

        self.vistas = {}
        self.vistas["menu"] = VistaMenu(self.contenedor_principal, self)
        self.vistas["practica"] = VistaPractica(self.contenedor_principal, self)
        self.vistas["desafio"] = VistaDesafio(self.contenedor_principal, self)
        self.vistas["manual"] = VistaManual(self.contenedor_principal, self)
        
        self.mostrar_vista("menu")

    def mostrar_vista(self, nombre_vista, limpiar_historial=False):
        """Muestra una nueva vista y guarda la anterior en el historial."""
        if limpiar_historial:
            self.historial = []
        elif self.vista_actual and self.vista_actual != nombre_vista:
            self.historial.append(self.vista_actual)

        self.vista_actual = nombre_vista
        for vista in self.vistas.values():
            vista.pack_forget() 
            
        vista_objetivo = self.vistas.get(nombre_vista)
        if vista_objetivo:
            vista_objetivo.pack(expand=True, fill="both")

    def regresar_vista(self):
        """Vuelve exactamente a la pantalla anterior."""
        if self.historial:
            vista_previa = self.historial.pop()
            self.vista_actual = vista_previa
            for vista in self.vistas.values():
                vista.pack_forget()
            self.vistas[vista_previa].pack(expand=True, fill="both")
        else:
            self.mostrar_vista("menu")

if __name__ == "__main__":
    app = ZeroLimitApp()
    app.mainloop()