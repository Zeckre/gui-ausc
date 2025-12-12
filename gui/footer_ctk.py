import customtkinter as ctk
from datetime import datetime

def create_footer(root, check_spi_func):
    """
    Crea y añade el footer a `root` y arranca el bucle de actualización.
    - root: ventana principal (CTk)
    - check_spi_func: función que retorna True/False según estado del dispositivo SPI
    """
    footer = ctk.CTkFrame(root, fg_color="transparent")
    footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
    footer.grid_columnconfigure(1, weight=1)

    status_label = ctk.CTkLabel(
        footer,
        text="Estado del dispositivo: comprobando...",
        text_color="#0077B6",
        font=(None, 18)
    )
    status_label.grid(row=0, column=0, sticky="w")

    time_label = ctk.CTkLabel(footer, text="--:--:--", font=(None, 18))
    time_label.grid(row=0, column=1)

    credit = ctk.CTkLabel(
        footer,
        text="By: Duvan Rico (Zeckre)",
        font=(None, 18)
    )
    credit.grid(row=0, column=2, sticky="e")

    def update_time_and_status():
        # Actualiza hora y estado SPI cada segundo.
        now = datetime.now().strftime("%H:%M:%S")
        time_label.configure(text=now)

        try:
            connected = check_spi_func()
        except Exception:
            connected = False

        status_label.configure(
            text=f"Estado del dispositivo: {'Activo' if connected else 'Desconectado'}"
        )

        root.after(1000, update_time_and_status)

    # Arrancar primer ciclo
    update_time_and_status()

    return footer
