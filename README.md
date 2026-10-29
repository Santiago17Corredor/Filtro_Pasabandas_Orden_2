# Filtro de audio

```powershell
python -m pip install -r requirements.txt
python main.py
```

El programa captura audio del micrófono a **44100 Hz**, aplica un filtro
fijo de **300–3300 Hz** y compara la entrada y la salida en gráficas en vivo.

## Cómo se usa

1. **Grabar**: empieza la captura. La grabación dura lo que quieras
   (máximo 5 min como tope de seguridad); el indicador rojo muestra el tiempo.
2. **Detener grabación**: termina la toma. Se muestra la grabación completa y
   el espectro de toda la toma.
3. **Escuchar original / Escuchar filtrada**: reproducen la toma completa con
   la misma ganancia para poder compararlas. **Detener audio** corta la
   reproducción.
4. **Grabar de nuevo**: descarta la toma anterior y empieza otra (el filtro
   arranca desde cero en cada toma).

Los botones que no aplican en cada momento aparecen en gris.

## Archivos

- `captura.py`: recibe el audio del micrófono (una instancia por toma).
- `filtro.py`: aplica directamente la ecuación en diferencias.
- `graficas.py`: ventana, gráficas en vivo y botones.
- `reproduccion.py`: reproduce los audios con una ganancia común.
- `configuracion.py`: valores fijos de la captura y la banda.
- `main.py`: crea cada toma (micrófono + memoria del filtro) y abre la ventana.
