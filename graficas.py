import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from matplotlib.widgets import Button

from reproduccion import detener, ganancia_comun, reproducir

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


    def mostrar(self, captura, procesar_bloque):
        # Conectar la captura, el procesamiento y los botones de la ventana.
        self.captura = captura
        self.procesar_bloque = procesar_bloque
        self.originales = []
        self.filtrados = []
        self.ventana_original = np.array([])
        self.ventana_filtrada = np.array([])
        self.audios = {}
        self.ganancia = 1.0

        self.original.on_clicked(self.escuchar_original)
        self.filtrada.on_clicked(self.escuchar_filtrada)
        self.detener.on_clicked(self.parar_audio)
        self.fig.canvas.mpl_connect("close_event", self.cerrar)

        self.temporizador = self.fig.canvas.new_timer(interval=100)
        self.temporizador.add_callback(self.actualizar_audio)
        try:
            self.captura.iniciar()
            self.temporizador.start()
            plt.show()
        except KeyboardInterrupt:
            print("Ejecución detenida.")
        except sd.PortAudioError as error:
            print("No se pudo iniciar el audio:", error)
        finally:
            self.cerrar()
            plt.close(self.fig)

    def actualizar_audio(self):
        # Leer los bloques disponibles, filtrarlos y renovar las gráficas.
        hubo_audio = False
        try:
            for bloque in self.captura.bloques():
                salida = self.procesar_bloque(bloque)
                self.originales.append(bloque)
                self.filtrados.append(salida)
                self.ventana_original = np.concatenate((self.ventana_original, bloque))[-8192:]
                self.ventana_filtrada = np.concatenate((self.ventana_filtrada, salida))[-8192:]
                hubo_audio = True

            if self.captura.terminada.is_set() and self.captura.cola.empty():
                self.finalizar_grabacion()
                return False

            if hubo_audio:
                self.actualizar(self.ventana_original, self.ventana_filtrada)
                transcurrido = round(self.captura.recibidas / FS, 1)
                duracion = round(self.captura.total / FS, 1)
                self.mensaje("Grabando: " + str(transcurrido) + " / " + str(duracion) + " s")
        except (ValueError, ArithmeticError, sd.PortAudioError) as error:
            self.parar_audio()
            self.mensaje(str(error))
            return False

    def finalizar_grabacion(self):
        # Reunir la grabación completa para analizarla y escucharla.
        self.captura.detener()
        if self.originales:
            self.audios["original"] = np.concatenate(self.originales)
            self.audios["filtrado"] = np.concatenate(self.filtrados)
            self.ganancia = ganancia_comun(self.audios["original"], self.audios["filtrado"])
            self.actualizar(self.audios["original"], self.audios["filtrado"])
            self.mensaje("Grabación terminada. Usa los botones para comparar los audios.")
        else:
            self.mensaje("La captura terminó sin muestras de audio.")
        if self.captura.advertencias:
            self.mensaje("Captura con incidencias: " + "; ".join(self.captura.advertencias))

    def escuchar_original(self, evento):
        self.escuchar("original")

    def escuchar_filtrada(self, evento):
        self.escuchar("filtrado")

    def escuchar(self, nombre):
        if nombre not in self.audios:
            self.mensaje("Espera a que termine la grabación o pulsa Detener.")
            return
        try:
            reproducir(self.audios[nombre], self.ganancia)
            self.mensaje("Reproduciendo audio " + nombre + ".")
        except sd.PortAudioError as error:
            self.mensaje("No se pudo reproducir: " + str(error))

    def parar_audio(self, evento=None):
        detener()
        self.captura.detener()

    def cerrar(self, evento=None):
        self.temporizador.stop()
        self.parar_audio()
