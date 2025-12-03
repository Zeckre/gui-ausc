import customtkinter as ctk
from datetime import datetime
from tab_content_ctk import get_tab_frame
from check_i2c import check_i2c_device
from footer_ctk import create_footer
import os

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None


def _load_image(path, size=None):
    # Cargar una imagen desde el disco y devolver un objeto de imagen compatible con CTk.
    img = Image.open(path)
    if size:
        img = img.resize(size, Image.LANCZOS)
    # Intentar cargar la imagen para tantallas normales y de alta resolución
    if hasattr(ctk, "CTkImage"):
        try:
            return ctk.CTkImage(light_image=img, size=size)
        except Exception:
            pass
    return ImageTk.PhotoImage(img)

def main():
    # Configuración inicial de CTk
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Crear la ventana principal
    root = ctk.CTk()
    root.title("BioMonitor - Estetoscopio Digital")
    root.geometry("2120x1180")
    root.grid_columnconfigure(0, weight=1)
    # Hacer que la fila de la vista de pestañas sea expandible para
    # que el contenido de las pestañas ocupe todo el espacio disponible.
    root.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(root, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
    header.grid_columnconfigure(1, weight=1)

    # Cargamos las imagenes en variables
    left_img = _load_image("escudounipamplona.png", size=(90, 90))
    right_img = _load_image("siibtel_logo.png", size=(90, 90))

    # posición de la imagen izquierda
    if left_img:
        lbl_left = ctk.CTkLabel(header, image=left_img, text="")
    else:
        lbl_left = ctk.CTkLabel(header, text="[Logo]")
    lbl_left.grid(row=0, column=0, sticky="w")

    # título y subtítulo en el centro del header
    title_frame = ctk.CTkFrame(header, fg_color="transparent")
    title_frame.grid(row=0, column=1, sticky="ew")
    title_frame.grid_columnconfigure(0, weight=1)
    title = ctk.CTkLabel(title_frame, text="Auscultation Monitor", font=(None, 26, "bold"), text_color="#03045E")
    subtitle = ctk.CTkLabel(title_frame, text="Sistema de monitoreo estetoscopio digital", font=(None, 20), text_color="#0077B6")
    title.pack(anchor="center")
    subtitle.pack(anchor="center")

    # posición de la imagen derecha
    if right_img:
        lbl_right = ctk.CTkLabel(header, image=right_img, text="")
    else:
        lbl_right = ctk.CTkLabel(header, text="[Sponsor]")
    lbl_right.grid(row=0, column=2, sticky="e")

    # Pestañas (hacer que la vista de pestañas se expanda verticalmente)
    tabview = ctk.CTkTabview(root, width=1000)
    tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(14, 0))
    tab_names = ["Adquisición", "Análisis", "Registro", "Tiempo real", "Acerca de"]
    for name in tab_names:
        tabview.add(name)

    # Coloca el contenido de cada pestaña dentro de su propio marco de pestaña
    # para que el tamaño se ajuste a la vista de pestañas.
    for name in tab_names:
        container = tabview.tab(name)
        # permitir que el contenedor se expanda
        try:
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
        except Exception:
            pass
        frame = get_tab_frame(container, name)
        frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)

    # FOOTER: delegar la creación y actualización al módulo `footer_ctk`.
    # `create_footer` añadirá el frame al `root` y arrancará su propio loop de actualización.
    create_footer(root, check_i2c_device)
    root.mainloop()

if __name__ == "__main__":
    main()
