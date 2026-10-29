# Filtro de audio

```powershell
python -m pip install -r requirements.txt
python main.py
```

El programa captura audio durante 10 segundos a **44100 Hz**, aplica un filtro
fijo de **300–3300 Hz** y compara la entrada y la salida en gráficas en vivo.
Al terminar, los botones permiten escuchar ambos audios. **Detener** interrumpe
la captura o la reproducción.

- `captura.py`: recibe el audio del micrófono.
- `filtro.py`: aplica directamente la ecuación en diferencias.
- `graficas.py`: actualiza las gráficas en vivo y maneja los botones de audio.
- `reproduccion.py`: reproduce los audios con una ganancia común.
- `configuracion.py`: valores fijos de la captura y la banda.
- `main.py`: prepara la captura, define cómo filtrar cada bloque y abre la ventana.
