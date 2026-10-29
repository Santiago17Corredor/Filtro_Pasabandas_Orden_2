import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from matplotlib.widgets import Button

from configuracion import (
    DURACION_MAXIMA,
    FRECUENCIA_CORTE_INFERIOR as FC1,
    FRECUENCIA_CORTE_SUPERIOR as FC2,
    FRECUENCIA_MUESTREO as FS,
)
from reproduccion import (
    detener as detener_audio,
    ganancia_comun,
    reproducir,
    reproduciendo,
)

COLOR_ORIGINAL = "#9a9a9a"
COLOR_FILTRADA = "#1f5fbf"
COLOR_GRABANDO = "#b3261e"

VENTANA_VIVO = 4096
VENTANA_ESPECTRO = 8192


def espectro(audio):
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


def resumen_temporal(audio, columnas=2000):
    if len(audio) <= 2 * columnas:
        return np.arange(len(audio)) / FS, audio
    paso = len(audio) // columnas
    tramos = audio[:paso * columnas].reshape(columnas, paso)
    y = np.empty(2 * columnas)
    y[0::2] = tramos.min(axis=1)
    y[1::2] = tramos.max(axis=1)
    x = np.repeat((np.arange(columnas) + 0.5) * paso / FS, 2)
    return x, y


def formato_tiempo(segundos):
    segundos = int(segundos)
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


class Graficas:
    def __init__(self):
        plt.rcParams.update({
            "font.size": 9,
            "text.color": "#333333",
            "axes.edgecolor": "#aaaaaa",
            "axes.labelcolor": "#666666",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": "#666666",
            "ytick.color": "#666666",
            "axes.grid": True,
            "grid.color": "#ebebeb",
            "grid.linewidth": 0.6,
        })
        self.fig = plt.figure(figsize=(10, 6.5), facecolor="white")
        try:
            self.fig.canvas.manager.set_window_title("Filtro pasabandas")
        except AttributeError:
            pass
        self._limpiar_barra()

        self.fig.text(0.07, 0.945,
                      f"Filtro pasabandas Butterworth · {FC1}–{FC2} Hz · fs {FS} Hz",
                      fontsize=10, color="#666666", va="center")
        self.indicador = self.fig.text(0.97, 0.945, "", ha="right", va="center", fontsize=10)

        self.temporal = self.fig.add_axes([0.07, 0.645, 0.90, 0.24])
        self.espectral = self.fig.add_axes([0.07, 0.245, 0.90, 0.26])

        self.lineas_t, self.lineas_f = [], []
        for eje, lineas in [(self.temporal, self.lineas_t), (self.espectral, self.lineas_f)]:
            for nombre, color, orden in [("Original", COLOR_ORIGINAL, 2), ("Filtrada", COLOR_FILTRADA, 3)]:
                lineas.append(eje.plot([], [], label=nombre, color=color, linewidth=0.8, zorder=orden)[0])
            eje.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2, frameon=False)
        self.temporal.set_title("Señal", loc="left", fontsize=9, color="#666666")
        self.temporal.set(xlabel="Tiempo (s)", ylabel="Amplitud", xlim=(0, VENTANA_VIVO / FS))
        self.espectral.set_title("Espectro", loc="left", fontsize=9, color="#666666")
        self.espectral.set(
            xlabel="Frecuencia (Hz)", ylabel="Potencia (dBFS/Hz)",
            xlim=(0, FS / 2), ylim=(-140, 0),
        )
        self.espectral.axvspan(FC1, FC2, color=COLOR_FILTRADA, alpha=0.07, linewidth=0)
        for frecuencia in (FC1, FC2):
            self.espectral.axvline(frecuencia, color="#888888", linestyle=":", linewidth=0.8)
        self.espectral.text((FC1 + FC2) / 2, -8, "banda de paso", ha="center",
                            fontsize=8, color="#888888")

        self.botones = {}
        for i, (clave, texto) in enumerate([
            ("grabar", "Grabar"),
            ("original", "Escuchar original"),
            ("filtrada", "Escuchar filtrada"),
        ]):
            eje = self.fig.add_axes([0.07 + i * 0.21, 0.075, 0.19, 0.065])
            for borde in eje.spines.values():
                borde.set_visible(False)
            eje.set_navigate(False)
            boton = Button(eje, texto, color="#efefef", hovercolor="#e2e2e2")
            boton.label.set_fontsize(10)
            self.botones[clave] = boton

        self.texto_estado = self.fig.text(0.07, 0.035, "", fontsize=9, color="#666666", va="center")

    def _limpiar_barra(self):
        barra = self.fig.canvas.toolbar
        if barra is None:
            return
        try:
            for nombre in ("Subplots",):
                if nombre in getattr(barra, "_buttons", {}):
                    barra._buttons[nombre].pack_forget()
            for metodo in ("configure_subplots", "edit_parameters"):
                if metodo in getattr(barra, "_actions", {}):
                    barra._actions[metodo].setVisible(False)
        except Exception:
            pass

    def _reiniciar_zoom(self):
        barra = self.fig.canvas.toolbar
        if barra is not None:
            barra.update()

    def mostrar(self, nueva_grabacion):
        self.nueva_grabacion = nueva_grabacion
        self.captura = None
        self.procesar_bloque = None
        self.grabando = False
        self.sonando = None
        self.audios = {}
        self.ganancia = 1.0
        self._vaciar_buffers()

        self.botones["grabar"].on_clicked(self.alternar_grabacion)
        self.botones["original"].on_clicked(lambda evento: self.escuchar("original"))
        self.botones["filtrada"].on_clicked(lambda evento: self.escuchar("filtrado"))
        self.fig.canvas.mpl_connect("close_event", self.cerrar)

        self.temporizador = self.fig.canvas.new_timer(interval=100)
        self.temporizador.add_callback(self.tic)
        self._refrescar()
        self.mensaje("Pulsa Grabar para empezar.")
        try:
            self.temporizador.start()
            plt.show()
        except KeyboardInterrupt:
            print("Ejecución detenida.")
        finally:
            self.cerrar()
            plt.close(self.fig)

    def _vaciar_buffers(self):
        self.originales = []
        self.filtrados = []
        self.ventana_original = np.array([])
        self.ventana_filtrada = np.array([])

    def alternar_grabacion(self, evento=None):
        if self.grabando:
            self.captura.detener()
            self._leer_bloques()
            self._terminar("Grabación detenida.")
        else:
            self._iniciar_grabacion()

    def _iniciar_grabacion(self):
        detener_audio()
        self.sonando = None
        captura = None
        try:
            captura, procesar = self.nueva_grabacion()
            captura.iniciar()
        except (sd.PortAudioError, ValueError, OSError) as error:
            if captura is not None:
                captura.detener()
            self.mensaje("No se pudo abrir el micrófono: " + str(error))
            self._refrescar()
            return

        self.captura, self.procesar_bloque = captura, procesar
        self.audios = {}
        self._vaciar_buffers()
        for linea in self.lineas_t + self.lineas_f:
            linea.set_data([], [])
        self.temporal.set(xlim=(0, VENTANA_VIVO / FS))
        for eje in (self.temporal, self.espectral):
            eje.set_navigate(False)
        self.grabando = True
        self._refrescar()
        self.mensaje("Grabando. Pulsa Detener para terminar.")

    def escuchar(self, nombre):
        if self.grabando:
            self.mensaje("Detén la grabación antes de escuchar.")
            return
        if nombre not in self.audios:
            self.mensaje("Primero graba un audio.")
            return
        if self.sonando == nombre:
            detener_audio()
            self.sonando = None
            self.mensaje("Reproducción detenida.")
            self._refrescar()
            return
        try:
            reproducir(self.audios[nombre], self.ganancia)
        except sd.PortAudioError as error:
            self.mensaje("No se pudo reproducir: " + str(error))
            return
        self.sonando = nombre
        self.mensaje("Reproduciendo " + ("original." if nombre == "original" else "filtrada."))
        self._refrescar()

    def cerrar(self, evento=None):
        self.temporizador.stop()
        detener_audio()
        if self.captura is not None:
            self.captura.detener()

    def tic(self):
        if self.grabando:
            try:
                hubo_audio = self._leer_bloques()
                if self.captura.terminada.is_set() and self.captura.cola.empty():
                    if self.captura.alcanzo_tope():
                        self._terminar(f"Se alcanzó el máximo de {DURACION_MAXIMA // 60} min.")
                    else:
                        self._terminar("La captura se cerró.")
                elif hubo_audio:
                    self._dibujar_vivo()
            except (ValueError, ArithmeticError, sd.PortAudioError) as error:
                self._terminar("Error: " + str(error))
        elif self.sonando and not reproduciendo():
            self.sonando = None
            self.mensaje("Reproducción terminada.")
            self._refrescar()

    def _leer_bloques(self):
        hubo_audio = False
        for bloque in self.captura.bloques():
            salida = self.procesar_bloque(bloque)
            self.originales.append(bloque)
            self.filtrados.append(salida)
            self.ventana_original = np.concatenate((self.ventana_original, bloque))[-VENTANA_ESPECTRO:]
            self.ventana_filtrada = np.concatenate((self.ventana_filtrada, salida))[-VENTANA_ESPECTRO:]
            hubo_audio = True
        return hubo_audio

    def _terminar(self, motivo):
        self.captura.detener()
        self.grabando = False
        for eje in (self.temporal, self.espectral):
            eje.set_navigate(True)
        if self.originales:
            original = np.concatenate(self.originales)
            filtrada = np.concatenate(self.filtrados)
            self.originales, self.filtrados = [], []
            self.audios = {"original": original, "filtrado": filtrada}
            self.ganancia = ganancia_comun(original, filtrada)
            self._dibujar_completo()
            texto = motivo + f" Duración {len(original) / FS:.1f} s."
        else:
            texto = motivo + " No se recibió audio."
        if self.captura.advertencias:
            texto += "\nIncidencias: " + "; ".join(self.captura.advertencias)
        self.mensaje(texto)
        self._refrescar()

    def _dibujar_vivo(self):
        for audio, linea_t, linea_f in zip(
            (self.ventana_original, self.ventana_filtrada), self.lineas_t, self.lineas_f
        ):
            tramo = audio[-VENTANA_VIVO:]
            linea_t.set_data(np.arange(len(tramo)) / FS, tramo)
            linea_f.set_data(*espectro(audio))
        pico = max(0.05, np.max(np.abs(self.ventana_original[-VENTANA_VIVO:])),
                   np.max(np.abs(self.ventana_filtrada[-VENTANA_VIVO:])))
        self.temporal.set_ylim(-1.1 * pico, 1.1 * pico)
        self._actualizar_indicador()
        self.fig.canvas.draw_idle()

    def _dibujar_completo(self):
        original, filtrada = self.audios["original"], self.audios["filtrado"]
        for audio, linea_t, linea_f in zip((original, filtrada), self.lineas_t, self.lineas_f):
            linea_t.set_data(*resumen_temporal(audio))
            linea_f.set_data(*espectro(audio))
        self.temporal.set_xlim(0, len(original) / FS)
        pico = max(0.05, np.max(np.abs(original)), np.max(np.abs(filtrada)))
        self.temporal.set_ylim(-1.1 * pico, 1.1 * pico)
        self.espectral.set(xlim=(0, FS / 2), ylim=(-140, 0))
        self._reiniciar_zoom()

    def mensaje(self, texto):
        self.texto_estado.set_text(texto)
        self.fig.canvas.draw_idle()

    def _actualizar_indicador(self):
        if self.grabando:
            self.indicador.set_text("Grabando " + formato_tiempo(self.captura.recibidas / FS))
            self.indicador.set_color(COLOR_GRABANDO)
        elif self.audios:
            self.indicador.set_text(formato_tiempo(len(self.audios["original"]) / FS))
            self.indicador.set_color("#666666")
        else:
            self.indicador.set_text("")

    def _boton(self, clave, activo, texto, resaltado=False):
        boton = self.botones[clave]
        boton.label.set_text(texto)
        if resaltado:
            color, hover, letra = "#262626", "#000000", "white"
        elif activo:
            color, hover, letra = "#efefef", "#e2e2e2", "#262626"
        else:
            color, hover, letra = "#f6f6f6", "#f6f6f6", "#bbbbbb"
        boton.color, boton.hovercolor = color, hover
        boton.ax.set_facecolor(color)
        boton.label.set_color(letra)

    def _refrescar(self):
        hay_audio = bool(self.audios)
        if self.grabando:
            self._boton("grabar", True, "Detener", resaltado=True)
        else:
            self._boton("grabar", True, "Grabar de nuevo" if hay_audio else "Grabar")
        for clave, nombre in (("original", "original"), ("filtrada", "filtrado")):
            if self.sonando == nombre:
                self._boton(clave, True, "Detener", resaltado=True)
            else:
                self._boton(clave, hay_audio and not self.grabando, "Escuchar " + clave)
        self._actualizar_indicador()
        self.fig.canvas.draw_idle()