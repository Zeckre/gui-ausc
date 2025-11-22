import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import sys
import os

COLUMNA_TIEMPO = 'Tiempo (s)'
COLUMNA_VOLTAJE = 'Valor Voltios (sin offset)'

def plot_wavelet(path, wavelet='db6', nivel=1):
    """
    Genera la gráfica de la Transformada Wavelet Discreta (DWT) a partir de un archivo CSV.
    Devuelve la figura Matplotlib (fig) sin mostrar ventana.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo '{path}'")

    # Cargar datos
    df = pd.read_csv(path)
    tiempo = df[COLUMNA_TIEMPO].values
    if COLUMNA_VOLTAJE not in df.columns:
        raise ValueError(f"No se encontró la columna '{COLUMNA_VOLTAJE}' en el archivo CSV.")
    voltaje = df[COLUMNA_VOLTAJE].values
    N = len(voltaje)

    # --- Aplicar DWT ---
    cA, cD = pywt.dwt(voltaje, wavelet, mode='symmetric')

    # Reconstrucción
    A = pywt.idwt(cA, None, wavelet, mode='symmetric')[:N]
    D = pywt.idwt(None, cD, wavelet, mode='symmetric')[:N]

    # --- Figura ---
    fig, axes = plt.subplots(3, 1, figsize=(8, 6), sharex=True)

    axes[0].plot(tiempo, voltaje, linewidth=0.5, label='Señal Original')
    axes[0].set_title('Señal Original Adquirida')
    axes[0].set_ylabel('Voltaje (V)')
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(tiempo, A, color='green', linewidth=0.5,
                 label=f'Aproximación (Baja Frecuencia) - {wavelet}')
    axes[1].set_title('Componente de Aproximación')
    axes[1].set_ylabel('Voltaje (V)')
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(tiempo, D, color='red', linewidth=0.5,
                 label=f'Detalle (Alta Frecuencia) - {wavelet}')
    axes[2].set_title('Componente de Detalle (Ruido)')
    axes[2].set_xlabel('Tiempo (s)')
    axes[2].set_ylabel('Voltaje (V)')
    axes[2].grid(True)
    axes[2].legend()

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