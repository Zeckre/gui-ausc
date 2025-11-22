import pandas as pd
import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import sys

NOMBRE_ARCHIVO_CSV = 'muestras-daq.csv'

try:
    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(NOMBRE_ARCHIVO_CSV)
    tiempo = df['Tiempo (s)'].values
    senal_original = df['Valor Voltios (sin offset)'].values
    
    print(f"Datos cargados. Cantidad de muestras: {len(senal_original)}")

    # --- Aplicar la Transformada de Hilbert ---
    # hilbert() devuelve la señal analítica (un array de números complejos)
    senal_analitica = hilbert(senal_original)
    
    # Calcular la envolvente de amplitud (magnitud del resultado complejo)
    envolvente = np.abs(senal_analitica)
    
    # Calcular la fase instantánea (ángulo del resultado complejo)
    fase_instantanea = np.angle(senal_analitica)
    
    # Opcional: Calcular la frecuencia instantánea (derivada de la fase)
    # Necesitamos la tasa de muestreo (fs) para esto
    if len(tiempo) > 1:
        # Tasa de muestreo promedio de tus datos
        fs = 1.0 / np.mean(np.diff(tiempo))
        # Desempaquetar la fase y calcular la derivada
        frecuencia_instantanea = (np.diff(np.unwrap(fase_instantanea)) * fs) / (2.0 * np.pi)
    else:
        frecuencia_instantanea = np.array([])
        print("No hay suficientes datos para calcular la frecuencia instantánea.")

    print("Transformada de Hilbert aplicada exitosamente.")

    # --- Visualización de resultados ---
    plt.figure(figsize=(12, 8))
    
    # Gráfico 1: Señal original y su envolvente
    plt.subplot(3, 1, 1)
    plt.plot(tiempo, senal_original, label='Señal Original (Voltios)', alpha=0.6, linewidth=0.5)
    plt.plot(tiempo, envolvente, label='Envolvente de Amplitud (Hilbert)', color='red', linestyle='--', linewidth=0.5)
    plt.title('Señal Original y Envolvente de Amplitud')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud (V)')
    plt.legend()
    plt.grid(True)

    # Gráfico 2: Fase instantánea
    plt.subplot(3, 1, 2)
    plt.plot(tiempo, fase_instantanea, color='green', linewidth=0.5)
    plt.title('Fase Instantánea (Radianes)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Fase')
    plt.grid(True)

    # Gráfico 3: Frecuencia instantánea (nota: tendrá un punto menos que la señal original)
    if len(frecuencia_instantanea) > 0:
        plt.subplot(3, 1, 3)
        # Ajustamos el eje X para que coincida con los puntos de frecuencia calculados
        plt.plot(tiempo[:-1], frecuencia_instantanea, color='purple', linewidth=0.5)
        plt.title(f'Frecuencia Instantánea (Tasa de muestreo original aprox: {fs:.2f} Hz)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Frecuencia (Hz)')
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

except FileNotFoundError:
    print(f"Error: El archivo '{NOMBRE_ARCHIVO_CSV}' no se encontró.")
    print("Asegúrate de ejecutar primero el script de recolección de datos.")
except Exception as e:
    print(f"Ocurrió un error: {e}")

