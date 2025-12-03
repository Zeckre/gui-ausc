import pandas as pd
import numpy as np
import customtkinter as ctk
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import sys, os

def plot_fft(path):
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo '{path}'")
        sys.exit(1)

    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(path)
    tiempo = df['tiempo'].values
    voltaje = df['voltios'].values
    num_datos = len(voltaje) # Número de puntos de datos

    # Calcular la tasa de muestreo promedio (Fs)
    if num_datos > 1:
        duracion_total = tiempo[-1] - tiempo[0]
        Fs = num_datos / duracion_total
        print(f"Tasa de muestreo (Fs) aproximada: {Fs:.2f} Hz")
    else:
        print("Error: No hay suficientes datos para calcular Fs.")
        sys.exit(1)

    # Aplicamos la FFT
    yf = np.abs(fft(voltaje))
    xf = fftfreq(num_datos, 1/Fs)

   # --- Figura ---
    fig, ax = plt.subplots(figsize=(4,2))
    ax.plot(xf[:num_datos//2], 2.0/num_datos * yf[:num_datos//2],
            linewidth=0.5) 
    ax.set_title('Espectro de Frecuencia (FFT)')
    ax.set_xlabel('Frecuencia (Hz)')
    ax.set_ylabel('Amplitud Normalizada (Vp)')
    ax.grid(True)
    ax.set_xlim(0, 1200)  # opcional

    return fig

# Bloque para ejecución independiente desde consola
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python fft_csv.py archivo.csv")
    else:
        fig = plot_fft(sys.argv[1])
        plt.show()

