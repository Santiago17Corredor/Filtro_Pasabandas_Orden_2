"""Grabar, filtrar, graficar en vivo y escuchar ambos audios."""

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

from captura import CapturaAudio
from configuracion import DURACION_GRABACION, FRECUENCIA_MUESTREO as FS
from filtro import aplicar_filtro
from graficas import Graficas
from reproduccion import detener, ganancia_comun, reproducir


def ejecutar(segundos=DURACION_GRABACION, dispositivo=None):
    memoria = [0.0] * 8
    captura = CapturaAudio(segundos, dispositivo)
    graficas = Graficas()
    originales, filtrados = [], []
    ventana_x = ventana_y = np.array([])
    audios = {}
    ganancia = 1.0

    def escuchar(nombre):
        if nombre not in audios:
            graficas.mensaje("Espera a que termine la grabación o pulsa Detener.")
            return
        try:
            reproducir(audios[nombre], ganancia)
            graficas.mensaje("Reproduciendo audio " + nombre + ".")
        except sd.PortAudioError as error:
            graficas.mensaje("No se pudo reproducir: " + str(error))

    def parar(evento=None):
        detener()
        captura.detener()

    def actualizar():
        nonlocal ventana_x, ventana_y, ganancia
        hubo_audio = False
        try:
            for bloque in captura.bloques():
                salida = aplicar_filtro(bloque, memoria)
                originales.append(bloque)
                filtrados.append(salida)
                ventana_x = np.concatenate((ventana_x, bloque))[-8192:]
                ventana_y = np.concatenate((ventana_y, salida))[-8192:]
                hubo_audio = True
            if captura.terminada.is_set() and captura.cola.empty():
                captura.detener()
                if originales:
                    audios["original"] = np.concatenate(originales)
                    audios["filtrado"] = np.concatenate(filtrados)
                    ganancia = ganancia_comun(audios["original"], audios["filtrado"])
                    graficas.actualizar(audios["original"], audios["filtrado"])
                    graficas.mensaje("Grabación terminada. Usa los botones para comparar los audios.")
                else:
                    graficas.mensaje("La captura terminó sin muestras de audio.")
                if captura.advertencias:
                    graficas.mensaje("Captura con incidencias: " + "; ".join(captura.advertencias))
                return False
            if hubo_audio:
                graficas.actualizar(ventana_x, ventana_y)
                graficas.mensaje("Grabando: " + str(round(captura.recibidas / FS, 1))
                                 + " / " + str(segundos) + " s")
        except (ValueError, ArithmeticError, sd.PortAudioError) as error:
            parar()
            graficas.mensaje(str(error))
            return False

    graficas.original.on_clicked(lambda evento: escuchar("original"))
    graficas.filtrada.on_clicked(lambda evento: escuchar("filtrado"))
    graficas.detener.on_clicked(parar)
    temporizador = graficas.fig.canvas.new_timer(interval=100)
    temporizador.add_callback(actualizar)

    def cerrar(evento=None):
        temporizador.stop()
        parar()

    graficas.fig.canvas.mpl_connect("close_event", cerrar)
    try:
        captura.iniciar()
        temporizador.start()
        plt.show()
    finally:
        cerrar()
        plt.close(graficas.fig)


if __name__ == "__main__":
    try:
        ejecutar()
    except sd.PortAudioError as error:
        print("No se pudo iniciar el audio:", error)
