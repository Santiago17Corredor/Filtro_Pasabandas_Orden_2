"""Presentación matemática de la misma ecuación que aplica filtro.py."""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def terminos(valores, variables):
    texto = ""
    for valor, variable in zip(valores, variables):
        signo = " - " if valor < 0 else " + "
        if not texto:
            signo = "-" if valor < 0 else ""
        texto += signo + str(round(abs(float(valor)), 8)) + r"\," + variable
    return texto


def mostrar_ecuacion(coeficientes, continuar=False):
    configuracion = coeficientes.configuracion
    b, a = coeficientes.b, coeficientes.a
    print("Corte inferior:", configuracion.fc1, "Hz")
    print("Corte superior:", configuracion.fc2, "Hz")
    print("Ancho de banda:", configuracion.ancho_banda, "Hz")
    print("Frecuencia de muestreo:", configuracion.fs, "Hz")

    fig = plt.figure(figsize=(12, 7))
    fig.canvas.manager.set_window_title("Ecuación del filtro")
    fig.text(0.06, 0.92, "Filtro Butterworth pasabandas", fontsize=21, weight="bold")
    parametros = (
        r"$f_{c1}=" + str(configuracion.fc1) + r"\ \mathrm{Hz},\quad f_{c2}="
        + str(configuracion.fc2) + r"\ \mathrm{Hz},\quad f_s="
        + str(configuracion.fs) + r"\ \mathrm{Hz}$"
    )
    fig.text(0.06, 0.84, parametros, fontsize=17)
    fig.text(0.06, 0.73, "Función de transferencia digital", fontsize=13)
    fig.text(
        0.06, 0.62,
        r"$H_{BP}(z)=\frac{b_0+b_2z^{-2}+b_4z^{-4}}"
        r"{1+a_1z^{-1}+a_2z^{-2}+a_3z^{-3}+a_4z^{-4}}$",
        fontsize=23,
    )
    fig.text(0.06, 0.50, "Ecuación numérica aplicada a cada muestra", fontsize=13)
    entrada = terminos([b[0], b[2], b[4]], ["x(n)", "x(n-2)", "x(n-4)"])
    salida_1 = terminos([-a[1], -a[2]], ["y(n-1)", "y(n-2)"])
    salida_2 = terminos([-a[3], -a[4]], ["y(n-3)", "y(n-4)"])
    fig.text(0.06, 0.41, "$y(n)=" + entrada + "$", fontsize=19)
    fig.text(0.15, 0.32, "$" + ("+" if -a[1] >= 0 else "") + salida_1 + "$", fontsize=19)
    fig.text(0.15, 0.23, "$" + ("+" if -a[3] >= 0 else "") + salida_2 + "$", fontsize=19)
    fig.text(0.06, 0.14, "Vista redondeada a 8 decimales; el cálculo conserva toda la precisión.", fontsize=10)

    iniciar = False

    def aceptar(evento):
        nonlocal iniciar
        iniciar = True
        plt.close(fig)

    if continuar:
        boton = Button(fig.add_axes([0.34, 0.035, 0.32, 0.065]), "Iniciar grabación")
        boton.on_clicked(aceptar)
    plt.show()
    return iniciar
