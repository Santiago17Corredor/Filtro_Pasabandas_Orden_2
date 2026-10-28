# Laboratorio: filtro Butterworth pasabandas

## Ejecutar

```powershell
python -m pip install -r requirements.txt
python main.py
```

1. Escribir **Fc1** y **Fc2** en las dos casillas de la interfaz.
2. Pulsar **Calcular filtro** para ver la ecuación resultante.
3. Pulsar **Iniciar grabación** y hablar al micrófono durante 10 segundos.
4. Comparar las señales y sus espectros en vivo.
5. Escuchar el audio original y el filtrado con los botones de las gráficas.

**Detener** termina la captura antes de los 10 segundos o interrumpe la
reproducción. Cerrar cualquiera de las ventanas iniciales cancela el inicio.

El muestreo es fijo a **44100 Hz**. La duración se encuentra en
`DURACION_GRABACION`, dentro de `configuracion.py`.

## Validación de las frecuencias

Se comprueban estas dos condiciones, con los límites solicitados para esta versión:

```text
0 < Fc1 < Fc2 <= 5000 Hz
200 <= BW <= 3000 Hz
```

Aquí `BW = Fc2 - Fc1` está en Hz. El mínimo de **200 Hz** corresponde al ajuste
solicitado para el programa; el enunciado original del PDF establece 2000 Hz.

## Diseño, paso a paso

Las funciones de `filtro.py` siguen este orden:

1. `prewarping(fc1, fc2)`: devuelve las dos frecuencias ajustadas, en rad/s.
2. `calcular_B_y_omega0(omega1, omega2)`: devuelve el ancho de banda analógico
   `B = omega2 - omega1` y la frecuencia central `omega0 = sqrt(omega1*omega2)`.
3. `transformar_prototipo(B, omega0)`: transforma el prototipo Butterworth
   pasabajas `1/(s² + sqrt(2)*s + 1)` en pasabandas. Devuelve su numerador y
   denominador analógicos, ordenados desde la mayor potencia de `s`.
4. `transformacion_bilineal(numerador, denominador)`: sustituye
   `s = 2*fs*(1-z⁻¹)/(1+z⁻¹)` y devuelve los polinomios digitales. Las pequeñas
   listas `p4` a `p0` son los productos de las potencias desarrolladas; junto a
   cada lista está escrito el producto al que corresponde.
5. `obtener_coeficientes(numerador_z, denominador_z)`: divide por el primer
   coeficiente del denominador para obtener `b` y `a`, con `a[0] = 1`.
6. `aplicar_ecuacion_diferencias(audio, b, a, memoria)`: utiliza esos coeficientes
   para calcular las muestras de salida. La memoria conserva cuatro entradas y
   cuatro salidas entre los bloques de la misma grabación.

`disenar_filtro(fc1, fc2)` llama a los cinco pasos de diseño, una sola vez al
escoger las frecuencias. Durante la captura se aplica únicamente la ecuación en
diferencias. Los coeficientes están ordenados por potencias de `z⁻¹`:

```text
b = [b0, b1, b2, b3, b4]
a = [1, a1, a2, a3, a4]
```

## Archivos

- `configuracion.py`: constantes y validación de las frecuencias.
- `interfaz.py`: las dos casillas para elegir Fc1 y Fc2.
- `filtro.py`: funciones matemáticas del diseño y del filtrado.
- `ecuacion.py`: ecuación presentada con símbolos matemáticos mediante Matplotlib.
- `captura.py`: captura mono por bloques desde el micrófono.
- `graficas.py`: señales y espectros en la misma escala para comparar.
- `reproduccion.py`: reproducción de ambos audios con una ganancia común.
- `main.py`: conecta las funciones y las ventanas.

Para ver la ecuación sin activar el micrófono:

```powershell
python filtro.py
```

## Correspondencia con el PDF

El diseño sigue el ejemplo 4, páginas 26–27 de *Sección Filtrado Digital y
Compresión* (Fabian Velasquez Clavijo, 2026). El prototipo de orden 2 se
transforma en un pasabandas de grado 4. Se conserva el ancho de banda analógico
positivo `B = omega2 - omega1`, según la definición del PDF; en la sustitución
numérica inferior de la página 26 la resta aparece invertida.

Los espectros son promedios de periodogramas con ventana Hann, en dBFS/Hz. En
vivo se usan las últimas 8192 muestras; al terminar se promedia la grabación.
La gráfica temporal muestra las últimas 4096 muestras. El filtrado y la
reproducción utilizan el audio completo.
