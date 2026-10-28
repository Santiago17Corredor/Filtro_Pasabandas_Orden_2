"""Condiciones del laboratorio 1, tercer corte (página 30 de la guía)."""

from dataclasses import dataclass
from math import isfinite


FRECUENCIA_MUESTREO = 44_100
ANCHO_BANDA_MINIMO = 2_000
ANCHO_BANDA_MAXIMO = 3_000
FRECUENCIA_CORTE_MAXIMA = 5_000
TAMANO_BLOQUE = 1_024


@dataclass(frozen=True)
class ConfiguracionFiltro:
    fc1: float = 1_000.0
    fc2: float = 3_500.0

    def __post_init__(self):
        if not (isfinite(self.fc1) and isfinite(self.fc2)):
            raise ValueError("Las frecuencias deben ser números finitos.")
        if not 0 < self.fc1 < self.fc2 <= FRECUENCIA_CORTE_MAXIMA:
            raise ValueError("Debe cumplirse: 0 < fc1 < fc2 <= 5000 Hz.")
        if not ANCHO_BANDA_MINIMO <= self.ancho_banda <= ANCHO_BANDA_MAXIMO:
            raise ValueError("El ancho de banda fc2 - fc1 debe estar entre 2000 y 3000 Hz.")

    @property
    def ancho_banda(self) -> float:
        """Ancho de banda seleccionado, en Hz (no es el BW analógico)."""
        return self.fc2 - self.fc1

    @property
    def fs(self) -> int:
        return FRECUENCIA_MUESTREO
