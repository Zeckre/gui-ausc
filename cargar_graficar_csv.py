import pandas as pd
import customtkinter as ctk
import matplotlib.pyplot as plt
import sys, os

def plot_g1(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo '{path}'")

    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(path)

    # Crear figura
    fig, ax = plt.subplots(figsize=(4,2))
    ax.plot(df['tiempo'], df['voltios'],
            label='Voltaje MCP3202',
            color='r',
            linewidth=0.5)
    ax.set_title('Lecturas DAQ')
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Voltios')
    ax.set_ylim(-1.5, 1.5)
    ax.legend()
    ax.grid(True)

    return fig

# Bloque para ejecución independiente desde consola
if __name__ == "__main__":
    #import sys
    if len(sys.argv) < 2:
        print("Uso: python cargar_graficar_csv.py archivo.csv")
    else:
        fig = plot_g1(sys.argv[1])
        plt.show()
