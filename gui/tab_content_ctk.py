import customtkinter as ctk
import subprocess, os, sys, threading, sqlite3
from io import BytesIO
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from core import cargar_graficar_csv, fft_csv, dwt_csv, csv_to_wav
from gui.tabs.aa_adquisicion import TabAdquisicion
from gui.tabs.ab_analisis import TabAnalisis
from gui.tabs.ac_registro import TabRegistro
from gui.tabs.ad_prediccion import TabPrediccion
from gui.tabs.af_acerca_de import TabAcercaDe



# Compat helpers: algunas versiones de customtkinter no incluyen CTkTextbox o CTkComboBox
CTkTextboxClass = getattr(ctk, "CTkTextbox", None)
CTkComboBoxClass = getattr(ctk, "CTkComboBox", None)
CTkOptionMenuClass = getattr(ctk, "CTkOptionMenu", None)


def create_textbox(parent, width=None, height=None):
    # Crear un widget editable o un fallback.
    # - Si la versión de customtkinter provee `CTkTextbox` lo usa.
    # - Si no, muestra una etiqueta informativa en su lugar.
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
    # Un combo mínimo hecho solo con CTk: etiqueta + botón que cicla opciones.
    # Esto evita depender de `tk.OptionMenu` o variables de tkinter en versiones antiguas.

    def __init__(self, parent, values, width=None, default=None):
        super().__init__(parent, fg_color="transparent")
        self.values = values or []
        self.index = 0
        if default and default in self.values:
            self.index = self.values.index(default)

        # Etiqueta que muestra la opción actual
        self.label = ctk.CTkLabel(self, text=self.values[self.index] if self.values else "")
        self.label.pack(side="left", fill="x", expand=True)

    def _next(self):
        # Avanza a la siguiente opción (cíclico).
        if not self.values:
            return
        self.index = (self.index + 1) % len(self.values)
        self.label.configure(text=self.values[self.index])

    def set(self, v):
        # Establece un valor si existe en la lista.
        if v in self.values:
            self.index = self.values.index(v)
            self.label.configure(text=v)

    def get(self):
        # Retorna la opción actual.
        return self.values[self.index] if self.values else ""


def create_combo(parent, values, width=None, default=None):
    # Crear un combo box o un fallback compatible con CTk.
    # Prioriza `CTkComboBox` o `CTkOptionMenu` si existen; si no, usa `SimpleOptionWrapper`.
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
    # Devuelve un `CTkFrame` que contiene el contenido para la pestaña indicada.
    # Separe la generación del contenido por pestaña para mantener la UI modular.
    frame = ctk.CTkFrame(parent, corner_radius=10)

    if tab_name == "Predicción":
        TabPrediccion(frame).pack(expand=True, fill="both")
    
    elif tab_name == "Registro":
        TabRegistro(frame).pack(expand=True, fill="both")

    elif tab_name == "Acerca de":
       TabAcercaDe(frame).pack(expand=True, fill="both")

    elif tab_name == "Análisis":
        TabAnalisis(frame).pack(expand=True, fill="both")

    elif tab_name == "Adquisición":
       TabAdquisicion(frame).pack(expand=True, fill="both")

    else:
        msg = ctk.CTkLabel(frame, text="Selecciona una pestaña")
        msg.pack(padx=12, pady=12)

    return frame
