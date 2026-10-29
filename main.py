from captura import CapturaAudio
from configuracion import DURACION_GRABACION
from filtro import aplicar_filtro
from graficas import Graficas


def ejecutar():
    #prepara micro y memoria
    captura = CapturaAudio(DURACION_GRABACION)
    memoria = [0.0] * 8

    #se procesa cada bloque de audio
    def procesar_bloque(bloque):
        return aplicar_filtro(bloque, memoria)

    #graficas en vivo y poder escuchar los audios original y filtrado
    graficas = Graficas()
    graficas.mostrar(captura, procesar_bloque)


if __name__ == "__main__":
    ejecutar()