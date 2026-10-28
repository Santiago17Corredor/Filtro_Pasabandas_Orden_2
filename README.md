# Laboratorio 1: filtro Butterworth pasabandas

Procesamiento de Señales e Imágenes, tercer corte. Implementación modular en Python
con frecuencia de muestreo fija de **44 100 Hz**.

## Primer commit: filtro matemático

- `configuracion.py`: valores permitidos por el enunciado.
- `filtro.py`: coeficientes explícitos y ecuación en diferencias con memoria entre bloques.

Condiciones para seleccionar las frecuencias, expresadas en Hz:

```text
0 < fc1 < fc2 <= 5000
2000 <= fc2 - fc1 <= 3000
```

Ejemplo: `fc1 = 1000`, `fc2 = 3500`, ancho de banda de `2500 Hz`.

Instalar las dependencias y mostrar la ecuación numérica:

```powershell
python -m pip install -r requirements.txt
python filtro.py --fc1 1000 --fc2 3500
```

Para procesar audio desde otro módulo:

```python
from configuracion import ConfiguracionFiltro
from filtro import FiltroPasabandas

filtro = FiltroPasabandas(ConfiguracionFiltro(fc1=1000, fc2=3500))
salida = filtro.procesar(bloque_mono)
```

Se conserva **la misma instancia** durante toda la grabación: las cuatro muestras
anteriores de entrada y salida se mantienen entre bloques. Cada grabación nueva
empieza en reposo.

## Correspondencia con el PDF

Fuente: *Sección Filtrado Digital y Compresión*, profesor Fabian Velasquez Clavijo,
2026, ejemplo 4 de las páginas 26–27; enunciado del laboratorio en la página 30.

Se utiliza el prototipo Butterworth `1/(s² + sqrt(2)*s + 1)`, la transformación
pasabandas del ejemplo y la transformación bilineal con prewarping de los dos
cortes. Los coeficientes finales están escritos explícitamente en `filtro.py`.

El prototipo de orden 2 se convierte en un pasabandas de **grado 4**, tal como
ocurre en el ejemplo del profesor. La ecuación aplicada es:

```text
y[n] = b0*x[n] + b2*x[n-2] + b4*x[n-4]
       - a1*y[n-1] - a2*y[n-2] - a3*y[n-3] - a4*y[n-4]
```

**Corrección de signo del ejemplo:** la guía define `BW = wc2 - wc1`, pero en
la sustitución numérica inferior de la página 26 aparece la resta invertida.
El código conserva la definición positiva: `BW = wd2 - wd1`, con los cortes
predeformados. La resta invertida produciría un filtro inestable. El ancho de
banda elegido en Hz y este `BW` analógico en rad/s son cantidades diferentes.

La interfaz, la captura, la reproducción y las gráficas se incorporarán en los
siguientes commits.
