from dataclasses import dataclass
from math import pi, sqrt, tan
import numpy as np
from configuracion import ConfiguracionFiltro


@dataclass(frozen=True)
class CoeficientesFiltro:
    configuracion: ConfiguracionFiltro
    b: np.ndarray
    a: np.ndarray
    wd1: float
    wd2: float
    w0: float
    bw_analogico: float



def obtener_coeficientes(configuracion: ConfiguracionFiltro) -> CoeficientesFiltro:

    k = 2.0 * configuracion.fs
    wd1 = k * tan(pi * configuracion.fc1 / configuracion.fs)
    wd2 = k * tan(pi * configuracion.fc2 / configuracion.fs)
    bw = wd2 - wd1
    w0 = sqrt(wd1 * wd2)

    B = bw / k
    P = (w0 / k) ** 2
    R = sqrt(2.0)
    A = 2.0 * P + B * B

    d = np.array([
        1.0 + R*B + A + R*B*P + P*P,
        -4.0 - 2.0*R*B + 2.0*R*B*P + 4.0*P*P,
        6.0 - 2.0*A + 6.0*P*P,
        -4.0 + 2.0*R*B - 2.0*R*B*P + 4.0*P*P,
        1.0 - R*B + A - R*B*P + P*P,
    ], dtype=np.float64)
    b = (B * B / d[0]) * np.array([1.0, 0.0, -2.0, 0.0, 1.0])
    a = d / d[0]

    return CoeficientesFiltro(configuracion, b, a, wd1, wd2, w0, bw)


class FiltroPasabandas:

    def __init__(self, configuracion: ConfiguracionFiltro):
        self.coeficientes = obtener_coeficientes(configuracion)
        self.reiniciar()

    def reiniciar(self):
        self._x = (0.0, 0.0, 0.0, 0.0)
        self._y = (0.0, 0.0, 0.0, 0.0)

    def procesar(self, muestras) -> np.ndarray:
        entrada = np.asarray(muestras, dtype=np.float64)

        salida = np.empty(len(entrada), dtype=np.float64)
        b0, _, b2, _, b4 = map(float, self.coeficientes.b)
        _, a1, a2, a3, a4 = map(float, self.coeficientes.a)
        x1, x2, x3, x4 = self._x
        y1, y2, y3, y4 = self._y

        for n, muestra in enumerate(entrada):
            x0 = float(muestra)
            # Algoritmo matemático del procesamiento, visible para sustentar.
            y0 = (b0*x0 + b2*x2 + b4*x4
                  - a1*y1 - a2*y2 - a3*y3 - a4*y4)
            salida[n] = y0
            x4, x3, x2, x1 = x3, x2, x1, x0
            y4, y3, y2, y1 = y3, y2, y1, y0

        self._x = (x1, x2, x3, x4)
        self._y = (y1, y2, y3, y4)
        return salida


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ecuación del filtro del laboratorio.")
    parser.add_argument("--fc1", type=float, default=1000.0, help="Corte inferior en Hz.")
    parser.add_argument("--fc2", type=float, default=3500.0, help="Corte superior en Hz.")
    args = parser.parse_args()
    try:
        coef = obtener_coeficientes(ConfiguracionFiltro(args.fc1, args.fc2))
    except ValueError as error:
        parser.error(str(error))
    from ecuacion import mostrar_ecuacion

    mostrar_ecuacion(coef)
