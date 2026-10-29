"""Comparación temporal y espectral con la misma escala para ambos audios."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

from configuracion import (
    FRECUENCIA_CORTE_INFERIOR as FC1,
    FRECUENCIA_CORTE_SUPERIOR as FC2,
    FRECUENCIA_MUESTREO as FS,
    ANCHO_BANDA,
)


def espectro(audio):
    # Promedio de periodogramas con ventana Hann, sin normalizar cada audio.
    n = min(8192, len(audio))
    if n < 4:
        return np.array([]), np.array([])
    ventana = np.hanning(n)
    potencia = np.zeros(n // 2 + 1)
    cantidad = 0
    for inicio in range(0, len(audio) - n + 1, n // 2):
        potencia += np.abs(np.fft.rfft(audio[inicio:inicio+n] * ventana))**2
        cantidad += 1
    potencia /= cantidad * FS * np.sum(ventana**2)
    potencia[1:-1 if n % 2 == 0 else None] *= 2
    return np.fft.rfftfreq(n, 1 / FS), 10 * np.log10(np.maximum(potencia, 1e-14))


class Graficas:
    def __init__(self):
        self.fig, (self.temporal, self.espectral) = plt.subplots(2, 1, figsize=(11, 7))
        self.fig.subplots_adjust(bottom=0.23, hspace=0.5)
        self.fig.suptitle(
            "Butterworth pasabandas | " + str(FC1) + "–"
            + str(FC2) + " Hz | BW: " + str(ANCHO_BANDA)
            + " Hz | fs: " + str(FS) + " Hz"
        )
        self.lineas_t, self.lineas_f = [], []
        for eje, lineas in [(self.temporal, self.lineas_t), (self.espectral, self.lineas_f)]:
            for nombre, color in [("Original", "#2364aa"), ("Filtrada", "#df6500")]:
                lineas.append(eje.plot([], [], label=nombre, color=color, linewidth=1)[0])
            eje.grid(alpha=0.25)
            eje.legend(loc="upper right")
        self.temporal.set(xlabel="Tiempo (s), último bloque visible", ylabel="Amplitud")
        self.espectral.set(
            xlabel="Frecuencia (Hz)", ylabel="Potencia (dBFS/Hz)",
            xlim=(0, FS / 2), ylim=(-140, 0), title="Espectros con la misma referencia",
        )
        self.espectral.axvspan(0, FC1, color="gray", alpha=0.12)
        self.espectral.axvspan(FC1, FC2, color="green", alpha=0.12)
        self.espectral.axvspan(FC2, FS / 2, color="gray", alpha=0.12)
        for frecuencia in (FC1, FC2):
            self.espectral.axvline(frecuencia, color="green", linestyle="--", linewidth=0.8)
        self.espectral.text(0.02, 0.05, "Verde: paso | Gris: rechazo", transform=self.espectral.transAxes)
        self.original = Button(self.fig.add_axes([0.13, 0.09, 0.22, 0.055]), "Escuchar original")
        self.filtrada = Button(self.fig.add_axes([0.39, 0.09, 0.22, 0.055]), "Escuchar filtrada")
        self.detener = Button(self.fig.add_axes([0.65, 0.09, 0.22, 0.055]), "Detener")
        self.estado = self.fig.text(0.08, 0.025, "Grabando… habla al micrófono.", fontsize=9)

    def actualizar(self, original, filtrada):
        for audio, linea_t, linea_f in zip(
            (original, filtrada), self.lineas_t, self.lineas_f
        ):
            tramo = audio[-4096:]
            linea_t.set_data(np.arange(len(tramo)) / FS, tramo)
            linea_f.set_data(*espectro(audio))
        self.temporal.set_xlim(0, max(1 / FS, min(len(original), 4096) / FS))
        pico = max(0.05, np.max(np.abs(original[-4096:])), np.max(np.abs(filtrada[-4096:])))
        self.temporal.set_ylim(-1.1 * pico, 1.1 * pico)
        self.fig.canvas.draw_idle()

    def mensaje(self, texto):
        self.estado.set_text(texto)
        self.fig.canvas.draw_idle()
