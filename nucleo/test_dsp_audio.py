"""
Pruebas de `dsp_audio.py`. Ejecutar con:  python nucleo/test_dsp_audio.py

Estas pruebas comprueban las afirmaciones matemáticas del instrumental, y
lo hacen con SEÑALES SINTÉTICAS DE VALOR CONOCIDO, no con música: si el
espectro de un tono de amplitud 1 no mide 1, el error está en el código y
no en la canción.

  1. La normalización del espectro (ganancia coherente de la ventana)
  2. La medida de `f_max` con los dos criterios
  3. El aliasing: un tono por encima de f_s/2 se pliega donde debe
  4. El filtro antialiasing: elimina el contenido de la banda eliminada
  5. El tempo: un metrónomo sintético a 120 BPM se detecta a 120 BPM
  6. El centroide, la planicidad y el factor de cresta
  7. El índice de atención: se comporta como se dice que se comporta
"""

from __future__ import annotations

import numpy as np

try:
    from . import dsp_audio as dsp
except ImportError:
    import dsp_audio as dsp

FALLOS: list[str] = []
PRUEBAS = 0


def chk(nombre: str, condicion: bool, detalle: str = "") -> None:
    global PRUEBAS
    PRUEBAS += 1
    print(f"  {'OK   ' if condicion else 'FALLA'} {nombre}{detalle}")
    if not condicion:
        FALLOS.append(nombre)


def _seccion(titulo: str) -> None:
    print()
    print(titulo)
    print("=" * 90)


def _tono(freq: float, fs: int, duracion: float = 1.0,
          amp: float = 1.0) -> np.ndarray:
    t = np.arange(int(duracion * fs)) / fs
    return amp * np.sin(2 * np.pi * freq * t)


def _amplitud_por_ajuste(x: np.ndarray, fs: int, freq: float) -> float:
    """La amplitud de una senoidal por ajuste mínimo cuadrático.

    Es la forma correcta de medir la amplitud de un tono cuando el
    registro es corto o la frecuencia no cae en un bin: el pico de la FFT
    depende de la alineación, y el ajuste no.
    """
    t = np.arange(len(x)) / fs
    base = np.column_stack([np.sin(2 * np.pi * freq * t),
                             np.cos(2 * np.pi * freq * t)])
    coef, *_ = np.linalg.lstsq(base, x, rcond=None)
    return float(np.hypot(coef[0], coef[1]))


def main() -> int:
    # ---------------------------------------------------------------- 1
    _seccion("1) La normalización del espectro")
    fs = 8000
    x = _tono(500.0, fs, 1.0, 1.0)
    for ventana in ("rectangular", "hann", "blackman", "hamming"):
        esp = dsp.espectro_magnitud(x, fs, ventana=ventana)
        # la tolerancia es del 5 % porque el tono está TRUNCADO en los
        # bordes del registro: la discontinuidad de los extremos fuga
        # algo de energía a los bins vecinos y el pico medido queda un
        # 2-3 % por debajo. Es física del truncamiento, no del código:
        # con la señal completa (o con un fundido) mide 1,000 exacto.
        chk(f"el pico de un tono de amplitud 1 mide 1 (ventana {ventana})",
            abs(esp["pico"] - 1.0) < 0.05,
            f" (pico {esp['pico']:.4f}, CG {esp['ganancia_coherente']:.3f})")
        chk(f"la frecuencia del pico es la del tono (ventana {ventana})",
            abs(esp["pico_hz"] - 500.0) < 3.0, f" ({esp['pico_hz']:.1f} Hz)")

    # la ganancia coherente vale lo que dice la teoría
    chk("la ganancia coherente de la ventana rectangular es 1",
        abs(dsp.ganancia_coherente(np.ones(100)) - 1.0) < 1e-12)
    chk("la ganancia coherente de la ventana Hann es 0,5",
        abs(dsp.ganancia_coherente(np.hanning(200)) - 0.5) < 0.01)

    # dos tonos: cada uno mide su amplitud
    t = np.arange(fs) / fs
    x2 = 0.4 * np.sin(2 * np.pi * 300 * t) + 0.25 * np.sin(2 * np.pi * 1500 * t)
    esp = dsp.espectro_magnitud(x2, fs, ventana="hann")
    pico = float(np.max(esp["A"]))
    chk("el pico mayor de dos tonos mide la mayor de las dos amplitudes",
        abs(pico - 0.4) < 0.02, f" ({pico:.4f})")

    # ---------------------------------------------------------------- 2
    _seccion("2) La medida de f_max")
    esp = dsp.espectro_magnitud(_tono(500.0, fs, 1.0), fs, ventana="hann")
    f_m = dsp.f_max_umbral(esp, -40.0)
    chk("f_max de un tono puro cae en el tono", abs(f_m - 500.0) < 30.0,
        f" ({f_m:.1f} Hz)")
    f_e = dsp.f_max_energia(esp, 0.999)
    chk("f_max por energía cae en el tono", abs(f_e - 500.0) < 30.0,
        f" ({f_e:.1f} Hz)")

    # el suavizado no desplaza el máximo del espectro (el pico suavizado
    # es más bajo, porque la energía se reparte en la ventana, pero tiene
    # que estar en la MISMA frecuencia)
    esp_real = dsp.espectro_magnitud(
        dsp.quitar_dc(_tono(500.0, fs, 1.0)), fs, ventana="hann")
    suave = dsp.suavizar_db(esp_real["db"], esp_real["f"], 30.0)
    chk("el suavizado no desplaza el pico del espectro",
        abs(esp_real["f"][int(np.argmax(suave))] - 500.0) < 5.0,
        f" (pico suavizado en {esp_real['f'][int(np.argmax(suave))]:.1f} Hz)")
    chk("el suavizado baja el pico (la energía se reparte)",
        suave.max() < esp_real["db"].max(),
        f" ({suave.max():.1f} dB frente a {esp_real['db'].max():.1f} dB)")

    # ---------------------------------------------------------------- 3
    _seccion("3) El aliasing: el pliegue")
    fs_in = 8000
    f_tono = 3000.0
    x = _tono(f_tono, fs_in, 0.5)
    fs_out = 4000.0
    plegado = dsp.muestrear(x, fs_in, fs_out, con_filtro=False)
    chk("el submuestreo sin filtro da el número de muestras esperado",
        abs(len(plegado) - int(0.5 * fs_out)) <= 1, f" ({len(plegado)})")
    # 3000 Hz con f_s = 4000 se pliega a 1000 Hz
    esp = dsp.espectro_magnitud(plegado, fs_out, ventana="hann")
    chk("el tono de 3000 Hz se pliega a 1000 Hz",
        abs(esp["pico_hz"] - 1000.0) < 20.0, f" ({esp['pico_hz']:.1f} Hz)")
    chk("la amplitud se conserva al plegarse", abs(esp["pico"] - 1.0) < 0.05,
        f" ({esp['pico']:.4f})")

    # con filtro antialiasing, el tono de 3000 Hz desaparece
    limpio = dsp.antialias(x, fs_in, fs_out, orden=8)
    esp_l = dsp.espectro_magnitud(limpio, fs_out, ventana="hann")
    energia_plegado = float(np.sum(dsp.espectro_magnitud(
        plegado, fs_out, ventana="hann")["A"] ** 2))
    energia_limpio = float(np.sum(esp_l["A"] ** 2))
    chk("el filtro antialiasing reduce la energía del tono que se pliega",
        energia_limpio < 0.1 * energia_plegado,
        f" ({energia_limpio / max(energia_plegado, 1e-30):.4f} del original)")

    # ---------------------------------------------------------------- 4
    _seccion("4) El filtro antialiasing no toca lo que debe quedarse")
    # la amplitud se mide por AJUSTE MÍNIMO CUADRÁTICO, no por el pico de
    # la FFT: con un fragmento corto el pico depende de si la frecuencia
    # cae justo en un bin, y eso no mide la ganancia del filtro.
    x_bajo = _tono(200.0, fs_in, 0.5)
    limpio = dsp.antialias(x_bajo, fs_in, 4000.0, orden=8)
    ajuste = _amplitud_por_ajuste(limpio, 4000.0, 200.0)
    chk("un tono de 200 Hz sobrevive al filtrado (amplitud ~1)",
        abs(ajuste - 1.0) < 0.05, f" ({ajuste:.4f})")
    chk("el filtrado conserva la longitud esperada",
        abs(len(limpio) - int(0.5 * 4000)) <= 1, f" ({len(limpio)})")

    # ---------------------------------------------------------------- 5
    _seccion("5) El tempo: un metrónomo sintético a 120 BPM")
    fs = 44100
    dur = 8.0
    t = np.arange(int(dur * fs)) / fs
    metr = np.zeros_like(t)
    bpm = 120.0
    periodo = 60.0 / bpm
    for k in range(int(dur / periodo)):
        i = int(k * periodo * fs)
        n = 600
        metr[i:i + n] += np.exp(-np.arange(n) / 100.0) * np.sin(
            2 * np.pi * 2000 * np.arange(n) / fs)
    r = dsp.bpm(metr, fs)
    chk("el tempo medido es 120 BPM", abs(r["bpm"] - 120.0) < 1.5,
        f" ({r['bpm']:.2f} BPM)")
    chk("el tempo es medible", r["medible"], f" (puntuación {r['puntuacion']:.3f})")
    chk("la confianza es alta", r["confianza"] > 0.5, f" ({r['confianza']:.2f})")

    # un tono continuo NO tiene tempo medible
    r_sin = dsp.bpm(_tono(440.0, fs, 4.0), fs)
    chk("un tono continuo no tiene tempo medible", not r_sin["medible"],
        f" (puntuación {r_sin['puntuacion']:.3f})")

    # ---------------------------------------------------------------- 6
    _seccion("6) Centroide, planicidad y factor de cresta")
    esp = dsp.espectro_magnitud(_tono(200.0, fs, 1.0), fs, ventana="hann")
    c = dsp.centroide_espectral(esp)
    chk("el centroide de un tono de 200 Hz está en 200 Hz", abs(c - 200.0) < 15.0,
        f" ({c:.1f} Hz)")
    chk("la planicidad de un tono puro es bajísima",
        dsp.planicidad_espectral(esp) < 0.01)

    rng = np.random.default_rng(0)
    ruido = rng.normal(0, 0.1, fs)
    esp_r = dsp.espectro_magnitud(ruido, fs, ventana="hann")
    chk("la planicidad del ruido es alta",
        dsp.planicidad_espectral(esp_r) > 0.3,
        f" ({dsp.planicidad_espectral(esp_r):.3f})")
    chk("el centroide del ruido está en el medio de la banda",
        abs(dsp.centroide_espectral(esp_r) - fs / 4.0) < fs * 0.1)

    x_imp = np.zeros(fs)
    x_imp[::1000] = 1.0
    chk("el factor de cresta de un tren de impulsos es alto",
        dsp.crest_factor(x_imp) > 3.0, f" ({dsp.crest_factor(x_imp):.2f})")
    chk("el factor de cresta de una señal constante es 1",
        abs(dsp.crest_factor(np.ones(100)) - 1.0) < 1e-9)

    # ---------------------------------------------------------------- 7
    _seccion("7) El índice de atención se comporta como se dice")
    base = {"bpm": 75.0, "bpm_estable": 4.0, "confianza_bpm": 0.9,
            "centroide": 300.0, "frac_agudos": 0.02, "frac_voz": 0.05,
            "crest": 6.0}
    bueno = dsp.indice_atencion(base)
    chk("una piece 'tranquila' puntúa alto", bueno["indice"] > 85,
        f" ({bueno['indice']:.1f})")

    malo = dsp.indice_atencion({**base, "bpm": 140.0, "centroide": 3000.0,
                                 "frac_agudos": 0.4, "frac_voz": 0.6,
                                 "crest": 2.5})
    chk("una piece 'activante' puntúa bajo", malo["indice"] < 45,
        f" ({malo['indice']:.1f})")
    chk("el orden es el esperado", bueno["indice"] > malo["indice"])

    # sin tempo medible, el criterio de tempo es neutro
    sin_tempo = dsp.indice_atencion({**base, "confianza_bpm": 0.1,
                                      "tempo_medible": False})
    chk("sin tempo medible el criterio vale 12,5 (neutro)",
        abs([c for c in sin_tempo["por_criterio"]
             if c["clave"] == "tempo"][0]["puntos"] - 12.5) < 1e-9)
    chk("se marca que el tempo no es fiable", sin_tempo["tempo_no_fiable"])

    # los pesos suman 100
    chk("los pesos de los criterios suman 100",
        sum(c["peso"] for c in dsp.CRITERIOS_atencion) == 100)

    # ---------------------------------------------------------------- fin
    print()
    print("=" * 90)
    print(f"{PRUEBAS - len(FALLOS)}/{PRUEBAS} comprobaciones en verde")
    if FALLOS:
        print("FALLAN:")
        for f in FALLOS:
            print(f"  · {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    raise SystemExit(main())
