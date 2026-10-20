"""
views.py — las vistas de la aplicación.

CÓMO SE ORGANIZA EL CACHÉ
--------------------------
El análisis de una pista tarda entre 1 y 2 segundos (es un FFT de 2^20
bins, un filtro de fase cero y cuatro experimentos de muestreo con
reconstrucción de Shannon). Y en un entorno SERVERLESS (Vercel) tarda
mucho más, porque las cinco pistas juntas son unos 20 segundos y la
función tiene un límite de 10 s.

Por eso la web funciona en DOS MODOS:

    · CON LOS DATOS PRECALCULADOS (`salida/datos.json`): es el modo
      normal, y el único que funciona en Vercel. Los números salen del
      JSON y las figuras del PNG ya dibujado, así que la respuesta es
      de milisegundos.
    · CALCULANDO EN VIVO: si el JSON no está (un clonar recién hecho,
      por ejemplo), se analiza todo al vuelo. Funciona, pero es lento, y
      en Vercel puede agotar el tiempo de la función.

Y en los dos casos, lo que sube el usuario se analiza en el momento,
porque cada subida es distinta.

EL AUDIO QUE SE PUEDE ESCUCHAR
------------------------------
La aplicación genera WAV de verdad y los sirve:

    original      el clip tal cual
    bits8         el mismo audio cuantizado a 8 bits (se oye la &
                  el ruido de cuantización)
    bits12        cuantizado a 12 bits
    telefonica    la cadena completa a 8 kHz y 8 bits: la voz telefónica

Eso es lo que convierte el proyecto en algo que se puede DEMOSTRAR: no
solo mirar el gráfico del error, sino oírlo.
"""

from __future__ import annotations

import functools
import io
import pathlib

from django.http import (FileResponse, Http404, HttpResponse, JsonResponse)
from django.shortcuts import render

from nucleo import analisis
from nucleo import comparativa as modulo_comparativa
from nucleo import figuras, informe as modulo_informe
from nucleo import serializacion, wav_io
from nucleo.analisis import Parametros

#: La carpeta de salida (figuras, informe y datos precalculados).
SALIDA = pathlib.Path(__file__).resolve().parent.parent / "salida"

#: La carpeta de audio.
AUDIO = pathlib.Path(__file__).resolve().parent.parent / "audio"

#: La carpeta con los ficheros estáticos que Vercel sirve directamente.
PUBLICO = pathlib.Path(__file__).resolve().parent.parent / "public"

#: Los parámetros del análisis por defecto. Se podrían exponer en la
#: interfaz, pero se dejan fijos para que las cifras del informe y las de
#: la web sean siempre las mismas.
PARAMETROS = Parametros()


@functools.lru_cache(maxsize=1)
def datos_precalculados() -> dict | None:
    """El JSON con los resultados, si está.

    Es lo que hace que la web responda en milisegundos, y lo que la
    hace funcionar dentro de un entorno serverless.
    """
    return serializacion.cargar_datos(SALIDA / "datos.json")


@functools.lru_cache(maxsize=1)
def catalogo_analizado() -> dict:
    """El análisis de las pistas del catálogo, cacheado.

    Prefiere los datos precalculados; si no están, los calcula.
    """
    pre = datos_precalculados()
    if pre is not None:
        return {"resultados": pre["resultados"],
                "faltantes": pre.get("faltantes", []),
                "precalculado": True}
    return {**analisis.analizar_catalogo(PARAMETROS, directorio=AUDIO),
            "precalculado": False}


@functools.lru_cache(maxsize=1)
def analisis_completo() -> dict:
    """El análisis con los arrays, para dibujar figuras que falten."""
    return analisis.analizar_catalogo(PARAMETROS, directorio=AUDIO)


@functools.lru_cache(maxsize=1)
def comparativa_calculada() -> dict:
    """La comparación entre los cinco, cacheada."""
    pre = datos_precalculados()
    if pre is not None and "comparativa" in pre:
        return pre["comparativa"]
    res = catalogo_analizado()
    return modulo_comparativa.resumen_tablas(res["resultados"])


def _figura_en_disco(clave: str, nombre: str) -> pathlib.Path:
    """La ruta de una figura, generándola si no existe.

    Las figuras que ya están dibujadas (y que se suben al repositorio)
    se sirven tal cual: es lo que permite que la web funcione dentro de
    Vercel sin dibujar nada.
    """
    ruta = SALIDA / f"{clave}_{nombre}.png"
    if ruta.exists():
        return ruta
    res = analisis_completo()
    if clave not in res["resultados"]:
        raise Http404(f"No hay ninguna pista '{clave}'")
    fn = figuras.FIGURAS_PISTA.get(nombre)
    if fn is None:
        raise Http404(f"No hay ninguna figura '{nombre}'")
    figuras.guardar(fn(res["resultados"][clave]), ruta)
    return ruta


# =============================================================================
# LAS PÁGINAS
# =============================================================================

def portada(request):
    """La portada: el resumen y el veredicto."""
    res = catalogo_analizado()
    comp = comparativa_calculada()
    veredicto = comp["veredicto"]
    fichas = []
    for clave, r in res["resultados"].items():
        fichas.append({
            "clave": clave,
            "nombre": r["nombre"],
            "musico": r["ficha"]["músico"],
            "obra": r["ficha"]["obra"],
            "anio": r["ficha"]["año"],
            "indice": r["atencion"]["indice"],
            "f_max": r["espectro"]["f_max"],
            "centroide": r["espectro"]["centroide"],
        })
    fs_minima_max = max((f["fs_minima"] for f in comp["veredicto"]["tabla"]),
                        default=0.0)
    return render(request, "motor/portada.html", {
        "resultados": res["resultados"],
        "comparativa": comp,
        "veredicto": veredicto,
        "fichas": fichas,
        "faltantes": res["faltantes"],
        "fs_minima_max": fs_minima_max,
        "factor_escala": (r_cuant(res) if res["resultados"] else 0.0),
    })


def r_cuant(res: dict) -> float:
    """El factor de escala a 16 bits de la primera pista."""
    if not res["resultados"]:
        return 0.0
    primero = next(iter(res["resultados"].values()))
    return primero["cuantizacion"]["casos"]["16"]["delta"]


def genero(request, clave):
    """La ficha de un género, con sus figuras, sus tablas y su audio."""
    res = catalogo_analizado()
    if clave not in res["resultados"]:
        raise Http404(f"No hay ninguna pista '{clave}'")
    r = res["resultados"][clave]
    comp = comparativa_calculada()
    return render(request, "motor/genero.html", {
        "r": r,
        "clave": clave,
        "comp": comp,
        "critérios": comp["criterios"].get(clave, {}),
        "critérios_es": "criterios",
    })


def comparativa(request):
    """Los cinco juntos: el punto (e) del enunciado."""
    res = catalogo_analizado()
    comp = comparativa_calculada()
    return render(request, "motor/comparativa.html", {
        "resultados": res["resultados"],
        "comp": comp,
        "veredicto": comp["veredicto"],
    })


def subir(request):
    """Subir tu propio WAV y analizarlo.

    Es el requisito (a) del enunciado, en su versión interactiva: el
    programa tiene que poder cargar audios cortos en formato WAV.
    """
    if request.method != "POST":
        return render(request, "motor/subir.html", {})

    subido = request.FILES.get("audio")
    if not subido:
        return render(request, "motor/subir.html", {
            "error": "No se ha elegido ningún fichero.",
        })

    nombre = subido.name
    if not nombre.lower().endswith(".wav"):
        return render(request, "motor/subir.html", {
            "error": "El fichero tiene que ser un WAV (.wav).",
        })

    destino = AUDIO / f"subido_{nombre}"
    try:
        with open(destino, "wb") as fh:
            for trozo in subido.chunks():
                fh.write(trozo)
    except Exception as exc:
        return render(request, "motor/subir.html", {
            "error": f"No se pudo guardar el fichero: {exc}",
        })

    try:
        pista = wav_io.leer_pista(destino, duracion=PARAMETROS.duracion)
    except Exception as exc:
        destino.unlink(missing_ok=True)
        return render(request, "motor/subir.html", {
            "error": f"El fichero no se pudo leer como un WAV: {exc}",
        })

    if pista.duracion < 1.0:
        destino.unlink(missing_ok=True)
        return render(request, "motor/subir.html", {
            "error": "El audio es demasiado corto (menos de 1 segundo).",
        })

    # se analiza con el mismo instrumental que el catálogo
    from nucleo.catalogo import Genero
    genero_subido = Genero(
        clave="subido",
        nombre=f"Subido · {nombre}",
        genero="Audio propio",
        musico="(el fichero que has subido)",
        obra=nombre,
        anio=0,
        compositor="—",
        estilo="—",
        instrumentacion="—",
        bpm_esperado="—",
        banda_clave="—",
        por_que="Pista subida por el usuario, analizada con el mismo "
                "instrumental que las del catálogo.",
    )
    try:
        r = analisis.analizar_pista(destino, PARAMETROS, genero_subido)
    except Exception as exc:
        return render(request, "motor/subir.html", {
            "error": f"El análisis falló: {exc}",
        })

    atencion = r["atencion"]
    return render(request, "motor/subir.html", {
        "r": r,
        "nombre": nombre,
        "atencion": atencion,
    })


def informe(request):
    """La página del informe: el resumen y las descargas."""
    return render(request, "motor/informe.html", {
        "ruta_informe": modulo_informe.SALIDA / "informe.md",
        "existe": (modulo_informe.SALIDA / "informe.md").exists(),
        "figuras": sorted(p.name for p in modulo_informe.SALIDA.glob("*.png")),
    })


# =============================================================================
# LOS FICHEROS
# =============================================================================

def figura(request, clave, nombre):
    """Sirve una figura como PNG.

    Primero se busca el PNG ya dibujado (los hay en `salida/` y se
    suben al repositorio): servir un fichero es instantáneo y no gasta
    tiempo de función, que en Vercel es el recurso escaso. Solo si no
    existe se dibuja al vuelo.
    """
    comparaciones = {
        "espectros_comparados": figuras.figura_espectros_comparados,
        "bandas_comparadas": figuras.figura_bandas,
        "indice_atencion": figuras.figura_indice,
        "veredicto": figuras.figura_veredicto,
    }
    if nombre in comparaciones:
        ruta = SALIDA / f"comparacion_{nombre}.png"
        if ruta.exists():
            return FileResponse(open(ruta, "rb"), content_type="image/png")
        res = analisis_completo()
        fig = comparaciones[nombre](res["resultados"])
        return HttpResponse(figuras.a_png(fig), content_type="image/png")

    ruta = _figura_en_disco(clave, nombre)
    return FileResponse(open(ruta, "rb"), content_type="image/png")


def estilo(request):
    """La hoja de estilos.

    Se busca primero en la carpeta de estáticos de la aplicación
    (`motor/static/motor/`) y luego en `public/`. El primero es el que
    siempre está: Vercel sirve `public/` solo si el constructor copia
    sus ficheros a la salida, y con el constructor de Python eso no
    ocurre. Servirla desde Django es un poco más lento, pero funciona
    en todas partes.
    """
    candidatos = (PUBLICO / "estilo.css",
                   pathlib.Path(__file__).resolve().parent / "static" /
                   "motor" / "estilo.css")
    for ruta in candidatos:
        if ruta.exists():
            return FileResponse(open(ruta, "rb"), content_type="text/css")
    raise Http404("No está la hoja de estilos")


def descarga_informe(request):
    """El informe en markdown, tal cual."""
    ruta = SALIDA / "informe.md"
    if not ruta.exists():
        raise Http404("El informe todavía no se ha generado")
    respuesta = FileResponse(open(ruta, "rb"), content_type="text/markdown")
    respuesta["Content-Disposition"] = 'attachment; filename="informe.md"'
    return respuesta


def descarga_figuras(request):
    """Todas las figuras en un ZIP, para descargarlo de una vez."""
    import zipfile
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for png in sorted(SALIDA.glob("*.png")):
            z.write(png, arcname=png.name)
    respuesta = HttpResponse(buffer.getvalue(),
                              content_type="application/zip")
    respuesta["Content-Disposition"] = (
        'attachment; filename="figuras_adc_dac.zip"')
    return respuesta


def _wav_en_bytes(x, fs: int) -> bytes:
    """Un array en [-1, 1] como bytes de un WAV PCM de 16 bits."""
    import wave
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(fs))
        w.writeframes(np_int16(x).tobytes())
    return buffer.getvalue()


def _cuantizar_en_vivo(clave: str, bits: int) -> tuple[bytes, int]:
    """Cuantiza el audio original AL MOMENTO y lo devuelve como WAV.

    Por qué se hace aquí y no se guarda un WAV por variante: el
    repositorio solo tiene que guardar el audio original (5 MB), y las
    versiones degradadas se generan en cada visita. Cuantizar 12 s de
    audio son unas operaciones aritméticas: tarda milisegundos, y así
    el repositorio no crece con cuatro copias de cada pista.
    """
    from nucleo import dsp_audio as dsp
    from nucleo import primitivas

    ruta = AUDIO / f"{clave}.wav"
    if not ruta.exists():
        raise Http404("Ese audio no está en el servidor")
    pista = wav_io.leer_pista(ruta)
    x = dsp.quitar_dc(pista.x)
    vfs = PARAMETROS.vfs
    x_v = wav_io.a_voltios(x, vfs)
    xq = primitivas.cuantizar(x_v, bits, 2.0 * vfs, saturar=True)
    return _wav_en_bytes(xq, pista.fs), pista.fs


def _telefonica_en_vivo(clave: str) -> tuple[bytes, int]:
    """La cadena telefónica (8 kHz, 8 bits) calculada al momento."""
    from nucleo import dsp_audio as dsp
    from nucleo import primitivas

    ruta = AUDIO / f"{clave}.wav"
    if not ruta.exists():
        raise Http404("Ese audio no está en el servidor")
    pista = wav_io.leer_pista(ruta)
    x = dsp.quitar_dc(pista.x)
    vfs = PARAMETROS.vfs
    fs_o = 8000
    n = int(len(x) * fs_o / pista.fs)
    x8 = dsp.antialias(x, pista.fs, fs_o, orden=PARAMETROS.orden_filtro)[:n]
    x8_v = wav_io.a_voltios(x8, vfs)
    xq = primitivas.cuantizar(x8_v, 8, 2.0 * vfs, saturar=True)
    t = np_arange(len(xq)) / fs_o
    x_zoh = primitivas.reconstruir_zoh(t, t, xq)
    return _wav_en_bytes(x_zoh, fs_o), fs_o


def np_arange(n: int):
    """`np.arange` sin importar NumPy en la cabecera del módulo."""
    import numpy as np
    return np.arange(n)


def audio(request, clave, variante):
    """Sirve un WAV generado: el original, el cuantizado, el telefónico.

    En el modo precalculado (el de Vercel) las versiones degradadas se
    generan en el momento a partir del audio original; con los datos
    completos en memoria, se usan las que ya trae el análisis.
    """
    res = catalogo_analizado()
    if clave not in res["resultados"]:
        raise Http404(f"No hay ninguna pista '{clave}'")
    r = res["resultados"][clave]
    fs = r["pista"]["fs"]

    if variante == "original":
        ruta = AUDIO / f"{clave}.wav"
        if not ruta.exists():
            raise Http404("Ese audio no está en el servidor")
        datos = ruta.read_bytes()
    elif variante in ("bits8", "bits12", "bits24"):
        bits = int(variante[4:])
        caso = r["cuantizacion"]["casos"].get(str(bits))
        if caso and "x_q" in caso:
            datos = _wav_en_bytes(caso["x_q"], fs)
        else:
            datos, _ = _cuantizar_en_vivo(clave, bits)
    elif variante == "telefonica":
        tel = r["cadena"]["telefonica"]
        if "x_zoh" in tel:
            datos = _wav_en_bytes(tel["x_zoh"], tel["fs"])
        else:
            datos, _ = _telefonica_en_vivo(clave)
    else:
        raise Http404("Esa variante no existe")

    respuesta = HttpResponse(datos, content_type="audio/wav")
    respuesta["Content-Disposition"] = (
        f'inline; filename="{clave}_{variante}.wav"')
    return respuesta


def np_int16(x):
    """Un array en [-1, 1] como enteros de 16 bits."""
    import numpy as np
    return np.clip(np.round(np.asarray(x) * 32767.0), -32768, 32767).astype("<i2")


def api_datos(request):
    """Los datos crudos en JSON, por si alguien quiere otra cosa."""
    res = catalogo_analizado()
    salida = {}
    for clave, r in res["resultados"].items():
        salida[clave] = {
            "nombre": r["nombre"],
            "f_max": r["espectro"]["f_max"],
            "fs_minima": r["espectro"]["fs_minima"],
            "centroide": r["espectro"]["centroide"],
            "bandas": {k: v["fraccion"] for k, v in
                       r["espectro"]["bandas"].items()},
            "indice": r["atencion"]["indice"],
            "bpm": r["ritmo"]["bpm"],
            "bpm_medible": r["ritmo"].get("medible", True),
        }
    return JsonResponse(salida)
