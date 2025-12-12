import customtkinter as ctk
from tkinter import filedialog
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.predict import predict_audio
from core import cargar_graficar_csv, fft_csv, dwt_csv

def TabPrediccion(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Variables internas
    audio_path = {"path": None}
    user_choice = ctk.StringVar(value="Healthy")
    canvas_cm = {"widget": None}
    main_frame = ctk.CTkFrame(frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Columna izquierda
    left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    # Columna derecha 
    right_frame = ctk.CTkFrame(main_frame, fg_color="white")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    cm_frame = right_frame
    
    def seleccionar_archivo():
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            audio_path["path"] = path
            label_ruta.configure(text=path)

    def reproducir_audio():
        if not audio_path["path"]:
            label_resultado.configure(text="Selecciona un archivo primero")
            return
        data, fs = sf.read(audio_path["path"])
        sd.play(data, fs)

    def iniciar_prediccion():
        if not audio_path["path"]:
            label_resultado.configure(text="Selecciona un archivo primero")
            return
        pred = predict_audio(audio_path["path"])
        user = user_choice.get()
        if pred == user:
            label_resultado.configure(text=f"Correcto: El modelo también predijo {pred}")
        else:
            label_resultado.configure(text=f"Incorrecto: El modelo predijo {pred}")
        mostrar_matriz_confusion(user, pred)

    def mostrar_matriz_confusion(user, pred):
        etiquetas = ["Healthy", "COPD"]
        cm = np.zeros((2, 2), dtype=int)
        cm[etiquetas.index(user), etiquetas.index(pred)] = 1
        # Limpiar matriz anterior
        for widget in cm_frame.winfo_children():
            widget.destroy()
        # Crear figura
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=etiquetas, yticklabels=etiquetas, ax=ax)
        ax.set_xlabel("Predicción del modelo")
        ax.set_ylabel("Tu elección")
        ax.set_title("Matriz de confusión (1 ejemplo)")
        # Incrustar en GUI
        canvas = FigureCanvasTkAgg(fig, master=cm_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas_cm["widget"] = canvas
        
    # Elementos de control de la ventana
    ctk.CTkLabel(left_frame, text="Predicción de Señales", font=("Arial", 18, "bold")).pack(pady=10)

    ctk.CTkButton(left_frame, text="Seleccionar archivo .wav", command=seleccionar_archivo).pack(pady=10)
    label_ruta = ctk.CTkLabel(left_frame, text="Ningún archivo seleccionado", wraplength=200)
    label_ruta.pack(pady=5)

    ctk.CTkButton(left_frame, text="Reproducir audio", command=reproducir_audio).pack(pady=10)

    ctk.CTkLabel(left_frame, text="¿Qué crees que es la señal?").pack(pady=5)
    ctk.CTkRadioButton(left_frame, text="Healthy", variable=user_choice, value="Healthy").pack(anchor="w")
    ctk.CTkRadioButton(left_frame, text="COPD", variable=user_choice, value="COPD").pack(anchor="w")

    ctk.CTkButton(left_frame, text="Iniciar predicción", command=iniciar_prediccion).pack(pady=20)

    label_resultado = ctk.CTkLabel(left_frame, text="", font=("Arial", 14))
    label_resultado.pack(pady=10)

    return frame
