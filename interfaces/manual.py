import customtkinter as ctk
from logica.gestor_manual import GestorManual

class VistaManual(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.fichas = GestorManual.obtener_todas_las_fichas()
        self.construir_ui()

    def construir_ui(self):
        # Título superior
        ctk.CTkLabel(self, text="[ BASE DE DATOS: MANUAL DEL INGENIERO ]", 
                     font=("Consolas", 25, "bold"), text_color="yellow").pack(pady=(20, 10))

        # Contenedor dividido en dos paneles (Izquierdo: Botones, Derecho: Texto)
        self.frame_contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contenido.pack(expand=True, fill="both", padx=20, pady=10)

        # Panel Izquierdo (Índice)
        self.panel_indice = ctk.CTkFrame(self.frame_contenido, width=250, fg_color="#111111", border_width=1, border_color="#00FF00")
        self.panel_indice.pack(side="left", fill="y", padx=(0, 10))
        
        ctk.CTkLabel(self.panel_indice, text="> INDICE DE PROTOCOLOS", font=("Consolas", 16, "bold"), text_color="#00FF00").pack(pady=20, padx=10)

        for ficha in self.fichas:
            ctk.CTkButton(self.panel_indice, text=f"[{ficha['nombre']}]", font=("Consolas", 14), 
                          fg_color="transparent", border_width=1, text_color="white", border_color="gray",
                          hover_color="#003300", command=lambda f=ficha: self.mostrar_ficha(f)).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(self.panel_indice, text="[ CERRAR MANUAL ]", font=("Consolas", 14, "bold"), fg_color="transparent", 
                      text_color="gray", hover_color="#333333", 
                      command=self.controlador.regresar_vista).pack(side="bottom", pady=20, padx=10),
            

        # Panel Derecho (Lector Scrolleable)
        self.panel_lector = ctk.CTkScrollableFrame(self.frame_contenido, fg_color="#050505", border_width=1, border_color="#00FF00")
        self.panel_lector.pack(side="right", expand=True, fill="both")

        self.label_pantalla_vacia = ctk.CTkLabel(self.panel_lector, text="Seleccione un protocolo en el índice para leer su ficha técnica.", 
                                                 font=("Consolas", 14), text_color="gray")
        self.label_pantalla_vacia.pack(pady=50)

    def mostrar_ficha(self, ficha):
        # Limpiar panel derecho
        for widget in self.panel_lector.winfo_children():
            widget.destroy()

        # Dibujar la información extraída del JSON
        self.agregar_seccion(ficha["nombre"], "", color_titulo="#00FF00", tam_titulo=24)
        self.agregar_seccion("1. DESCRIPCION", ficha["descripcion"])
        self.agregar_seccion("2. OBJETIVO Y APLICACIONES", ficha["objetivo"])
        self.agregar_seccion("3. FORMULA GENERAL", ficha["formula"], color_texto="cyan")
        self.agregar_seccion("4. VARIABLES", ficha["variables"])
        self.agregar_seccion("5. CONDICIONES DE APLICACION", ficha["condiciones"])
        self.agregar_seccion("6. CRITERIOS DE CONVERGENCIA / PARO", ficha["criterios_paro"])
        self.agregar_seccion("7. VENTAJAS Y LIMITACIONES", ficha["ventajas_limitaciones"])
        self.agregar_seccion("8. EJEMPLO PASO A PASO", ficha["ejemplo"], color_texto="yellow")

    def agregar_seccion(self, titulo, contenido, color_titulo="white", color_texto="white", tam_titulo=16):
        ctk.CTkLabel(self.panel_lector, text=titulo, font=("Consolas", tam_titulo, "bold"), text_color=color_titulo, anchor="w").pack(fill="x", pady=(15, 5), padx=10)
        if contenido:
            ctk.CTkLabel(self.panel_lector, text=contenido, font=("Consolas", 14), text_color=color_texto, justify="left", wraplength=450).pack(fill="x", padx=20)