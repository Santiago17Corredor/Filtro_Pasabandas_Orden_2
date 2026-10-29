from captura import CapturaAudio
from configuracion import DURACION_GRABACION
from filtro import aplicar_filtro
from graficas import Graficas


def ejecutar():
    # 1. Preparar el micrófono y la memoria del filtro.
    captura = CapturaAudio(DURACION_GRABACION)
    memoria = [0.0] * 8

    # 2. Cada bloque de audio pasa por la misma ecuación y memoria.
    def procesar_bloque(bloque):
        return aplicar_filtro(bloque, memoria)

    # 3. Grabar, mostrar los resultados en vivo y permitir escuchar los audios.
    graficas = Graficas()
    graficas.mostrar(captura, procesar_bloque)


if __name__ == "__main__":
    ejecutar()
