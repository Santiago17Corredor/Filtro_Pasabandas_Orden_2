"""Filtro del ejemplo 4, páginas 26–27 del PDF, aplicado muestra a muestra."""

from math import pi, sqrt, tan

import numpy as np

from configuracion import ConfiguracionFiltro


def obtener_coeficientes(configuracion):
    # Fórmula final de la bilineal con prewarping; BW = wd2 - wd1.
    t1 = tan(pi * configuracion.fc1 / configuracion.fs)
    t2 = tan(pi * configuracion.fc2 / configuracion.fs)
    B, P, R = t2 - t1, t1 * t2, sqrt(2)
    A = 2 * P + B**2
    a = np.array([
        1 + R*B + A + R*B*P + P**2,
        -4 - 2*R*B + 2*R*B*P + 4*P**2,
        6 - 2*A + 6*P**2,
        -4 + 2*R*B - 2*R*B*P + 4*P**2,
        1 - R*B + A - R*B*P + P**2,
    ])
    b = B**2 * np.array([1, 0, -2, 0, 1]) / a[0]
    a /= a[0]
    if np.any(np.abs(np.roots(a)) >= 1):
        raise ValueError("Aumenta fc1: está demasiado cerca de cero para este cálculo.")
    return b, a


class FiltroPasabandas:
    def __init__(self, configuracion: ConfiguracionFiltro):
        self.b, self.a = obtener_coeficientes(configuracion)
        self.reiniciar()

    def reiniciar(self):
        self._x = self._y = (0.0, 0.0, 0.0, 0.0)

    def procesar(self, muestras):
        entrada = np.asarray(muestras, dtype=np.float64)
        if entrada.ndim != 1 or not np.all(np.isfinite(entrada)):
            raise ValueError("El audio debe ser un vector mono de muestras finitas.")
        salida = np.empty_like(entrada)
        b0, _, b2, _, b4 = map(float, self.b)
        _, a1, a2, a3, a4 = map(float, self.a)
        x1, x2, x3, x4 = self._x
        y1, y2, y3, y4 = self._y

        for n, muestra in enumerate(entrada):
            x0 = float(muestra)
            y0 = (b0*x0 + b2*x2 + b4*x4
                  - a1*y1 - a2*y2 - a3*y3 - a4*y4)
            salida[n] = y0
            x4, x3, x2, x1 = x3, x2, x1, x0
            y4, y3, y2, y1 = y3, y2, y1, y0

        if not np.all(np.isfinite(salida)):
            raise ArithmeticError("El filtro produjo valores no finitos.")
        self._x, self._y = (x1, x2, x3, x4), (y1, y2, y3, y4)
        return salida
