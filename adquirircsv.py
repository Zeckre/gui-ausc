import time
import Adafruit_ADS1x15
import csv
import sys
import numpy as np # Necesitamos numpy para la media si quieres quitar el offset estadísticamente


def adquirir_csv(cantidad_muestras, nombre_archivo):
    # Configuración del ADS1115
    adc = Adafruit_ADS1x15.ADS1115(busnum=1)
    GAIN = 1  # Rango +/-4.096V
    CANTIDAD_MUESTRAS = cantidad_muestras
    NOMBRE_ARCHIVO = nombre_archivo

    # Parámetros de conversión a Voltios
    VOLTAJE_REFERENCIA = 4.096
    MAX_VALOR_CRUDO = 32767.0
    CONVERSION_FACTOR = VOLTAJE_REFERENCIA / MAX_VALOR_CRUDO

    # Valor del offset del DAQ
    OFFSET_APLICADO_HARDWARE = 1.5

    print(f"Iniciando recolección de {CANTIDAD_MUESTRAS} muestras")

    datos = []
    inicio_tiempo = time.time()

    try:
        for i in range(CANTIDAD_MUESTRAS):
            # Leer el canal 0 (A0)
            valor_crudo = adc.read_adc(0, gain=GAIN, data_rate=860)

            # Convertir a Voltaje del ADC
            voltaje_leido_con_offset = valor_crudo * CONVERSION_FACTOR

            # --- ELIMINAR EL OFFSET APLICADO FÍSICAMENTE (NUEVO) ---
            voltaje_real_sin_offset = voltaje_leido_con_offset - OFFSET_APLICADO_HARDWARE

            tiempo_actual = time.time() - inicio_tiempo

            # Guardamos el voltaje sin offset en la lista:
            datos.append([tiempo_actual, voltaje_real_sin_offset])

            # Opcional: imprimir progreso cada 1000 muestras
            if i % 1000 == 0:
                print(f"Muestra {i}/{CANTIDAD_MUESTRAS} - {voltaje_real_sin_offset:.4f}V (sin offset)")

    except KeyboardInterrupt:
        print("Recolección interrumpida por el usuario.")
        sys.exit(0)
    except OSError as e:
        print(f"Error de E/S (I2C): {e}")
        sys.exit(1)


    fin_tiempo = time.time()
    duracion = fin_tiempo - inicio_tiempo
    print(f"Recolección completada en {duracion:.2f} segundos.")
    print(f"Tasa de muestreo aproximada: {CANTIDAD_MUESTRAS / duracion:.2f} Hz")

    # Opcional: Verificar la media de los datos (debería estar cerca de cero si el offset se aplicó correctamente)
    media_final = np.mean([d[1] for d in datos])
    print(f"Media de los datos adquiridos (verificación de offset): {media_final:.4f}V")

    # Guardar los datos en un archivo CSV
    try:
        with open(NOMBRE_ARCHIVO, mode='w', newline='') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            escritor_csv.writerow(['Tiempo (s)', 'Valor Voltios (sin offset)'])
            escritor_csv.writerows(datos) # Escribir todas las filas

        print(f"Datos guardados en '{NOMBRE_ARCHIVO}'")

    except PermissionError:
        print(f"ERROR DE PERMISOS: No se pudo escribir en '{NOMBRE_ARCHIVO}'")
