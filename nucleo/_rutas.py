"""
_rutas.py — deja accesible la biblioteca `Nyquist_Shannon` desde aquí.

POR QUÉ EXISTE
--------------
Este proyecto vive en `Generos_Musicales_ADC_DAC/`, dentro de la carpeta
`COMUNICACIONES I/`, y la biblioteca de DSP que ya tenías
(`Nyquist_Shannon/`) está un nivel más arriba. Python solo busca en el
directorio del script y en el `sys.path`, así que sin este archivo el
import fallaría.

`asegurar_rutas()` añade la carpeta `COMUNICACIONES I/` al `sys.path`, de
modo que:

    from Nyquist_Shannon import espectro, metricas, muestreo, realistic

funcione igual que dentro del propio paquete `Nyquist_Shannon`.

No hace nada NEW: la estructura de la biblioteca es

    Nyquist_Shannon/
        senales.py     la señal como serie de Fourier
        muestreo.py    muestreo, Shannon, aliasing
        espectro.py    FT, réplicas, FFT, coherencia
        metricas.py    NRMSE, SNR, THD
        realistic.py   antialiasing, cuantizador, ruido, dither
        panels.py      las 9 figuras en Plotly
        graficos_mpl.py  las mismas figuras en matplotlib
        informe.py     el .md del entregable
        app.py         la interfaz Streamlit

y todo lo que este proyecto hace de nuevo (leer WAV, analizar audio real,
comparar géneros, el índice de atención) se apoya en ella.
"""

from __future__ import annotations

import pathlib
import sys

#: La carpeta `COMUNICACIONES I/`, que contiene `Nyquist_Shannon/`.
RAIZ_COMUNICACIONES = pathlib.Path(__file__).resolve().parent.parent.parent

#: La carpeta de este proyecto.
RAIZ_PROYECTO = pathlib.Path(__file__).resolve().parent.parent


def asegurar_rutas() -> pathlib.Path:
    """Añade la carpeta `COMUNICACIONES I/` al `sys.path`.

    Es idempotente: si ya está, no hace nada. Devuelve la ruta añadida.
    """
    ruta = str(RAIZ_COMUNICACIONES)
    if ruta not in sys.path:
        sys.path.insert(0, ruta)
    return RAIZ_COMUNICACIONES
