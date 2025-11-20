import customtkinter as ctk

# Compat helpers: algunas versiones de customtkinter no incluyen CTkTextbox o CTkComboBox
CTkTextboxClass = getattr(ctk, "CTkTextbox", None)
CTkComboBoxClass = getattr(ctk, "CTkComboBox", None)
import customtkinter as ctk


# Compat helpers: algunas versiones de customtkinter no incluyen CTkTextbox o CTkComboBox
CTkTextboxClass = getattr(ctk, "CTkTextbox", None)
CTkComboBoxClass = getattr(ctk, "CTkComboBox", None)
CTkOptionMenuClass = getattr(ctk, "CTkOptionMenu", None)


def create_textbox(parent, width=None, height=None):
    """Crear un widget editable o un fallback.

    - Si la versión de customtkinter provee `CTkTextbox` lo usa.
    - Si no, muestra una etiqueta informativa en su lugar.
    """
    if CTkTextboxClass:
        return CTkTextboxClass(parent, width=width, height=height)

    # Fallback: mostrar una etiqueta que indique que el editor no está disponible
    frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    label = ctk.CTkLabel(
        frame,
        text="(Editor de texto no disponible en esta versión)",
        wraplength=width or 400,
        text_color="#333333",
    )
    label.pack(fill="both", expand=True, padx=8, pady=8)
    return frame


class SimpleOptionWrapper(ctk.CTkFrame):
    """Un combo mínimo hecho solo con CTk: etiqueta + botón que cicla opciones.

    Esto evita depender de `tk.OptionMenu` o variables de tkinter en versiones antiguas.
    """

    def __init__(self, parent, values, width=None, default=None):
        super().__init__(parent, fg_color="transparent")
        self.values = values or []
        self.index = 0
        if default and default in self.values:
            self.index = self.values.index(default)

        # Etiqueta que muestra la opción actual
        self.label = ctk.CTkLabel(self, text=self.values[self.index] if self.values else "")
        self.label.pack(side="left", fill="x", expand=True)

        # Botón pequeño para avanzar a la siguiente opción
        self.btn = ctk.CTkButton(self, text="▼", width=30, command=self._next)
        self.btn.pack(side="right")

    def _next(self):
        """Avanza a la siguiente opción (cíclico)."""
        if not self.values:
            return
        self.index = (self.index + 1) % len(self.values)
        self.label.configure(text=self.values[self.index])

    def set(self, v):
        """Establece un valor si existe en la lista."""
        if v in self.values:
            self.index = self.values.index(v)
            self.label.configure(text=v)

    def get(self):
        """Retorna la opción actual."""
        return self.values[self.index] if self.values else ""


def create_combo(parent, values, width=None, default=None):
    """Crear un combo box o un fallback compatible con CTk.

    Prioriza `CTkComboBox` o `CTkOptionMenu` si existen; si no, usa `SimpleOptionWrapper`.
    """
    if CTkComboBoxClass:
        cb = CTkComboBoxClass(parent, values=values, width=width)
        if default:
            try:
                cb.set(default)
            except Exception:
                pass
        return cb

    if CTkOptionMenuClass:
        om = CTkOptionMenuClass(parent, values=values, width=width)
        if default:
            try:
                om.set(default)
            except Exception:
                pass
        return om

    return SimpleOptionWrapper(parent, values=values, width=width, default=default)


def get_tab_frame(parent, tab_name):
    """Devuelve un `CTkFrame` que contiene el contenido para la pestaña indicada.

    Separe la generación del contenido por pestaña para mantener la UI modular.
    """
    frame = ctk.CTkFrame(parent, corner_radius=10)

    if tab_name == "Tiempo Real":
        # Título y placeholder para el gráfico en tiempo real
        title = ctk.CTkLabel(frame, text="Señal en tiempo real", font=(None, 18, "bold"))
        title.pack(pady=(8, 4))

        container = ctk.CTkFrame(frame, fg_color="white", corner_radius=10)
        container.pack(fill="both", expand=False, padx=12, pady=6)
        placeholder = ctk.CTkLabel(container, text="Aquí irá el gráfico en tiempo real", text_color="#333333")
        placeholder.pack(padx=12, pady=24)

        # Botones de control de grabación
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)
        btn_record = ctk.CTkButton(btn_frame, text="Grabar", command=lambda: print("Grabando..."))
        btn_stop = ctk.CTkButton(btn_frame, text="Detener", command=lambda: print("Grabación detenida"))
        btn_save = ctk.CTkButton(btn_frame, text="Guardar señal", command=lambda: print("Grabación guardada"))
        btn_record.grid(row=0, column=0, padx=6)
        btn_stop.grid(row=0, column=1, padx=6)
        btn_save.grid(row=0, column=2, padx=6)

    elif tab_name == "Grabaciones":
        # Listado de grabaciones (placeholder)
        title = ctk.CTkLabel(frame, text="Señales guardadas", font=(None, 16, "bold"))
        title.pack(pady=(8, 4))
        info = ctk.CTkLabel(frame, text="Aquí se listarán las grabaciones con opciones de ver, eliminar y exportar.")
        info.pack(padx=12, pady=8)

    elif tab_name == "Comparar":
        # Dos paneles para comparar señales y un campo de observaciones
        title = ctk.CTkLabel(frame, text="Comparación de señales", font=(None, 16, "bold"))
        title.pack(pady=(8, 6))
        graphs = ctk.CTkFrame(frame, fg_color="transparent")
        graphs.pack(fill="x", padx=12)
        g1 = ctk.CTkFrame(graphs, fg_color="white", width=300, height=200, corner_radius=10)
        g2 = ctk.CTkFrame(graphs, fg_color="white", width=300, height=200, corner_radius=10)
        g1.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        g2.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        obs = create_textbox(frame, width=640, height=120)
        obs.pack(padx=12, pady=10)
        save_obs = ctk.CTkButton(frame, text="Guardar observaciones", command=lambda: print("Observaciones guardadas"))
        save_obs.pack(pady=(0, 8))

    elif tab_name == "Configuración":
        # Controles de configuración (modo oscuro y selección de idioma)
        title = ctk.CTkLabel(frame, text="Configuración", font=(None, 16, "bold"))
        title.pack(pady=(8, 6))

        # Switch: mantenemos el estado en una closure para no depender de tkinter.Variable
        dark_state = {"value": False}

        def switch_cmd():
            dark_state["value"] = not dark_state["value"]
            print("Modo oscuro:", dark_state["value"])

        switch = ctk.CTkSwitch(frame, text="Modo oscuro", command=switch_cmd)
        switch.pack(padx=12, pady=6)

        # Selector de idioma (fallback con SimpleOptionWrapper si no hay ComboBox)
        lang = create_combo(frame, values=["Español", "Inglés"], width=200, default="Español")
        try:
            lang.set("Español")
        except Exception:
            pass
        lang.pack(padx=12, pady=6)

    else:
        msg = ctk.CTkLabel(frame, text="Selecciona una pestaña")
        msg.pack(padx=12, pady=12)

    return frame
