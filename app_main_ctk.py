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
    # Try the path as given first
    if not Image:
        print("Pillow not installed: cannot load images (PIL missing)")
        return None

    # If path doesn't exist, also try relative to this script directory
    tried_paths = [path]
    if not os.path.exists(path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt = os.path.join(script_dir, path)
        tried_paths.append(alt)
        if os.path.exists(alt):
            path = alt
    if not os.path.exists(path):
        print(f"_load_image: file not found. Tried: {tried_paths}")
        return None

    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        # Prefer CTkImage for proper scaling on HighDPI displays
        if hasattr(ctk, "CTkImage"):
            try:
                return ctk.CTkImage(light_image=img, size=size)
            except Exception:
                pass
        return ImageTk.PhotoImage(img)
    except Exception:
        import traceback
        print(f"_load_image: failed to open/process image '{path}'")
        traceback.print_exc()
        return None


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("BioMonitor - Estetoscopio Digital")
    root.geometry("1100x700")
    root.grid_columnconfigure(0, weight=1)
    # make the tabview row expandable so tab content fills available space
    root.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(root, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
    header.grid_columnconfigure(1, weight=1)

    left_img = _load_image("escudounipamplona.png", size=(90, 90))
    right_img = _load_image("siibtel_logo.png", size=(90, 90))

    if left_img:
        lbl_left = ctk.CTkLabel(header, image=left_img, text="")
    else:
        lbl_left = ctk.CTkLabel(header, text="[Logo]")
    lbl_left.grid(row=0, column=0, sticky="w")

    title_frame = ctk.CTkFrame(header, fg_color="transparent")
    title_frame.grid(row=0, column=1, sticky="ew")
    title_frame.grid_columnconfigure(0, weight=1)
    title = ctk.CTkLabel(title_frame, text="Auscultation Monitor", font=(None, 26, "bold"), text_color="#03045E")
    subtitle = ctk.CTkLabel(title_frame, text="Sistema de monitoreo estetoscopio digital", font=(None, 20), text_color="#0077B6")
    title.pack(anchor="center")
    subtitle.pack(anchor="center")

    if right_img:
        lbl_right = ctk.CTkLabel(header, image=right_img, text="")
    else:
        lbl_right = ctk.CTkLabel(header, text="[Sponsor]")
    lbl_right.grid(row=0, column=2, sticky="e")

    # Tabs (let tabview expand vertically)
    tabview = ctk.CTkTabview(root, width=1000)
    tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(14, 0))
    tab_names = ["Tiempo Real", "Grabaciones", "Comparar", "Configuración"]
    for name in tab_names:
        tabview.add(name)

    # Put each tab's content inside its own tab frame so sizing follows the tabview
    for name in tab_names:
        container = tabview.tab(name)
        # allow the container to expand
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
