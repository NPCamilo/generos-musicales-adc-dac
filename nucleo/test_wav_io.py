"""
Pruebas de `wav_io.py`. Ejecutar con:  python nucleo/test_wav_io.py

El parser de WAV es la primera barrera del proyecto: si lee mal, todo
lo demás está mal. Estas pruebas comprueban:

  1. La ida y la vuelta (escribir → leer) en los formatos soportados
  2. Que los valores leídos son los que se escribieron
  3. Que el PCM de 8 bits (sin signo, con el cero en 128) se decodifica
     bien, que es el error clásico
  4. Que el estéreo se promedia a mono
  5. Que los errores se detectan (fichero que no es WAV, códec no
     soportado, bits raros)
  6. Que el factor de escala en voltios es el que dice la fórmula
"""

from __future__ import annotations

import pathlib
import struct
import tempfile

import numpy as np

try:
    from . import wav_io
except ImportError:
    import wav_io

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
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="wav_io_test_"))
    fs = 8000
    t = np.arange(fs) / fs
    x = 0.5 * np.sin(2 * np.pi * 440 * t)

    # ---------------------------------------------------------------- 1
    _seccion("1) Ida y vuelta en todos los formatos")
    for bits in (8, 16, 24, 32):
        ruta = tmp / f"v{bits}.wav"
        wav_io.escribir_wav(ruta, x, fs, bits=bits)
        p = wav_io.leer_wav(ruta)
        chk(f"{bits} bits: fs leída", p.fs == fs, f" ({p.fs})")
        chk(f"{bits} bits: bits leídos", p.bits == bits, f" ({p.bits})")
        chk(f"{bits} bits: mono", p.canales == 1)
        chk(f"{bits} bits: nº de muestras",
            p.n_muestras == len(x), f" ({p.n_muestras})")
        chk(f"{bits} bits: duración",
            abs(p.duracion - 1.0) < 1e-9, f" ({p.duracion})")
        # la tolerancia es la del cuantizador de ese formato
        tol = 2.0 / (2 ** (bits - 1))
        error = float(np.max(np.abs(p.x - x)))
        chk(f"{bits} bits: el error de la vuelta es el de un LSB",
            error <= tol * 1.01, f" (error {error:.3e}, tol {tol:.3e})")

    # ---------------------------------------------------------------- 2
    _seccion("2) El PCM de 8 bits: sin signo, con el cero en 128")
    # un WAV de 8 bits con el valor 128 tiene que leerse como 0
    ruta8 = tmp / "cero128.wav"
    with open(ruta8, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", 36 + 8) + b"WAVE")
        fh.write(b"fmt " + struct.pack("<I", 16))
        fh.write(struct.pack("<HHIIHH", 1, 1, fs, fs, 1, 8))
        fh.write(b"data" + struct.pack("<I", 4) + bytes([128, 128, 128, 128]))
    p8 = wav_io.leer_wav(ruta8)
    chk("el 128 del PCM de 8 bits es el cero", float(np.max(np.abs(p8.x))) < 1e-12,
        f" (máx {float(np.max(np.abs(p8.x)))})")
    chk("el PCM de 8 bits da 4 muestras", p8.n_muestras == 4)

    # ---------------------------------------------------------------- 3
    _seccion("3) El estéreo se promedia a mono")
    ruta_es = tmp / "estereo.wav"
    with open(ruta_es, "wb") as fh:
        n = 100
        datos = np.zeros(n * 2, dtype="<i2")
        datos[0::2] = 32767      # canal izquierdo
        datos[1::2] = 32767      # canal derecho
        fh.write(b"RIFF" + struct.pack("<I", 36 + len(datos)) + b"WAVE")
        fh.write(b"fmt " + struct.pack("<I", 16))
        fh.write(struct.pack("<HHIIHH", 1, 2, fs, fs * 4, 4, 16))
        fh.write(b"data" + struct.pack("<I", datos.nbytes) + datos.tobytes())
    pes = wav_io.leer_wav(ruta_es)
    chk("el estéreo tiene 2 canales", pes.canales == 2)
    chk("el estéreo se lee en mono", pes.n_muestras == 100)
    chk("la media de los canales es correcta",
        abs(float(pes.x[0]) - 32767 / 32768.0) < 1e-6)

    # ---------------------------------------------------------------- 4
    _seccion("4) Los errores se detectan")
    basura = tmp / "basura.wav"
    basura.write_bytes(b"esto no es un wav")
    try:
        wav_io.leer_wav(basura)
        chk("un fichero que no es WAV lanza error", False)
    except ValueError:
        chk("un fichero que no es WAV lanza error", True)
    except Exception as exc:
        chk("un fichero que no es WAV lanza error", False, f" ({exc})")

    try:
        wav_io.leer_wav(tmp / "no_existe.wav")
        chk("un fichero inexistente lanza error", False)
    except FileNotFoundError:
        chk("un fichero inexistente lanza error", True)

    # un códec que no es PCM (por ejemplo ADPCM, códec 2)
    ruta_adpcm = tmp / "adpcm.wav"
    with open(ruta_adpcm, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", 36 + 8) + b"WAVE")
        fh.write(b"fmt " + struct.pack("<I", 16))
        fh.write(struct.pack("<HHIIHH", 2, 1, fs, fs, 1, 4))
        fh.write(b"data" + struct.pack("<I", 8) + b"\x00" * 8)
    try:
        wav_io.leer_wav(ruta_adpcm)
        chk("un códec no soportado lanza error", False)
    except ValueError:
        chk("un códec no soportado lanza error", True)

    # ---------------------------------------------------------------- 5
    _seccion("5) El factor de escala, en voltios y en bits")
    esc = wav_io.factor_de_escala(1.0, 16)
    chk("el factor de escala de 16 bits es V_fs/2^15",
        abs(esc["y_voltios"] - 1.0 / 32768.0) < 1e-18,
        f" ({esc['y_voltios']:.3e} V)")
    chk("el número de niveles es 2^16", esc["niveles"] == 65536)
    chk("el SNR teórico de 16 bits es 98 dB",
        abs(esc["snr_teorico_db"] - (1.76 + 6.0206 * 16)) < 1e-9)
    esc12 = wav_io.factor_de_escala(5.0, 12)
    chk("con ±5 V, el paso de 12 bits es 2·5/4096",
        abs(esc12["y_voltios"] - 10.0 / 4096.0) < 1e-12,
        f" ({esc12['y_voltios']:.6f} V)")
    try:
        wav_io.factor_de_escala(1.0, 0)
        chk("bits = 0 lanza error", False)
    except ValueError:
        chk("bits = 0 lanza error", True)

    v = wav_io.a_voltios(np.array([1.0, -1.0, 0.0]), 5.0)
    chk("a_voltios escala bien", abs(v[0] - 5.0) < 1e-12 and abs(v[1] + 5.0) < 1e-12)

    # ---------------------------------------------------------------- 6
    _seccion("6) El recorte por duración")
    ruta = tmp / "largo.wav"
    wav_io.escribir_wav(ruta, x, fs, bits=16)
    corto = wav_io.leer_pista(ruta, duracion=0.25)
    chk("el recorte deja 0,25 s", abs(corto.duracion - 0.25) < 1e-9,
        f" ({corto.duracion})")
    chk("el recorte deja las muestras correctas", corto.n_muestras == 2000)

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
