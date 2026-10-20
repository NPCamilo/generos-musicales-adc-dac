"""
nucleo — el motor de cálculo del proyecto.

Módulos
-------
    wav_io.py     lectura y escritura de WAV (parser propio, sin deps)
    dsp_audio.py  el instrumental de DSP sobre audio real
    catalogo.py   las cinco pistas y su ficha de investigación
    analisis.py   el pipeline completo por pista
    comparativa.py la comparación entre géneros y el índice de atención
    figuras.py    las figuras en matplotlib (PNG)
    informe.py    el informe .md del entregable
    descarga.py   la descarga y el recorte de las pistas

Este paquete NO depende de Django: la interfaz web es una capa encima.
"""

from __future__ import annotations

__all__ = [
    "wav_io",
    "dsp_audio",
    "catalogo",
    "analisis",
    "comparativa",
    "figuras",
    "informe",
]
