import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq
from scipy.io.wavfile import write

def cargar_csv(ruta_csv):
    df = pd.read_csv(ruta_csv)

    if df.shape[1] == 1:
        senal = df.iloc[:, 0].values
        tiempo = np.arange(len(senal))
    else:
        tiempo = df.iloc[:, 0].values
        senal = df.iloc[:, 1].values

    return tiempo, senal

def filtro_pasabanda(senal, fs, lowcut=100, highcut=1200, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, senal)

def calcular_fft(senal, fs):
    N = len(senal)
    fft_vals = np.abs(fft(senal))
    freqs = fftfreq(N, 1/fs)
    return freqs[:N//2], fft_vals[:N//2]

if __name__ == "__main__":
    ruta_csv = "/home/zeckre/Videos/Domingo2.csv"
    fs = 6400 
    

    # 1. Cargar señal
    tiempo, senal = cargar_csv(ruta_csv)
    senal = senal - np.mean(senal)
    # 2. FFT original
    freqs, fft_vals = calcular_fft(senal, fs)

    # 3. Filtrar señal
    senal_filtrada = filtro_pasabanda(senal, fs)

    # 4. FFT filtrada
    freqs_f, fft_vals_f = calcular_fft(senal_filtrada, fs)

    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Análisis de Señal de Auscultación Pulmonar", fontsize=16)

    # Señal original
    axs[0, 0].plot(tiempo, senal, color="blue", lw=0.5)
    axs[0, 0].set_title("Señal Original")
    axs[0, 0].set_xlabel("Tiempo (s)")
    axs[0, 0].set_ylabel("Amplitud")
    axs[0, 0].grid()

    # FFT original
    axs[1, 0].plot(freqs, fft_vals, color="green", lw=0.5)
    axs[1, 0].set_title("FFT Original")
    axs[1, 0].set_xlabel("Frecuencia (Hz)")
    axs[1, 0].set_ylabel("Magnitud")
    axs[1, 0].grid()

    # Señal filtrada
    axs[0, 1].plot(tiempo, senal_filtrada, color="red",lw=0.5)
    axs[0, 1].set_title("Señal Filtrada (100–1300 Hz)")
    axs[0, 1].set_xlabel("Tiempo (s)")
    axs[0, 1].set_ylabel("Amplitud")
    axs[0, 1].grid()

    # FFT filtrada
    axs[1, 1].plot(freqs_f, fft_vals_f, color="purple",lw=0.5)
    axs[1, 1].set_title("FFT Filtrada")
    axs[1, 1].set_xlabel("Frecuencia (Hz)")
    axs[1, 1].set_ylabel("Magnitud")
    axs[1, 1].grid()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    senal_norm = senal_filtrada / np.max(np.abs(senal_filtrada))
    write("senal_filtrada.wav", fs, senal_norm.astype(np.float32))

    print("Proceso completado. Archivo 'senal_filtrada.wav' generado.")
