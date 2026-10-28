"""Butterworth pasabandas por la ecuación de las páginas 26–27 de la guía.

Prototipo: H(s) = 1 / (s² + sqrt(2)*s + 1).
Pasabandas: BW²*s² / [s⁴ + sqrt(2)*BW*s³ + (2*w0²+BW²)*s²
                         + sqrt(2)*BW*w0²*s + w0⁴].
Bilineal: s = (2/T)*(1-z⁻¹)/(1+z⁻¹), con prewarping de ambos cortes.

Se usan directamente los coeficientes expandidos de esa expresión y su
ecuación en diferencias. El estado se conserva entre bloques de audio.
"""

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

    def ecuacion(self) -> str:
        """Ecuación numérica lista para usar, con a[0] = 1."""
        b, a = self.b, self.a
        return (
            f"y[n] = {b[0]:.12g} x[n] {b[2]:+.12g} x[n-2] "
            f"{b[4]:+.12g} x[n-4]\n"
            f"       {-a[1]:+.12g} y[n-1] {-a[2]:+.12g} y[n-2] "
            f"{-a[3]:+.12g} y[n-3] {-a[4]:+.12g} y[n-4]"
        )


def obtener_coeficientes(configuracion: ConfiguracionFiltro) -> CoeficientesFiltro:
    """Evalúa la fórmula final; no realiza una deducción simbólica en ejecución.

    B = BW/(2/T), P = w0²/(2/T)². El factor (2/T)⁴ se cancela en H(z).
    El numerador queda B²*(1 - 2*z⁻² + z⁻⁴).
    El denominador se expande en potencias de z⁻¹ y se divide entre d[0].

    BW = wd2 - wd1, según la definición de la propia guía. La sustitución
    numérica al pie de la página 26 invierte esa resta por error tipográfico.
    """
    k = 2.0 * configuracion.fs
    wd1 = k * tan(pi * configuracion.fc1 / configuracion.fs)
    wd2 = k * tan(pi * configuracion.fc2 / configuracion.fs)
    bw = wd2 - wd1
    w0 = sqrt(wd1 * wd2)

    B = bw / k
    P = (w0 / k) ** 2
    R = sqrt(2.0)
    A = 2.0 * P + B * B

    # Coeficientes de (1-q)^4 + R*B*(1-q)^3*(1+q)
    # + A*(1-q)^2*(1+q)^2 + R*B*P*(1-q)*(1+q)^3 + P²*(1+q)^4;
    # q = z⁻¹. Es la expresión de la página 27 con denominador común.
    d = np.array([
        1.0 + R*B + A + R*B*P + P*P,
        -4.0 - 2.0*R*B + 2.0*R*B*P + 4.0*P*P,
        6.0 - 2.0*A + 6.0*P*P,
        -4.0 + 2.0*R*B - 2.0*R*B*P + 4.0*P*P,
        1.0 - R*B + A - R*B*P + P*P,
    ], dtype=np.float64)
    b = (B * B / d[0]) * np.array([1.0, 0.0, -2.0, 0.0, 1.0])
    a = d / d[0]

    # Evita usar una frecuencia casi nula que la precisión de esta forma
    # directa de grado 4 no pueda representar de manera estable.
    if not np.all(np.abs(np.roots(a)) < 1.0):
        raise ValueError(
            "La frecuencia inferior es demasiado cercana a cero para representar "
            "este filtro con precisión. Aumenta fc1 conservando el ancho permitido."
        )
    a.setflags(write=False)
    b.setflags(write=False)
    return CoeficientesFiltro(configuracion, b, a, wd1, wd2, w0, bw)


class FiltroPasabandas:
    """Ecuación en diferencias causal, con reposo inicial.

    y[n] = b0*x[n] + b2*x[n-2] + b4*x[n-4]
           - a1*y[n-1] - a2*y[n-2] - a3*y[n-3] - a4*y[n-4].

    Usar la misma instancia para todos los bloques de una grabación.
    Crear otra instancia, o reiniciar(), únicamente al iniciar otra señal.
    """

    def __init__(self, configuracion: ConfiguracionFiltro):
        self.coeficientes = obtener_coeficientes(configuracion)
        self.reiniciar()

    def reiniciar(self):
        self._x = (0.0, 0.0, 0.0, 0.0)
        self._y = (0.0, 0.0, 0.0, 0.0)

    def procesar(self, muestras) -> np.ndarray:
        entrada = np.asarray(muestras, dtype=np.float64)
        if entrada.ndim != 1:
            raise ValueError("El filtro recibe audio mono: un vector de muestras.")
        if not np.all(np.isfinite(entrada)):
            raise ValueError("El audio contiene muestras no finitas.")

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

        if not np.all(np.isfinite(salida)):
            raise ArithmeticError("El filtrado produjo valores no finitos.")
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
    print(f"fs = {coef.configuracion.fs} Hz; BW = {coef.configuracion.ancho_banda:g} Hz")
    print("b =", np.array2string(coef.b, precision=12))
    print("a =", np.array2string(coef.a, precision=12))
    print(coef.ecuacion())
