import customtkinter as ctk


class EtapaTresDesafio:
    """
    ETAPA 3 DEL MODO DESAFÍO: SOBRECARGA DEL NÚCLEO (problemas de Nivel 3).

    Es un "mixin": VistaDesafio hereda de esta clase y usa sus métodos. Así la etapa 3
    vive en su propio archivo y no se mezcla con las etapas 1 y 2.
    Usa los mismos widgets/atributos que ya existen en VistaDesafio
    (frame_accion, gestor, label_etapa, detener_reloj, limpiar_frame, game_over...).

    Flujo:  transicion_etapa_3 -> cargar_etapa_3 -> (paso a paso) -> mostrar_victoria
            Si todavía no hay ningún método de Nivel 3 implementado:
            transicion_etapa_3 -> cargar_etapa_3 -> mostrar_sin_protocolos_etapa_3 -> victoria
    """

    # ------------------------------------------------------------------
    # TRANSICIÓN
    # ------------------------------------------------------------------
    def transicion_etapa_3(self):
        if not self.gestor.en_juego:
            return

        for widget in self.frame_accion.winfo_children():
            widget.destroy()

        self.gestor.etapa_actual = 3
        self.label_etapa.configure(text=f"ETAPA {self.gestor.etapa_actual}")

        ctk.CTkLabel(self.frame_accion, text="¡FASE 2 COMPLETADA!", font=("Consolas", 30, "bold"), text_color="#00FF00").pack(pady=(50, 20))
        ctk.CTkLabel(self.frame_accion, text="Iniciando Fase 3: Sobrecarga del Núcleo (Cálculo Complejo)...", font=("Consolas", 16), text_color="white").pack(pady=20)

        ctk.CTkButton(self.frame_accion, text="[ CONTINUAR ]", font=("Consolas", 20, "bold"), fg_color="transparent",
                      border_width=2, text_color="cyan", border_color="cyan", hover_color="#003333",
                      command=self.cargar_etapa_3).pack(pady=30)

    # ------------------------------------------------------------------
    # CARGA DEL PROBLEMA
    # ------------------------------------------------------------------
    def cargar_etapa_3(self):
        if not self.gestor.en_juego:
            return

        if not self.gestor.preparar_etapa_3():
            self.mostrar_sin_protocolos_etapa_3()
            return

        problema = self.gestor.problema_actual_n3
        metodo = self.gestor.metodo_actual_n3
        numero = self.gestor.problemas_resueltos_etapa_3 + 1
        total = self.gestor.problemas_totales_etapa_3
        self._esperando_e3 = False

        for widget in self.frame_accion.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame_accion, text=f"> FASE 3: SOBRECARGA DEL NÚCLEO ({metodo})  [{numero}/{total}]",
                     font=("Consolas", 18, "bold"), text_color="cyan").pack(pady=(5, 5))
        ctk.CTkLabel(self.frame_accion, text=problema["titulo"], font=("Consolas", 14, "bold"),
                     text_color="yellow").pack(pady=(0, 5))
        ctk.CTkLabel(self.frame_accion, text=self.gestor.texto_problema_etapa_3(), font=("Consolas", 13),
                     text_color="white", wraplength=700, justify="left").pack(pady=(0, 8))

        # Tabla de resultados (sin fórmulas: en el Desafío no hay ayudas)
        self.frame_tabla = ctk.CTkScrollableFrame(self.frame_accion, fg_color="#050505", border_width=1,
                                                  border_color="gray", height=110)
        self.frame_tabla.pack(pady=5, padx=20, fill="x")

        cabecera = f"{'It':<4} | {'Paso / Término':<35} | {'Valor':<15}"
        ctk.CTkLabel(self.frame_tabla, text=cabecera, font=("Consolas", 12, "bold"), text_color="cyan", anchor="w").pack(fill="x", padx=5)
        ctk.CTkLabel(self.frame_tabla, text="-" * 60, font=("Consolas", 12), text_color="gray", anchor="w").pack(fill="x", padx=5)

        # Controles de entrada
        self.frame_juego = ctk.CTkFrame(self.frame_accion, fg_color="#111111", border_width=1, border_color="#00FF00")
        self.frame_juego.pack(pady=10, padx=20, fill="x")

        self.label_instruccion = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 15), text_color="yellow")
        self.label_instruccion.pack(pady=10)

        self.entrada_jugador = ctk.CTkEntry(self.frame_juego, font=("Consolas", 18), width=150, justify="center")
        self.entrada_jugador.pack(pady=5)
        self.entrada_jugador.bind("<Return>", lambda evento: self.procesar_respuesta_etapa_3())

        self.label_feedback = ctk.CTkLabel(self.frame_juego, text="", font=("Consolas", 14))
        self.label_feedback.pack(pady=5)

        self.btn_enviar = ctk.CTkButton(self.frame_juego, text="[ ENVIAR DATOS ]", font=("Consolas", 16, "bold"),
                                        fg_color="transparent", border_width=2, text_color="#00FF00",
                                        border_color="#00FF00", hover_color="#003300",
                                        command=self.procesar_respuesta_etapa_3)
        self.btn_enviar.pack(pady=10)

        self.actualizar_paso_etapa_3()

    # ------------------------------------------------------------------
    # PASOS
    # ------------------------------------------------------------------
    def actualizar_paso_etapa_3(self):
        if not self.gestor.en_juego:
            return

        self._esperando_e3 = False
        datos_paso = self.gestor.paso_etapa_3_actual()

        if not datos_paso:
            # Terminó el problema actual
            self.label_instruccion.configure(text="¡NÚCLEO ESTABILIZADO! PROBLEMA COMPLETADO.")
            self.entrada_jugador.configure(state="disabled")
            self.btn_enviar.pack_forget()

            if self.gestor.registrar_problema_etapa_3_resuelto():
                self.after(2000, self.mostrar_victoria)
            else:
                self.after(2000, self.cargar_etapa_3)
            return

        total = self.gestor.total_pasos_etapa_3()
        texto = (f"PASO {datos_paso['iteracion']}/{total}: {datos_paso['etiqueta']}\n"
                 f"Ingrese el valor de [{datos_paso['corto']}]:")
        self.label_instruccion.configure(text=texto)
        self.entrada_jugador.configure(state="normal")
        self.entrada_jugador.delete(0, "end")
        self.entrada_jugador.focus()
        self.label_feedback.configure(text="")
        self.btn_enviar.configure(state="normal")

    def limpiar_error_e3(self):
        texto_actual = self.label_feedback.cget("text")
        if "Correcto" not in texto_actual and texto_actual != "":
            self.label_feedback.configure(text="")
            self.entrada_jugador.delete(0, "end")

    def procesar_respuesta_etapa_3(self):
        if not self.gestor.en_juego or self._esperando_e3:
            return

        try:
            valor = float(self.entrada_jugador.get().strip().replace(",", "."))
        except ValueError:
            self.label_feedback.configure(text="Error: Ingrese un valor numérico.", text_color="red")
            self.after(2000, self.limpiar_error_e3)
            return

        datos_resueltos = self.gestor.paso_etapa_3_actual()
        correcto, valor_real = self.gestor.verificar_respuesta_etapa_3(valor)
        
        self.gestor.sumar_puntos(100)
        self.actualizar_hud_puntos()
        
        if correcto:
            self._esperando_e3 = True
            self.btn_enviar.configure(state="disabled")
            self.label_feedback.configure(text=f"¡Correcto! Valor = {valor_real}", text_color="#00FF00")

            it_str = str(datos_resueltos.get("iteracion", "?"))
            paso_str = str(datos_resueltos.get("corto", "---"))[:35]
            fila = f"{it_str:<4} | {paso_str:<35} | {str(valor_real):<15}"
            ctk.CTkLabel(self.frame_tabla, text=fila, font=("Consolas", 12), text_color="white", anchor="w").pack(fill="x", padx=5)
            self.frame_tabla._parent_canvas.yview_moveto(1.0)

            self.after(1000, self.actualizar_paso_etapa_3)
        else:
            # PENALIZACIÓN DE ESCUDOS
            self.gestor.restar_vida()
            self.actualizar_hud_vidas()
            self.label_feedback.configure(text="¡FALLA CRÍTICA! ESCUDO DAÑADO.", text_color="red")

            if not self.gestor.en_juego:
                self.after(1000, lambda: self.game_over("INTEGRIDAD ESTRUCTURAL AL 0%. SISTEMA DESTRUIDO."))
            else:
                self.after(2000, self.limpiar_error_e3)

    # ------------------------------------------------------------------
    # SIN PROTOCOLOS DISPONIBLES (mientras falten métodos de Nivel 3)
    # ------------------------------------------------------------------
    def mostrar_sin_protocolos_etapa_3(self):
        pendientes = self.gestor.metodos_pendientes_etapa_3()
        print(f"[Etapa 3] Sin problemas disponibles. Métodos de Nivel 3 pendientes: {', '.join(pendientes)}")

        for widget in self.frame_accion.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame_accion, text="> FASE 3: SIN PROTOCOLOS DISPONIBLES", font=("Consolas", 22, "bold"),
                     text_color="yellow").pack(pady=(50, 15))
        ctk.CTkLabel(self.frame_accion, text="Los protocolos de cálculo complejo aún no están integrados al sistema.",
                     font=("Consolas", 15), text_color="white").pack(pady=5)
        ctk.CTkLabel(self.frame_accion, text="Pendientes: " + ", ".join(pendientes), font=("Consolas", 12),
                     text_color="gray", wraplength=700).pack(pady=15)

        ctk.CTkButton(self.frame_accion, text="[ FINALIZAR MISIÓN ]", font=("Consolas", 20, "bold"), fg_color="transparent",
                      border_width=2, text_color="cyan", border_color="cyan", hover_color="#003333",
                      command=self.mostrar_victoria).pack(pady=30)

    # ------------------------------------------------------------------
    # VICTORIA
    # ------------------------------------------------------------------
    def mostrar_victoria(self):
        if not self.gestor.en_juego:
            return

        self.gestor.en_juego = False   # detiene el reloj y bloquea cualquier respuesta pendiente
        self.detener_reloj()
        self.limpiar_frame()

        ctk.CTkLabel(self, text="[ MISIÓN CUMPLIDA ]", font=("Consolas", 50, "bold"), text_color="#00FF00").pack(pady=(100, 20))
        ctk.CTkLabel(self, text="NÚCLEO ESTABILIZADO. EL SISTEMA HA SIDO RECUPERADO.", font=("Consolas", 20),
                     text_color="white").pack(pady=10)

        
        self.gestor.registrar_solucionario_cierre("MISIÓN CUMPLIDA")
        resumen = (f"SCORE FINAL: {self.gestor.puntuacion:05d}   |   "
                 f"ESCUDOS: {'♥ ' * self.gestor.vidas}   |   "
                 f"TIEMPO: {self.gestor.formatear_tiempo()}")
        ctk.CTkLabel(self, text=resumen, font=("Consolas", 18, "bold"), text_color="cyan").pack(pady=20)

        ctk.CTkButton(self, text="[ JUGAR DE NUEVO ]", font=("Consolas", 20), fg_color="transparent", text_color="#00FF00",
                      border_width=1, border_color="#00FF00", hover_color="#003300",
                      command=self.mostrar_pantalla_inicio).pack(pady=(30, 10))
        ctk.CTkButton(self, text="[ VOLVER AL MENÚ ]", font=("Consolas", 16), fg_color="transparent", text_color="gray",
                      hover_color="#333333", command=lambda: self.controlador.mostrar_vista("menu")).pack(pady=10)