from math import pi, sqrt, tan

import numpy as np

from configuracion import FRECUENCIA_MUESTREO


def prewarping(fc1, fc2):
    # Paso 1: ajustar las dos frecuencias antes de la transformación bilineal.
    fs = FRECUENCIA_MUESTREO
    omega1 = 2 * fs * tan(pi * fc1 / fs)
    omega2 = 2 * fs * tan(pi * fc2 / fs)
    return omega1, omega2


def calcular_B_y_omega0(omega1, omega2):
    # Paso 2: ancho de banda analógico y frecuencia central, en rad/s.
    B = omega2 - omega1
    omega0 = sqrt(omega1 * omega2)
    return B, omega0


def transformar_prototipo(B, omega0):
    # Paso 3: partir de H(s) = 1 / (s² + sqrt(2)*s + 1).
    # Sustituir s por (s² + omega0²) / (B*s), como en el PDF.
    # Numerador: B²*s². Denominador: polinomio de grado 4.
    numerador = np.array([B**2, 0, 0])
    denominador = np.array([
        1,
        sqrt(2) * B,
        2 * omega0**2 + B**2,
        sqrt(2) * B * omega0**2,
        omega0**4,
    ])
    return numerador, denominador


def transformacion_bilineal(numerador, denominador):
    # Paso 4: sustituir s = K*(1-q)/(1+q), con q = z⁻¹ y K = 2*fs.
    K = 2 * FRECUENCIA_MUESTREO

    # Al multiplicar por (1+q)^4, estas son las potencias desarrolladas.
    p4 = np.array([1, -4, 6, -4, 1])   # (1-q)^4
    p3 = np.array([1, -2, 0, 2, -1])   # (1-q)^3 * (1+q)
    p2 = np.array([1, 0, -2, 0, 1])    # (1-q)^2 * (1+q)^2
    p1 = np.array([1, 2, 0, -2, -1])   # (1-q) * (1+q)^3
    p0 = np.array([1, 4, 6, 4, 1])     # (1+q)^4

    # Los cinco lugares corresponden a: 1, z⁻¹, z⁻², z⁻³, z⁻⁴.
    numerador_z = (numerador[0] * K**2 * p2
                   + numerador[1] * K * p1
                   + numerador[2] * p0)

    denominador_z = (denominador[0] * K**4 * p4
                     + denominador[1] * K**3 * p3
                     + denominador[2] * K**2 * p2
                     + denominador[3] * K * p1
                     + denominador[4] * p0)
    return numerador_z, denominador_z


def obtener_coeficientes(numerador_z, denominador_z):
    # Paso 5: dividir entre el primer coeficiente para que a[0] sea 1.
    a0 = denominador_z[0]
    b = numerador_z / a0
    a = denominador_z / a0
    return b, a


def disenar_filtro(fc1, fc2):
    # Ejecutar el diseño una sola vez, en el mismo orden del informe.
    omega1, omega2 = prewarping(fc1, fc2)
    B, omega0 = calcular_B_y_omega0(omega1, omega2)
    numerador, denominador = transformar_prototipo(B, omega0)
    numerador_z, denominador_z = transformacion_bilineal(numerador, denominador)
    b, a = obtener_coeficientes(numerador_z, denominador_z)
    return b, a


def crear_memoria():
    # Guardar cuatro entradas y cuatro salidas anteriores, inicialmente cero.
    return [0.0] * 8


def aplicar_ecuacion_diferencias(audio, b, a, memoria):
    # Paso 6: aplicar la ecuación a cada muestra del bloque de audio.
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
    from interfaz import seleccionar_frecuencias

    configuracion = seleccionar_frecuencias()
    if configuracion is not None:
        b, a = disenar_filtro(configuracion.fc1, configuracion.fc2)
        mostrar_ecuacion(configuracion, b, a)
