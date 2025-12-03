import customtkinter as ctk
import subprocess, os, sys, threading, sqlite3
import adquirircsv as adquisicion
from io import BytesIO
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
        # Función auxiliar para limpiar un frame si existe
        def clear_frame_safe(frame):
            if frame and frame.winfo_exists():
                for w in frame.winfo_children():
                    w.destroy()

        registro_frame = ctk.CTkFrame(frame, fg_color="transparent")
        registro_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Columna izquierda: formulario ---
        form_frame = ctk.CTkFrame(registro_frame, fg_color="transparent")
        form_frame.pack(side="left", fill="y", padx=10)

        title = ctk.CTkLabel(form_frame, text="Registro de Usuario", font=(None, 18, "bold"))
        title.pack(pady=(8, 4), fill="x")

        entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombres")
        entry_nombre.pack(pady=4, fill="x")
        
        entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellidos")
        entry_apellido.pack(pady=4, fill="x")
                
        entry_nit = ctk.CTkEntry(form_frame, placeholder_text="NIT")
        entry_nit.pack(pady=4, fill="x")

        entry_edad = ctk.CTkEntry(form_frame, placeholder_text="Edad")
        entry_edad.pack(pady=4, fill="x")

        entry_correo = ctk.CTkEntry(form_frame, placeholder_text="Correo electrónico")
        entry_correo.pack(pady=4, fill="x")

        selected_signals = []

        def select_signals():
            files = ctk.filedialog.askopenfilenames(
                title="Seleccionar señales",
                filetypes=[("Archivos de señal", "*.csv *.txt *.dat"), ("Todos", "*.*")]
            )
            if files:
                selected_signals.clear()
                selected_signals.extend(files)
                signals_label.configure(text=f"{len(files)} señales seleccionadas")

                # Limpiar vista previa antes de actualizar
                for widget in preview_frame.winfo_children():
                        widget.destroy()

                # Graficar solo la primera señal
                archivo = selected_signals[0]
                try:
                    fig = cargar_graficar_csv.plot_g1(archivo)

                    canvas = FigureCanvasTkAgg(fig, master=preview_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

                    toolbar = NavigationToolbar2Tk(canvas, preview_frame)
                    toolbar.update()
                    toolbar.pack(side="top", fill="x")

                except Exception as e:
                    ctk.CTkLabel(preview_frame, text=f"Error al graficar {archivo}: {e}", text_color="red").pack()


        btn_signals = ctk.CTkButton(form_frame, text="Seleccionar señales", command=select_signals)
        btn_signals.pack(pady=4, fill="x")

        signals_label = ctk.CTkLabel(form_frame, text="Ninguna señal seleccionada", text_color="#333333")
        signals_label.pack(pady=4, fill="x")

        def save_to_db():
            nombre = entry_nombre.get()
            edad = entry_edad.get()
            apellido = entry_apellido.get()
            correo = entry_correo.get()
            nit = entry_nit.get()

            if not nombre or not apellido or not edad or not correo or not nit or not selected_signals:
                status_label.configure(text="Error: complete todos los campos y seleccione señales")
                return

            try:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()

                # Crear tablas si no existen
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registro (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nit INTEGER,
                        nombre TEXT,
                        apellido TEXT,
                        edad INTEGER,
                        correo TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS señales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nit TEXT,
                        archivo TEXT,
                        FOREIGN KEY (nit) REFERENCES registro(nit)
                    )
                """)

                # Verificar si el NIT ya existe
                cursor.execute("SELECT nit FROM registro WHERE nit = ?", (nit,))
                existe = cursor.fetchone()

                if not existe:
                    cursor.execute("INSERT INTO registro (nit, nombre, apellido, edad, correo) VALUES (?, ?, ?, ?, ?)",
                                (nit, nombre, apellido, edad, correo))

                # Insertar señales asociadas
                for archivo in selected_signals:
                    cursor.execute("INSERT INTO señales (nit, archivo) VALUES (?, ?)", (nit, archivo))

                conn.commit()
                conn.close()
                status_label.configure(text="Datos guardados correctamente en la base de datos")
            except Exception as e:
                status_label.configure(text=f"Error al guardar: {e}")

        btn_save = ctk.CTkButton(form_frame, text="Guardar en base de datos", command=save_to_db)
        btn_save.pack(pady=10, fill="x")

        # Buscador por NIT
        entry_search_nit = ctk.CTkEntry(form_frame, placeholder_text="Buscar por NIT")
        entry_search_nit.pack(pady=4, fill="x")

        preview_frame = ctk.CTkFrame(registro_frame, fg_color="white")
        preview_frame.pack(side="left", fill="both", expand=True, padx=12, pady=6)

        preview_label = ctk.CTkLabel(preview_frame, text="Vista previa de usuario y señales", font=(None, 14, "bold"))
        preview_label.pack(pady=6)
        
        # Subframes
        user_info_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        user_info_frame.pack(fill="x", pady=6)

        selector_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        selector_frame.pack(fill="x", pady=6)

        graph_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        graph_frame.pack(fill="both", expand=True, pady=6)

        def search_by_nit():
            nit = entry_search_nit.get()
            if not nit:
                status_label.configure(text="Ingrese un NIT para buscar")
                return

            try:
                import sqlite3
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()

                # Buscar usuario
                cursor.execute("SELECT nombre, edad, correo FROM registro WHERE nit = ?", (nit,))
                usuario = cursor.fetchone()

                # Limpiar solo si los subframes existen
                clear_frame_safe(user_info_frame)
                clear_frame_safe(selector_frame)
                clear_frame_safe(graph_frame)

                if usuario:
                    nombre, edad, correo = usuario
                    ctk.CTkLabel(user_info_frame, text=f"Usuario: {nombre}", font=(None, 14, "bold")).pack(anchor="w")
                    ctk.CTkLabel(user_info_frame, text=f"Edad: {edad}").pack(anchor="w")
                    ctk.CTkLabel(user_info_frame, text=f"Correo: {correo}").pack(anchor="w")

                    # Buscar señales asociadas
                    cursor.execute("SELECT archivo FROM señales WHERE nit = ?", (nit,))
                    archivos = [a[0] for a in cursor.fetchall()]

                    if archivos:
                        def mostrar_señal(archivo):
                            clear_frame_safe(graph_frame)
                            try:
                                fig = cargar_graficar_csv.plot_g1(archivo)
                                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                                canvas.draw()
                                canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

                                toolbar = NavigationToolbar2Tk(canvas, graph_frame)
                                toolbar.update()
                                toolbar.pack(side="top", fill="x")
                            except Exception as e:
                                ctk.CTkLabel(graph_frame, text=f"Error al graficar {archivo}: {e}", text_color="red").pack()

                        selector = ctk.CTkOptionMenu(selector_frame, values=archivos, command=mostrar_señal)
                        selector.pack(fill="x", pady=4)

                        # Mostrar la primera señal por defecto
                        mostrar_señal(archivos[0])
                    else:
                        ctk.CTkLabel(graph_frame, text="No hay señales asociadas a este NIT", text_color="red").pack()
                else:
                    ctk.CTkLabel(graph_frame, text="NIT no encontrado en la base de datos", text_color="red").pack()

                conn.close()
            except Exception as e:
                status_label.configure(text=f"Error en la búsqueda: {e}")


        btn_search = ctk.CTkButton(form_frame, text="Buscar", command=search_by_nit)
        btn_search.pack(pady=4, fill="x")

        status_label = ctk.CTkLabel(form_frame, text="Complete el formulario y seleccione señales", text_color="#333333")
        status_label.pack(pady=6, fill="x")


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
        #title = ctk.CTkLabel(frame, text="Análisis de señales", font=(None, 18, "bold"))
        #title.pack(pady=(8, 4))

        selected_file = {"path": None}

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
                # Limpiar placeholders
                for widget in g1_placeholder.winfo_children():
                    widget.destroy()
                for widget in g2_placeholder.winfo_children():
                    widget.destroy()

                # g1
                fig1 = cargar_graficar_csv.plot_g1(selected_file["path"])
                canvas1 = FigureCanvasTkAgg(fig1, master=g1_placeholder)
                canvas1.draw()
                canvas1.get_tk_widget().pack(side="top", fill="both", expand=True)
                canvas1.get_tk_widget().configure(width=400, height=330)  
                toolbar1 = NavigationToolbar2Tk(canvas1, g1_placeholder)
                toolbar1.update()
                toolbar1.pack(side="top", fill="x")

                # g2 según método
                method = method_var.get()
                if method == "fft":
                    fig2 = fft_csv.plot_fft(selected_file["path"])
                else:
                    fig2 = dwt_csv.plot_wavelet(selected_file["path"])

                canvas2 = FigureCanvasTkAgg(fig2, master=g2_placeholder)
                canvas2.draw()
                canvas2.get_tk_widget().pack(side="top", fill="both", expand=True)
                canvas2.get_tk_widget().configure(width=400, height=330)  
                toolbar2 = NavigationToolbar2Tk(canvas2, g2_placeholder)
                toolbar2.update()
                toolbar2.pack(side="top", fill="x")

                status_label.configure(text="Gráficas interactivas incrustadas")
            except Exception as e:
                status_label.configure(text=f"Error al generar gráficas: {e}")

        def play_signal():
            if not selected_file["path"]:
                return status_label.configure(text="Error: seleccione un archivo primero")
            try:
                wav_file = csv_to_wav.csv_to_wav(selected_file["path"])
                csv_to_wav.play_wav(wav_file)
                status_label.configure(text=f"Reproduciendo señal: {os.path.basename(wav_file)}")
            except Exception as e:
                status_label.configure(text=f"Error al reproducir: {e}")

        # --- Layout principal: gráficas a la izquierda, controles a la derecha ---
        main_frame = ctk.CTkFrame(frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Columna izquierda con gráficas
        graphs_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        graphs_frame.pack(side="right", fill="both", expand=True)

        g1_placeholder = ctk.CTkFrame(graphs_frame, fg_color="white", height=200)
        g1_placeholder.pack(fill="both", expand=True, padx=12, pady=6)

        g2_placeholder = ctk.CTkFrame(graphs_frame, fg_color="white", height=200)
        g2_placeholder.pack(fill="both", expand=True, padx=12, pady=6)

        # Columna derecha con controles en vertical
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(side="left", fill="y", padx=10)
        
        title = ctk.CTkLabel(controls_frame, text="Análisis de señales", font=(None, 18, "bold"))
        title.pack(pady=(8, 4), fill="x")

        btn_file = ctk.CTkButton(controls_frame, text="Seleccionar archivo", command=select_file)
        btn_file.pack(pady=4, fill="x")

        file_label = ctk.CTkLabel(controls_frame, text="Ningún archivo seleccionado", text_color="#333333")
        file_label.pack(pady=4, fill="x")

        method_var = ctk.StringVar(value="fft")
        ctk.CTkRadioButton(controls_frame, text="FFT", variable=method_var, value="fft").pack(pady=4, fill="x")
        ctk.CTkRadioButton(controls_frame, text="Wavelet", variable=method_var, value="wavelet").pack(pady=4, fill="x")

        btn_run = ctk.CTkButton(controls_frame, text="Iniciar", command=run_both_graphs)
        btn_run.pack(pady=4, fill="x")

        btn_audio = ctk.CTkButton(controls_frame, text="Escuchar señal", command=play_signal)
        btn_audio.pack(pady=4, fill="x")

        status_label = ctk.CTkLabel(controls_frame, text="Seleccione un archivo para comenzar", text_color="#333333")
        status_label.pack(pady=10, fill="x")

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
