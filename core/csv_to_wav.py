import pandas as pd
import numpy as np
from scipy.io.wavfile import write
import sys, subprocess, os

COLUMNA_VOLTAJE = 'voltios'
SAMPLE_RATE_AUDIO = 6800  # usa un valor estándar para que se escuche bien

def csv_to_wav(path_csv, sample_rate=SAMPLE_RATE_AUDIO):
    if not os.path.exists(path_csv):
        raise FileNotFoundError(f"No se encontró el archivo '{path_csv}'")

    # Generar nombre del archivo WAV en la misma ruta
    base, _ = os.path.splitext(path_csv)
    path_wav = base + ".wav"

    # Cargar datos
    df = pd.read_csv(path_csv)
    if COLUMNA_VOLTAJE not in df.columns:
        raise ValueError(f"No se encontró la columna '{COLUMNA_VOLTAJE}' en el archivo CSV.")

    voltajes = df[COLUMNA_VOLTAJE].values
    N = len(voltajes)
    if N == 0:
        raise ValueError("El archivo CSV no contiene datos en la columna de voltaje.")

    # Normalizar al rango int16
    max_abs_val = np.max(np.abs(voltajes))
    if max_abs_val == 0:
        raise ValueError("La señal es plana (voltaje constante), no se puede generar audio.")

    escala_audio = 4096/ max_abs_val
    audio_data = (voltajes * escala_audio).astype(np.int16)

    # Guardar WAV
    write(path_wav, sample_rate, audio_data)

    return path_wav

def play_wav(path_wav):
    """
    Reproduce el archivo WAV usando 'aplay' o 'omxplayer' en segundo plano.
    """
    if not os.path.exists(path_wav):
        raise FileNotFoundError(f"No se encontró el archivo WAV '{path_wav}'")

    try:
        subprocess.Popen(["aplay", path_wav])
    except FileNotFoundError:
        try:
            subprocess.Popen(["omxplayer", path_wav])
        except FileNotFoundError:
            print("No se encontró 'aplay' ni 'omxplayer'. Reproduce el archivo manualmente.")

# Bloque para ejecución independiente desde consola
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python csv_to_wav.py archivo.csv")
    else:
        path_csv = sys.argv[1]
        wav_file = csv_to_wav(path_csv)
        print(f"Archivo de audio '{wav_file}' generado exitosamente.")
        play_wav(wav_file)
