"""
serializacion.py — pasar los resultados del análisis a un JSON.

POR QUÉ HACE FALTA ESTE MÓDULO
-----------------------------
En un servidor normal (o en un contenedor) el análisis se calcula en
cuanto se pide. En un entorno SERVERLESS como Vercel no:

    · la función tiene un límite de tiempo (10 s en el plan gratuito),
      y el análisis de las cinco pistas tarda unos 20 s;
    · cada invocación puede ser en una máquina distinta, así que no hay
      memoria entre peticiones;
    · el disco es de solo lectura, así que no se puede cachear en disco.

La solución es la de siempre en estos casos: **calcular antes y servir
después**. Este módulo extrae de los resultados del análisis SOLO los
números (sin los arrays de NumPy, que serían giganticecos) y los escribe
en un JSON, que es lo que la web lee.

Qué NO se serializa
-------------------
Los arrays: la señal, los espectros, las reconstrucciones. Son
millones de puntos y no los usa ninguna plantilla: solo los usan las
figuras, que ya están dibujadas y se sirven como PNG.

    salida/datos.json    los números de las cinco pistas
    salida/*.png         las figuras, ya dibujadas

Y el resultado es que la web responde en milisegundos, y que el
análisis en vivo (subir tu propio WAV) sigue funcionando: eso tarda
2-3 s, que sí cabe en el límite.
"""

from __future__ import annotations

import json
import pathlib

#: La versión del formato. Si se cambia la estructura, se sube el número
#: y la web comprueba que el JSON que tiene delante es compatible.
VERSION = 2


def _podar(valor, profundidad: int = 0):
    """Quita de un diccionario todo lo que sea un array de NumPy.

    Se hace en profundidad, y no con una lista de claves, porque los
    arrays están en sitios distintos según la sección y esta función
    tiene que ser a prueba de que eso cambie.
    """
    if profundidad > 6:
        return None
    if isinstance(valor, dict):
        return {k: _podar(v, profundidad + 1) for k, v in valor.items()
                if not _es_array(v)}
    if isinstance(valor, (list, tuple)):
        if valor and all(isinstance(v, (int, float)) for v in valor):
            return list(valor)
        return None
    if hasattr(valor, "item") and hasattr(valor, "dtype"):
        return None
    return valor


def _es_array(valor) -> bool:
    """True si el valor es un array de NumPy (y no un número)."""
    return hasattr(valor, "dtype") and hasattr(valor, "shape")


def resumen_serializable(r: dict) -> dict:
    """Los números de una pista, listos para el JSON.

    Devuelve un diccionario con las mismas claves que devuelve
    `analisis.analizar_pista`, pero sin los arrays: lo que las
    plantillas necesitan y nada más.
    """
    salida = {
        "clave": r["clave"],
        "nombre": r["nombre"],
        "ficha": r["ficha"],
        "pista": r["pista"],
        "parametros": r["parametros"],
        "espectro": {
            "f_max": r["espectro"]["f_max"],
            "f_max_umbral": r["espectro"]["f_max_umbral"],
            "f_max_energia": r["espectro"]["f_max_energia"],
            "f_max_por_umbral": r["espectro"]["f_max_por_umbral"],
            "umbral_db": r["espectro"]["umbral_db"],
            "bandas": r["espectro"]["bandas"],
            "bandas_eeg": r["espectro"]["bandas_eeg"],
            "centroide": r["espectro"]["centroide"],
            "planicidad": r["espectro"]["planicidad"],
            "crest": r["espectro"]["crest"],
            "fs_minima": r["espectro"]["fs_minima"],
            "nyquist": r["espectro"]["nyquist"],
            "ancho_banda": r["espectro"]["ancho_banda"],
            "pico_hz": r["espectro"]["pico_hz"],
        },
        "muestreo": {
            "fs_minima": r["muestreo"]["fs_minima"],
            "experimentos": [
                {k: v for k, v in e.items() if not _es_array(v)}
                for e in r["muestreo"]["experimentos"]
            ],
        },
        "cuantizacion": {
            "vfs": r["cuantizacion"]["vfs"],
            "rango_v": r["cuantizacion"]["rango_v"],
            "bits": r["cuantizacion"]["bits"],
            "factor_escala_v": r["cuantizacion"]["factor_escala_v"],
            "factor_escala_medio": r["cuantizacion"]["factor_escala_medio"],
            "niveles": r["cuantizacion"]["niveles"],
            "snr_teorico": r["cuantizacion"]["snr_teorico"],
            "carga": _podar(r["cuantizacion"]["carga"]),
            "casos": {
                k: {kk: vv for kk, vv in v.items() if not _es_array(vv)}
                for k, v in r["cuantizacion"]["casos"].items()
            },
            "tabla_codigos": r["cuantizacion"]["tabla_codigos"],
        },
        "cadena": {
            "etapas": {
                k: {kk: vv for kk, vv in v.items() if not _es_array(vv)}
                for k, v in r["cadena"]["etapas"].items()
            },
            "presupuesto": r["cadena"]["presupuesto"],
            "snr_cadena": r["cadena"]["snr_cadena"],
            "nrmse_cadena": r["cadena"]["nrmse_cadena"],
            "telefonica": {
                "fs": r["cadena"]["telefonica"]["fs"],
                "bits": r["cadena"]["telefonica"]["bits"],
                "n_muestras": r["cadena"]["telefonica"]["n_muestras"],
                "presupuesto": r["cadena"]["telefonica"]["presupuesto"],
                "snr_cadena": r["cadena"]["telefonica"]["snr_cadena"],
                "nrmse_cadena": r["cadena"]["telefonica"]["nrmse_cadena"],
                "nrmse_sobre_banda_completa":
                    r["cadena"]["telefonica"]["nrmse_sobre_banda_completa"],
            },
        },
        "ritmo": r["ritmo"],
        "atencion": r["atencion"],
    }
    return salida


def guardar_datos(resultados: dict, destino: str | pathlib.Path,
                  extra: dict | None = None) -> pathlib.Path:
    """Escribe los resultados en un JSON.

    Parámetros
    ----------
    resultados : dict
        El `{"resultados": {...}}` que devuelve `analisis.analizar_catalogo`.
    destino : str o pathlib.Path
        El fichero donde escribir.
    extra : dict
        El resumen de la comparativa, que también se guarda (así la web no
        tiene que recalcularlo).
    """
    destino = pathlib.Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "version": VERSION,
        "generado": _ahora(),
        "resultados": {k: resumen_serializable(v)
                       for k, v in resultados["resultados"].items()},
        "faltantes": resultados.get("faltantes", []),
    }
    if extra is not None:
        datos["comparativa"] = extra
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    return destino


def _ahora() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def cargar_datos(destino: str | pathlib.Path) -> dict | None:
    """Lee el JSON de los datos, o devuelve None si no está o no sirve.

    Se devuelve None (y no un error) cuando el JSON no existe o su
    versión no es la que espera este código: en ese caso la web vuelve a
    calcularlo en vivo, que es lo de siempre.
    """
    destino = pathlib.Path(destino)
    if not destino.exists():
        return None
    try:
        datos = json.loads(destino.read_text(encoding="utf-8"))
    except Exception:
        return None
    if datos.get("version") != VERSION:
        return None
    if not datos.get("resultados"):
        return None
    return datos
