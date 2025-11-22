import customtkinter as ctk
import subprocess, os, sys, threading
import adquirircsv as adquisicion
from io import BytesIO
from PIL import Image
import cargar_graficar_csv, fft_csv, dwt_csv, csv_to_wav

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

        # Botón pequeño para avanzar a la siguiente opción
        #self.btn = ctk.CTkButton(self, text="▼", width=30, command=self._next)
        #self.btn.pack(side="right")

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

    if tab_name == "Tiempo real":
        # Título y placeholder para el gráfico en tiempo real
        title = ctk.CTkLabel(frame, text="Señal en tiempo real", font=(None, 18, "bold"))
        title.pack(pady=(8, 4))

        container = ctk.CTkFrame(frame, fg_color="white", corner_radius=10)
        container.pack(fill="both", expand=True, padx=12, pady=6)

        # Diccionario para guardar el proceso en ejecución (si existe)
        live_proc = {"p": None}

        # Ruta del script externo que se quiere lanzar
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live-signal.py")
        #script_path = "live-signal.py"

        # Función auxiliar para actualizar el texto del label de estado
        def update_status(label, text):
            label.configure(text=text)   # Cambia el texto mostrado en la GUI
            print(text)                  # También imprime en consola para depuración

        # Función principal que controla el proceso (start/stop)
        def control_plot(action, label):
            p = live_proc.get("p")       # Obtiene el proceso actual (si existe)
            if action == "start":
                # Si ya hay un proceso corriendo, no lanza otro
                if p and p.poll() is None:
                    update_status(label, "Estado: corriendo")
                    return

                # Verifica que el script exista en la ruta indicada
                if not os.path.exists(script_path):
                    update_status(label, "Error: script no encontrado")
                    return

                try:
                    # Construye el comando usando el mismo intérprete de Python
                    cmd = [sys.executable, script_path]

                    # Lanza el proceso en segundo plano (independiente del GUI)
                    live_proc["p"] = subprocess.Popen(cmd, cwd=os.path.dirname(script_path))

                    # Actualiza el estado en la interfaz
                    update_status(label, "Estado: corriendo")
                except Exception as e:
                    # Si hay error al lanzar el script, lo muestra
                    update_status(label, f"Error: {e}")

            elif action == "stop":
                # Si no hay proceso, simplemente marca como detenido
                if not p:
                    update_status(label, "Estado: detenido")
                    return

                try:
                    # Si el proceso sigue vivo, lo termina de forma ordenada
                    if p.poll() is None:
                        p.terminate()
                        p.wait(timeout=2)   # Espera hasta 2 segundos a que termine
                        print("live-signal terminated")
                except Exception:
                    # Si no se pudo terminar, intenta forzar con kill()
                    try:
                        p.kill()
                    except:
                        pass
                finally:
                    # Limpia la referencia y actualiza estado
                    live_proc["p"] = None
                    update_status(label, "Estado: detenido")

        # Frame contenedor para los botones de visualización
        vis_frame = ctk.CTkFrame(frame, fg_color="transparent")
        vis_frame.pack(pady=6)

        # Label que muestra el estado actual del proceso
        status_label = ctk.CTkLabel(vis_frame, text="Estado: detenido")
        status_label.grid(row=0, column=2, padx=8)

        # Botón para iniciar el proceso (mostrar gráfica)
        btn_show = ctk.CTkButton(
            vis_frame, text="Mostrar gráfica",
            command=lambda: control_plot("start", status_label)
        ).grid(row=0, column=0, padx=6)

        # Botón para detener el proceso (parar gráfica)
        btn_stop = ctk.CTkButton(
            vis_frame, text="Parar gráfica",
            command=lambda: control_plot("stop", status_label)
        ).grid(row=0, column=1, padx=6)

    elif tab_name == "Registro":
        # Listado de grabaciones (placeholder)
        title = ctk.CTkLabel(frame, text="Señales guardadas", font=(None, 18, "bold"))
        title.pack(pady=(8, 4))
        info = ctk.CTkLabel(frame, text="Aquí se listarán las grabaciones con opciones de ver, eliminar y exportar.")
        info.pack(padx=12, pady=8)

    elif tab_name == "Acerca de":
        # Listado de grabaciones (placeholder)
        title = ctk.CTkLabel(frame, text="Acerca de este proyecto", font=(None, 18, "bold"))
        title.pack(pady=(8, 4))
        info = ctk.CTkLabel(frame, text="Este proyecto es el resultado de un proyecto de final de carrera del programa de " \
        "Ingeniería Electrónica; \n es la interfaz gráfica de usuario (GUI) para la DAQ desarrollada para procesos de auscultación " \
        "pulmonar.", font=(None, 20))
        info.pack(padx=16, pady=8)
        info2 = ctk.CTkLabel(frame, text="Titulo del proyecto:", font=(None, 26, "italic"))
        info2.pack(padx=16, pady=8)
        info3 = ctk.CTkLabel(frame, text="Desarrollo de una interfaz didáctica para \n el análisis en procesos de " \
        "auscultación \n pulmonar mediante la adquisción de \n señales con Raspberri PI", font=(None, 32, "italic", "bold"))
        info3.pack(padx=32, pady=32)
        info4 = ctk.CTkLabel(frame, text="Desarrollado por:\nDuván Antonio Rico Cacua\nZeckre", font=(None, 20))
        info4.pack(padx=16, pady=8)
        info5 = ctk.CTkLabel(frame, text="Programa de Ingeniería Electrónica\n Facultad de Ingenierías y" \
        "Arquitectura\nUniversidad de Pamplona, Colombia\n 2025-2", font=(None, 20))
        info5.pack(padx=16, pady=8)

    elif tab_name == "Análisis":
        selected_file = {"path": None}

        # --- Funciones auxiliares ---
        def fig_to_ctkimage(fig, size=(1000,350)):
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=100)
            buf.seek(0)
            pil_img = Image.open(buf)
            return ctk.CTkImage(light_image=pil_img, size=size)

        def update_placeholder(placeholder, img):
            for widget in placeholder.winfo_children():
                widget.destroy()
            lbl = ctk.CTkLabel(placeholder, image=img, text="")
            lbl.pack(fill="both", expand=True)

        # --- Funciones principales ---
        def select_file():
            file_path = ctk.filedialog.askopenfilename(
                title="Seleccionar archivo",
                filetypes=[("Archivos de señal", "*.txt *.csv *.dat"), ("Todos", "*.*")]
            )
            if file_path:
                selected_file["path"] = file_path
                file_label.configure(text=os.path.basename(file_path))
                status_label.configure(text=f"Archivo seleccionado: {os.path.basename(file_path)}")

        def run_both_graphs():
            if not selected_file["path"]:
                return status_label.configure(text="Error: seleccione un archivo primero")
            try:
                # g1
                fig1 = cargar_graficar_csv.plot_g1(selected_file["path"])
                img1 = fig_to_ctkimage(fig1)
                update_placeholder(g1_placeholder, img1)

                # g2 según método
                method = method_var.get()
                if method == "fft":
                    fig2 = fft_csv.plot_fft(selected_file["path"])
                else:
                    fig2 = dwt_csv.plot_wavelet(selected_file["path"])
                img2 = fig_to_ctkimage(fig2)
                update_placeholder(g2_placeholder, img2)

                status_label.configure(text="Gráficas g1 y g2 incrustadas")
            except Exception as e:
                status_label.configure(text=f"Error al generar gráficas: {e}")

        def play_signal():
            if not selected_file["path"]:
                return status_label.configure(text="Error: seleccione un archivo primero")
            try:
                # Generar el archivo WAV en la misma ruta y con el mismo nombre base
                wav_file = csv_to_wav.csv_to_wav(selected_file["path"])

                # Reproducirlo en segundo plano (no bloquea la GUI)
                csv_to_wav.play_wav(wav_file)

                status_label.configure(text=f"Reproduciendo señal: {os.path.basename(wav_file)}")
            except Exception as e:
                status_label.configure(text=f"Error al reproducir: {e}")

        # Controles de la pestaña
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(pady=6, fill="x")

        btn_file = ctk.CTkButton(top_frame, text="Seleccionar archivo", command=select_file)
        btn_file.pack(side="left", padx=6)
        file_label = ctk.CTkLabel(top_frame, text="Ningún archivo seleccionado", text_color="#333333")
        file_label.pack(side="left", padx=6)

        method_var = ctk.StringVar(value="fft")
        ctk.CTkRadioButton(top_frame, text="FFT", variable=method_var, value="fft").pack(side="left", padx=6)
        ctk.CTkRadioButton(top_frame, text="Wavelet", variable=method_var, value="wavelet").pack(side="left", padx=6)

        btn_run = ctk.CTkButton(top_frame, text="Generar gráficas g1 y g2", command=run_both_graphs)
        btn_run.pack(side="left", padx=6)

        btn_audio = ctk.CTkButton(top_frame, text="Escuchar señal", command=play_signal)
        btn_audio.pack(side="left", padx=6)

        # Placeholders verticales
        g1_placeholder = ctk.CTkFrame(frame, fg_color="white", height=300)
        g1_placeholder.pack(fill="both", expand=True, padx=12, pady=6)
        g2_placeholder = ctk.CTkFrame(frame, fg_color="white", height=200)
        g2_placeholder.pack(fill="both", expand=True, padx=12, pady=6)

        status_label = ctk.CTkLabel(frame, text="Seleccione un archivo para comenzar", text_color="#333333")
        status_label.pack(pady=6)

    elif tab_name == "Adquisición":
        # Controles de adquisción de la señal
        title = ctk.CTkLabel(frame, text="Adquirir de la DAQ", font=(None, 16, "bold"))
        title.pack(pady=(8, 6))

        # Switch: mantenemos el estado en una closure para no depender de tkinter.Variable
        dark_state = {"value": False}

        # Clase para redirigir la salida estándar (print) a un Textbox
        class RedirectText(object):
            def __init__(self, widget):
                self.widget = widget
            def write(self, string):
                # Insertar texto en el widget
                self.widget.insert("end", string)
                # Hacer scroll automático al final
                self.widget.see("end")
            def flush(self):
                # Necesario para compatibilidad con sys.stdout
                pass

        # Selector de ruta, nombre de archivo y botón para guardar
        # Crear un CTkTextbox para mostrar logs
        log_box = ctk.CTkTextbox(frame, width=580, height=350)
        log_box.pack(padx=10, pady=10)
        sys.stdout = RedirectText(log_box)

        # Entrada para cantidad de muestras
        label_muestras = ctk.CTkLabel(frame, text="Cantidad de muestras:")
        label_muestras.pack(pady=(10,0))
        entry_muestras = ctk.CTkEntry(frame, width=200, placeholder_text="Ej: 5000")
        entry_muestras.pack(pady=5)

        # Campo para ruta
        label_path = ctk.CTkLabel(frame, text="Ruta de guardado:")
        label_path.pack(pady=(10,0))
        entry_path = ctk.CTkEntry(frame, width=400, placeholder_text="Ej: /home/pi/Documents")
        entry_path.pack(pady=5)

        # Campo para nombre de archivo
        label_nombre = ctk.CTkLabel(frame, text="Nombre del archivo:")
        label_nombre.pack(pady=(10,0))
        entry_nombre = ctk.CTkEntry(frame, width=400, placeholder_text="Ej: datos_sesion")
        entry_nombre.pack(pady=5)

        # Botón para ejecutar adquisición
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
                hilo = threading.Thread(target=lambda: adquisicion.adquirir_csv(cantidad, archivo))
                hilo.start()
                print(f"Archivo guardado en: {archivo}")
            else:
                print("Por favor ingresa ruta y nombre.")
        btn = ctk.CTkButton(frame, text="Iniciar adquisición", command=ejecutar)
        btn.pack(pady=20)

    else:
        msg = ctk.CTkLabel(frame, text="Selecciona una pestaña")
        msg.pack(padx=12, pady=12)

    return frame
