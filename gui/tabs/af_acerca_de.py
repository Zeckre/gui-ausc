import customtkinter as ctk

def TabAcercaDe(parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Título frame
    title = ctk.CTkLabel(frame, text="Acerca de este proyecto", font=(None, 18, "bold"))
    title.pack(pady=(8, 4))
    # Información general
    info = ctk.CTkLabel(
        frame,
        text=(
            "Este proyecto es el resultado de un proyecto de final de carrera del programa de "
            "Ingeniería Electrónica;\n"
            "es la interfaz gráfica de usuario (GUI) para la DAQ desarrollada para procesos de "
            "auscultación pulmonar."
        ),
        font=(None, 20),
        justify="center"
    )
    info.pack(padx=16, pady=8)

    # Título del proyecto
    info2 = ctk.CTkLabel(frame, text="Título del proyecto:", font=(None, 26, "italic"))
    info2.pack(padx=16, pady=8)
    info3 = ctk.CTkLabel(
        frame,
        text=(
            "Desarrollo de una interfaz didáctica para\n"
            "el análisis en procesos de auscultación\n"
            "pulmonar mediante la adquisición de\n"
            "señales con Raspberry Pi"
        ),
        font=(None, 32, "italic", "bold"),
        justify="center"
    )
    info3.pack(padx=32, pady=32)

    # Autores
    info4 = ctk.CTkLabel(
        frame,
        text="Desarrollado por:\nDuván Antonio Rico Cacua\nZeckre",
        font=(None, 20),
        justify="center"
    )
    info4.pack(padx=16, pady=8)

    # Información UP
    info5 = ctk.CTkLabel(
        frame,
        text=(
            "Programa de Ingeniería Electrónica\n"
            "Facultad de Ingenierías y Arquitectura\n"
            "Universidad de Pamplona, Colombia\n"
            "2025-2"
        ),
        font=(None, 20),
        justify="center"
    )
    info5.pack(padx=16, pady=8)

    return frame
