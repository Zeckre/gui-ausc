import customtkinter as ctk
import os
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from core import cargar_graficar_csv, fft_csv, dwt_csv, csv_to_wav

def TabAnalisis(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    selected_file = {"path": None}
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos de señal", "*.txt *.csv *.dat"), ("Todos", "*.*")]
        )
        if file_path:
            selected_file["path"] = file_path
            file_label.configure(text=os.path.basename(file_path))
            status_label.configure(text=f"Archivo seleccionado: {os.path.basename(file_path)}")

    def run_both_graphs():
        if not selected_file["path"]:
            status_label.configure(text="Error: seleccione un archivo primero")
            return

        try:
            # Limpiar placeholders
            for widget in g1_placeholder.winfo_children():
                widget.destroy()
            for widget in g2_placeholder.winfo_children():
                widget.destroy()

            # Gráfica original
            fig1 = cargar_graficar_csv.plot_g1(selected_file["path"])
            canvas1 = FigureCanvasTkAgg(fig1, master=g1_placeholder)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="top", fill="both", expand=True)
            toolbar1 = NavigationToolbar2Tk(canvas1, g1_placeholder)
            toolbar1.update()
            toolbar1.pack(side="top", fill="x")

            # FFT o Wavelet
            method = method_var.get()
            if method == "fft":
                fig2 = fft_csv.plot_fft(selected_file["path"])
            else:
                fig2 = dwt_csv.plot_wavelet(selected_file["path"])

            canvas2 = FigureCanvasTkAgg(fig2, master=g2_placeholder)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="top", fill="both", expand=True)
            toolbar2 = NavigationToolbar2Tk(canvas2, g2_placeholder)
            toolbar2.update()
            toolbar2.pack(side="top", fill="x")

            status_label.configure(text="Gráficas interactivas incrustadas")

        except Exception as e:
            status_label.configure(text=f"Error al generar gráficas: {e}")

    def play_signal():
        if not selected_file["path"]:
            status_label.configure(text="Error: seleccione un archivo primero")
            return

        try:
            wav_file = csv_to_wav.csv_to_wav(selected_file["path"])
            csv_to_wav.play_wav(wav_file)
            status_label.configure(text=f"Reproduciendo señal: {os.path.basename(wav_file)}")
        except Exception as e:
            status_label.configure(text=f"Error al reproducir: {e}")

    main_frame = ctk.CTkFrame(frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Columna derecha
    graphs_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    graphs_frame.pack(side="right", fill="both", expand=True)

    g1_placeholder = ctk.CTkFrame(graphs_frame, fg_color="white", height=200)
    g1_placeholder.pack(fill="both", expand=True, padx=12, pady=6)

    g2_placeholder = ctk.CTkFrame(graphs_frame, fg_color="white", height=200)
    g2_placeholder.pack(fill="both", expand=True, padx=12, pady=6)

    # Columna izquierda
    controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    controls_frame.pack(side="left", fill="y", padx=10)

    ctk.CTkLabel(controls_frame, text="Análisis de señales", font=(None, 18, "bold")).pack(pady=(8, 4), fill="x")

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

    return frame
