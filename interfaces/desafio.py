import random
from logica.gestor_problemas import GestorProblemas
import customtkinter as ctk
from utilidades.fondo import COLOR_FONDO, aplicar_fondo
from logica.gestor_desafio import GestorDesafio
from interfaces.desafio_etapa3 import EtapaTresDesafio

class VistaDesafio(EtapaTresDesafio, ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color=COLOR_FONDO)
        aplicar_fondo(self)
        self.controlador = controlador
        self.gestor = GestorDesafio()
        self.id_timer = None 
        
        self.mostrar_pantalla_inicio()

    def limpiar_frame(self):
        for widget in self.winfo_children():
            if not getattr(widget, "es_fondo", False):   # el fondo con diseño no se borra
                widget.destroy()

    def detener_reloj(self):
        if self.id_timer:
            self.after_cancel(self.id_timer)
            self.id_timer = None

    def mostrar_pantalla_inicio(self):
        self.detener_reloj()
        self.limpiar_frame()
        
        ctk.CTkLabel(self, text="ADVERTENCIA - MODO DESAFÍO", font=("Consolas", 30, "bold"), text_color="red").pack(pady=(50, 20))
        instrucciones = (
            "SISTEMA EN MODO CRÍTICO.\n\n"
            "> El acceso al Manual del Ingeniero está BLOQUEADO.\n"
            "> El tiempo corre. La presión es absoluta.\n"
            "> Cuenta con 3 Escudos de Integridad (Vidas).\n"
            "> Fallas en los cálculos resultarán en pérdida de escudos.\n\n"
            "Fase 1: Reconocimiento de Patrones (Teoría).\n"
            "Fase 2: Estabilización de Módulos (Iteraciones Rápidas).\n"
            "Fase 3: Sobrecarga del Núcleo (Cálculo Complejo).\n"
        )
        ctk.CTkLabel(self, text=instrucciones, font=("Consolas", 20), text_color="white", justify="center").pack(pady=20)
        
        ctk.CTkButton(self, text="[ INICIAR PROTOCOLO DE CRISIS ]", font=("Consolas", 25, "bold"), fg_color="transparent", 
                      border_width=2, text_color="red", border_color="red", hover_color="#330000", 
                      command=self.iniciar_juego).pack(pady=20)
                      
        ctk.CTkButton(self, text="[ CANCELAR ]", font=("Consolas", 20), fg_color="transparent", text_color="gray", hover_color="#333333", 
                      command=lambda: self.controlador.mostrar_vista("menu")).pack(pady=10)

    def construir_hud(self):
        self.frame_hud = ctk.CTkFrame(self, fg_color="#111111", border_width=1, border_color="red")
        self.frame_hud.pack(fill="x", padx=20, pady=10)
        
        vidas_str = "♥ " * self.gestor.vidas
        self.label_vidas = ctk.CTkLabel(self.frame_hud, text=f"ESCUDOS: {vidas_str}", font=("Consolas", 20, "bold"), text_color="#00FF00")
        self.label_vidas.pack(side="left", padx=20, pady=10)
        
        self.label_puntuacion = ctk.CTkLabel(self.frame_hud, text=f"SCORE: {self.gestor.puntuacion:05d}", font=("Consolas", 20, "bold"), text_color="yellow")
        self.label_puntuacion.pack(side="left", padx=30)
        
        self.label_etapa = ctk.CTkLabel(self.frame_hud, text=f"ETAPA {self.gestor.etapa_actual}", font=("Consolas", 20, "bold"), text_color="white")
        self.label_etapa.pack(side="left", expand=True, pady=10)
        
        self.label_reloj = ctk.CTkLabel(self.frame_hud, text=f"T-MINUS {self.gestor.formatear_tiempo()}", font=("Consolas", 20, "bold"), text_color="#00FF00")
        self.label_reloj.pack(side="right", padx=20, pady=10)

    def iniciar_juego(self):
        self.gestor.iniciar_partida()
        self.limpiar_frame()
        self.construir_hud()
        
        self.frame_accion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_accion.pack(expand=True, fill="both", padx=20, pady=10)
        
        # --- NUEVO: Panel inferior con el botón de abortar ---
        self.frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controles.pack(side="bottom", pady=20)
        
        ctk.CTkButton(self.frame_controles, text="[ ABORTAR MISIÓN ]", font=("Consolas", 16, "bold"), 
                      fg_color="transparent", text_color="red", border_width=1, border_color="red", 
                      hover_color="#330000", command=self.mostrar_advertencia_abortar).pack()
        
        self.ciclo_reloj()
        self.cargar_etapa_1()

    def ciclo_reloj(self):
        if self.gestor.en_juego:
            self.gestor.decrementar_tiempo()
            tiempo_str = self.gestor.formatear_tiempo()
            self.label_reloj.configure(text=f"T-MINUS {tiempo_str}")
            
            if self.gestor.tiempo_restante <= 60:
                self.label_reloj.configure(text_color="red")
                
            if self.gestor.tiempo_restante <= 0:
                self.game_over("TIEMPO AGOTADO. EL NÚCLEO HA COLAPSADO.")
            else:
                self.id_timer = self.after(1000, self.ciclo_reloj)

    def actualizar_hud_vidas(self):
        vidas_str = "♥ " * self.gestor.vidas
        color = "#00FF00" if self.gestor.vidas > 1 else "red"
        self.label_vidas.configure(text=f"ESCUDOS: {vidas_str}", text_color=color)
        
    def actualizar_hud_puntos(self):
        self.label_puntuacion.configure(text=f"SCORE: {self.gestor.puntuacion:05d}")

    # --- NUEVAS FUNCIONES DE ABORTO ---
    def mostrar_advertencia_abortar(self):
        # Evitar que abra múltiples ventanas si da varios clics rápidos
        if hasattr(self, "ventana_advertencia") and self.ventana_advertencia.winfo_exists():
            self.ventana_advertencia.focus()
            return

        self.ventana_advertencia = ctk.CTkToplevel(self)
        self.ventana_advertencia.title("¡ADVERTENCIA CRÍTICA!")
        self.ventana_advertencia.geometry("550x250")
        self.ventana_advertencia.attributes("-topmost", True)
        
        # Esto bloquea que pueda interactuar con el juego de fondo, PERO el tiempo sigue corriendo
        self.ventana_advertencia.grab_set() 
        
        ctk.CTkLabel(self.ventana_advertencia, text="¿CONFIRMAR ABORTO DE MISIÓN?", font=("Consolas", 22, "bold"), text_color="red").pack(pady=(30, 10))
        
        texto_adv = (
            "Todo el progreso actual se perderá.\n"
            "Los protocolos de falla serán reasignados aleatoriamente.\n\n"
            "¡EL TIEMPO SIGUE CORRIENDO!"
        )
        ctk.CTkLabel(self.ventana_advertencia, text=texto_adv, font=("Consolas", 14), text_color="white", justify="center").pack(pady=10)
        
        frame_botones = ctk.CTkFrame(self.ventana_advertencia, fg_color="transparent")
        frame_botones.pack(pady=20)
        
        ctk.CTkButton(frame_botones, text="[ SÍ, ABORTAR ]", font=("Consolas", 14, "bold"), fg_color="transparent", 
                      text_color="red", border_width=1, border_color="red", hover_color="#330000", 
                      command=self.confirmar_aborto).pack(side="left", padx=10)
                      
        ctk.CTkButton(frame_botones, text="[ CANCELAR ]", font=("Consolas", 14), fg_color="transparent", 
                      text_color="gray", border_width=1, border_color="gray", hover_color="#333333", 
                      command=self.ventana_advertencia.destroy).pack(side="left", padx=10)

    def confirmar_aborto(self):
        if hasattr(self, "ventana_advertencia") and self.ventana_advertencia.winfo_exists():
            self.ventana_advertencia.destroy()
        self.gestor.en_juego = False
        self.gestor.registrar_solucionario_cierre("MISIÓN ABORTADA")
        self.detener_reloj()
        self.controlador.mostrar_vista("menu")
    # ==========================================
    # ETAPA 1: VALIDACIÓN TEÓRICA
    # ==========================================
    def cargar_etapa_1(self):
        if not self.gestor.en_juego: return
        self._esperando_e1 = False
        for widget in self.frame_accion.winfo_children():   
            widget.destroy()
            
        pregunta, opciones = self.gestor.obtener_pregunta_etapa_1()
        if not pregunta:
            return 
        
        progreso = f"({self.gestor.preguntas_respondidas + 1}/{self.gestor.preguntas_totales_etapa_1})"
        
        ctk.CTkLabel(self.frame_accion, text=f"> FASE 1: RECONOCIMIENTO DE PATRONES {progreso}", font=("Consolas", 18, "bold"), text_color="cyan").pack(pady=(10, 30))
        ctk.CTkLabel(self.frame_accion, text=pregunta, font=("Consolas", 16), text_color="white", wraplength=700).pack(pady=20)
        
        self.label_feedback = ctk.CTkLabel(self.frame_accion, text="", font=("Consolas", 16, "bold"))
        self.label_feedback.pack(pady=10)
        
        frame_opciones = ctk.CTkFrame(self.frame_accion, fg_color="transparent")
        frame_opciones.pack(pady=20)
        
        for opcion in opciones:
            btn = ctk.CTkButton(frame_opciones, text=opcion, font=("Consolas", 16), fg_color="#111111", 
                                border_width=1, text_color="white", border_color="gray", hover_color="#333333", width=300,
                                command=lambda r=opcion: self.procesar_respuesta_etapa_1(r))
            btn.pack(pady=10)

    def procesar_respuesta_etapa_1(self, respuesta):
        if not self.gestor.en_juego or getattr(self, "_esperando_e1", False): return
        
        if self.gestor.verificar_respuesta_etapa_1(respuesta):
            self._esperando_e1 = True
            self.gestor.sumar_puntos(100)
            self.actualizar_hud_puntos()
            self.label_feedback.configure(text="¡VALIDACIÓN CORRECTA!", text_color="#00FF00")
            
            if self.gestor.etapa_1_completada():
                self.after(1000, self.cargar_quiz_intermedio)
            else:
                self.after(1000, self.cargar_etapa_1)
        else:
            self.gestor.restar_vida()
            self.gestor.restar_puntos(50)
            self.actualizar_hud_vidas()
            self.actualizar_hud_puntos()
            self.label_feedback.configure(text="¡FALLA CRÍTICA! ESCUDO DAÑADO (-50 PTS).", text_color="red")

            if not self.gestor.en_juego:
                self.after(1000, lambda: self.game_over("INTEGRIDAD ESTRUCTURAL AL 0%. SISTEMA DESTRUIDO."))
    
     # quizz
        
    def cargar_quiz_intermedio(self):
        if not self.gestor.en_juego: return
        self.quiz_actual = GestorProblemas.obtener_quiz_intermedio()
        if not self.quiz_actual:
            self.cargar_etapa_2()
            return

        self._quiz_respondido = False
        self.label_etapa.configure(text="ANOMALÍA")
        self.gestor.registrar_solucionario_quiz(self.quiz_actual)  # <--- Guarda en el .txt

        for widget in self.frame_accion.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame_accion, text="⚠️ ALERTA: ANOMALÍA MATRICIAL DETECTADA", font=("Consolas", 22, "bold"), text_color="yellow").pack(pady=(20, 10))
        ctk.CTkLabel(self.frame_accion, text="Resuelva el protocolo para obtener un bono de integridad.", font=("Consolas", 14), text_color="white").pack(pady=(0, 20))

        frame_quiz = ctk.CTkFrame(self.frame_accion, fg_color="#111111", border_width=1, border_color="yellow")
        frame_quiz.pack(pady=10, padx=50, fill="both", expand=True)

        ctk.CTkLabel(frame_quiz, text=self.quiz_actual["texto_pregunta"], font=("Consolas", 16), text_color="cyan", justify="center").pack(pady=20, padx=20)

        self.label_feedback_quiz = ctk.CTkLabel(frame_quiz, text="", font=("Consolas", 16))
        self.label_feedback_quiz.pack(pady=10)

        if self.quiz_actual["tipo_input"] == "botones":
            opciones = self.quiz_actual["opciones_pantalla"].copy()
            random.shuffle(opciones)
            for op in opciones:
                ctk.CTkButton(frame_quiz, text=str(op), font=("Consolas", 16), fg_color="transparent",
                              border_width=1, text_color="white", border_color="gray", hover_color="#333300",
                              command=lambda r=op: self.verificar_quiz(r)).pack(pady=5)
        elif self.quiz_actual["tipo_input"] == "texto":
            self.entrada_quiz = ctk.CTkEntry(frame_quiz, font=("Consolas", 18), justify="center")
            self.entrada_quiz.pack(pady=10)
            self.entrada_quiz.bind("<Return>", lambda event: self.verificar_quiz(self.entrada_quiz.get().strip()))
            self.entrada_quiz.bind("<KP_Enter>", lambda event: self.verificar_quiz(self.entrada_quiz.get().strip()))
            self.entrada_quiz.focus()
            ctk.CTkButton(frame_quiz, text="[ APLICAR TRANSFORMACIÓN ]", font=("Consolas", 16, "bold"),
                          fg_color="transparent", border_width=2, text_color="yellow", border_color="yellow",
                          command=lambda: self.verificar_quiz(self.entrada_quiz.get().strip())).pack(pady=10)

        # Ahora queda FUERA del elif para aparecer en todos los quizzes
        ctk.CTkButton(self.frame_accion, text="[ OMITIR ANOMALÍA ]", font=("Consolas", 14), fg_color="transparent", text_color="gray",
                      command=self.omitir_quiz).pack(side="bottom", pady=20)

    def omitir_quiz(self):
        if self._quiz_respondido: return
        self._quiz_respondido = True
        self.cargar_etapa_2()

    def verificar_quiz(self, respuesta_jugador):
        if not self.gestor.en_juego or self._quiz_respondido: return
        respuesta_correcta = self.quiz_actual["respuesta_correcta"]

        if self.quiz_actual["tipo_input"] == "texto":
            try:
                es_correcta = float(respuesta_jugador.replace(",", ".")) == float(respuesta_correcta)
            except ValueError:
                self.label_feedback_quiz.configure(text="Error de formato.", text_color="red")
                return
        else:
            es_correcta = str(respuesta_jugador) == str(respuesta_correcta)

        self._quiz_respondido = True

        if es_correcta:
            self.gestor.sumar_puntos(250)
            self.actualizar_hud_puntos()
            if self.gestor.vidas < 3:
                self.gestor.vidas += 1
                self.actualizar_hud_vidas()
                mensaje = "¡CORRECTO! PROTOCOLO RESTAURADO (+1 ESCUDO)"
            else:
                self.gestor.tiempo_restante += 30
                mensaje = "¡CORRECTO! EFICIENCIA ÓPTIMA (+30 SEGUNDOS)"
            self.label_feedback_quiz.configure(text=mensaje, text_color="#00FF00")
        else:
            self.gestor.puntuacion = max(0, self.gestor.puntuacion - 100)
            self.actualizar_hud_puntos()
            self.label_feedback_quiz.configure(text=f"INCORRECTO. La respuesta era {respuesta_correcta}.\n¡PENALIZACIÓN APLICADA: -100 PTS!", text_color="red")

        self.after(2000, self.cargar_etapa_2)
            
    def transicion_etapa_2(self):
        for widget in self.frame_accion.winfo_children():
            widget.destroy()
            
        self.gestor.etapa_actual = 2
        self.label_etapa.configure(text=f"ETAPA {self.gestor.etapa_actual}")
        
        ctk.CTkLabel(self.frame_accion, text="¡FASE 1 COMPLETADA!", font=("Consolas", 30, "bold"), text_color="#00FF00").pack(pady=(50, 20))
        ctk.CTkLabel(self.frame_accion, text="Iniciando Fase 2: Estabilización de Módulos (Iteraciones Rápidas)...", font=("Consolas", 16), text_color="white").pack(pady=20)
        
        ctk.CTkButton(self.frame_accion, text="[ CONTINUAR ]", font=("Consolas", 20, "bold"), fg_color="transparent", 
                      border_width=2, text_color="cyan", border_color="cyan", hover_color="#003333",
                      command=self.cargar_etapa_2).pack(pady=30)
        
   
                      
    # ==========================================
    # ETAPA 2: ITERACIONES RÁPIDAS
    # ==========================================
    def cargar_etapa_2(self):
        if not self.gestor.en_juego: return
        self.gestor.etapa_actual = 2
        self.label_etapa.configure(text=f"ETAPA {self.gestor.etapa_actual}")

        if not self.gestor.preparar_etapa_2():
            self.transicion_etapa_3()
            return
        
        self.gestor.preparar_etapa_2()
        problema = self.gestor.problema_actual_n2
        metodo = self.gestor.metodo_actual_n2
        
        for widget in self.frame_accion.winfo_children():
            widget.destroy()
        numero = self.gestor.problemas_resueltos_etapa_2 + 1
        total = self.gestor.problemas_totales_etapa_2
        ctk.CTkLabel(
            self.frame_accion,
            text=f"> FASE 2: ESTABILIZACIÓN ({metodo})  [{numero}/{total}]",
            font=("Consolas", 18, "bold"),
            text_color="cyan",
        ).pack(pady=(5, 10))
        ctk.CTkLabel(self.frame_accion, text=problema["contexto"], font=("Consolas", 14), text_color="white", wraplength=700).pack(pady=(0, 10))

        # Tabla de resultados
        self.frame_tabla = ctk.CTkScrollableFrame(self.frame_accion, fg_color="#050505", border_width=1, border_color="gray", height=130)
        self.frame_tabla.pack(pady=5, padx=20, fill="x")

        # Cabecera Dinámica reutilizada de Práctica
        # --- CABECERA DINÁMICA SIN AYUDAS ---
        if self.gestor.motor_matematico.es_interpolacion():
            # Eliminamos la columna de fórmula y reajustamos los espacios
            cabecera = f"{'It':<4} | {'Paso / Término':<35} | {'Valor':<15}"
        elif metodo in ["BISECTRIZ", "FALSA_POSICION"]:
            cabecera = f"{'It':<4} | {'a':<10} | {'b':<10} | {'x_medio':<10} | {'f(x)':<10} | {'Error':<10}"
        else:
            cabecera = f"{'It':<4} | {'x_actual':<10} | {'x_nueva':<10} | {'f(x_nueva)':<10} | {'Error':<10}"

        ctk.CTkLabel(self.frame_tabla, text=cabecera, font=("Consolas", 12, "bold"), text_color="cyan", anchor="w").pack(fill="x", padx=5)
        ctk.CTkLabel(self.frame_tabla, text="-"*85, font=("Consolas", 12), text_color="gray", anchor="w").pack(fill="x", padx=5)

        # Controles de Entrada
        self.frame_juego = ctk.CTkFrame(self.frame_accion, fg_color="#111111", border_width=1, border_color="#00FF00")
        self.frame_juego.pack(pady=10, padx=20, fill="x")

        self.label_instruccion = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 16), text_color="yellow")
        self.label_instruccion.pack(pady=10)

        self.entrada_jugador = ctk.CTkEntry(self.frame_juego, font=("Consolas", 18), width=150, justify="center")
        self.entrada_jugador.pack(pady=5)
        self.entrada_jugador.bind("<Return>", lambda event: self.procesar_respuesta_etapa_2())
        self.entrada_jugador.bind("<KP_Enter>", lambda event: self.procesar_respuesta_etapa_2())

        self.label_feedback = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 14))
        self.label_feedback.pack(pady=5)

        self.btn_enviar = ctk.CTkButton(self.frame_juego, text="[ ENVIAR DATOS ]", font=("Consolas", 16, "bold"), fg_color="transparent", 
                                        border_width=2, text_color="#00FF00", border_color="#00FF00", hover_color="#003300", 
                                        command=self.procesar_respuesta_etapa_2)
        self.btn_enviar.pack(pady=10)

        self.actualizar_paso_etapa_2()

    def actualizar_paso_etapa_2(self):
        datos_paso = self.gestor.motor_matematico.obtener_datos_paso_actual()
        
        if not datos_paso:
            self.label_instruccion.configure(text="¡MÓDULO ESTABILIZADO! PROBLEMA COMPLETADO.")
            self.entrada_jugador.configure(state="disabled")
            self.btn_enviar.pack_forget()

            if self.gestor.registrar_problema_etapa_2_resuelto():
                self.after(2000, self.transicion_etapa_3)
            else:
                self.after(2000, self.cargar_etapa_2)
            return

        # Texto de Instrucción Dinámico
        if self.gestor.motor_matematico.es_interpolacion():
            texto = f"PASO {datos_paso['iteracion']}: {datos_paso['etiqueta']}\nIngrese el valor de [{datos_paso['corto']}]:"
        elif self.gestor.metodo_actual_n2 in ["BISECTRIZ", "FALSA_POSICION"]:
            texto = f"ITERACIÓN {datos_paso['iteracion']} | a = {datos_paso.get('a','?')} | b = {datos_paso.get('b','?')}\nIngrese x_medio:"
        else:
            x_act = datos_paso.get("xi", datos_paso.get("x0", "?"))
            texto = f"ITERACIÓN {datos_paso.get('iteracion', '?')} | Aproximación actual = {x_act}\nIngrese nueva aproximación:"

        self.label_instruccion.configure(text=texto)
        self.entrada_jugador.delete(0, 'end')
        self.label_feedback.configure(text="")
        self.entrada_jugador.focus()

    def limpiar_error_e2(self):
        texto_actual = self.label_feedback.cget("text")
        if "Correcto" not in texto_actual and texto_actual != "":
            self.label_feedback.configure(text="")
            self.entrada_jugador.delete(0, 'end')
    
    

    def procesar_respuesta_etapa_2(self):
        if not self.gestor.en_juego: return
        
        try:
            valor = float(self.entrada_jugador.get())
        except ValueError:
            self.label_feedback.configure(text="Error: Ingrese un valor numérico.", text_color="red")
            self.after(2000, self.limpiar_error_e2)
            return

        datos_resueltos = self.gestor.motor_matematico.obtener_datos_paso_actual()
        correcto, valor_real = self.gestor.verificar_respuesta_etapa_2(valor)

        if correcto:
            self.gestor.sumar_puntos(50)
            self.actualizar_hud_puntos()
            self.label_feedback.configure(text=f"¡Correcto! Valor = {valor_real}", text_color="#00FF00")

            it_str = str(datos_resueltos.get('iteracion', '?'))
            metodo_actual = self.gestor.metodo_actual_n2

            if self.gestor.motor_matematico.es_interpolacion():
                paso_str = str(datos_resueltos.get('corto', '---'))[:25]
                formula_str = str(datos_resueltos.get('formula', '---'))[:35]
                valor_str = str(valor_real)
                fila = f"{it_str:<4} | {paso_str:<35} | {valor_str:<15}"
                
            elif metodo_actual in ["BISECTRIZ", "FALSA_POSICION"]:
                a_str = str(datos_resueltos.get('a', '---'))
                b_str = str(datos_resueltos.get('b', '---'))
                x_str = str(valor_real)
                fx_str = str(datos_resueltos.get('f_x_medio', '---'))
                error_str = str(datos_resueltos.get('error', '---')) if datos_resueltos.get('error') is not None else "---"
                fila = f"{it_str:<4} | {a_str:<10} | {b_str:<10} | {x_str:<10} | {fx_str:<10} | {error_str:<10}"
                
            else:
                x_actual = str(datos_resueltos.get('xi', datos_resueltos.get('x0', '---')))
                x_nueva = str(valor_real)
                fx_nueva = str(datos_resueltos.get('f_xi', datos_resueltos.get('f_x_nueva', '---')))
                error_str = str(datos_resueltos.get('error', '---')) if datos_resueltos.get('error') is not None else "---"
                fila = f"{it_str:<4} | {x_actual:<10} | {x_nueva:<10} | {fx_nueva:<10} | {error_str:<10}"

            ctk.CTkLabel(self.frame_tabla, text=fila, font=("Consolas", 12), text_color="white", anchor="w").pack(fill="x", padx=5)
            self.frame_tabla._parent_canvas.yview_moveto(1.0)
            
            self.after(1000, self.actualizar_paso_etapa_2)
        else:
            # PENALIZACIÓN DE ESCUDOS Y PUNTOS
            self.gestor.restar_vida()
            self.gestor.restar_puntos(50)
            self.actualizar_hud_vidas()
            self.actualizar_hud_puntos()
            self.label_feedback.configure(text="¡FALLA CRÍTICA! ESCUDO DAÑADO (-50 PTS).", text_color="red")

            if not self.gestor.en_juego:
                self.after(1000, lambda: self.game_over("INTEGRIDAD ESTRUCTURAL AL 0%. SISTEMA DESTRUIDO."))
            else:
                self.after(2000, self.limpiar_error_e2)
        
    def game_over(self, motivo):
        if hasattr(self, "ventana_advertencia") and self.ventana_advertencia.winfo_exists():
            self.ventana_advertencia.destroy()

        self.gestor.en_juego = False
        self.gestor.registrar_solucionario_cierre(f"GAME OVER - {motivo}")
        self.detener_reloj()
        self.limpiar_frame()

        ctk.CTkLabel(self, text="[ G A M E  O V E R ]", font=("Consolas", 50, "bold"), text_color="red").pack(pady=(90, 20))
        ctk.CTkLabel(self, text=motivo, font=("Consolas", 20), text_color="yellow").pack(pady=10)
        ctk.CTkLabel(self, text=f"SCORE FINAL: {self.gestor.puntuacion:05d}", font=("Consolas", 22, "bold"), text_color="cyan").pack(pady=15)

        ctk.CTkButton(self, text="[ REINICIAR SISTEMA ]", font=("Consolas", 20), fg_color="transparent", text_color="white", hover_color="#333333",
                      border_width=1, border_color="white", command=self.mostrar_pantalla_inicio).pack(pady=(30, 10))
        ctk.CTkButton(self, text="[ VOLVER AL MENÚ ]", font=("Consolas", 16), fg_color="transparent", text_color="gray", hover_color="#333333",
                      command=lambda: self.controlador.mostrar_vista("menu")).pack(pady=10)