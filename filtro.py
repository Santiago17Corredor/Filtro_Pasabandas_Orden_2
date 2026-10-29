import numpy as np


def aplicar_filtro(audio, memoria):
    # Ecuación fija: banda de 300 a 3300 Hz, muestreo de 44100 Hz.
    salida = np.zeros(len(audio))
    x1, x2, x3, x4, y1, y2, y3, y4 = memoria

    for n in range(len(audio)):
        x0 = float(audio[n])
        y0 = (
            0.03478603744173827 * x0
            - 0.06957207488347654 * x2
            + 0.03478603744173827 * x4
            + 3.3727934785213742 * y1
            - 4.301779470165419 * y2
            + 2.4753289249153996 * y3
            - 0.5466494936820961 * y4
        )
        salida[n] = y0
        x4, x3, x2, x1 = x3, x2, x1, x0
        y4, y3, y2, y1 = y3, y2, y1, y0

    # Conservar las muestras anteriores para el siguiente bloque.
    memoria[:] = [x1, x2, x3, x4, y1, y2, y3, y4]
    return salida
