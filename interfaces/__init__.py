def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.gestor = GestorPractica()
        self.fallas_consecutivas = 0 # <-- NUEVO CONTADOR
        self.mostrar_instrucciones()