import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import customtkinter as ctk
import pandas as pd

# Datos de ejemplo
df = pd.DataFrame({
    'tiempo': [0, 1, 2, 3, 4, 5],
    'voltios': [0.1, 0.5, -0.2, 0.8, -0.5, 0.3]
})

# Ventana principal
root = ctk.CTk()
root.geometry("800x600")

# Frame contenedor para gráfica + toolbar
frame_plot = ctk.CTkFrame(root)
frame_plot.pack(pady=20)

# Crear figura
fig, ax = plt.subplots(figsize=(6,4))
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

# Canvas incrustado
canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas.draw()
canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

# Toolbar justo debajo del canvas
toolbar = NavigationToolbar2Tk(canvas, frame_plot)
toolbar.update()
toolbar.pack(side="top", fill="x")

# Iniciar GUI
root.mainloop()
