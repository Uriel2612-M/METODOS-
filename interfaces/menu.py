import customtkinter as ctk

class VistaMenu(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.construir_ui()

    def ir_a_practica(self):
        # 1. Forzamos a que la vista de práctica se resetee a las instrucciones
        self.controlador.vistas["practica"].mostrar_instrucciones()
        # 2. Le decimos al controlador que muestre la pantalla
        self.controlador.mostrar_vista("practica")

    def construir_ui(self):
        ctk.CTkLabel(self, text="ZERO LIMIT", font=("Consolas", 80, "bold"), text_color="#00FF00").pack(pady=(40, 5))
        ctk.CTkLabel(self, text="PROYECTO: METODOS NUMERICOS (MODULO DE DIAGNOSTICO)", font=("Consolas", 14), text_color="#00FF00").pack(pady=(0, 30))

        # El botón ahora usa la nueva función 'ir_a_practica'
        ctk.CTkButton(self, text="[ MODO PRACTICA ]", font=("Consolas", 30, "bold"), fg_color="transparent", 
                      border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", 
                      command=self.ir_a_practica).pack(pady=10)

        ctk.CTkButton(self, text="[ MODO DESAFIO ]", font=("Consolas", 30, "bold"), fg_color="transparent", 
                      border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300").pack(pady=10)

        ctk.CTkButton(self, text="[ MANUAL DEL INGENIERO ]", font=("Consolas", 20, "bold"), fg_color="transparent", 
                      border_width=2, text_color="yellow", border_color="yellow", hover_color="#333300",
                      command=lambda: self.controlador.mostrar_vista("manual")).pack(pady=(30, 10))

        ctk.CTkLabel(self, text="NOTA: Se requieren conocimientos básicos de álgebra y cálculo para poder participar.", font=("Consolas", 15), text_color="gray").pack(side="bottom", pady=20)