import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt, sys, os

def plot_wavelet(path, wavelet='db6', nivel=1):

    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo '{path}'")

    # Cargar datos CSV
    df = pd.read_csv(path)
    tiempo = df['tiempo'].values
    voltaje = df['voltios'].values
    num_datos = len(voltaje) # Número de puntos de datos

    # Aplicamos la DWT 
    cA, cD = pywt.dwt(voltaje, wavelet, mode='symmetric')

    # Reconstrucción de la señal en sus dos componentes (detalle y aproximación)
    A = pywt.idwt(cA, None, wavelet, mode='symmetric')[:N]
    D = pywt.idwt(None, cD, wavelet, mode='symmetric')[:N]

    # Figura de la DWT
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    axes[0].plot(tiempo, A, color='green', linewidth=0.5,
                 label=f'Aproximación (Baja Frecuencia) - {wavelet}')
    axes[0].set_title('Componente de Aproximación')
    axes[0].set_ylabel('Voltaje (V)')
    axes[0].grid(True)
    axes[0].legend()
    axes[1].plot(tiempo, D, color='red', linewidth=0.5,
                 label=f'Detalle (Alta Frecuencia) - {wavelet}')
    axes[1].set_title('Componente de Detalle ')
    axes[1].set_xlabel('Tiempo (s)')
    axes[1].set_ylabel('Voltaje (V)')
    axes[1].grid(True)
    axes[1].legend()

    fig.tight_layout()
    return fig

# Bloque para ejecución independiente desde consola
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python dwt_csv.py archivo.csv")
    else:
        fig = plot_wavelet(sys.argv[1])
        plt.show()
