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


def create_combo(parent, values, width=None, default=None):
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
