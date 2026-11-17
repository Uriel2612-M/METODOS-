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

        lista = ctk.CTkScrollableFrame(self, fg_color="transparent", height=380)
        lista.pack(pady=10, padx=50, fill="x")

        # 1. Usamos la nueva función para obtener el catálogo
        for problema in GestorProblemas.obtener_todos_instanciados():
            ctk.CTkButton(lista, text=f"[ {problema['id']}: {problema['titulo']} ]", font=("Consolas", 20), fg_color="transparent",
                          border_width=1, text_color="white", border_color="gray", hover_color="#003300",
                          command=lambda i=problema["id"]: self.mostrar_analisis_problema(i)).pack(pady=6, fill="x")

        ctk.CTkButton(self, text="[ REGRESAR AL MENU ]", font=("Consolas", 20), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=lambda: self.controlador.mostrar_vista("menu")).pack(side="bottom", pady=30)
    # --- NUEVA PANTALLA INTERMEDIA ---
    def mostrar_analisis_problema(self, id_problema):
        # 2. Generamos el problema aleatorio UNA SOLA VEZ aquí
        problema_instanciado = GestorProblemas.obtener_problema_instanciado(id_problema)
        if not problema_instanciado: return

        self.limpiar_frame()
        ctk.CTkLabel(self, text=f"> EXPEDIENTE: {problema_instanciado['titulo']}", font=("Consolas", 20, "bold"), text_color="#00FF00").pack(pady=(30, 10))
        
        frame_datos = ctk.CTkFrame(self, fg_color="#111111", border_width=1, border_color="#00FF00")
        frame_datos.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(frame_datos, text=problema_instanciado["contexto"], font=("Consolas", 16), text_color="white", justify="left").pack(pady=20, padx=20)

        ctk.CTkLabel(self, text="ANALISIS: PROTOCOLOS DE RECUPERACION VIABLES DETECTADOS", font=("Consolas", 14, "bold"), text_color="yellow").pack(pady=(20, 10))

        for metodo in problema_instanciado.get("metodos_viables", []):
            # 3. Le pasamos todo el "problema_instanciado" (con sus números ya fijos) a la siguiente pantalla
            ctk.CTkButton(self, text=f"[ EJECUTAR PROTOCOLO: {metodo} ]", font=("Consolas", 16), fg_color="transparent", 
                          border_width=1, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", width=350,
                          command=lambda p=problema_instanciado, m=metodo: self.iniciar_diagnostico(p, m)).pack(pady=5)

        ctk.CTkButton(self, text="[ VOLVER AL DIRECTORIO ]", font=("Consolas", 16), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=self.mostrar_directorio).pack(side="bottom", pady=30)

    def mostrar_protocolo_no_disponible(self, metodo):
        self.limpiar_frame()
        ctk.CTkLabel(self, text="> PROTOCOLO NO DISPONIBLE", font=("Consolas", 24, "bold"), text_color="red").pack(pady=(80, 20))
        ctk.CTkLabel(self, text=f"El protocolo {metodo} aún no está habilitado en el Modo Práctica\n(o los datos del problema no son válidos para ese método).",
                     font=("Consolas", 16), text_color="white", justify="center").pack(pady=20)
        ctk.CTkButton(self, text="[ VOLVER AL DIRECTORIO ]", font=("Consolas", 18), fg_color="transparent", border_width=1,
                      text_color="yellow", border_color="yellow", hover_color="#333300", command=self.mostrar_directorio).pack(pady=30)

    # --- INICIO DEL JUEGO ---
    def iniciar_diagnostico(self, problema_instanciado, metodo_seleccionado):
        # 4. Ya no buscamos el problema en el Gestor, usamos el que nos pasaron por parámetro
        if not self.gestor.inicializar_sesion(problema_instanciado, metodo_seleccionado):
            self.mostrar_protocolo_no_disponible(metodo_seleccionado)
            return

        self.fallas_consecutivas = 0
        interpolacion = self.gestor.es_interpolacion()

        self.limpiar_frame()
        ctk.CTkLabel(self, text=f"> DIAGNOSTICO EN CURSO: {metodo_seleccionado}", font=("Consolas", 20, "bold"), text_color="#00FF00").pack(pady=(15, 5))
        # En interpolación el contexto incluye la tabla de datos, así que se usa letra más pequeña
        ctk.CTkLabel(self, text=problema_instanciado["contexto"], font=("Consolas", 13 if interpolacion else 16),
                     text_color="white", justify="left" if interpolacion else "center").pack(pady=(0, 8))

        # Se empaquetan primero para que siempre queden visibles abajo
        frame_botones_inferiores = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones_inferiores.pack(side="bottom", pady=(5, 12))

        ctk.CTkButton(frame_botones_inferiores, text="[ CONSULTAR MANUAL ]", font=("Consolas", 14), fg_color="transparent", 
                      border_width=1, text_color="yellow", border_color="yellow", hover_color="#333300", 
                      command=lambda: self.controlador.mostrar_vista("manual")).pack(side="left", padx=10)

        ctk.CTkButton(frame_botones_inferiores, text="[ ABORTAR DIAGNÓSTICO ]", font=("Consolas", 14), fg_color="transparent", 
                      text_color="gray", hover_color="#333333", command=self.mostrar_directorio).pack(side="left", padx=10)

        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="#050505", border_width=1, border_color="gray", height=100 if interpolacion else 130)
        self.frame_tabla.pack(pady=8, padx=50, fill="x")

        if interpolacion:
            cabecera = f"{'Paso':<5}| {'Valor':<12}| {'Concepto':<14}"
        else:
            cabecera = f"{'It':<4} | {'a':<10} | {'b':<10} | {'x_medio':<10} | {'f(x)':<10} | {'Error':<10}"
        ctk.CTkLabel(self.frame_tabla, text=cabecera, font=("Consolas", 14, "bold"), text_color="cyan", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(self.frame_tabla, text="-"*75, font=("Consolas", 14), text_color="gray", anchor="w").pack(fill="x", padx=10)

        self.frame_juego = ctk.CTkFrame(self, fg_color="#111111", border_width=1, border_color="#00FF00")
        self.frame_juego.pack(pady=10, padx=50, fill="x")

        self.label_instruccion = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 16), text_color="yellow", wraplength=650)
        self.label_instruccion.pack(pady=10)

        # Entrada y botón en la misma fila para ahorrar espacio vertical
        self.frame_entrada = ctk.CTkFrame(self.frame_juego, fg_color="transparent")
        self.frame_entrada.pack(pady=(5, 0))

        self.entrada_jugador = ctk.CTkEntry(self.frame_entrada, font=("Consolas", 18), width=150, justify="center")
        self.entrada_jugador.pack(side="left", padx=8)
        self.entrada_jugador.bind("<Return>", lambda evento: self.procesar_respuesta())

        self.btn_enviar = ctk.CTkButton(self.frame_entrada, text="[ ENVIAR DATOS ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                                        border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", 
                                        command=self.procesar_respuesta)
        self.btn_enviar.pack(side="left", padx=8)

        self.label_feedback = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 14), wraplength=650)
        self.label_feedback.pack(pady=(5, 12))
        
        self.actualizar_paso()
        
    def actualizar_paso(self):
        datos_paso = self.gestor.obtener_datos_paso_actual()
        if not datos_paso:
            if self.gestor.es_interpolacion():
                self.label_instruccion.configure(text=f"¡MÓDULO ESTABILIZADO! Diagnóstico completado.\nValor interpolado: g(x) = {self.gestor.resultado_final}")
            else:
                self.label_instruccion.configure(text="¡MÓDULO ESTABILIZADO! Diagnóstico completado.")
            # 1. Ocultamos la fila de entrada (caja de texto + botón Enviar)
            self.frame_entrada.pack_forget()
            
            # 2. La graficadora (recompensa) por ahora solo aplica a bisección
            if not self.gestor.es_interpolacion():
                ctk.CTkButton(self.frame_juego, text="[ VER TELEMETRÍA GRÁFICA ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                              border_width=2, text_color="cyan", border_color="cyan", hover_color="#003333", 
                              command=self.mostrar_grafica).pack(pady=(10, 5))

            # 3. Mostramos el botón para salir
            ctk.CTkButton(self.frame_juego, text="[ REGRESAR AL DIRECTORIO ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                          border_width=2, text_color="yellow", border_color="yellow", hover_color="#333300", 
                          command=self.mostrar_directorio).pack(pady=(5, 20))
            return

        if self.gestor.es_interpolacion():
            total = len(self.gestor.tabla_respuestas)
            texto = f"PASO {datos_paso['iteracion']} de {total}: {datos_paso['etiqueta']}"
            if datos_paso["formula"]:
                texto += f"\n[ {datos_paso['formula']} ]"
            texto += "\nIngrese el valor:"
        else:
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
            self.label_feedback.configure(text=f"¡Correcto! {'valor' if self.gestor.es_interpolacion() else 'x'} = {valor_real}", text_color="#00FF00")
            
            if self.gestor.es_interpolacion():
                fila = f"{datos_resueltos['iteracion']:<5}| {datos_resueltos['valor']:<12}| {datos_resueltos['corto']}"
            else:
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