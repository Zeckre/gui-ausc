import time
import Adafruit_ADS1x15
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Configuración del Hardware ---
adc = Adafruit_ADS1x15.ADS1115(busnum=1)
GAIN = 1  # 1 = +/-4.096V
VOLTAGE_FSR = 4.096 
MAX_VALUE_16BIT = 32767

# --- Configuración de la Gráfica ---
fig, ax = plt.subplots()
# Creamos un objeto de línea vacío inicialmente
line, = ax.plot([], [], lw=1) 
ax.set_ylim(0, 3)  # Establecemos el rango del eje Y al máximo voltaje posible
ax.set_xlim(0, 10)           # Mostramos los últimos 10 segundos en el eje X
ax.set_xlabel("Tiempo (segundos)")
ax.set_ylabel("Voltaje (V)")
ax.set_title("Lectura ADC ADS1115 en Tiempo Real")
ax.grid(True)

# Listas para almacenar los datos a lo largo del tiempo
time_data = []
voltage_data = []
start_time = time.time()

def update_graph(i):
    """
    Función que se llama repetidamente para actualizar el gráfico.
    """
    # 1. Leer un nuevo valor del ADC
    value = adc.read_adc(0, gain=GAIN, data_rate=860)
    voltage = value * (VOLTAGE_FSR / MAX_VALUE_16BIT)
    current_time = time.time() - start_time
    
    # 2. Añadir los datos a las listas
    time_data.append(current_time)
    voltage_data.append(voltage)
    
    # Opcional: Imprimir en consola para depurar
    # print(f"Tiempo: {current_time:.2f}s, Voltaje: {voltage:.4f}V")

    # 3. Actualizar los datos de la línea del gráfico
    line.set_data(time_data, voltage_data)
    
    # 4. Deslizar la vista del eje X para mostrar solo los últimos 10 segundos
    if current_time >= 10:
        ax.set_xlim(current_time - 10, current_time + 1)
    
    # Devolvemos la línea actualizada para que FuncAnimation sepa qué redibujar
    return line,

# Configurar la animación para llamar a 'update_graph' cada 50 milisegundos (20 FPS aprox)
# blit=True optimiza el redibujado solo de las partes que cambian
ani = animation.FuncAnimation(fig, update_graph, interval=0.01, blit=True)

# Mostrar el gráfico interactivo (esto bloquea el programa hasta que cierras la ventana)
plt.show()
