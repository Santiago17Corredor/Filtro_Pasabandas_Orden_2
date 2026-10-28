"""Captura mono a 44 100 Hz; el micrófono entrega los bloques a una cola."""

from queue import Empty, Queue
from threading import Event

import sounddevice as sd

from configuracion import FRECUENCIA_MUESTREO, TAMANO_BLOQUE


class CapturaAudio:
    def __init__(self, segundos, dispositivo=None):
        self.cola = Queue()
        self.terminada = Event()
        self.advertencias = set()
        self.total = round(segundos * FRECUENCIA_MUESTREO)
        self.recibidas = 0
        self.stream = sd.InputStream(
            samplerate=FRECUENCIA_MUESTREO, channels=1, dtype="float32",
            blocksize=TAMANO_BLOQUE, device=dispositivo,
            callback=self._capturar, finished_callback=self.terminada.set,
        )

    def _capturar(self, entrada, frames, tiempo, estado):
        if estado:
            self.advertencias.add(str(estado))
        cantidad = min(frames, self.total - self.recibidas)
        if cantidad > 0:
            self.cola.put(entrada[:cantidad, 0].copy())
            self.recibidas += cantidad
        if self.recibidas >= self.total:
            raise sd.CallbackStop

    def iniciar(self):
        self.stream.start()

    def bloques(self):
        while True:
            try:
                yield self.cola.get_nowait()
            except Empty:
                return

    def detener(self):
        if not self.stream.closed:
            try:
                self.stream.stop()
            finally:
                self.stream.close()
                self.terminada.set()
