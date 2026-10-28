# Filtro Butterworth pasabandas de voz

Laboratorio 1, tercer corte. Python, audio mono y muestreo fijo de **44 100 Hz**.

## Ejecutar

```powershell
python -m pip install -r requirements.txt
python main.py --fc1 1000 --fc2 3500 --duracion 10
```

Primero se imprimen los parámetros en la consola y aparece una ventana con la
función de transferencia y la ecuación numérica en notación matemática. Pulsa
**Iniciar grabación** para activar el micrófono y ver las señales y sus
espectros en vivo. Cerrar la ventana de la ecuación cancela el inicio. Al terminar, los botones **Escuchar original** y **Escuchar
filtrada** reproducen la misma grabación antes y después del filtro. **Detener**
finaliza anticipadamente la captura o interrumpe la reproducción. Cerrar la
ventana libera el micrófono y detiene el audio.

Las frecuencias se seleccionan con `--fc1` y `--fc2`, siempre en Hz:

```text
0 < fc1 < fc2 <= 5000
2000 <= fc2 - fc1 <= 3000
```

Para elegir otro micrófono:

```powershell
python main.py --dispositivos
python main.py --microfono 1 --fc1 2000 --fc2 5000
```

## Módulos

- `configuracion.py`: límites del enunciado y frecuencia de muestreo.
- `captura.py`: audio del micrófono por bloques.
- `filtro.py`: aplicación directa de la ecuación en diferencias, con memoria entre bloques.
- `ecuacion.py`: presentación de la función de transferencia y la recurrencia numérica.
- `graficas.py`: comparación temporal y espectral, con bandas de paso y rechazo marcadas.
- `reproduccion.py`: reproducción de ambos audios con la misma ganancia.
- `main.py`: selección de parámetros y coordinación.

Los espectros usan la misma escala de potencia en dBFS/Hz: promedio de
periodogramas con ventana Hann. En vivo se muestran las últimas 8192 muestras;
al terminar se promedia toda la grabación. La gráfica temporal muestra las
últimas 4096 muestras. El filtro y los audios conservan todas las muestras.

## Referencia del filtro

Se aplica la ecuación final del ejemplo 4, páginas 26–27 de *Sección Filtrado
Digital y Compresión* (Fabian Velasquez Clavijo, 2026), con prewarping y
transformación bilineal. El prototipo Butterworth de orden 2 produce el
pasabandas de grado 4 que aparece en ese ejemplo. Cambiar los cortes únicamente
evalúa los coeficientes de la fórmula final; el programa aplica la recurrencia
muestra a muestra y muestra los resultados del audio.

Se conserva `BW = wd2 - wd1`, la definición positiva del PDF. En la sustitución
numérica inferior de la página 26, la resta aparece invertida; copiar ese signo
produciría un filtro inestable.

Para ver únicamente la ecuación, sin activar el micrófono:

```powershell
python filtro.py --fc1 1000 --fc2 3500
```

La presentación utiliza [Mathtext de Matplotlib](https://matplotlib.org/stable/tutorials/text/mathtext.html) para dibujar
fracciones, subíndices y exponentes. Los números se redondean solo en la vista.
Las validaciones de selección se limitan a los cortes y al ancho de banda
del enunciado, y a una duración positiva y finita.
