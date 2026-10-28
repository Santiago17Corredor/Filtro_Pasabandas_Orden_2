import tkinter as tk
from tkinter import messagebox

from configuracion import ConfiguracionFiltro, FRECUENCIA_MUESTREO


def seleccionar_frecuencias():
    ventana = tk.Tk()
    ventana.title("Laboratorio: filtro pasabandas")
    ventana.resizable(False, False)
    seleccion = []

    tk.Label(ventana, text="Filtro Butterworth pasabandas", font=("Segoe UI", 17, "bold")).grid(
        row=0, column=0, columnspan=2, padx=30, pady=(24, 10)
    )
    tk.Label(ventana, text="Elige las dos frecuencias de corte en Hz.").grid(
        row=1, column=0, columnspan=2, pady=(0, 20)
    )
    tk.Label(ventana, text="Fc1: corte inferior (Hz)").grid(row=2, column=0, padx=20, pady=8)
    entrada_fc1 = tk.Entry(ventana, width=17, font=("Segoe UI", 12))
    entrada_fc1.insert(0, "1000")
    entrada_fc1.grid(row=2, column=1, padx=(0, 25), pady=8)

    tk.Label(ventana, text="Fc2: corte superior (Hz)").grid(row=3, column=0, padx=20, pady=8)
    entrada_fc2 = tk.Entry(ventana, width=17, font=("Segoe UI", 12))
    entrada_fc2.insert(0, "3500")
    entrada_fc2.grid(row=3, column=1, padx=(0, 25), pady=8)

    tk.Label(ventana, text="0 < Fc1 < Fc2 ≤ 5000 Hz\n200 ≤ BW ≤ 3000 Hz").grid(
        row=4, column=0, columnspan=2, pady=15
    )
    tk.Label(ventana, text="Frecuencia de muestreo: " + str(FRECUENCIA_MUESTREO) + " Hz").grid(
        row=5, column=0, columnspan=2
    )

    def aceptar(evento=None):
        try:
            fc1 = float(entrada_fc1.get().replace(",", "."))
            fc2 = float(entrada_fc2.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Frecuencias", "Escribe un número en cada casilla.", parent=ventana)
            return

        try:
            configuracion = ConfiguracionFiltro(fc1, fc2)
        except ValueError as error:
            messagebox.showerror("Frecuencias", str(error), parent=ventana)
            return

        seleccion.append(configuracion)
        ventana.destroy()

    tk.Button(ventana, text="Calcular filtro", command=aceptar, width=22).grid(
        row=6, column=0, columnspan=2, pady=24
    )
    ventana.bind("<Return>", aceptar)
    entrada_fc1.focus_set()
    ventana.mainloop()

    if seleccion:
        return seleccion[0]
    return None
