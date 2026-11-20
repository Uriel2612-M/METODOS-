import customtkinter as ctk
from logica.gestor_manual import GestorManual
from utilidades.fondo import COLOR_FONDO, aplicar_fondo

# Ancho (en píxeles) al que se parte el texto corrido si todavía no se puede medir el lector.
ANCHO_TEXTO_DEFECTO = 430


class VistaManual(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color=COLOR_FONDO)
        aplicar_fondo(self)
        self.controlador = controlador
        self.fichas = GestorManual.obtener_todas_las_fichas()
        self.ancho_texto = ANCHO_TEXTO_DEFECTO
        self._etiquetas_ajustables = []   # (etiqueta, descuento) cuyo wraplength sigue al ancho del lector
        self._tarea_ajuste = None
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

        # Botón de salida fijo en la parte inferior.
        # Se empaca ANTES que la lista para que siempre conserve su espacio y nunca desaparezca.
        ctk.CTkButton(self.panel_indice, text="[ CERRAR MANUAL ]", font=("Consolas", 14, "bold"), fg_color="transparent",
                      text_color="gray", hover_color="#333333",
                      command=self.controlador.regresar_vista).pack(side="bottom", pady=20, padx=10)

        # Lista de protocolos con scroll lateral (ocupa el espacio que queda entre el título y el botón de salida)
        self.lista_indice = ctk.CTkScrollableFrame(self.panel_indice, width=320, fg_color="transparent")
        self.lista_indice.pack(side="top", expand=True, fill="both", padx=5)

        for ficha in self.fichas:
            ctk.CTkButton(self.lista_indice, text=f"[{ficha['nombre']}]", font=("Consolas", 14),
                          fg_color="transparent", border_width=1, text_color="white", border_color="gray",
                          hover_color="#003300", command=lambda f=ficha: self.mostrar_ficha(f)).pack(pady=5, padx=5, fill="x")

        # Panel Derecho (Lector Scrolleable)
        self.panel_lector = ctk.CTkScrollableFrame(self.frame_contenido, fg_color="#050505", border_width=1, border_color="#00FF00")
        self.panel_lector.pack(side="right", expand=True, fill="both")
        self.panel_lector.bind("<Configure>", self._al_cambiar_tamano, add="+")

        self.label_pantalla_vacia = ctk.CTkLabel(self.panel_lector, text="Seleccione un protocolo en el índice para leer su ficha técnica.",
                                                 font=("Consolas", 14), text_color="gray")
        self.label_pantalla_vacia.pack(pady=50)

    # ------------------------------------------------------------------
    # Ficha
    # ------------------------------------------------------------------
    def mostrar_ficha(self, ficha):
        # El texto se parte al ancho real del lector y se reajusta si la ventana cambia de tamaño
        self.ancho_texto = self._medir_ancho()
        self._etiquetas_ajustables = []

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

        ejemplo = ficha["ejemplo"]
        if isinstance(ejemplo, dict):
            self.dibujar_ejemplo(ejemplo)
        else:
            # Formato antiguo: un solo bloque de texto
            self.agregar_seccion("8. EJEMPLO PASO A PASO", ejemplo, color_texto="yellow")

    def _medir_ancho(self):
        """Ancho disponible para el texto, en las mismas unidades que usa wraplength (ya sin la escala de pantalla)."""
        ancho_panel = self.panel_lector.winfo_width()
        if ancho_panel <= 150:
            return ANCHO_TEXTO_DEFECTO
        try:
            escala = self.panel_lector._get_widget_scaling()
        except Exception:
            escala = 1
        return max(250, int(ancho_panel / escala) - 80)

    def _al_cambiar_tamano(self, _evento=None):
        # Espera a que termine el arrastre de la ventana antes de reajustar
        if self._tarea_ajuste:
            self.after_cancel(self._tarea_ajuste)
        self._tarea_ajuste = self.after(80, self._reajustar_texto)

    def _reajustar_texto(self):
        self._tarea_ajuste = None
        nuevo = self._medir_ancho()
        if abs(nuevo - self.ancho_texto) < 8:
            return
        self.ancho_texto = nuevo
        for etiqueta, descuento in self._etiquetas_ajustables:
            try:
                etiqueta.configure(wraplength=nuevo - descuento)
            except Exception:
                pass  # etiqueta ya destruida

    def _etiqueta(self, padre, descuento=0, **opciones):
        """CTkLabel de texto corrido: su wraplength sigue al ancho del lector."""
        etiqueta = ctk.CTkLabel(padre, wraplength=self.ancho_texto - descuento, **opciones)
        self._etiquetas_ajustables.append((etiqueta, descuento))
        return etiqueta

    def agregar_seccion(self, titulo, contenido, color_titulo="white", color_texto="white", tam_titulo=16):
        ctk.CTkLabel(self.panel_lector, text=titulo, font=("Consolas", tam_titulo, "bold"), text_color=color_titulo, anchor="w").pack(fill="x", pady=(15, 5), padx=10)
        if contenido:
            self._etiqueta(self.panel_lector, text=contenido, font=("Consolas", 14), text_color=color_texto, justify="left").pack(fill="x", padx=20)

    # ------------------------------------------------------------------
    # Ejemplo estructurado
    #
    # "ejemplo": {
    #     "enunciado":   [bloque, ...],
    #     "pasos":       [{"titulo": "...", "bloques": [bloque, ...]}, ...],
    #     "resultado":   "texto"   (opcional),
    #     "comprobacion": "texto"  (opcional)
    # }
    # bloque = {"tipo": "texto", "lineas": [...]}      párrafo; las líneas que inician con "- " salen con viñeta
    #        | {"tipo": "subtitulo", "texto": "..."}   encabezado pequeño dentro de un paso
    #        | {"tipo": "tabla", "lineas": [...]}      texto monoespaciado alineado (tablas y matrices)
    # ------------------------------------------------------------------
    def dibujar_ejemplo(self, ejemplo):
        self.agregar_seccion("8. EJEMPLO PASO A PASO", "", color_titulo="yellow")

        enunciado = ejemplo.get("enunciado")
        if enunciado:
            caja = self._caja("#0d0d0d", "#555555")
            ctk.CTkLabel(caja, text="PROBLEMA", font=("Consolas", 12, "bold"), text_color="gray", anchor="w").pack(fill="x", padx=12, pady=(8, 2))
            for bloque in enunciado:
                self._dibujar_bloque(caja, bloque, color_texto="white")
            ctk.CTkFrame(caja, height=6, fg_color="transparent").pack()

        for numero, paso in enumerate(ejemplo.get("pasos", []), start=1):
            self._etiqueta(self.panel_lector, text=f"PASO {numero}  ·  {paso['titulo']}",
                         font=("Consolas", 14, "bold"), text_color="yellow", anchor="w", justify="left").pack(fill="x", padx=10, pady=(18, 2))
            ctk.CTkFrame(self.panel_lector, height=1, fg_color="#444400").pack(fill="x", padx=10, pady=(0, 4))
            for bloque in paso.get("bloques", []):
                self._dibujar_bloque(self.panel_lector, bloque, color_texto="white", sangria=20)

        resultado = ejemplo.get("resultado")
        if resultado:
            caja = self._caja("#001a00", "#00FF00", espacio_arriba=18)
            ctk.CTkLabel(caja, text="RESULTADO", font=("Consolas", 12, "bold"), text_color="#00aa00", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
            self._etiqueta(caja, descuento=20, text=resultado, font=("Consolas", 16, "bold"), text_color="#00FF00",
                         justify="left", anchor="w").pack(fill="x", padx=12, pady=(0, 10))

        comprobacion = ejemplo.get("comprobacion")
        if comprobacion:
            self._etiqueta(self.panel_lector, text=f"✓ Comprobación: {comprobacion}", font=("Consolas", 13),
                         text_color="#aaaaaa", justify="left", anchor="w").pack(fill="x", padx=10, pady=(10, 20))

    def _caja(self, fondo, borde, espacio_arriba=8):
        caja = ctk.CTkFrame(self.panel_lector, fg_color=fondo, border_width=1, border_color=borde)
        caja.pack(fill="x", padx=10, pady=(espacio_arriba, 4))
        return caja

    def _dibujar_bloque(self, padre, bloque, color_texto="white", sangria=10):
        tipo = bloque.get("tipo")
        if tipo == "subtitulo":
            self._etiqueta(padre, text=bloque["texto"], font=("Consolas", 14, "bold"), text_color="cyan",
                         anchor="w", justify="left").pack(fill="x", padx=sangria, pady=(10, 2))
        elif tipo == "tabla":
            self._dibujar_tabla(padre, bloque["lineas"], sangria)
        else:
            lineas = [("•  " + l[2:]) if l.startswith("- ") else l for l in bloque.get("lineas", [])]
            self._etiqueta(padre, text="\n".join(lineas), font=("Consolas", 14), text_color=color_texto,
                         anchor="w", justify="left").pack(fill="x", padx=sangria, pady=(4, 2))

    def _dibujar_tabla(self, padre, lineas, sangria):
        """Tabla/matriz en monoespaciado: no se parte (eso desalinea las columnas); si es más ancha que el panel, hace scroll horizontal."""
        fuente = ctk.CTkFont(family="Consolas", size=13)
        alto = len(lineas) * fuente.metrics("linespace") + 28  # +28 deja lugar a la barra horizontal
        cuadro = ctk.CTkTextbox(padre, font=fuente, height=alto, wrap="none", fg_color="#0a0f0a",
                                text_color="#7CFC00", border_width=1, border_color="#224422")
        cuadro.insert("1.0", "\n".join(lineas))
        cuadro.configure(state="disabled")
        cuadro.pack(fill="x", padx=sangria, pady=6)
        self._reenviar_rueda(cuadro)

    def _reenviar_rueda(self, cuadro):
        """La rueda del ratón sobre una tabla sigue desplazando el lector, en vez de quedarse atrapada en la tabla."""
        lienzo = self.panel_lector._parent_canvas

        def rueda(evento):
            if getattr(evento, "num", None) == 4:
                pasos = -1
            elif getattr(evento, "num", None) == 5:
                pasos = 1
            else:
                pasos = -1 if evento.delta > 0 else 1
            lienzo.yview_scroll(pasos * 3, "units")
            return "break"

        interno = getattr(cuadro, "_textbox", cuadro)
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            interno.bind(secuencia, rueda)