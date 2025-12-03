import time
from gpiozero import MCP3202
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Configuración del Hardware ---
adc = MCP3202(channel=0)   # Usamos canal 0 del MCP3202
VREF = 3.3                 # Voltaje de referencia del MCP3202
MAX_VALUE_12BIT = 4095     # Resolución de 12 bits

# --- Configuración de la Gráfica ---
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1) 
ax.set_ylim(0, VREF)       # Rango del eje Y hasta el voltaje de referencia
ax.set_xlim(0, 10)         # Mostramos los últimos 10 segundos en el eje X
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Voltaje (V)")
ax.set_title("Lectura DAQ en Tiempo Real (MCP3202)")
ax.grid(True)

# Listas para almacenar los datos
time_data = []
voltage_data = []
start_time = time.time()

def update_graph(i):
    """
    Función que se llama repetidamente para actualizar el gráfico.
    """
    # 1. Leer un nuevo valor del ADC
    raw_value = adc.raw_value
    voltage = (raw_value / MAX_VALUE_12BIT) * VREF
    current_time = time.time() - start_time
    
    # 2. Añadir los datos a las listas
    time_data.append(current_time)
    voltage_data.append(voltage)
    
    # 3. Actualizar los datos de la línea del gráfico
    line.set_data(time_data, voltage_data)
    
    # 4. Deslizar la vista del eje X para mostrar solo los últimos 10 segundos
    if current_time >= 10:
        ax.set_xlim(current_time - 10, current_time + 1)
    
    return line,

# Configurar la animación para llamar a 'update_graph'
ani = animation.FuncAnimation(fig, update_graph, interval=50, blit=True)

# Mostrar el gráfico interactivo
plt.show()
