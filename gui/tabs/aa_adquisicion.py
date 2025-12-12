import customtkinter as ctk
import os, sys, threading
from core import  adquirircsv

def TabAdquisicion(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    # Titulo de la ventana
    title = ctk.CTkLabel(frame, text="Adquirir de la DAQ", font=(None, 16, "bold"))
    title.pack(pady=(8, 6))

   # Para el log (registro)
    class RedirectText:
        def __init__(self, widget):
            self.widget = widget
        def write(self, string):
            self.widget.insert("end", string)
            self.widget.see("end")
        def flush(self):
            pass

    # Caja de logs
    log_box = ctk.CTkTextbox(frame, width=580, height=350)
    log_box.pack(padx=10, pady=10)
    sys.stdout = RedirectText(log_box)

    # Cantidad de muestras
    label_muestras = ctk.CTkLabel(frame, text="Cantidad de muestras:")
    label_muestras.pack(pady=(10, 0))

    entry_muestras = ctk.CTkEntry(frame, width=200, placeholder_text="Ej: 5000")
    entry_muestras.pack(pady=5)

    # Ruta de guardado
    label_path = ctk.CTkLabel(frame, text="Ruta de guardado:")
    label_path.pack(pady=(10, 0))

    entry_path = ctk.CTkEntry(frame, width=400, placeholder_text="Ej: /home/pi/Documents")
    entry_path.pack(pady=5)

    # Nombre del archivo
    label_nombre = ctk.CTkLabel(frame, text="Nombre del archivo:")
    label_nombre.pack(pady=(10, 0))

    entry_nombre = ctk.CTkEntry(frame, width=400, placeholder_text="Ej: datos_sesion")
    entry_nombre.pack(pady=5)
    
    # Para adquirir
    def ejecutar():
        try:
            cantidad = int(entry_muestras.get())
        except ValueError:
            print("Ingrese un número válido para las muestras.")
            return

        nombre = entry_nombre.get().strip()
        ruta = entry_path.get().strip()

        if ruta and nombre:
            archivo = os.path.join(ruta, nombre + ".csv")

            # Hilo para no congelar la GUI
            hilo = threading.Thread(target=lambda: adquisicion.adquirir_csv(cantidad, archivo))
            hilo.start()

            print(f"Archivo guardado en: {archivo}")
        else:
            print("Por favor ingresa ruta y nombre.")

    # Botón de iniciar
    btn = ctk.CTkButton(frame, text="Iniciar adquisición", command=ejecutar)
    btn.pack(pady=20)

    return frame
