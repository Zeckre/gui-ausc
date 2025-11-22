import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import sys
import os

COLUMNA_VOLTAJE = 'Valor Voltios (sin offset)'

def plot_fft(path):
    """
    Genera la gráfica FFT a partir de un archivo CSV.
    Devuelve la figura Matplotlib (fig) sin mostrar ventana.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo '{path}'")

    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(path)
    tiempo = df['Tiempo (s)'].values
    voltaje = df[COLUMNA_VOLTAJE].values
    N = len(voltaje)

    # Calcular la tasa de muestreo promedio (Fs)
    if N > 1:
        duracion_total = tiempo[-1] - tiempo[0]
        Fs = N / duracion_total
    else:
        raise ValueError("No hay suficientes datos para calcular Fs.")

    # --- FFT ---
    yf = np.abs(fft(voltaje))
    xf = fftfreq(N, 1/Fs)

    # --- Figura ---
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(xf[:N//2], 2.0/N * yf[:N//2], linewidth=0.5)
    ax.set_title('Espectro de Frecuencia (FFT)')
    ax.set_xlabel('Frecuencia (Hz)')
    ax.set_ylabel('Amplitud Normalizada (Voltios Pico)')
    ax.grid(True)
    # ax.set_xlim(0, Fs/2)  # opcional

    return fig

# Bloque para ejecución independiente desde consola
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python fft_csv.py archivo.csv")
    else:
        fig = plot_fft(sys.argv[1])
        plt.show()

