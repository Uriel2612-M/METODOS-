import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class VentanaGrafica(ctk.CTkToplevel):
    def __init__(self, parent, problema, tabla_respuestas):
        super().__init__(parent)
        self.title(f"Telemetría Gráfica: {problema['titulo']}")
        self.geometry("900x700")
        self.attributes("-topmost", True)
        
        # Contenedor principal para mantener ordenado el canvas y la barra de herramientas
        frame_grafica = ctk.CTkFrame(self, fg_color="#111111")
        frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuración visual estilo plano cartesiano clásico (Oscuro)
        self.figura = Figure(figsize=(8, 6), dpi=100, facecolor='#111111')
        self.ax = self.figura.add_subplot(111)
        self.ax.set_facecolor('#111111')
        self.ax.tick_params(colors='white')
        
        # Estilo de ejes centrados (Cruzando en 0,0)
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_color('none')  # Ocultamos el borde derecho
        self.ax.spines['top'].set_color('none')    # Ocultamos el borde superior
        self.ax.spines['left'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
            
        self.dibujar_grafica(problema, tabla_respuestas)
        
        # Incrustar Matplotlib en CustomTkinter
        self.canvas = FigureCanvasTkAgg(self.figura, master=frame_grafica)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # --- NUEVO: BARRA DE HERRAMIENTAS INTERACTIVA (ZOOM Y DESPLAZAMIENTO) ---
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_grafica)
        self.toolbar.update()
        self.toolbar.pack(side="bottom", fill="x")
        
        # Estilizar un poco la barra para que no desentone tanto con el tema oscuro
        self.toolbar.config(background='#222222')
        for widget in self.toolbar.winfo_children():
            widget.config(background='#222222')

        ctk.CTkButton(self, text="[ CERRAR TELEMETRÍA ]", font=("Consolas", 14, "bold"), 
                      fg_color="transparent", border_width=1, text_color="red", 
                      border_color="red", hover_color="#330000", 
                      command=self.destroy).pack(pady=10)

    def dibujar_grafica(self, problema, tabla_respuestas):
        # 1. Determinar un rango panorámico (El jugador ahora hará zoom manual)
        x_min, x_max = -8, 8
        datos_ini = {}
        datos_ini.update(problema.get("valores_iniciales", {}))
        datos_ini.update(problema.get("parametros_fijos", {}))
        datos_base = problema.get("datos_base", {})
        
        
        if "a" in datos_ini and "b" in datos_ini:
            centro = (datos_ini["a"] + datos_ini["b"]) / 2
            x_min, x_max = centro - 5, centro + 5
        elif "xi" in datos_base:
            x_min, x_max = min(datos_base["xi"]) - 3, max(datos_base["xi"]) + 3
        elif "x0" in datos_ini:
            x_min, x_max = datos_ini["x0"] - 5, datos_ini["x0"] + 5

        # Generar 1000 puntos para la suavidad de la curva
        x = np.linspace(x_min, x_max, 1000)
        
        # Cuadrícula fina para tener la referencia como en tu imagen
        self.ax.grid(True, color='#333333', linestyle='-', linewidth=1)
        
        # 2. Dibujar la Función Continua
        funcion_str = problema.get("funcion_python", "")
        if funcion_str:
            func_eval = funcion_str.replace("math.", "np.")
            try:
                y = eval(func_eval)
                if isinstance(y, (int, float)): 
                    y = np.full_like(x, y)
                self.ax.plot(x, y, color='cyan', label=problema.get("funcion_display", "f(x)"), linewidth=2)
            except Exception as e:
                print(f"Error al graficar la función: {e}")

        # 3. Dibujar Lecturas de Sensores
        if "xi" in datos_base and "yi" in datos_base:
            self.ax.scatter(datos_base["xi"], datos_base["yi"], color='yellow', s=60, label='Nodos Base', zorder=5)

        # 4. Localizar y Dibujar el Resultado Final del Jugador
        if tabla_respuestas:
            ultimo_paso = tabla_respuestas[-1]

            # Caso A: Integración numérica (tiene intervalo [a, b] y segmentos n)
            if "a" in datos_ini and "b" in datos_ini and "n" in datos_ini and funcion_str:
                x_area = np.linspace(datos_ini["a"], datos_ini["b"], 400)
                try:
                    y_area = eval(funcion_str.replace("math.", "np."), {"np": np, "x": x_area})
                    self.ax.fill_between(x_area, 0, y_area, color='#00FF00', alpha=0.25, label='Área Integrada')
                    area_val = ultimo_paso.get("valor", 0)
                    self.ax.set_title(f"{problema['titulo']}  |  Integral ≈ {area_val:.6f}", color="#00FF00")
                except Exception as e:
                    print(f"Error al sombrear área: {e}")
            else:
                x_interp = datos_ini.get("x_interpolar", datos_ini.get("x"))
                if x_interp is not None:
                    x_res = x_interp
                    y_res = ultimo_paso.get("valor", 0)
                    etiqueta_pt = "Interpolación"
                elif "xi" in datos_base and not funcion_str:
                    # Mínimos cuadrados sin función explícita
                    x_res, y_res = None, None
                else:
                    x_res = ultimo_paso.get("x_medio", ultimo_paso.get("valor", 0))
                    y_res = 0
                    etiqueta_pt = "Raíz / Falla"

                if x_res is not None:
                    self.ax.scatter([x_res], [y_res], color='red', s=150, marker='X', label=etiqueta_pt, zorder=6)
                    texto_coordenada = f"({x_res:.4f}, {y_res:.4f})"
                    self.ax.annotate(texto_coordenada, (x_res, y_res),
                                     textcoords="offset points", xytext=(10, 10), ha='left',
                                     fontsize=11, color='#00FF00', fontweight='bold',
                                     bbox=dict(boxstyle="round,pad=0.3", fc="#111111", ec="#00FF00", lw=1))

        # Añadir leyenda en la esquina superior derecha
        self.ax.legend(facecolor='#111111', edgecolor='gray', labelcolor='white', loc='upper right')