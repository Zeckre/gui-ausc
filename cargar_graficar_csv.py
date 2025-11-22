import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

COLUMNA_TIEMPO = 'Tiempo (s)'
COLUMNA_VOLTAJE = 'Valor Voltios (sin offset)'

def plot_g1(path):
    """
    Genera la gráfica principal (g1) a partir de un archivo CSV.
    Devuelve la figura Matplotlib (fig) sin mostrar ventana.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo '{path}'")

    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(path)

    # Crear figura
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(df[COLUMNA_TIEMPO], df[COLUMNA_VOLTAJE],
            label='Voltaje ADS1115',
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
    import sys
    if len(sys.argv) < 2:
        print("Uso: python cargar_graficar_csv.py archivo.csv")
    else:
        fig = plot_g1(sys.argv[1])
        plt.show()

