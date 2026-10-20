"""
wav_io.py — lectura y escritura de archivos WAV, sin dependencias.

POR QUÉ UN PARSER PROPIO Y NO `soundfile` o `librosa`
------------------------------------------------------
El enunciado pide trabajar con archivos WAV, y el formato WAV (RIFF) es
trivial de leer: una cabecera, un bloque de formato y un bloque de datos.
Escribirlo a mano tiene tres ventajas para un trabajo de DSP:

    1. No añade dependencias: el proyecto funciona con NumPy, SciPy,
       Matplotlib y nada más.
    2. Se VE lo que hace un ADC: los bytes se convierten a enteros con
       signo, se dividen por 2^(b-1) y se obtiene la tensión.
    3. Se puede limitar a un formato, o accepte los que se encuentran en
       la práctica: PCM de 8, 16, 24 y 32 bits, y coma flotante de 32 y
       64 bits.

QUÉ HACE
--------
    · `leer_wav(ruta)`  -> `Pista` con las muestras en mono, normalizadas.
    · `escribir_wav(ruta, x, fs, bits)`  -> escribe un WAV PCM.
    · `a_voltios(x, vfs)`  -> lleva la señal normalizada a ±vfs voltios.

EL FORMATO WAV, POR DENTRO
--------------------------
Un WAV es un contenedor RIFF con esta estructura:

    "RIFF"  <tamaño>  "WAVE"
    "fmt "  <16 o 18 o 40 bytes>   formato: canales, fs, bits, códec
    "data"  <tamaño>  <bytes de muestras>

El bloque `fmt ` dice, con 16 bytes:

    Bytes 0-1   format      1 = PCM entero, 3 = coma flotante IEEE
    Bytes 2-3   canales
    Bytes 4-7   fs          frecuencia de muestreo en Hz
    Bytes 8-11  byte_rate   fs · canales · bits/8
    Bytes 12-13 block_align canales · bits/8
    Bytes 14-15 bits        bits por muestra

Hay que leer los bloques en ORDEN y saltar los que no interesen (`LIST`,
`id3 `, `fact`...), porque un WAV exportado por un editor tiene bloques
extra antes del `data`. Ese es el error clásico: asumir que `data` está
justo después de `fmt `.

LA NORMALIZACIÓN
----------------
Las muestras se devuelven en [-1, 1], que es "plena escala" para un
conversor ideal. El valor exacto depende del formato:

    · PCM 8 bits: es SIN signo (0..255) y el cero está en 128.
    · PCM 16/24/32 bits: con signo, y el rango es -2^(b-1) .. 2^(b-1)-1.
    · Coma flotante: ya viene en [-1, 1] (o mayor, si el archivo tiene
      margen); se recorta a [-1, 1] para que "plena escala" signifique lo
      mismo en todos los casos.

El PCM de 8 bits es el único con signo cambiado, y es también el único
donde el error de cuantización es de 1/128 en vez de 1/32768: el
histograma de los valores sale desplazado. Por eso se resta 128 antes de
dividir.
"""

from __future__ import annotations

import pathlib
import struct
import wave
from dataclasses import dataclass, field

import numpy as np

#: Formatos de audio que se saben decodificar.
FORMATO_PCM = 1
FORMATO_FLOAT = 3
FORMATO_EXTENSIBLE = 0xFFFE

#: Separación entre canal y canal en un WAV multicanal.
_BLOQUE_FLOAT32 = "<f"
_BLOQUE_FLOAT64 = "<d"


# =============================================================================
# LA PISTA
# =============================================================================

@dataclass
class Pista:
    """Un audio cargado: sus muestras y todo lo que el WAV dice de él.

    Campos
    ------
    ruta       : pathlib.Path — de dónde se leyó
    fs         : int — frecuencia de muestreo en Hz (la del archivo, no la
                 que nos convenga)
    bits       : int — bits por muestra del archivo original
    canales    : int — canales del archivo original
    duracion   : float — duración en segundos
    x          : np.ndarray — las muestras en MONO, normalizadas a [-1, 1]
    etiqueta   : str — nombre corto para las gráficas
    """

    ruta: pathlib.Path
    fs: int
    bits: int
    canales: int
    duracion: float
    x: np.ndarray
    etiqueta: str = ""
    formato: str = "pcm"
    # información extra, no esencial
    extras: dict = field(default_factory=dict)

    @property
    def n_muestras(self) -> int:
        """Número de muestras del canal mono."""
        return int(len(self.x))

    @property
    def es_estereo(self) -> bool:
        """True si el archivo original tenía más de un canal."""
        return self.canales > 1

    @property
    def pico(self) -> float:
        """Valor absoluto máximo de la señal (0..1)."""
        return float(np.max(np.abs(self.x))) if len(self.x) else 0.0

    def resumen(self) -> dict:
        """Las cifras de cabecera, para las tablas del informe."""
        return {
            "archivo": self.ruta.name,
            "fs": self.fs,
            "bits": self.bits,
            "canales": self.canales,
            "duracion_s": round(self.duracion, 3),
            "n_muestras": self.n_muestras,
            "pico": round(self.pico, 6),
            "formato": self.formato,
        }


# =============================================================================
# LECTURA
# =============================================================================

def _decodificar(datos: bytes, formato: int, bits: int,
                  canales: int) -> np.ndarray:
    """Convierte los bytes crudos en muestras en coma flotante [-1, 1].

    Devuelve un array de forma (n_muestras, canales) con la columna 0 siendo
    el canal izquierdo.
    """
    if formato == FORMATO_FLOAT:
        if bits == 32:
            x = np.frombuffer(datos, dtype="<f4").astype(np.float64)
        elif bits == 64:
            x = np.frombuffer(datos, dtype="<f8").astype(np.float64)
        else:
            raise ValueError(f"coma flotante de {bits} bits no soportado")
        # un float WAV puede traer margen por encima de 1
        return np.clip(x, -1.0, 1.0).reshape(-1, canales)

    # PCM entero
    if bits == 8:
        # el PCM de 8 bits es SIN signo y su cero está en 128
        x = np.frombuffer(datos, dtype=np.uint8).astype(np.float64) - 128.0
        return (x / 128.0).reshape(-1, canales)
    if bits == 16:
        x = np.frombuffer(datos, dtype="<i2").astype(np.float64)
        return (x / 32768.0).reshape(-1, canales)
    if bits == 24:
        # 24 bits no tienen dtype en numpy: se leen como 32 y se desplaza
        crudos = np.frombuffer(datos, dtype=np.uint8).reshape(-1, 3)
        entero = (crudos[:, 0].astype(np.int32)
                  | (crudos[:, 1].astype(np.int32) << 8)
                  | (crudos[:, 2].astype(np.int32) << 16))
        entero = np.where(entero >= 1 << 23, entero - (1 << 24), entero)
        return (entero / 8388608.0).reshape(-1, canales)
    if bits == 32:
        x = np.frombuffer(datos, dtype="<i4").astype(np.float64)
        return (x / 2147483648.0).reshape(-1, canales)
    raise ValueError(f"PCM de {bits} bits no soportado")


def leer_wav(ruta: str | pathlib.Path) -> Pista:
    """Lee un archivo WAV y devuelve su `Pista` en mono.

    Parámetros
    ----------
    ruta : str o pathlib.Path
        El archivo a leer.

    Devuelve
    --------
    Pista
        Con las muestras normalizadas a [-1, 1], el canal izquierdo y el
        derecho promediados si el archivo es estéreo.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si el archivo no es un WAV válido, o su formato no se soporta.

    EJEMPLO
    -------
        >>> import numpy as np, tempfile, pathlib
        >>> p = pathlib.Path(tempfile.mkdtemp()) / "t.wav"
        >>> escribir_wav(p, np.zeros(1000), 8000, bits=16)
        >>> pista = leer_wav(p)
        >>> pista.fs, pista.bits, pista.canales, pista.n_muestras
        (8000, 16, 1, 1000)
    """
    ruta = pathlib.Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    return leer_wav_bytes(ruta.read_bytes(), nombre=ruta.name)


def leer_wav_bytes(datos: bytes, nombre: str = "audio.wav") -> Pista:
    """Lee un WAV que está EN MEMORIA, sin tocar el disco.

    Por qué hace falta: en un despliegue *serverless* (Vercel) el disco
    es de solo lectura, así que un WAV que sube el usuario no se puede
    guardar en el servidor. Se procesa en memoria y listo.

    Es el mismo analizador de RIFF que `leer_wav`, con la misma
    estructura: cabecera, bloques en orden, y los formatos soportados.
    """
    import io

    flujo = io.BytesIO(bytes(datos))

    def _leer_exactamente(n: int) -> bytes:
        datos_leidos = flujo.read(n)
        if len(datos_leidos) < n:
            raise ValueError(f"{nombre}: el fichero está incompleto")
        return datos_leidos

    cab = _leer_exactamente(12)
    if cab[0:4] != b"RIFF" or cab[8:12] != b"WAVE":
        raise ValueError(f"{nombre}: no es un archivo WAV (RIFF/WAVE)")

    formato = bits = canales = fs = None
    datos_muestras: bytes | None = None

    while True:
        cabecera = flujo.read(8)
        if len(cabecera) < 8:
            break
        id_chunk = cabecera[0:4]
        (tam,) = struct.unpack("<I", cabecera[4:8])

        if id_chunk == b"fmt ":
            cuerpo = _leer_exactamente(tam)
            fmt, canales, fs, _, _, bits = struct.unpack(
                "<HHIIHH", cuerpo[:16])
            if fmt == FORMATO_EXTENSIBLE and len(cuerpo) >= 26:
                fmt = struct.unpack("<H", cuerpo[24:26])[0]
        elif id_chunk == b"data":
            datos_muestras = _leer_exactamente(tam)
            if tam % 2:
                flujo.read(1)
        else:
            flujo.seek(tam + (tam % 2), 1)
            continue
        if tam % 2:
            flujo.read(1)

    if fmt is None or datos_muestras is None:
        raise ValueError(f"{nombre}: falta el bloque 'fmt ' o el 'data'")
    if fs is None or fs <= 0:
        raise ValueError(f"{nombre}: frecuencia de muestreo inválida")
    if canales is None or canales < 1:
        raise ValueError(f"{nombre}: número de canales inválido")
    if fmt not in (FORMATO_PCM, FORMATO_FLOAT):
        raise ValueError(
            f"{nombre}: códec {fmt} no soportado "
            f"(solo PCM entero y coma flotante IEEE)")

    muestras = _decodificar(datos_muestras, fmt, bits, canales)
    if muestras.size == 0:
        raise ValueError(f"{nombre}: el bloque 'data' está vacío")

    x_mono = muestras.mean(axis=1) if canales > 1 else muestras[:, 0]
    return Pista(
        ruta=pathlib.Path(nombre),
        fs=int(fs),
        bits=int(bits),
        canales=int(canales),
        duracion=len(x_mono) / float(fs),
        x=np.ascontiguousarray(x_mono, dtype=np.float64),
        etiqueta=pathlib.Path(nombre).stem,
        formato="pcm" if fmt == FORMATO_PCM else "float",
    )


def leer_pista(ruta: str | pathlib.Path, duracion: float | None = None,
               etiqueta: str = "") -> Pista:
    """Lee un WAV y, si se pide, lo recorta a los primeros `duracion` s.

    El recorte se hace en el origen: si el archivo tiene 3 minutos y solo
    interesan 12 segundos, se leen 12. En una interfaz web eso es la
    diferencia entre 2 segundos y 30.
    """
    pista = leer_wav(ruta)
    return recortar(pista, duracion, etiqueta)


def recortar(pista: Pista, duracion: float | None = None,
             etiqueta: str = "") -> Pista:
    """Recorta una `Pista` ya leída a los primeros `duracion` segundos.

    Se separa de `leer_pista` porque en un despliegue *serverless* el
    audio puede venir YA EN MEMORIA (subido por el usuario), y en ese
    caso no hay un fichero que leer: solo hay que recortar.
    """
    if duracion is not None and duracion > 0 and pista.duracion > duracion:
        n = int(duracion * pista.fs)
        pista.x = pista.x[:n]
        pista.duracion = n / float(pista.fs)
    if etiqueta:
        pista.etiqueta = etiqueta
    return pista


# =============================================================================
# ESCRITURA
# =============================================================================

def escribir_wav(destino: str | pathlib.Path, x: np.ndarray, fs: int,
                 bits: int = 16) -> pathlib.Path:
    """Escribe un WAV PCM de 8, 16, 24 o 32 bits con signo.

    Es la operación inversa de `leer_wav`, y se usa para exportar los
    resultados del ADC-DAC: el audio cuantizado a 8 bits, el reconstruido
    con aliasing, etc. Así se **escucha** lo que gráficos muestran.

    EJEMPLO
    -------
        >>> import numpy as np, tempfile, pathlib
        >>> p = pathlib.Path(tempfile.mkdtemp()) / "t.wav"
        >>> t = np.linspace(0, 1, 1000, endpoint=False)
        >>> escribir_wav(p, 0.5 * np.sin(2 * np.pi * 100 * t), 8000, bits=8)
        >>> leer_wav(p).bits
        8
    """
    destino = pathlib.Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(x, dtype=np.float64)

    if bits == 8:
        # sin signo, con el cero en 128
        entero = np.clip(np.round(x * 128.0) + 128.0, 0, 255).astype(np.uint8)
        muestras = entero.tobytes()
    elif bits == 16:
        entero = np.clip(np.round(x * 32768.0), -32768, 32767).astype("<i2")
        muestras = entero.tobytes()
    elif bits == 24:
        entero = np.clip(np.round(x * 8388608.0), -8388608, 8388607).astype("<i4")
        crudos = entero.astype("<u4").tobytes()
        muestras = b"".join(crudos[i:i + 3] for i in range(0, len(crudos), 4))
    elif bits == 32:
        entero = np.clip(np.round(x * 2147483648.0),
                         -2147483648, 2147483647).astype("<i4")
        muestras = entero.tobytes()
    else:
        raise ValueError(f"no se puede escribir un WAV de {bits} bits")

    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(bits // 8)
        w.setframerate(int(fs))
        w.writeframes(muestras)
    return destino


# =============================================================================
# VOLTIOS
# =============================================================================

def a_voltios(x: np.ndarray, vfs: float = 1.0) -> np.ndarray:
    """Lleva una señal normalizada [-1, 1] a ±`vfs` voltios.

    En un ADC real, el rango de entrada del convertidor está en voltios:
    un ADC de 12 bits con fondo de escala de ±5 V tiene 4096 niveles
    repartidos en 10 V, o sea 2,44 mV por nivel. Este es el factor de
    escala del punto (d) del enunciado: la razón entre el rango en voltios
    y el número de niveles.

    EJEMPLO
    -------
        >>> a_voltios(np.array([1.0, -1.0, 0.0]), vfs=5.0)
        array([ 5., -5.,  0.])
    """
    return np.asarray(x, dtype=np.float64) * float(vfs)


def factor_de_escala(vfs: float, bits: int) -> dict:
    """El factor de escala del cuantizador, en voltios y en bits.

    Devuelve
    --------
    dict con:
        vfs        : fondo de escala en voltios (±)
        rango_v    : rango total en voltios (2·vfs)
        niveles    : número de niveles (2^bits)
        y_voltios  : el factor de escala Y en VOLTIOS POR NIVEL (V/LSB)
        delta      : lo mismo, con otro nombre
        lsb        : y en voltios, abreviado
        snr_teorico_db : SNR de un cuantizador ideal de `bits` bits
        resolucion_relativa : Δ respecto al rango, en ppm (resolución en bits
                      equivalent: log2(rango/Δ) = bits, así que la
                      resolución RELATIVA es 2^-bits)

    POR QUÉ "Y" ES EL INVERSO DE 2^(b-1) Y NO DE 2^b
    -------------------------------------------------
    Un ADC de b bits tiene 2^b niveles, pero su código va de -2^(b-1) a
    2^(b-1)-1: el cero está en el centro, no en el extremo. Por eso el
    paso es

        Δ = (V_máx - V_mín) / 2^b = 2·V_fs / 2^b = V_fs / 2^(b-1)

    y NO 2·V_fs/2^(b+1). Es el error de un bit entero, y es el error más
    común al hacer cuentas de cuantización a mano.
    """
    if bits < 1:
        raise ValueError(f"bits debe ser >= 1, recibí {bits}")
    if vfs <= 0:
        raise ValueError(f"vfs debe ser positivo, recibí {vfs}")
    niveles = 2 ** bits
    rango_v = 2.0 * vfs
    delta = rango_v / niveles
    return {
        "vfs": float(vfs),
        "rango_v": rango_v,
        "niveles": niveles,
        "y_voltios": delta,
        "delta": delta,
        "lsb": delta,
        "snr_teorico_db": 1.76 + 6.0206 * bits,
        "resolucion_relativa": 1.0 / niveles,
    }
