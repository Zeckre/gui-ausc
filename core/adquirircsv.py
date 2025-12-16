import time, csv, sys 
import numpy as np
from gpiozero import MCP3202

def adquirir_csv(num_muestras, nombre_archivo):
    # Configuración del ADC
    adc = MCP3202(channel=0, device=0) 

    # Parámetros de conversión a Voltios 
    vref = 3.0
    num_bits = 4096.0
    to_volts = vref / num_bits
    offset = 1.5

    # Inicio del muestreo
    print(f"Iniciando recolección de {num_muestras} muestras")
    datos = []
    inicio_tiempo = time.time()

    try:
        for i in range(num_muestras):
            # Leer el canal 0 (A0)
            voltios = (adc.value * vref) - offset
            
            # Tiempo total de muestreo
            tiempo_actual = time.time() - inicio_tiempo
            datos.append([tiempo_actual, voltios]) 

    except KeyboardInterrupt:
        print("Recolección interrumpida por el usuario.")
        sys.exit(0)

    fin_tiempo = time.time()
    duracion = fin_tiempo - inicio_tiempo
    print(f"Recolección completada en {duracion:.2f} segundos.")
    print(f"Tasa de muestreo aproximada: {num_muestras / duracion:.2f} Hz")

    # Verificar si se aplicó el offset
    media_final = np.mean([d[1] for d in datos])
    print(f"Media de los datos adquiridos (verificación de offset): {media_final:.4f}V")
    datos_corregidos = [[t, v - media_final] for t, v in datos]

    # Guardar los datos en un archivo CSV
    try:
        with open(nombre_archivo, mode='w', newline='') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            escritor_csv.writerow(['tiempo', 'voltios']) 
            escritor_csv.writerows(datos_corregidos)

        print(f"Datos guardados en '{nombre_archivo}'")

    except PermissionError:
        print(f"ERROR DE PERMISOS: No se pudo escribir en '{nombre_archivo}'")
