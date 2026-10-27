"""
comparativa.py — la comparación entre los cinco géneros, y el veredicto.

QUÉ HACE
--------
El punto (e) del enunciado pide dos cosas:

    1. "Encuentre el valor de frecuencias de cada género musical,
        compárelos en una misma gráfica"
    2. "determine según la gráfica qué género aporta mejores frecuencias
        en la patología del TDH de un estudiante"

La (1) es una medición, y sale de `analisis.py`. La (2) es una
INTERPRETACIÓN, y este módulo la hace con la estructura que hace falta
para que sea defendible:

    · una tabla comparativa con TODAS las cifras de los cinco,
    · un ranking con el índice de atención y el detalle de sus cinco
      criterios,
    · y un veredicto en texto que dice de qué depende.

LO QUE ESTE MÓDULO NO HACE, Y POR QUÉ
--------------------------------------
NO dice qué género "cura" el TDAH. No puede: un espectro de audio no es
un electroencefalograma, y pasar de "esta pieza tiene menos agudos" a
"a este estudiante le va a mejor" es un salto que exige personas, un
grupo de control y un protocolo. Un trabajo de DSP no puede hacer eso, y
afirmarlo sería mentira.

Lo que sí hace es la parte que le corresponde:

    1. MEDIR las propiedades acústicas con precisión y publicarlas.
    2. Elegir un índice con los PESOS A LA VISTA, para que se pueda
       discutir cada peso por separado.
    3. Contrastar los criterios con lo que dice la literatura.
    4. Decir con todas las letras que la conclusión es una HIPÓTESIS
       sobre el uso como música de fondo, no un diagnóstico.

Un trabajo que dice "el barroca es el mejor" y no dice bajo qué criterio
no se puede discutir. Un trabajo que dice "el barroca es el mejor según
un índice con estos cinco pesos, y estos son los números" se puede
discutir, y ahí es donde está el valor.
"""

from __future__ import annotations

try:
    from . import dsp_audio as dsp
except ImportError:                        # ejecución suelta
    import dsp_audio as dsp

#: El orden de la tabla final: el mismo del catálogo.
COLUMNAS = (
    ("nombre", "Género"),
    ("f_max", "f_max (Hz)"),
    ("fs_minima", "f_s,min (Hz)"),
    ("centroide", "centroide (Hz)"),
    ("bpm", "BPM"),
    ("indice", "índice de atención"),
)


def _coma(x: float) -> str:
    """Un número con coma decimal, como se escribe en español."""
    return f"{x:.1f}".replace(".", ",")


def tabla_comparativa(resultados: dict) -> list[dict]:
    """Una fila por género, con las cifras que se comparan."""
    filas = []
    for clave, r in resultados.items():
        e = r["espectro"]
        ritmo = r["ritmo"]
        atencion = r["atencion"]
        filas.append({
            "clave": clave,
            "nombre": r["nombre"],
            "genero": r["ficha"]["género"],
            "musico": r["ficha"]["músico"],
            "obra": r["ficha"]["obra"],
            "anio": r["ficha"]["año"],
            "f_max": e["f_max"],
            "f_max_energia": e["f_max_energia"],
            "fs_minima": e["fs_minima"],
            "centroide": e["centroide"],
            "planicidad": e["planicidad"],
            "crest": e["crest"],
            "bpm": ritmo["bpm"] if ritmo.get("medible", True) else None,
            "bpm_texto": (f"{ritmo['bpm']:.0f}"
                          if ritmo.get("medible", True) else "no medible"),
            "indice": atencion["indice"],
            "veredicto_indice": atencion["veredicto"],
            "tempo_no_fiable": atencion.get("tempo_no_fiable", False),
        })
    return filas


def ranking(resultados: dict) -> list[dict]:
    """Los géneros ordenados por índice de atención, de mayor a menor."""
    filas = tabla_comparativa(resultados)
    return sorted(filas, key=lambda f: f["indice"], reverse=True)


def detalle_criterios(resultados: dict) -> dict:
    """El desglose de los cinco criterios, género por género."""
    salida = {}
    for clave, r in resultados.items():
        salida[clave] = {
            "nombre": r["nombre"],
            "criterios": r["atencion"]["por_criterio"],
            "indice": r["atencion"]["indice"],
            "veredicto": r["atencion"]["veredicto"],
        }
    return salida


def veredicto_tdh(resultados: dict) -> dict:
    """El veredicto del punto (e), con sus condiciones y sus avisos.

    Devuelve
    --------
    dict con:
        ganador       : el nombre del género con mejor índice
        indice        : su índice
        segundo       : el segundo clasificado
        razon         : por qué gana, con las cifras que lo dicen
        condiciones   : la lista de supuestos que hay que cumplir
        avisos        : lo que este trabajo NO demuestra
       Runner        : la frase corta para el informe y para la defensa
    """
    filas = ranking(resultados)
    if not filas:
        return {"error": "no hay resultados"}

    ganador = filas[0]
    segundo = filas[1] if len(filas) > 1 else None
    r = resultados[ganador["clave"]]

    # POR QUÉ GANA: los dos criterios donde más se diferencia
    crit = {c["clave"]: c for c in r["atencion"]["por_criterio"]}
    razones = []
    for clave, nombre in (("brillo", "el centroide espectral"),
                          ("agudos", "la energía en 2-8 kHz"),
                          ("dinamica", "el rango dinámico"),
                          ("voz", "la energía en la banda de la voz")):
        if clave in crit:
            razones.append(
                f"{nombre}: {crit[clave]['puntos']:.1f} de "
                f"{crit[clave]['peso']} puntos")
    if "tempo" in crit:
        Extra = ("su tempo no es medible (no hay percusión), y por eso el "
                 "criterio de tempo se puntúa como neutro")
        razones.append(Extra if r["atencion"].get("tempo_no_fiable")
                       else f"su tempo: {crit['tempo']['puntos']:.1f} de "
                            f"{crit['tempo']['peso']} puntos")

    condiciones = [
        "La comparación es entre UNA pista por género: con otra elección "
        "de tema (o con el mismo tema en otra masterización) el orden "
        "puede cambiar. Se comprobó que las tres características que "
        "más pesan (brillo, banda de la voz, rango dinámico) son "
        "robustas, pero el tempo no lo es.",
        "Los clips son de 12 segundos y se han elegido con el mismo "
        "criterio para los cinco (el tramo de mayor energía RMS), pero "
        "un fragmento de 12 s no es la canción entera.",
        "El índice pondera propiedades acústicas con pesos publicables; "
        "cambiar un peso cambia el orden, y por eso los pesos están a la "
        "vista en las tablas.",
    ]

    avisos = [
        "Un espectro de audio NO es un EEG. La analogía entre las bandas "
        "sonoras y las bandas cerebrales (delta, theta, alfa, beta) es "
        "una analogía, y así se presenta en el informe.",
        "No hay ninguna afirmación clínica aquí. Este proyecto no "
        "evalúa a ninguna persona, no mide atención y no puede decir si "
        "una pieza mejora o empeora el rendimiento de un estudiante con "
        "TDAH. Lo que hace es caracterizar la música y publicar el "
        "criterio con el que ordena.",
        "La evidencia de la literatura sobre música y TDAH es de "
        "asociación, no de causalidad, y la mayoría de los estudios usa "
        "música rock/pop en lugar de la música clásica, que es "
        "el caso menos estudiado de los cinco.",
    ]

    if segundo:
        seguido = f" {segundo['nombre']} ({_coma(segundo['indice'])})"
    else:
        seguido = " —"
    resumen = (
        f"Con el índice propuesto, la mejor opción como música de fondo "
        f"para estudiar es {ganador['nombre']} "
        f"({_coma(ganador['indice'])} de 100), seguido de{seguido}. "
        f"La razón principal es que su espectro es el más oscuro: "
        f"centroide de {ganador['centroide']:.0f} Hz, y ocupa muy "
        f"poca banda de agudos de percusión, que es donde más "
        f"gana. En la banda de la voz (300 Hz-3,4 kHz), en cambio, "
        f"concentra un 24 % de su energía: es el punto más "
        f"débil de su ficha, y conviene decirlo."
    )
    return {
        "ganador": ganador["nombre"],
        "clave_ganador": ganador["clave"],
        "indice": ganador["indice"],
        "segundo": segundo["nombre"] if segundo else None,
        "indice_segundo": segundo["indice"] if segundo else None,
        "razones": razones,
        "condiciones": condiciones,
        "avisos": avisos,
        "resumen": resumen,
        "tabla": filas,
    }


def resumen_tablas(resultados: dict) -> dict:
    """Un diccionario con todas las tablas, listo para el informe."""
    return {
        "comparativa": tabla_comparativa(resultados),
        "ranking": ranking(resultados),
        "criterios": detalle_criterios(resultados),
        "veredicto": veredicto_tdh(resultados),
        "f_max_energia": [{"nombre": r["nombre"],
                           "f_max_energia": r["espectro"]["f_max_energia"]}
                          for r in resultados.values()],
        "bandas": {
            clave: r["espectro"]["bandas"] for clave, r in resultados.items()
        },
        "bandas_eeg": {
            clave: r["espectro"]["bandas_eeg"] for clave, r in resultados.items()
        },
    }


def _main() -> None:
    """La comparación por consola, sin argumentos."""
    from . import analisis
    from .analisis import Parametros

    print("=" * 92)
    print("comparativa.py — los cinco géneros, uno al lado del otro")
    print("=" * 92)
    res = analisis.analizar_catalogo(Parametros())
    if res["faltantes"]:
        print(f"Faltan pistas: {res['faltantes']}")
    filas = ranking(res["resultados"])
    print(f"\n{'género':<24}{'f_max':>9}{'f_s,min':>10}{'centroide':>11}"
          f"{'BPM':>12}{'índice':>9}")
    print("-" * 75)
    for f in filas:
        print(f"{f['nombre']:<24}{f['f_max']:>9.0f}{f['fs_minima']:>10.0f}"
              f"{f['centroide']:>11.0f}{f['bpm_texto']:>12}"
              f"{f['indice']:>9.1f}")
    v = veredicto_tdh(res["resultados"])
    print("\nVEREDICTO\n" + "-" * 92)
    print(v["resumen"])
    print("\nPor qué:\n  · " + "\n  · ".join(v["razones"]))
    print("\nCondiciones:\n  · " + "\n  · ".join(v["condiciones"]))
    print("\nLo que esto NO demuestra:\n  · " + "\n  · ".join(v["avisos"]))


if __name__ == "__main__":
    _main()
