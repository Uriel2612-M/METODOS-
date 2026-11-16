import customtkinter as ctk
from logica.gestor_desafio import GestorDesafio

class VistaDesafio(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.gestor = GestorDesafio()
        self.id_timer = None 
        
        self.mostrar_pantalla_inicio()

    def limpiar_frame(self):
        for widget in self.winfo_children():
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
        self.detener_reloj()
        self.controlador.mostrar_vista("menu")

    # ==========================================
    # ETAPA 1: VALIDACIÓN TEÓRICA
    # ==========================================
# ==========================================
    # ETAPA 1: VALIDACIÓN TEÓRICA
    # ==========================================
    def cargar_etapa_1(self):
        for widget in self.frame_accion.winfo_children():
            widget.destroy()
            
        pregunta, opciones = self.gestor.obtener_pregunta_etapa_1()
        if not pregunta:
            return # Seguridad por si el arreglo viene vacío
            
        # Marcador visual de progreso (ej. 1/7)
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
        if not self.gestor.en_juego: return
        
        if self.gestor.verificar_respuesta_etapa_1(respuesta):
            self.label_feedback.configure(text="¡VALIDACIÓN CORRECTA!", text_color="#00FF00")
            
            # Verificamos si completó las 7 preguntas para avanzar de nivel
            if self.gestor.etapa_1_completada():
                self.after(1000, self.transicion_etapa_2)
            else:
                self.after(1000, self.cargar_etapa_1)
        else:
            self.gestor.restar_vida()
            self.actualizar_hud_vidas()
            self.label_feedback.configure(text="¡FALLA CRÍTICA! ESCUDO DAÑADO.", text_color="red")
            
            if not self.gestor.en_juego:
                self.after(1000, lambda: self.game_over("INTEGRIDAD ESTRUCTURAL AL 0%. SISTEMA DESTRUIDO."))

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
                      
    def cargar_etapa_2(self):
        # Limpiar frame temporalmente para indicar que la fase 2 está en construcción
        for widget in self.frame_accion.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.frame_accion, text="> FASE 2 EN ESPERA DE INTEGRACIÓN...", font=("Consolas", 18, "bold"), text_color="yellow").pack(pady=50)

    def game_over(self, motivo):
        # Si el tiempo se acaba mientras el jugador está leyendo la advertencia, se cierra la ventana forzosamente
        if hasattr(self, "ventana_advertencia") and self.ventana_advertencia.winfo_exists():
            self.ventana_advertencia.destroy()
            
        self.detener_reloj()
        self.limpiar_frame()
        
        ctk.CTkLabel(self, text="[ G A M E  O V E R ]", font=("Consolas", 50, "bold"), text_color="red").pack(pady=(100, 20))
        ctk.CTkLabel(self, text=motivo, font=("Consolas", 20), text_color="yellow").pack(pady=20)
        
        ctk.CTkButton(self, text="[ REINICIAR SISTEMA ]", font=("Consolas", 20), fg_color="transparent", text_color="white", hover_color="#333333", 
                      border_width=1, border_color="white", command=self.mostrar_pantalla_inicio).pack(pady=40)