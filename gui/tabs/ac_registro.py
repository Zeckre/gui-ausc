import customtkinter as ctk
import sqlite3, os
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from core import cargar_graficar_csv


def TabRegistro(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    base_dir  = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "data", "usuarios.db")

    # ------------------------------
    # Función auxiliar para limpiar frames
    # ------------------------------
    def clear_frame_safe(f):
        if f and f.winfo_exists():
            for w in f.winfo_children():
                w.destroy()

    # ------------------------------
    # Estructura principal
    # ------------------------------
    registro_frame = ctk.CTkFrame(frame, fg_color="transparent")
    registro_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Columna izquierda (formulario)
    form_frame = ctk.CTkFrame(registro_frame, fg_color="transparent")
    form_frame.pack(side="left", fill="y", padx=10)

    ctk.CTkLabel(form_frame, text="Registro de Usuario", font=(None, 18, "bold")).pack(pady=(8, 4), fill="x")

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

    # ------------------------------
    # Seleccionar señales
    # ------------------------------
    def select_signals():
        files = filedialog.askopenfilenames(
            title="Seleccionar señales",
            filetypes=[("Archivos de señal", "*.csv *.txt *.dat"), ("Todos", "*.*")]
        )
        if files:
            selected_signals.clear()
            selected_signals.extend(files)
            signals_label.configure(text=f"{len(files)} señales seleccionadas")

            # Limpiar vista previa
            clear_frame_safe(preview_frame)

            # Graficar primera señal
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

    ctk.CTkButton(form_frame, text="Seleccionar señales", command=select_signals).pack(pady=4, fill="x")
    signals_label = ctk.CTkLabel(form_frame, text="Ninguna señal seleccionada", text_color="#333333")
    signals_label.pack(pady=4, fill="x")

    # ------------------------------
    # Guardar en base de datos
    # ------------------------------
    def save_to_db():
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        edad = entry_edad.get()
        correo = entry_correo.get()
        nit = entry_nit.get()

        if not nombre or not apellido or not edad or not correo or not nit or not selected_signals:
            status_label.configure(text="Error: complete todos los campos y seleccione señales")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

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

            cursor.execute("SELECT nit FROM registro WHERE nit = ?", (nit,))
            existe = cursor.fetchone()

            if not existe:
                cursor.execute("INSERT INTO registro (nit, nombre, apellido, edad, correo) VALUES (?, ?, ?, ?, ?)",
                               (nit, nombre, apellido, edad, correo))

            for archivo in selected_signals:
                cursor.execute("INSERT INTO señales (nit, archivo) VALUES (?, ?)", (nit, archivo))

            conn.commit()
            conn.close()
            status_label.configure(text="Datos guardados correctamente")

        except Exception as e:
            status_label.configure(text=f"Error al guardar: {e}")

    ctk.CTkButton(form_frame, text="Guardar en base de datos", command=save_to_db).pack(pady=10, fill="x")

    # ------------------------------
    # Búsqueda por NIT
    # ------------------------------
    entry_search_nit = ctk.CTkEntry(form_frame, placeholder_text="Buscar por NIT")
    entry_search_nit.pack(pady=4, fill="x")

    # ------------------------------
    # Vista previa derecha
    # ------------------------------
    preview_frame = ctk.CTkFrame(registro_frame, fg_color="white")
    preview_frame.pack(side="left", fill="both", expand=True, padx=12, pady=6)

    ctk.CTkLabel(preview_frame, text="Vista previa de usuario y señales", font=(None, 14, "bold")).pack(pady=6)

    user_info_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
    user_info_frame.pack(fill="x", pady=6)

    selector_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
    selector_frame.pack(fill="x", pady=6)

    graph_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
    graph_frame.pack(fill="both", expand=True, pady=6)

    # ------------------------------
    # Buscar usuario por NIT
    # ------------------------------
    def search_by_nit():
        nit = entry_search_nit.get()
        if not nit:
            status_label.configure(text="Ingrese un NIT para buscar")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT nombre, apellido, edad, correo FROM registro WHERE nit = ?", (nit,))
            usuario = cursor.fetchone()

            clear_frame_safe(user_info_frame)
            clear_frame_safe(selector_frame)
            clear_frame_safe(graph_frame)

            if usuario:
                nombre, apellido, edad, correo = usuario

                ctk.CTkLabel(user_info_frame, text=f"Usuario: {nombre} {apellido}", font=(None, 14, "bold")).pack(anchor="w")
                ctk.CTkLabel(user_info_frame, text=f"Edad: {edad}").pack(anchor="w")
                ctk.CTkLabel(user_info_frame, text=f"Correo: {correo}").pack(anchor="w")

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

                    mostrar_señal(archivos[0])
                else:
                    ctk.CTkLabel(graph_frame, text="No hay señales asociadas", text_color="red").pack()

            else:
                ctk.CTkLabel(graph_frame, text="NIT no encontrado", text_color="red").pack()

            conn.close()

        except Exception as e:
            status_label.configure(text=f"Error en la búsqueda: {e}")

    ctk.CTkButton(form_frame, text="Buscar", command=search_by_nit).pack(pady=4, fill="x")

    status_label = ctk.CTkLabel(form_frame, text="Complete el formulario y seleccione señales", text_color="#333333")
    status_label.pack(pady=6, fill="x")

    return frame
