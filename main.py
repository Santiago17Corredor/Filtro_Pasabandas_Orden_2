from captura import CapturaAudio
from configuracion import DURACION_MAXIMA
from filtro import aplicar_filtro
from graficas import Graficas


def nueva_grabacion():
    captura = CapturaAudio(DURACION_MAXIMA)
    memoria = [0.0] * 8

    def procesar_bloque(bloque):
        return aplicar_filtro(bloque, memoria)

    return captura, procesar_bloque


def ejecutar():
    graficas = Graficas()
    graficas.mostrar(nueva_grabacion)


if __name__ == "__main__":
    ejecutar()