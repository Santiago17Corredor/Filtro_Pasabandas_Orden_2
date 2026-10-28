FRECUENCIA_MUESTREO = 44100
TAMANO_BLOQUE = 1024
DURACION_GRABACION = 10


def validar_frecuencias(fc1, fc2):
    # Las únicas dos condiciones para elegir las frecuencias.
    if not 0 < fc1 < fc2 <= 5000:
        raise ValueError("Debe cumplirse: 0 < Fc1 < Fc2 <= 5000 Hz.")

    BW = fc2 - fc1
    if not 200 <= BW <= 3000:
        raise ValueError("El ancho de banda debe estar entre 200 y 3000 Hz.")

    return BW


class ConfiguracionFiltro:
    def __init__(self, fc1=1000, fc2=3500):
        self.ancho_banda = validar_frecuencias(fc1, fc2)
        self.fc1 = fc1
        self.fc2 = fc2
        self.fs = FRECUENCIA_MUESTREO
