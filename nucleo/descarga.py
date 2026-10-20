"""
descarga.py — baja las pistas de la muestra y las deja como WAV cortos.

QUÉ HACE
--------
Para cada pista del catálogo:

    1. Busca el tema en YouTube con `yt-dlp` y descarga el audio.
    2. Lo convierte a WAV PCM de 16 bits, mono, 44 1 kHz.
    3. ELIGE EL TRAMO DE 12 SEGUNDOS CON MAYOR ENERGÍA RMS.
    4. Guarda `audio/<clave>.wav` y anota la procedencia en
       `audio/descargas.json`.

POR QUÉ EL TRAMO SE ELIGE POR ENERGÍA Y NO A MANO
-------------------------------------------------
Las canciones empiezan con intros suaves o silencios. Si el corte es
arbitrario, unas pistas se analizan con la guitarra y otras con un silencio,
y la comparación entre géneros deja de ser justa. Eligiendo el tramo de
mayor RMS:

    · todos los clips tienen la misma duración (12 s),
    · todos contienen la parte más representativa de la pieza,
    · la regla es la misma para los cinco géneros y está publicada.

Es la misma idea que "medir en la rejilla densa y no en los nodos" del
proyecto Nyquist_Shannon: si no comparas en las mismas condiciones, la
comparación no vale.

REQUISITOS
----------
    · `yt-dlp` (ya instalado: `python -m yt_dlp`)
    · `ffmpeg` — se busca en el PATH y, si no está, se usa el que trae
      `imageio-ffmpeg` (`pip install imageio-ffmpeg`).

USO
---
    python -m nucleo.descarga              # baja las cinco pistas
    python -m nucleo.descarga --clave metal # solo una
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import wave

import numpy as np

# --------------------------------------------------------------------------
# RUTAS
# --------------------------------------------------------------------------

RAIZ = pathlib.Path(__file__).resolve().parent.parent
AUDIO = RAIZ / "audio"
TEMPORAL = RAIZ / ".tmp_descarga"

#: Duración del clip final, en segundos.
DURACION_CLIP = 12.0

#: Frecuencia de muestreo a la que se normalizan todos los clips.
FS_OBJETIVO = 44100

#: Pistas del catálogo. La clave es el nombre del fichero (sin extensión).
PISTAS: tuple[tuple[str, str, str], ...] = (
    ("barroca",
     "Bach Cello Suite No 1 G major BWV 1007 Netherlands Bach Society",
     "Bach - Cello Suite no. 1 in G major BWV 1007"),
    ("metal",
     "Megadeth Tornado of Souls",
     "Tornado Of Souls"),
    ("salsa",
     "Frankie Ruiz La Rueda",
     "Frankie Ruiz - La Rueda"),
    ("reggaeton",
     "Feid ATL Jacob LUNA",
     "LUNA"),
    ("popular",
     "Fredy Montoya Angel o Demonio Luisito Munoz",
     "Angel O Demonio"),
)


# --------------------------------------------------------------------------
# ffmpeg
# --------------------------------------------------------------------------

def ruta_ffmpeg() -> str:
    """La ruta al ejecutable de ffmpeg, o "" si no hay ninguna."""
    en_path = shutil.which("ffmpeg")
    if en_path:
        return en_path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ""


def convertir_a_wav(origen: pathlib.Path, destino: pathlib.Path,
                    fs: int = FS_OBJETIVO) -> bool:
    """Convierte cualquier audio a WAV PCM de 16 bits, mono, a `fs` Hz."""
    ffmpeg = ruta_ffmpeg()
    if not ffmpeg:
        print("  ERROR: no hay ffmpeg. Instálalo con: pip install imageio-ffmpeg")
        return False
    cmd = [
        ffmpeg, "-y", "-loglevel", "error", "-i", str(origen),
        "-ac", "1", "-ar", str(fs), "-c:a", "pcm_s16le", str(destino),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        detalle = exc.stderr.decode("utf-8", "replace")[:400]
        print(f"  ERROR de ffmpeg: {detalle}")
        return False
    return destino.exists()


# --------------------------------------------------------------------------
# SELECCIÓN DEL TRAMO
# --------------------------------------------------------------------------

def leer_wav_mono(ruta: pathlib.Path) -> tuple[np.ndarray, int]:
    """Lee un WAV PCM de 16 bits y devuelve (muestras en [-1,1], fs)."""
    with wave.open(str(ruta), "rb") as w:
        fs = w.getframerate()
        n_canales = w.getnchannels()
        ancho = w.getsampwidth()
        datos = w.readframes(w.getnframes())
    if ancho != 2:
        raise ValueError(f"{ruta.name}: se esperaba 16 bits, hay {ancho * 8}")
    x = np.frombuffer(datos, dtype="<i2").astype(np.float64) / 32768.0
    if n_canales > 1:
        x = x.reshape(-1, n_canales).mean(axis=1)
    return x, fs


def mejor_tramo(x: np.ndarray, fs: int,
                duracion: float = DURACION_CLIP) -> tuple[int, int, float]:
    """El tramo de `duracion` segundos con mayor energía RMS.

    Devuelve (inicio_muestra, fin_muestra, rms_del_tramo).

    Se recorre la pista en ventanas de 1 s y se queda con la de mayor RMS.
    Las ventanas se solapan, así que el resultado no depende de la
    alineación de la rejilla.
    """
    n = len(x)
    n_vent = int(duracion * fs)
    if n <= n_vent:
        return 0, n, float(np.sqrt(np.mean(x ** 2)))
    salto = fs
    mejor = (0, n_vent, -1.0)
    for inicio in range(0, n - n_vent + 1, salto):
        trozo = x[inicio:inicio + n_vent]
        rms = float(np.sqrt(np.mean(trozo ** 2)))
        if rms > mejor[2]:
            mejor = (inicio, inicio + n_vent, rms)
    return mejor


def escribir_wav(destino: pathlib.Path, x: np.ndarray, fs: int) -> None:
    """Escribe un WAV PCM de 16 bits, mono."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    enteros = np.clip(np.round(x * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(fs))
        w.writeframes(enteros.tobytes())


# --------------------------------------------------------------------------
# DESCARGA
# --------------------------------------------------------------------------

def bajar(clave: str, consulta: str, titulo_esperado: str) -> dict:
    """Baja una pista, la recorta y la guarda en `audio/<clave>.wav`."""
    import yt_dlp

    TEMPORAL.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    bruto = TEMPORAL / f"{clave}.%(ext)s"

    opciones = {
        "format": "bestaudio/best",
        "outtmpl": str(bruto),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "retries": 3,
        "ignoreerrors": False,
    }

    print(f"[{clave}] buscando: {consulta}")
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(f"ytsearch1:{consulta}", download=True)
        if info is None:
            raise RuntimeError(f"{clave}: la búsqueda no devolvió nada")
        if "entries" in info:
            info = info["entries"][0]
        archivo = pathlib.Path(ydl.prepare_filename(info))
        # yt-dlp puede cambiar la extensión si el formato no es el esperado
        if not archivo.exists():
            candidatos = sorted(TEMPORAL.glob(f"{clave}.*"))
            if not candidatos:
                raise RuntimeError(f"{clave}: no se descargó ningún fichero")
            archivo = candidatos[0]

    print(f"[{clave}] descargado: {info.get('title', '?')}"
          f" — {info.get('uploader', '?')}")

    wav_completo = TEMPORAL / f"{clave}_completo.wav"
    if not convertir_a_wav(archivo, wav_completo):
        raise RuntimeError(f"{clave}: falló la conversión a WAV")

    x, fs = leer_wav_mono(wav_completo)
    ini, fin, rms = mejor_tramo(x, fs)
    destino = AUDIO / f"{clave}.wav"
    escribir_wav(destino, x[ini:fin], fs)

    for sucio in TEMPORAL.glob(f"{clave}.*"):
        sucio.unlink(missing_ok=True)

    return {
        "clave": clave,
        "consulta": consulta,
        "titulo": info.get("title", ""),
        "artista": info.get("uploader", ""),
        "duracion_total_s": round(float(info.get("duration") or 0.0), 2),
        "inicio_tramo_s": round(ini / fs, 2),
        "rms_tramo": round(rms, 6),
        "fs": fs,
        "bits": 16,
        "canales": 1,
        "clip_s": round((fin - ini) / fs, 2),
        "url": info.get("webpage_url", ""),
        "archivo": destino.name,
    }


def cargar_registro() -> dict:
    """Lee `audio/descargas.json` (o devuelve un registro vacío)."""
    ruta = AUDIO / "descargas.json"
    if not ruta.exists():
        return {}
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar_registro(datos: dict) -> None:
    ruta = AUDIO / "descargas.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                    encoding="utf-8")


def descargar_todas(claves: list[str] | None = None) -> dict:
    """Descarga todas las pistas (o solo las claves indicadas)."""
    registro = cargar_registro()
    objetivo = [p for p in PISTAS if claves is None or p[0] in claves]
    for clave, consulta, titulo in objetivo:
        destino = AUDIO / f"{clave}.wav"
        if destino.exists() and clave in registro:
            print(f"[{clave}] ya está, se conserva")
            continue
        try:
            registro[clave] = bajar(clave, consulta, titulo)
            print(f"[{clave}] -> {destino.name} "
                  f"({registro[clave]['clip_s']} s desde "
                  f"{registro[clave]['inicio_tramo_s']} s)")
        except Exception as exc:
            print(f"[{clave}] ERROR: {exc}")
        guardar_registro(registro)
    return registro


def _main() -> int:
    claves = None
    if "--clave" in sys.argv:
        i = sys.argv.index("--clave")
        claves = [sys.argv[i + 1]] if i + 1 < len(sys.argv) else None
    descargar_todas(claves)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
