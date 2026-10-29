import numpy as np


# Coeficientes fijos: Fc1 = 300 Hz, Fc2 = 3300 Hz, fs = 44100 Hz.
# Prototipo Butterworth de orden 2 con transformación bilineal.
b = [
    0.03478603744173827,
    0.0,
    -0.06957207488347654,
    0.0,
    0.03478603744173827,
]

a = [
    1.0,
    -3.3727934785213742,
    4.301779470165419,
    -2.4753289249153996,
    0.5466494936820961,
]


def crear_memoria():
    # Guardar cuatro entradas y cuatro salidas anteriores, inicialmente cero.
    return [0.0] * 8


def aplicar_ecuacion_diferencias(audio, memoria):
    # Aplicar la ecuación con los coeficientes fijos de arriba.
    salida = np.zeros(len(audio))
    b0 = float(b[0])
    b2 = float(b[2])
    b4 = float(b[4])
    a1 = float(a[1])
    a2 = float(a[2])
    a3 = float(a[3])
    a4 = float(a[4])
    x1, x2, x3, x4, y1, y2, y3, y4 = memoria

    for n in range(len(audio)):
        x0 = float(audio[n])
        y0 = (b0*x0 + b2*x2 + b4*x4
              - a1*y1 - a2*y2 - a3*y3 - a4*y4)
        salida[n] = y0

        # Desplazar las muestras para calcular la siguiente salida.
        x4, x3, x2, x1 = x3, x2, x1, x0
        y4, y3, y2, y1 = y3, y2, y1, y0

    # Conservar la memoria para el siguiente bloque de la misma grabación.
    memoria[:] = [x1, x2, x3, x4, y1, y2, y3, y4]
    return salida


if __name__ == "__main__":
    from ecuacion import mostrar_ecuacion

    mostrar_ecuacion(b, a)
