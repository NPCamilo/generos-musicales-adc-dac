"""
Pruebas de la aplicación web. Ejecutar con:  python nucleo/test_web.py

Comprueba que todas las páginas responden, que las figuras se sirven como
PNG y que los WAV generados son WAV válidos. Se usa el cliente de
pruebas de Django, así que no hace falta levantar el servidor.

La web es una CAPA encima del motor: si el motor está probado (eso lo
hacen las otras suites), aquí solo hay que comprobar que la capa no se
cae.
"""

from __future__ import annotations

import io
import os
import pathlib
import sys
import wave

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsp_web.settings")

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


def main() -> int:
    try:
        import django
        django.setup()
        from django.test import Client
    except Exception as exc:
        print(f"  FALLA no se pudo preparar Django: {exc}")
        return 1

    c = Client()

    # ---------------------------------------------------------------- 1
    _seccion("1) Las páginas responden")
    paginas = ["/", "/comparativa/", "/subir/", "/informe/"]
    for clave in ("barroca", "metal", "salsa", "reggaeton", "popular"):
        paginas.append(f"/genero/{clave}/")
    for url in paginas:
        try:
            r = c.get(url)
            chk(f"{url} responde 200", r.status_code == 200,
                f" ({r.status_code})")
        except Exception as exc:
            chk(f"{url} responde 200", False, f" ({exc})")

    # una página que no existe tiene que dar 404, no un error 500
    r = c.get("/genero/inexistente/")
    chk("un género inexistente da 404", r.status_code == 404,
        f" ({r.status_code})")

    # ---------------------------------------------------------------- 2
    _seccion("2) Las figuras se sirven como PNG")
    for url in ("/figura/metal/espectro.png", "/figura/metal/senal.png",
                "/figura/metal/muestreo.png", "/figura/metal/cuantizacion.png",
                "/figura/metal/codigos.png", "/figura/metal/cadena.png",
                "/figura/x/espectros_comparados.png",
                "/figura/x/bandas_comparadas.png",
                "/figura/x/indice_atencion.png",
                "/figura/x/veredicto.png"):
        r = c.get(url)
        ok = r.status_code == 200 and r["Content-Type"] == "image/png"
        largo = len(b"".join(r.streaming_content)) if hasattr(
            r, "streaming_content") else len(r.content)
        chk(f"{url} es un PNG", ok, f" ({r.status_code}, "
            f"{r['Content-Type']}, {largo} bytes)")

    # ---------------------------------------------------------------- 3
    _seccion("3) Los WAV que se pueden escuchar son WAV válidos")
    for variante in ("original", "bits8", "bits12", "telefonica"):
        url = f"/audio/metal/{variante}.wav"
        r = c.get(url)
        chk(f"{url} responde 200", r.status_code == 200, f" ({r.status_code})")
        if r.status_code != 200:
            continue
        contenido = (b"".join(r.streaming_content)
                     if hasattr(r, "streaming_content") else r.content)
        try:
            with wave.open(io.BytesIO(contenido), "rb") as w:
                n = w.getnframes()
                fs = w.getframerate()
                bits = w.getsampwidth() * 8
                canales = w.getnchannels()
            chk(f"{url} es un WAV legible",
                n > 0 and fs > 0 and bits == 16 and canales == 1,
                f" ({n} muestras, {fs} Hz, {bits} bits, {canales} canal)")
        except Exception as exc:
            chk(f"{url} es un WAV legible", False, f" ({exc})")

    # ---------------------------------------------------------------- 4
    _seccion("4) La subida de un WAV propio")
    fs = 44100
    t = np.arange(fs * 3) / fs
    x = 0.5 * np.sin(2 * np.pi * 220 * t)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    from django.core.files.uploadedfile import SimpleUploadedFile

    r = c.post("/subir/", {
        "audio": SimpleUploadedFile("prueba.wav", buffer.getvalue(),
                                    content_type="audio/wav")})
    chk("un WAV válido se sube y se analiza", r.status_code == 200,
        f" ({r.status_code})")
    chk("la respuesta trae las cifras del análisis",
        b"f_max" in r.content and b"Hz" in r.content)

    r = c.post("/subir/", {
        "audio": SimpleUploadedFile("basura.wav", b"esto no es un wav",
                                    content_type="audio/wav")})
    chk("un fichero inválido se rechaza con un mensaje",
        r.status_code == 200 and b"No se pudo" in r.content)

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
