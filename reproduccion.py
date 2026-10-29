
import numpy as np
import sounddevice as sd

from configuracion import FRECUENCIA_MUESTREO


def ganancia_comun(original, filtrada):
    return 1.0 / max(1.0, np.max(np.abs(original)), np.max(np.abs(filtrada)))


def reproducir(audio, ganancia=1.0):
    sd.stop()
    sd.play(np.asarray(audio * ganancia, dtype=np.float32), FRECUENCIA_MUESTREO)


def detener():
    sd.stop()
