import customtkinter as ctk
from interfaces.menu import VistaMenu
from interfaces.practica import VistaPractica
from interfaces.manual import VistaManual

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ZeroLimitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZERO LIMIT - Terminal de Diagnóstico")
        self.geometry("850x650")

        self.contenedor_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_principal.pack(expand=True, fill="both")

        # Variables para el historial de navegación
        self.vista_actual = None
        self.historial = []

        self.vistas = {}
        self.vistas["menu"] = VistaMenu(self.contenedor_principal, self)
        self.vistas["practica"] = VistaPractica(self.contenedor_principal, self)
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