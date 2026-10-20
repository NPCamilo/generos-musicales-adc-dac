"""
Pruebas de `analisis.py`. Ejecutar con:  python nucleo/test_analisis.py

El pipeline se prueba sobre un WAV SINTÉTICO y COMPUESTO, no sobre las
canciones: así se sabe exactamente qué tiene que salir, y una prueba que
depende de una descarga de YouTube no es una prueba.

  1. El pipeline completo sobre un WAV sintético
  2. La cuantización: el factor de escala, el SNR y los bits efectivos
  3. La tabla de códigos binarios
  4. El aliasing: sin filtro el error crece al bajar f_s
  5. La cadena ADC-DAC y el presupuesto de error
  6. Las figuras y el informe se construyen sin errores
"""

from __future__ import annotations

import pathlib
import tempfile

import numpy as np

try:
    from . import analisis, comparativa, figuras, informe, wav_io
    from .analisis import Parametros
    from .catalogo import Genero
except ImportError:
    import analisis
    import comparativa
    import figuras
    import informe
    import wav_io
    from analisis import Parametros
    from catalogo import Genero

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


FICHA = Genero(
    clave="sintetica",
    nombre="Sintética",
    genero="Prueba",
    musico="—",
    obra="—",
    anio=2026,
    compositor="—",
    estilo="—",
    instrumentacion="—",
    bpm_esperado="—",
    banda_clave="—",
    por_que="—",
)


def _wav_de_prueba(destino: pathlib.Path) -> pathlib.Path:
    """Un WAV sintético: un tono de 200 Hz + armónicos + un golpe de bombo."""
    fs = 44100
    dur = 4.0
    t = np.arange(int(dur * fs)) / fs
    x = (0.6 * np.sin(2 * np.pi * 200 * t)
         + 0.3 * np.sin(2 * np.pi * 600 * t + 0.4)
         + 0.1 * np.sin(2 * np.pi * 1800 * t))
    # un bombo cada medio segundo
    for k in range(int(dur / 0.5)):
        i = int(k * 0.5 * fs)
        n = 1200
        x[i:i + n] += 0.8 * np.exp(-np.arange(n) / 300.0) * np.sin(
            2 * np.pi * 60 * np.arange(n) / fs)
    wav_io.escribir_wav(destino, 0.9 * x / np.max(np.abs(x)), fs, bits=16)
    return destino


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="analisis_test_"))
    ruta = _wav_de_prueba(tmp / "prueba.wav")

    # ---------------------------------------------------------------- 1
    _seccion("1) El pipeline completo")
    p = Parametros()
    r = analisis.analizar_pista(ruta, p, FICHA)
    chk("devuelve todas las secciones",
        all(k in r for k in ("pista", "tiempo", "espectro", "muestreo",
                             "cuantizacion", "cadena", "ritmo", "atencion")))
    chk("la pista se lee con sus metadatos", r["pista"]["fs"] == 44100)
    chk("el f_max medido está por encima del fundamental (200 Hz)",
        r["espectro"]["f_max"] > 200.0, f" ({r['espectro']['f_max']:.0f} Hz)")
    chk("el f_max está por debajo de Nyquist",
        r["espectro"]["f_max"] < 22050.0)
    chk("la f_s mínima es el doble del f_max",
        abs(r["espectro"]["fs_minima"] - 2 * r["espectro"]["f_max"]) < 1e-6)
    chk("el tiempo tiene la longitud de la señal",
        len(r["tiempo"]["t"]) == r["pista"]["n_muestras"])
    chk("el zoom tiene 20 ms", abs(r["tiempo"]["zoom"]["t"][-1] - 0.02) < 1e-3,
        f" ({r['tiempo']['zoom']['t'][-1]:.5f} s)")

    # ---------------------------------------------------------------- 2
    _seccion("2) La cuantización")
    cuanti = r["cuantizacion"]
    chk("el factor de escala de 16 bits es V_fs/2^15",
        abs(cuanti["factor_escala_v"] - 1.0 / 32768.0) < 1e-18)
    chk("hay casos para 24, 16, 12 y 8 bits",
        set(cuanti["casos"]) == {"24", "16", "12", "8"},
        f" ({sorted(cuanti['casos'])})")
    for bits in (8, 12, 16):
        c = cuanti["casos"][str(bits)]
        # el SNR medido no puede pasar del teórico en más de 1 dB
        chk(f"el SNR medido a {bits} bits no supera al teórico",
            c["snr_medido"] <= c["snr_teorico"] + 1.0,
            f" ({c['snr_medido']:.1f} frente a {c['snr_teorico']:.1f} dB)")
        chk(f"los bits efectivos a {bits} bits son menos que {bits}",
            c["enob"] <= bits, f" ({c['enob']:.2f})")
        chk(f"el error está acotado a ±Δ/2 a {bits} bits",
            float(np.max(np.abs(c["error"]))) <= c["delta"] / 2.0 + 1e-12,
            f" (máx {float(np.max(np.abs(c['error']))):.3e}, "
            f"Δ/2 {c['delta'] / 2:.3e})")
    # más bits, más SNR
    snrs = [cuanti["casos"][b]["snr_medido"] for b in ("8", "12", "16", "24")]
    chk("el SNR crece con el número de bits",
        all(snrs[i] < snrs[i + 1] for i in range(len(snrs) - 1)),
        f" ({[round(s, 1) for s in snrs]})")

    # ---------------------------------------------------------------- 3
    _seccion("3) La tabla de códigos binarios")
    tabla = cuanti["tabla_codigos"]
    chk("la tabla tiene las muestras pedidas",
        len(tabla) == p.n_muestras_tabla, f" ({len(tabla)})")
    chk("cada código tiene 16 bits de ancho",
        all(len(f["binario"]) == 16 for f in tabla))
    chk("el código reconstruye el valor con un error < Δ",
        all(abs(f["error"]) < cuanti["factor_escala_v"] for f in tabla))
    chk("el error medio está en medio LSB",
        all(0.0 <= f["error_medio_abs"] <= 0.5 + 1e-9 for f in tabla))
    chk("los índices son consecutivos",
        [f["n"] for f in tabla] == list(range(tabla[0]["n"],
                                               tabla[0]["n"] + len(tabla))))

    # ---------------------------------------------------------------- 4
    _seccion("4) El aliasing")
    exps = r["muestreo"]["experimentos"]
    chk("hay varios experimentos de muestreo", len(exps) >= 3)
    fs_orden = [e["fs"] for e in exps]
    chk("las frecuencias de muestreo están ordenadas",
        fs_orden == sorted(fs_orden))
    # El error de aliasing NO baja de forma estrictamente monótona al
    # subir f_s, y conviene saber por qué: depende de QUÉ contenido se
    # pliega y DÓNDE cae al plegarse. Un componente estrecho que se
    # pliega en una zona silenciosa apenas se nota; un transiente
    # broadband que se pliega justo encima de un pico, mucho. Lo que sí
    # está garantizado es la tendencia general y que el error de
    # aliasing siempre supera al de reconstrucción.
    chk("el error de aliasing es mucho mayor en la f_s más baja",
        exps[0]["nrmse_aliasing"] > 3 * exps[-1]["nrmse_aliasing"],
        f" ({exps[0]['nrmse_aliasing']:.2e} frente a "
        f"{exps[-1]['nrmse_aliasing']:.2e})")
    chk("el error de aliasing es SIEMPRE mayor que el de reconstrucción",
        all(e["nrmse_aliasing"] > e["nrmse_reconstruccion"] for e in exps))
    chk("la energía fuera de banda baja al subir f_s",
        all(exps[i]["energia_fuera_banda"] >= exps[i + 1]["energia_fuera_banda"]
            for i in range(len(exps) - 1)))

    # ---------------------------------------------------------------- 5
    _seccion("5) La cadena ADC-DAC")
    cadena = r["cadena"]
    chk("el presupuesto tiene las dos etapas",
        set(cadena["presupuesto"]) == {"cuantizador", "dac_zoh"})
    chk("los porcentajes del presupuesto suman ~100",
        abs(sum(v["porcentaje"] for v in cadena["presupuesto"].values()) - 100.0)
        < 1.0,
        f" ({sum(v['porcentaje'] for v in cadena['presupuesto'].values()):.1f} %)")
    chk("la cadena telefónica usa 8 kHz",
        cadena["telefonica"]["fs"] == 8000.0)
    chk("la telephone chain tiene menos SNR que la nativa",
        cadena["telefonica"]["snr_cadena"] < cadena["snr_cadena"],
        f" ({cadena['telefonica']['snr_cadena']:.1f} frente a "
        f"{cadena['snr_cadena']:.1f} dB)")

    # ---------------------------------------------------------------- 6
    _seccion("6) Las figuras y el informe")
    construidas = figuras.construir_todas(r)
    chk("se construyen las siete figuras de una pista",
        len(construidas) == len(figuras.FIGURAS_PISTA),
        f" ({len(construidas)})")
    for nombre, fig in construidas.items():
        bytes_png = figuras.a_png(fig)
        chk(f"la figura '{nombre}' se exporta como PNG",
            len(bytes_png) > 5000, f" ({len(bytes_png)} bytes)")

    destino = tmp / "informe.md"
    ruta_md = informe.generar_informe(Parametros(), destino=destino,
                                      regenerar_figuras=False)
    texto = ruta_md.read_text(encoding="utf-8")
    for seccion in ("Resumen ejecutivo", "La investigación", "La cadena ADC-DAC",
                    "Los resultados, género por género", "La comparación",
                    "El punto (e)", "Cómo se ha calculado",
                    "Limitaciones y honestidad"):
        chk(f"el informe tiene la sección «{seccion}»", seccion in texto)
    chk("el informe menciona a los cinco músicos",
        all(n in texto for n in ("Bach", "Megadeth", "Frankie Ruiz", "Feid",
                                 "Fredy Montoya")))
    chk("el informe declara los límites del punto (e)",
        "NO demuestra" in texto and "HIPÓTESIS" in texto.upper()
        or "no lo demuestra" in texto.lower())

    # ---------------------------------------------------------------- 7
    _seccion("7) La comparación")
    res = {"resultados": {"sintetica": r}}
    comp = comparativa.resumen_tablas(res["resultados"])
    chk("la comparativa tiene la tabla", len(comp["comparativa"]) == 1)
    chk("el veredicto tiene ganador", bool(comp["veredicto"]["ganador"]))
    chk("el veredicto tiene las condiciones",
        len(comp["veredicto"]["condiciones"]) >= 3)
    chk("el veredicto tiene los avisos",
        len(comp["veredicto"]["avisos"]) >= 3)
    chk("el veredicto no promete una mejora clínica",
        "clínic" in " ".join(comp["veredicto"]["avisos"]).lower())

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
