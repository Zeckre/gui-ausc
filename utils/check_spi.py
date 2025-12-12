import spidev

def check_spi(bus=0, device=0):
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = 1000000
        spi.mode = 0

        # Enviar comando mínimo
        resp = spi.xfer2([0x01, 0x80, 0x00])
        spi.close()

        # Si recibimos 3 bytes, asumimos comunicación OK
        return len(resp) == 3

    except Exception:
        return False
