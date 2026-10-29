# Laboratorio: filtro Butterworth pasabandas

## Ejecutar

```powershell
python -m pip install -r requirements.txt
python main.py
```

1. Observar la ecuación del filtro fijo y pulsar **Iniciar grabación**.
2. Hablar al micrófono durante 10 segundos y comparar las gráficas en vivo.
3. Usar **Escuchar original** y **Escuchar filtrada** al terminar.

**Detener** finaliza anticipadamente la captura o interrumpe la reproducción.
Cerrar la ventana inicial cancela el inicio. La duración se encuentra en
`DURACION_GRABACION`, dentro de `configuracion.py`.

## Banda elegida

- Corte inferior: **300 Hz**.
- Corte superior: **3300 Hz**.
- Ancho de banda: **3000 Hz**.
- Frecuencia de muestreo: **44100 Hz**.

La elección toma como referencia la banda telefónica convencional de
[300–3400 Hz de la UIT](https://www.itu.int/rec/T-REC-P.342), ajustando el corte
superior a 3300 Hz para respetar el máximo de 3000 Hz de ancho de banda del
laboratorio. Se busca conservar un rango útil para entender la voz y mostrar
la atenuación de componentes graves y agudos al comparar ambos audios.

Los cortes cumplen el rango original del laboratorio: ancho de banda entre
2000 y 3000 Hz y frecuencias de corte no superiores a 5000 Hz.

El programa utiliza coeficientes numéricos fijos escritos en `filtro.py`,
obtenidos previamente mediante el método del PDF. Las frecuencias de
`configuracion.py` describen esos coeficientes; un cambio de banda requiere
actualizar también los coeficientes.

## Archivos

- `configuracion.py`: constantes de la banda, el muestreo y la captura.
- `filtro.py`: coeficientes fijos y aplicación de la ecuación en diferencias.
- `ecuacion.py`: presentación de la ecuación con símbolos matemáticos.
- `captura.py`: captura mono desde el micrófono por bloques.
- `graficas.py`: comparación temporal y espectral en la misma escala.
- `reproduccion.py`: reproducción de ambos audios con una ganancia común.
- `main.py`: coordinación de la captura, el filtrado y las ventanas.
- `diseno.py`: desarrollo matemático por funciones como apoyo para el informe.

Para ver únicamente la ecuación:

```powershell
python filtro.py
```

Para consultar el cálculo de los coeficientes:

```powershell
python diseno.py
```

`main.py` utiliza directamente los números de `filtro.py`. `diseno.py` se
ejecuta de manera independiente y conserva las funciones de prewarping,
cálculo de B y omega0, transformación pasabandas y transformación bilineal.

## Correspondencia con el PDF

El diseño sigue el ejemplo 4, páginas 26–27 de *Sección Filtrado Digital y
Compresión* (Fabian Velasquez Clavijo, 2026). El prototipo de orden 2 produce
un pasabandas de grado 4. Se usa el ancho de banda analógico positivo
`B = omega2 - omega1`; en la sustitución numérica inferior de la página 26
la resta aparece invertida.

La ecuación se aplica muestra a muestra conservando cuatro entradas y cuatro
salidas entre bloques. Cada grabación comienza con esa memoria en cero.

Los espectros son promedios de periodogramas con ventana Hann, en dBFS/Hz.
En vivo se usan las últimas 8192 muestras; al terminar se promedia la
grabación. La gráfica temporal muestra las últimas 4096 muestras. El
filtrado y la reproducción utilizan el audio completo.
