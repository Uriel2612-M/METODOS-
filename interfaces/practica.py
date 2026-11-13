import customtkinter as ctk
from logica.gestor_problemas import GestorProblemas
from logica.gestor_practica import GestorPractica

class VistaPractica(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.gestor = GestorPractica()
        self.fallas_consecutivas = 0
        self.mostrar_instrucciones()

    def limpiar_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_instrucciones(self):
        self.limpiar_frame()
        ctk.CTkLabel(self, text="ADVERTENCIA LEER ANTES DE CONTINUAR - MODO PRACTICA", font=("Consolas", 30, "bold"), text_color="yellow").pack(pady=(50, 20))
        instrucciones = (
            "SISTEMA EN MODO SEGURO.\n\n"
            "> Tómese su tiempo para analizar la telemetría.\n"
            "> Herramientas externas (calculadoras/apuntes) PERMITIDAS.\n"
            "> Protocolos de estrés (Temporizador y Escudos) DESACTIVADOS.\n\n"
            "> En caso de duda, consulte el manual del ingeniero.\n\n"
            "> IMPORTANTE: Este modo no afecta su puntuación final.\n"
            "> Recuerde que el objetivo es aprender y practicar.\n\n"
            "> Si no desea continuar con el ejercicio seleccione [ ABORTAR DIAGNÓSTICO ] para regresar al menú principal.\n\n"
            "Seleccione un expediente de falla para comenzar el diagnóstico."
        )
        ctk.CTkLabel(self, text=instrucciones, font=("Consolas", 20), text_color="white", justify="center").pack(pady=20)
        ctk.CTkButton(self, text="[ ACCEDER AL SISTEMA ]", font=("Consolas", 25, "bold"), fg_color="transparent", 
                      border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", 
                      command=self.mostrar_directorio).pack(pady=20)
        ctk.CTkButton(self, text="[ CANCELAR ]", font=("Consolas", 25), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=lambda: self.controlador.mostrar_vista("menu")).pack(pady=10)

    def mostrar_directorio(self):
        self.limpiar_frame()
        ctk.CTkLabel(self, text="C:\\> DIRECTORIO DE FALLAS", font=("Consolas", 20, "bold"), text_color="#00FF00").pack(pady=(40, 30))

        # Un botón por cada problema del banco (dentro de un panel con scroll)
        lista = ctk.CTkScrollableFrame(self, fg_color="transparent", height=380)
        lista.pack(pady=10, padx=50, fill="x")

        for problema in GestorProblemas.obtener_todos():
            ctk.CTkButton(lista, text=f"[ {problema['id']}: {problema['titulo']} ]", font=("Consolas", 20), fg_color="transparent",
                          border_width=1, text_color="white", border_color="gray", hover_color="#003300",
                          command=lambda i=problema["id"]: self.mostrar_analisis_problema(i)).pack(pady=6, fill="x")

        ctk.CTkButton(self, text="[ REGRESAR AL MENU ]", font=("Consolas", 20), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=lambda: self.controlador.mostrar_vista("menu")).pack(side="bottom", pady=30)

    # --- NUEVA PANTALLA INTERMEDIA ---
    def mostrar_analisis_problema(self, id_problema):
        problema = GestorProblemas.obtener_problema(id_problema)
        if not problema: return

        self.limpiar_frame()
        ctk.CTkLabel(self, text=f"> EXPEDIENTE: {problema['titulo']}", font=("Consolas", 20, "bold"), text_color="#00FF00").pack(pady=(30, 10))
        
        frame_datos = ctk.CTkFrame(self, fg_color="#111111", border_width=1, border_color="#00FF00")
        frame_datos.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(frame_datos, text=problema["contexto"], font=("Consolas", 16), text_color="white", justify="left").pack(pady=20, padx=20)

        ctk.CTkLabel(self, text="ANALISIS: PROTOCOLOS DE RECUPERACION VIABLES DETECTADOS", font=("Consolas", 14, "bold"), text_color="yellow").pack(pady=(20, 10))

        # Genera un botón por cada método viable en el JSON
        for metodo in problema.get("metodos_viables", []):
            ctk.CTkButton(self, text=f"[ EJECUTAR PROTOCOLO: {metodo} ]", font=("Consolas", 16), fg_color="transparent", 
                          border_width=1, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", width=350,
                          command=lambda m=metodo: self.iniciar_diagnostico(id_problema, m)).pack(pady=5)

        ctk.CTkButton(self, text="[ VOLVER AL DIRECTORIO ]", font=("Consolas", 16), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=self.mostrar_directorio).pack(side="bottom", pady=30)

    # --- INICIO DEL JUEGO ---
    def iniciar_diagnostico(self, id_problema, metodo_seleccionado):
        problema = GestorProblemas.obtener_problema(id_problema)
        
        # Le pasamos el método seleccionado al gestor
        if not self.gestor.inicializar_sesion(problema, metodo_seleccionado):
            return 
        
        self.fallas_consecutivas = 0

        self.limpiar_frame()
        ctk.CTkLabel(self, text=f"> DIAGNOSTICO EN CURSO: {metodo_seleccionado}", font=("Consolas", 20, "bold"), text_color="#00FF00").pack(pady=(20, 10))
        ctk.CTkLabel(self, text=problema["contexto"], font=("Consolas", 16), text_color="white").pack(pady=(0, 15))
        
        # 3. La tabla visual
        
        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="#050505", border_width=1, border_color="gray", height=150)
        self.frame_tabla.pack(pady=10, padx=50, fill="x")

        cabecera = f"{'It':<4} | {'a':<10} | {'b':<10} | {'x_medio':<10} | {'f(x)':<10} | {'Error':<10}"
        ctk.CTkLabel(self.frame_tabla, text=cabecera, font=("Consolas", 14, "bold"), text_color="cyan", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(self.frame_tabla, text="-"*75, font=("Consolas", 14), text_color="gray", anchor="w").pack(fill="x", padx=10)

        self.frame_juego = ctk.CTkFrame(self, fg_color="#111111", border_width=1, border_color="#00FF00")
        self.frame_juego.pack(pady=10, padx=50, fill="x")

        self.label_instruccion = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 16), text_color="yellow")
        self.label_instruccion.pack(pady=15)

        self.entrada_jugador = ctk.CTkEntry(self.frame_juego, font=("Consolas", 18), width=150, justify="center")
        self.entrada_jugador.pack(pady=5)

        self.label_feedback = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 14))
        self.label_feedback.pack(pady=5)

        # Guardamos el botón en una variable (self.btn_enviar) para poder ocultarlo al ganar
        self.btn_enviar = ctk.CTkButton(self.frame_juego, text="[ ENVIAR DATOS ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                                        border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", 
                                        command=self.procesar_respuesta)
        self.btn_enviar.pack(pady=15)
        
        frame_botones_inferiores = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones_inferiores.pack(side="bottom", pady=20)

        ctk.CTkButton(frame_botones_inferiores, text="[ CONSULTAR MANUAL ]", font=("Consolas", 14), fg_color="transparent", 
                      border_width=1, text_color="yellow", border_color="yellow", hover_color="#333300", 
                      command=lambda: self.controlador.mostrar_vista("manual")).pack(side="left", padx=10)

        ctk.CTkButton(frame_botones_inferiores, text="[ ABORTAR DIAGNÓSTICO ]", font=("Consolas", 14), fg_color="transparent", 
                      text_color="gray", hover_color="#333333", command=self.mostrar_directorio).pack(side="left", padx=10)

        self.actualizar_paso()

    def actualizar_paso(self):
        datos_paso = self.gestor.obtener_datos_paso_actual()
        if not datos_paso:
            self.label_instruccion.configure(text="¡MÓDULO ESTABILIZADO! Diagnóstico completado.")
            self.entrada_jugador.configure(state="disabled")
            
            # 1. Ocultamos el botón de Enviar
            self.btn_enviar.pack_forget()
            
            # 2. Mostramos el botón de la Graficadora como recompensa
            ctk.CTkButton(self.frame_juego, text="[ VER TELEMETRÍA GRÁFICA ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                          border_width=2, text_color="cyan", border_color="cyan", hover_color="#003333", 
                          command=self.mostrar_grafica).pack(pady=(10, 5))

            # 3. Mostramos el botón para salir
            ctk.CTkButton(self.frame_juego, text="[ REGRESAR AL DIRECTORIO ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                          border_width=2, text_color="yellow", border_color="yellow", hover_color="#333300", 
                          command=self.mostrar_directorio).pack(pady=(5, 20))
            return

        texto = f"ITERACIÓN {datos_paso['iteracion']} | a = {datos_paso['a']}, b = {datos_paso['b']}\nIngrese el valor del punto medio (x):"
        self.label_instruccion.configure(text=texto)
        self.entrada_jugador.delete(0, 'end')
        self.label_feedback.configure(text="")
        
    def limpiar_error(self):
        """Borra el mensaje de error y vacía la caja de texto tras un fallo."""
        # Validamos que no borre el texto si el jugador justo acaba de acertar en ese instante
        texto_actual = self.label_feedback.cget("text")
        if "Correcto" not in texto_actual and texto_actual != "":
            self.label_feedback.configure(text="")
            self.entrada_jugador.delete(0, 'end')
        
    def procesar_respuesta(self):
        try:
            valor = float(self.entrada_jugador.get())
        except ValueError:
            self.label_feedback.configure(text="Error: Ingrese un valor numérico válido.", text_color="red")
            self.after(2000, self.limpiar_error) # <-- Limpia a los 2 segundos
            return

        datos_resueltos = self.gestor.obtener_datos_paso_actual()
        correcto, valor_real = self.gestor.verificar_respuesta(valor)
        
        if correcto:
            self.fallas_consecutivas = 0 
            self.label_feedback.configure(text=f"¡Correcto! x = {valor_real}", text_color="#00FF00")
            
            error_str = str(datos_resueltos['error']) if datos_resueltos['error'] is not None else "---"
            fila = f"{datos_resueltos['iteracion']:<4} | {datos_resueltos['a']:<10} | {datos_resueltos['b']:<10} | {datos_resueltos['x_medio']:<10} | {datos_resueltos['f_x_medio']:<10} | {error_str:<10}"
            ctk.CTkLabel(self.frame_tabla, text=fila, font=("Consolas", 14), text_color="white", anchor="w").pack(fill="x", padx=10)
            
            self.frame_tabla._parent_canvas.yview_moveto(1.0)
            self.after(1500, self.actualizar_paso)
        else:
            self.fallas_consecutivas += 1
            
            if self.fallas_consecutivas == 3:
                mensaje_advertencia = "⚠️ Has tenido 3 fallas continuas. Se recomienda\nconsultar el manual del ingeniero o escoger otro tema."
                self.label_feedback.configure(text=mensaje_advertencia, text_color="yellow")
                self.after(4000, self.limpiar_error) # <-- 4 segundos porque hay mucho que leer
            else:
                 self.label_feedback.configure(text="Datos incorrectos. Revisa tus cálculos.", text_color="red")
                 self.after(2000, self.limpiar_error) # <-- 2 segundos para el error normal
            
    def mostrar_grafica(self):
        print("Iniciando renderizado con matplotlib...")
        # Aquí irá el código de la ventana emergente CTkToplevel