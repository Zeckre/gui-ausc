# check_i2c.py
try:
    import smbus2 as smbus   # Preferir smbus2 si está instalado
except ImportError:
    import smbus             # Fallback a smbus clásico

I2C_BUS = 1        # En Raspberry Pi normalmente es bus 1
DEVICE_ADDR = 0x48 # Dirección del ADS1115

def check_i2c_device(bus_id=I2C_BUS, addr=DEVICE_ADDR):
    """
    Verifica si un dispositivo I2C responde en la dirección dada.
    Retorna True si está activo, False si no responde.
    """
    try:
        bus = smbus.SMBus(bus_id)
        bus.read_byte(addr)   # Intento de lectura mínima
        bus.close()
        return True
    except OSError:
        return False

# Uso
if check_i2c_device():
    print("Dispositivo I2C activo ✅")
else:
    print("Dispositivo no responde ❌")
