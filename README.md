# Migración Flet -> CustomTkinter

Estos archivos son una migración básica de la interfaz originalmente construida con Flet.

Archivos añadidos:

- `app_main_ctk.py` : Ventana principal usando `customtkinter` con `CTkTabview`, header, área de contenido y footer (hora + estado I2C).
- `tab_content_ctk.py` : Contenedores por pestaña (devuelve `Frame` con los widgets de cada pestaña).
- `requirements.txt` : Dependencias sugeridas.

Notas de uso:

1. Instalar dependencias (preferiblemente en un virtualenv):

```bash
python3 -m pip install -r requirements.txt
```

2. Ejecutar la aplicación en la Raspberry Pi:

```bash
cd /ruta/al/proyecto/gui
python3 app_main_ctk.py
```

3. Imágenes: Si quieres usar `escudounipamplona.png` y `siibtel_logo.png`, colócalas en el mismo directorio. Si no están presentes, se mostrarán etiquetas de texto en su lugar.

4. I2C: Se reutiliza la función `check_i2c_device` de `check_i2c.py`. Asegúrate de tener permisos para acceder a `/dev/i2c-1` y que `smbus2` o `smbus` esté instalado.

Limitaciones y siguientes pasos sugeridos:

- El diseño recrea la estructura principal pero no implementa gráficos reales (usa contenedores/placeholder). Puedes integrar `matplotlib` o `pyqtgraph` dentro de los `CTkFrame` para mostrar señales.
- Internacionalización/temas: `CTk` soporta modos claros/oscuros si quieres añadir cambio real de tema.

Si quieres, puedo:

- Reemplazar los placeholders con `matplotlib`/`pyplot` o `pyqtgraph` para la visualización en tiempo real.
- Añadir guardado/lectura de archivos para las grabaciones.
