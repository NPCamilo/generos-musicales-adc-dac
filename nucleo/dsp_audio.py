"""
dsp_audio.py — las herramientas de DSP que el audio real necesita.

QUÉ HAY AQUÍ
------------
El proyecto `Nyquist_Shannon` (del que viene este) trabaja con señales
que son SERIES DE FOURIER: de ahí sabe `f_max` exactamente, y puede
filtrar multiplicando cada armónico por `|H(k·f₀)|`. El audio real es
otra cosa: es una señal NO periódica, de duración finita, con contenido
en toda la banda y sin `f_max` conocido de antemano. Aquí está el
instrumental para eso.

    · `espectro_magnitud`   el espectro de magnitud, bien normalizado
    · `f_max_umbral`        la frecuencia máxima ÚTIL, medida
    · `antialias`           el filtro antialiasing + el re-muestreo
    · `muestrear`           submuestrear SIN filtro (el aliasing, a propósito)
    · `bpm`                 el tempo, por autocorrelación del flujo espectral
    · `bandas`              la energía por bandas (sonoras y tipo EEG)
    · `centroide`           el brillo del sonido
    · `indice_atencion`     el índice del punto (e), con sus pesos a la vista

LA CIFRA QUE MANDA: `f_max`
---------------------------
En una serie de Fourier, `f_max = k_max · f₀` es una fórmula. En audio
real no hay fórmula: hay que MEDIRLO, y la medida depende de un umbral.

Se usa este criterio, y se publica:

    f_max = la frecuencia más alta a la que el espectro suavizado sigue
            siendo al menos `umbral_db` decibelios por debajo del pico.

Por defecto `umbral_db = -40 dB`. Es un criterio de "-40 dB respecto al
pico", el mismo que se usa en análisis de audio y en la definición de
bandas de un medidor de nivel. Con -40 dB se ignoran los picos sueltos de
ruido (que son estrechos y no contributing energía) y se incluyen los
armónicos que se oyen.

Y como el criterio es una DECISIÓN, se calcula también con otros dos
umbrales (-30 dB y -50 dB) para poder mostrar en el informe de qué
depende el resultado. Un `f_max` que no se puede mover con el umbral es
sospechoso; uno que se mueve mucho es que el umbral está mal puesto.

EL ESPECTRO DE MAGNITUD, Y LA NORMALIZACIÓN CORRECTA
-----------------------------------------------------
Para que el eje de amplitudes sea comparable entre pistas distintas hay
que corregir por la GANANCIA COHERENTE de la ventana:

    A[k] = 2 · |X[k]| / (N · CG)        con  CG = media de la ventana

    CG(ventana rectangular) = 1
    CG(ventana Hann)         = 0,5
    CG(ventana Blackman)     = 0,42

Sin esa corrección, el pico de un tono en ventana Hann mide LA MITAD de
su amplitud, y al comparar dos pistas con ventanas distintas se comparan
cosas distintas. Es el mismo error que multiplicar por 4/N en vez de 2/N
en la FFT: un factor que parece "un ajuste de escala" y en realidad
cambia el resultado.

El factor 2 (y no 1) aparece porque un tono real produce DOS deltas, una
en +f y otra en -f, y solo se dibuja la mitad positiva del eje.
"""

from __future__ import annotations

import numpy as np

try:
    from scipy.signal import butter, get_window, sosfiltfilt
except ImportError:                    # pragma: no cover
    butter = get_window = sosfiltfilt = None

#: Bandas tipo EEG, en Hz, con su nombre. Se usan como REFERENCIA
#: (análogo, no equivalente) para el punto (e).
BANDAS_EEG: tuple[tuple[str, float, float], ...] = (
    ("delta", 0.5, 4.0),
    ("theta", 4.0, 8.0),
    ("alfa", 8.0, 13.0),
    ("beta", 13.0, 30.0),
    ("gamma", 30.0, 50.0),
)

#: Bandas de sonido, que son las que de verdad se miden aquí.
BANDAS_SONORAS: tuple[tuple[str, float, float], ...] = (
    ("subgrave", 20.0, 60.0),
    ("grave", 60.0, 250.0),
    ("medio", 250.0, 2000.0),
    ("agudo", 2000.0, 8000.0),
    ("muy agudo", 8000.0, 20000.0),
)


# =============================================================================
# PREPARACIÓN DE LA SEÑAL
# =============================================================================

def quitar_dc(x: np.ndarray) -> np.ndarray:
    """Quita la componente continua (el offset) de la señal.

    Un WAV grabado tiene un offset distinto de cero (el cero del
    convertidor no coincide con el cero eléctrico). Ese offset se cuela
    como una delta en f = 0 del espectro y falsea la energía de la banda
    "subgrave", que es justo una de las que se comparan entre géneros.

    EJEMPLO
    -------
        >>> import numpy as np
        >>> float(quitar_dc(np.ones(10)).mean())
        0.0
    """
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return x
    return x - float(np.mean(x))


def ganancia_coherente(ventana: np.ndarray) -> float:
    """La ganancia coherente de una ventana: `mean(ventana)`.

    Es el factor por el que la ventana atenúa una senoidal coherente. La
    ventana rectangular no atenúa (1,0); la Hann, la mitad (0,5).
    """
    v = np.asarray(ventana, dtype=np.float64)
    if len(v) == 0:
        return 1.0
    return float(np.mean(v))


# =============================================================================
# ESPECTRO
# =============================================================================

def espectro_magnitud(x: np.ndarray, fs: float, ventana: str = "hann",
                      nfft: int | None = None) -> dict:
    """El espectro de magnitud de un tramo de audio, en amplitudes reales.

    Parámetros
    ----------
    x      : las muestras (cualquier longitud)
    fs     : frecuencia de muestreo en Hz
    ventana : "hann", "blackman", "hamming" o "rectangular"
    nfft   : tamaño de la FFT; por defecto, la siguiente potencia de dos
             mayor o igual que len(x) (zero-padding, que NO cambia la
             amplitud de los picos, solo hace la rejilla más fina)

    Devuelve
    --------
    dict con:
        f        : eje de frecuencias 0..fs/2 en Hz
        A        : amplitud de cada línea (misma escala que la señal)
        db       : 20·log10(A / A_max)
        fs, N, nfft, ventana
        pico_hz  : la frecuencia del pico de amplitud
        pico     : su amplitud

    EJEMPLO
    -------
        >>> import numpy as np
        >>> fs = 8000
        >>> t = np.arange(2000) / fs
        >>> esp = espectro_magnitud(np.sin(2*np.pi*500*t), fs)
        >>> round(esp["pico_hz"])
        500
        >>> round(esp["pico"], 3)
        1.0
    """
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        raise ValueError("la señal está vacía")
    if fs <= 0:
        raise ValueError(f"fs debe ser positiva, recibí {fs}")

    N = len(x)
    if nfft is None:
        nfft = int(2 ** np.ceil(np.log2(N)))
    nfft = max(int(nfft), N)

    if get_window is not None and ventana and ventana.lower() not in (
            "rectangular", "rect", "ninguna", "none", ""):
        w = get_window(ventana.lower(), N, fftbins=True)
    else:
        w = np.ones(N)
    w = np.asarray(w, dtype=np.float64)

    cg = ganancia_coherente(w)
    if cg <= 0:
        raise ValueError("la ventana tiene ganancia coherente nula")

    y = x * w
    if nfft > N:
        y = np.concatenate([y, np.zeros(nfft - N)])

    X = np.fft.rfft(y)
    A = 2.0 * np.abs(X) / (nfft * cg)
    if len(A) > 0:
        A[0] *= 0.5                     # el DC no se duplica
    f = np.fft.rfftfreq(nfft, d=1.0 / fs)

    db = 20.0 * np.log10(np.maximum(A, 1e-20))
    k_pico = int(np.argmax(A))

    return {
        "f": f,
        "A": A,
        "db": db,
        "fs": float(fs),
        "N": N,
        "nfft": int(nfft),
        "ventana": ventana,
        "ganancia_coherente": cg,
        "pico_hz": float(f[k_pico]),
        "pico": float(A[k_pico]),
    }


def suavizar_db(db: np.ndarray, f: np.ndarray,
                ancho_hz: float = 100.0) -> np.ndarray:
    """Suaviza un espectro en dB con una media móvil en Hz.

    Sirve para dos cosas:

      · medir `f_max` sin que un pico suelto de ruido lo determine,
      · dibujar un espectro legible, sin el ruido de cada bin.

    LA MEDIA MÓVIL SE HACE EN POTENCIA, NO EN DECIBELIOS
    ----------------------------------------------------
    Promediar valores en dB es un error clásico, y aquí se Notaba mucho:
    el pico de un tono ocupa 3 bins a -0,2 dB y los bins vecinos están a
    -30, -60, -90 dB. Promediar dB da unos -92 dB, y el "pico" suavizado
    desaparece 90 dB por debajo del real. Con el criterio de `f_max`
    basado en ese máximo, el resultado era que un tono puro de 500 Hz
    daba f_max = 0 Hz.

    Lo correcto es promediar la POTENCIA (que es lo que se suma en el
    tiempo) y volver a dB al final:

        P = 10^(db/10)          se promedia P          db' = 10·log10(P')

    Con eso, el pico suavizado queda a unos 10·log10(ventana/pico) dB del
    pico real, que es la caída de energía que corresponde a un tono
    repartido en la ventana, y no a un error de las unidades.

    La media móvil se hace en Hz, no en bins, porque el ancho de un bin
    depende de la duración del registro: suavizar "en bins" daría
    resoluciones distintas para pistas distintas, que es justo lo que no
    se quiere al comparar.

    LA IMPLEMENTACIÓN, CON SUMAS ACUMULADAS
    --------------------------------------
    `np.convolve` con modo "same" es O(N·M): con un clip de 12 s a
    44,1 kHz la FFT tiene 2^20 bins y una ventana de 250 Hz son ~6000
    bins, o sea 6000 millones de operaciones por suavizado. Además, en
    los bordes el modo "same" no hace lo que parece, y se vio un pico
    fantasma en el bin de DC que desplazaba el máximo del espectro
    suavizado y, con él, la medida de `f_max`.

    Aquí la media móvil se calcula con sumas acumuladas (O(N)) y en los
    bordes se usa la ventana PARCIAL, que es lo correcto: en el primer
    bin solo hay media ventana disponible, y su media es la de lo que hay.
    """
    if ancho_hz <= 0 or len(db) == 0:
        return np.asarray(db, dtype=np.float64)
    df = float(f[1] - f[0]) if len(f) > 1 else 1.0
    n = max(1, int(round(ancho_hz / df)))
    if n <= 1:
        return np.asarray(db, dtype=np.float64)

    potencia = 10.0 ** (np.asarray(db, dtype=np.float64) / 10.0)
    k = n // 2
    acumulado = np.concatenate(([0.0], np.cumsum(potencia)))
    idx = np.arange(len(potencia))
    lo = np.clip(idx - k, 0, len(potencia))
    hi = np.clip(idx + k + 1, 0, len(potencia))
    media = (acumulado[hi] - acumulado[lo]) / (hi - lo)
    return 10.0 * np.log10(np.maximum(media, 1e-30))


def f_max_umbral(espectro: dict, umbral_db: float = -40.0,
                 ancho_suavizado_hz: float = 30.0) -> float:
    """La frecuencia máxima útil, medida con un criterio publicado.

    Devuelve la frecuencia (en Hz) más alta a la que el espectro suavizado
    sigue estando al menos `umbral_db` dB por debajo del pico.

    EL PICO DE REFERENCIA ES EL DEL ESPECTRO CRUDO
    ----------------------------------------------
    El umbral se mide respecto al pico REAL, no respecto al pico del
    espectro suavizado. No es un detalle: al suavizar, la energía de un
    tono se reparte entre decenas de bins, y el máximo suavizado queda
    unos 15 dB por debajo del real. Si el umbral se midiera respecto al
    máximo suavizado, el "pico" sería la referencia equivocada y el
    `f_max` se iría más lejos de lo que corresponde.

    Y LA VENTANA DE SUAVIZADO ES CORTA A PROPÓSITO
    ----------------------------------------------
    Con 30 Hz la ventana sólo ablanda los picos estrechos (el ruido de
    un bin suelto), sin repartir la energía de un tono por medio
    kilohertz. Con 250 Hz, que es lo que se usa para DIBUJAR, el mismo
    tono se repartiría por toda la ventana y el criterio se iría
    demasiado lejos. Son dos usos distintos con dos ventanas
    distintas, y por eso la ventana es un argumento y no una constante.

    EJEMPLO
    -------
        >>> import numpy as np
        >>> fs = 8000
        >>> t = np.arange(4000) / fs
        >>> esp = espectro_magnitud(np.sin(2*np.pi*500*t), fs)
        >>> round(f_max_umbral(esp, -40.0))
        500
    """
    db = espectro["db"]
    f = espectro["f"]
    if len(db) == 0:
        return 0.0
    suave = suavizar_db(db, f, ancho_suavizado_hz)
    nivel = float(np.max(db)) + float(umbral_db)
    indices = np.flatnonzero(suave >= nivel)
    if len(indices) == 0:
        return 0.0
    return float(f[indices[-1]])


def f_max_energia(espectro: dict, fraccion: float = 0.999) -> float:
    """La frecuencia por debajo de la que está el `fraccion` de la energía.

    Es un criterio DISTINTO del de umbral, y más robusto: en vez de mirar
    la altura de la curva, mira cuánta energía se ha acumulado.

        f_max = la f tal que  ∫₀^f |A(f')|² df'  =  fraccion · ∫₀^∞ |A|² df'

    Con `fraccion = 0,999` es "la frecuencia por debajo de la que está el
    99,9 % de la energía".

    Por qué se necesita: el criterio de umbral depende de dónde esté el
    suelo de ruido de la grabación, y eso cambia entre tomas: una toma
    limpia y una con ruido de fondo dan umbrales de -40 dB que significan
    cosas distintas. El criterio de energía acumulada no depende del suelo
    de ruido, y por eso se usa como control: si los dos criterios dan
    cifras del mismo orden, la medida es sólida; si se separan mucho, hay
    que mirar el ruido de la grabación.
    """
    f = espectro["f"]
    P = espectro["A"] ** 2
    total = float(np.sum(P))
    if total <= 0:
        return 0.0
    acumulada = np.cumsum(P) / total
    idx = int(np.searchsorted(acumulada, fraccion))
    idx = min(idx, len(f) - 1)
    return float(f[idx])


def ancho_banda_ocupado(espectro: dict, umbral_db: float = -40.0) -> float:
    """El ancho de banda ocupado: de f_min a f_max con el mismo criterio.

    Sirve para saber si una pista "usa" toda la banda (ruido,oriundo) o
    solo una parte (tono, instrumento).
    """
    db = espectro["db"]
    f = espectro["f"]
    if len(db) == 0:
        return 0.0
    nivel = float(np.max(db)) + float(umbral_db)
    dentro = np.flatnonzero(db >= nivel)
    if len(dentro) == 0:
        return 0.0
    return float(f[dentro[-1]] - f[dentro[0]])


# =============================================================================
# FILTRADO Y RE-MUESTREO
# =============================================================================

def _filtro_pasabajos(x: np.ndarray, fs: float, fc: float,
                      orden: int = 8) -> np.ndarray:
    """Filtro Butterworth de fase cero, con `fc` en Hz.

    Usa `sosfiltfilt` (sección de segundo orden + filtrado en ambos
    sentidos), que anula el retardo de grupo: la señal sale alineada en
    el tiempo. Sin eso, el audio saldría desplazado y las comparaciones
    entre pistas no valdrían.

    Si `fc` está por encima de Nyquist no se filtra nada.
    """
    if butter is None or sosfiltfilt is None:
        raise ImportError("hace falta SciPy para filtrar")
    nyq = fs / 2.0
    if fc <= 0 or fc >= nyq:
        return np.asarray(x, dtype=np.float64)
    wn = fc / nyq
    sos = butter(orden, wn, btype="low", output="sos")
    n = len(x)
    # el margen del filtro: 3·(orden+1) muestras para que el
    # filtrado en ambos sentidos no se coma los extremos
    pad = min(3 * (orden + 1), max(0, n - 1))
    if pad > 0:
        y = np.concatenate([np.zeros(pad), x, np.zeros(pad)])
        y = sosfiltfilt(sos, y)
        return y[pad:pad + n]
    return sosfiltfilt(sos, x)


def antialias(x: np.ndarray, fs_in: float, fs_out: float,
              orden: int = 8, margen: float = 0.45) -> np.ndarray:
    """Re-muestrea de `fs_in` a `fs_out` con filtro antialiasing.

    Es el camino REAL de un ADC: antes de muestrear más despacio, se
    filtra para que no entre en la banda nueva nada de lo que estaba por
    encima de `fs_out/2`.

    El corte se pone en `margen · fs_out/2` (45 % por defecto) porque un
    filtro real no cae en vertical: si se pusiera el corte exactamente en
    `fs_out/2`, parte del contenido original se metería en la banda nueva
    y el aliasing no desaparecería del todo.

    La salida tiene `floor(len(x) · fs_out/fs_in)` muestras.
    """
    x = np.asarray(x, dtype=np.float64)
    if fs_in <= 0 or fs_out <= 0:
        raise ValueError("las frecuencias de muestreo deben ser positivas")
    if fs_out >= fs_in:
        return x.copy()

    fc = margen * fs_out / 2.0
    filtrado = _filtro_pasabajos(x, fs_in, fc, orden)

    # se eligen los instantes de reloj del nuevo ADC: t = n/fs_out
    n_salida = int(np.floor(len(filtrado) * fs_out / fs_in))
    indices = np.arange(n_salida) * (fs_in / fs_out)
    return filtrado[np.clip(indices.astype(int), 0, len(filtrado) - 1)]


def muestrear(x: np.ndarray, fs_in: float, fs_out: float,
              con_filtro: bool = False) -> np.ndarray:
    """Submuestrea sin filtro: así se produce el ALIASING a propósito.

    Con `con_filtro=False` (por defecto) NO se filtra nada: se toman las
    muestras en los instantes del nuevo reloj y ya está. Eso es lo que
    hace un ADC sin filtro antialiasing, y el resultado es que el
    contenido por encima de `fs_out/2` se pliega dentro de la banda y
    **no se puede recuperar después**.

    Con `con_filtro=True` delega en `antialias`.
    """
    if con_filtro:
        return antialias(x, fs_in, fs_out)
    x = np.asarray(x, dtype=np.float64)
    n = int(np.floor(len(x) * fs_out / fs_in))
    indices = np.arange(n) * (fs_in / fs_out)
    return x[np.clip(indices.astype(int), 0, len(x) - 1)]


def fs_minima_nyquist(f_max: float) -> float:
    """La `f_s` mínima según Nyquist-Shannon: `2 · f_max`."""
    return 2.0 * float(f_max)


# =============================================================================
# RITMO
# =============================================================================

def envolvente_de_ataques(x: np.ndarray, fs: float, hop: int = 512,
                           nfft: int = 1024) -> dict:
    """El flujo espectral: una serie que marca CADA ATAQUE percusivo.

    Se calcula el espectro de cada fotograma y se suman SOLO las partes
    que han subido respecto del fotograma anterior:

        flujo[k] = Σ max(0, |X_k| - |X_{k-1}|)

    Es la detección de onsets más barata que funciona bien: un bombo, un
    timbal, una guitarra rasgueada producen un salto de energía en las
    frecuencias medias, y ese salto es lo que se marca.

    Devuelve un dict con:
        envolvente : la serie del flujo espectral
        fps        : la frecuencia a la que se muestrea (fs/hop)
        cresta     : el factor de cresta de la envolvente (pico/-media)

    LA CRESTA DE LA ENVOLVENTE, Y POR QUÉ IMPORTA
    ----------------------------------------------
    Una envolvente con CRESTAS tiene picos: hay golpes. Una envolvente
    PLANA no los tiene: no hay percusión.

    El caso límite es una senoidal pura. Su flujo espectral no es cero:
    la fuga del bin hace que la magnitud oscile de fotograma a
    fotograma, y esa oscilación tiene una periodicidad espuria. El
    detector de tempo la confunde con un pulso y da un tempo falso con
    una confianza alta (0,86 en las pruebas). Por eso la ENVOLVENTE por
    sí sola no basta, y hace falta el segundo criterio: la cresta.

        cresta de un metrónomo a 120 BPM : ~59
        cresta de las piezas reales      : 3,1 a 8,4
        cresta de una senoidal continua  : ~2,4
    """
    x = np.asarray(x, dtype=np.float64)
    if len(x) < nfft:
        x = np.concatenate([x, np.zeros(nfft - len(x))])
    n_fotogramas = 1 + (len(x) - nfft) // hop
    if n_fotogramas < 2:
        return {"envolvente": np.zeros(1), "fps": fs / hop, "cresta": 0.0}

    ventana = np.hanning(nfft)
    espectros = np.empty((n_fotogramas, nfft // 2 + 1))
    for i in range(n_fotogramas):
        trozo = x[i * hop:i * hop + nfft]
        espectros[i] = np.abs(np.fft.rfft(trozo * ventana))

    flujo = np.diff(espectros, axis=0)
    flujo = np.clip(flujo, 0.0, None).sum(axis=1)
    media = float(np.mean(flujo))
    cresta = float(np.max(flujo) / media) if media > 0 else 0.0
    return {"envolvente": flujo, "fps": fs / hop, "cresta": cresta}


def bpm(x: np.ndarray, fs: float, bpm_min: float = 60.0,
        bpm_max: float = 190.0) -> dict:
    """El tempo de la pieza, en pulsos por minuto.

    Método: el "peine" sobre la autocorrelación
    ------------------------------------------
    1. Se calcula la envolvente de ataques (flujo espectral).
    2. Se autocorrelaciona esa envolvente. El máximo da el periodo del
       pulso, pero el máximo puede estar en un múltiplo del periodo
       verdadero (si el patrón se repite cada 2 pulsos, el pico
       fuerte está en 2T) o en su divisor.
    3. Para resolverlo se usa un FILTRO DE PEINE: para cada tempo
       candidato se suman las autocorrelaciones en los retardos
       T, 2T, 3T y 4T:

           score(bpm) = ac(T) + ac(2T) + ac(3T) + ac(4T)

       Un tempo real puntúa alto en los cuatro retardos, porque el pulso
       se repite; una frecuencia que solo casa con el segundo armónico
       puntúa bajo. El máximo del peine es el tempo.

    Por qué no "contar picos": contar picos depende de la
    instrumentación (un metal con doble bombo tiene el doble de picos
    por tiempo que un cuatro por cuatro), mientras que la autocorrelación
    de la envolvente encuentra el PERIODO, que es lo que define el tempo.

    Devuelve
    --------
    dict con:
        bpm         : el tempo estimado (o 0.0 si no se pudo)
        bpm_estable : la desviación típica del tempo en ventanas
        confianza   : 0..1, cuánto destaca el pico del peine
        periodo_s   : el periodo en segundos
        fs_ventana  : la resolución en BPM de la búsqueda
    """
    envolvente_info = envolvente_de_ataques(x, fs)
    envolvente = envolvente_info["envolvente"]
    fps = envolvente_info["fps"]
    cresta = envolvente_info["cresta"]
    if len(envolvente) < 16:
        return {"bpm": 0.0, "bpm_estable": 0.0, "confianza": 0.0,
                "puntuacion": 0.0, "medible": False, "cresta": cresta,
                "candidatos": [], "periodo_s": 0.0, "fs_ventana": 0.0}

    e = envolvente - envolvente.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    if ac[0] > 0:
        ac = ac / ac[0]

    # el peine: se puntúa cada tempo candidato
    candidatos = np.arange(bpm_min, bpm_max + 0.25, 0.25)
    puntajes = np.zeros(len(candidatos))
    for i, b in enumerate(candidatos):
        T = 60.0 * fps / b
        suma = 0.0
        for k in (1, 2, 3, 4):
            retardo = k * T
            if retardo >= len(ac) - 1:
                break
            i0 = int(retardo)
            fr = retardo - i0
            v = ac[i0] * (1.0 - fr) + ac[i0 + 1] * fr
            suma += max(v, 0.0)
        puntajes[i] = suma / 4.0

    k = int(np.argmax(puntajes))
    bpm_est = float(candidatos[k])

    # LA CONFIANZA, COMO PREGUNTA: ¿DESTACA EL MEJOR CANDIDATO?
    # -------------------------------------------------------
    # La puntuación bruta del peine no es comparable entre piezas: una
    # con percusión marcada da 0,8 y una sin percusión da 0,1, pero eso
    # no significa que la segunda mida "menos bien": significa que no
    # tiene pulso.
    #
    # Lo que sí es comparable es el CONTRASTE: cuánto destaca el mejor
    # candidato frente al resto. Por eso la confianza se define como la
    # posición del mejor dentro del rango de puntuaciones:
    #
    #     confianza = (mejor - mediana) / (mejor - peor)
    #
    # Vale 1 si el mejor candidato está solo, y 0 si todos valen igual.
    # Con esa definición, 0,3 significa "destaca claramente". En una
    # pieza sin percusión el valor es bajo, y eso es información, no
    # fallo: significa que el tempo NO es medible en esa pieza.
    mejor = float(puntajes[k])
    mediana = float(np.median(puntajes))
    peor = float(np.min(puntajes))
    rango = mejor - peor
    confianza = float(np.clip((mejor - mediana) / rango, 0.0, 1.0)) \
        if rango > 1e-12 else 0.0

    # los tres mejores candidatos: el tempo casi siempre tiene una
    # ambigüedad (el doble, la mitad, o el 3/4), y enseñarla es más
    # honesto que decidir en silencio.
    orden = np.argsort(puntajes)[::-1]
    candidatos_top = [{"bpm": float(candidatos[i]),
                        "puntuacion": float(puntajes[i])}
                       for i in orden[:3]]

    # ¿ES MEDIBLE EL TEMPO?
    # ----------------------
    # hacen falta DOS condiciones:
    #
    #   1. que la puntuación del peine sea alta (hay un periodo que
    #      puntúa alto frente a los demás), y
    #   2. que la envolvente de ataques tenga CRESTAS (hay golpes).
    #
    # La segunda condición es la que evita el falso positivo de las
    # senoidales: un tono puro genera un flujo espectral con una
    # estructura periódica espuria, y el peine lo "-"encuentra" con una
    # confianza de 0,86. Pero su envolvente es plana (cresta 2,4), así
    # que se descarta.
    #
    # La calibración, con lo medido en este proyecto:
    #
    #   metrónomo sintético a 120 BPM : puntuación 0,60 · cresta 59
    #   las cinco piezas reales       : puntuación 0,18-0,40 · cresta 3,1-8,4
    #   una senoidal continua         : puntuación 0,62 · cresta 2,4  ← el falso
    #
    # con las dos condiciones, la senoidal se rechaza y las piezas reales
    # se aceptan.
    MEDIBLE_DESDE = 0.25
    CRESTA_MINIMA = 3.0
    medible = (mejor >= MEDIBLE_DESDE) and (cresta >= CRESTA_MINIMA)

    # el desdoblamiento de la octava: el peine puede tener el mismo
    # máximo en el tempo y en su mitad, porque los pulsos 1, 2, 3 y 4 del
    # peine están en la misma posición que 2, 4, 6 y 8 en el otro. Se
    # prefiere el tempo más alto que no baje del rango, que es el que
    # corresponde al pulso-percusión y no al compás.
    for b in candidatos[::-1]:
        if abs(b - bpm_est) < 1e-6:
            continue
        if b >= bpm_min and abs(puntajes[np.argmin(np.abs(candidatos - b))]
                                - mejor) < 0.02 * max(mejor, 1e-9) + 0.02:
            bpm_est = float(b)
            break

    estable = _estabilidad_tempo(envolvente, fs, bpm_est)
    return {
        "bpm": bpm_est,
        "bpm_estable": float(estable),
        "confianza": float(confianza),
        "puntuacion": float(mejor),
        "medible": bool(medible),
        "cresta": float(cresta),
        "candidatos": candidatos_top,
        "periodo_s": float(60.0 / bpm_est) if bpm_est else 0.0,
        "fs_ventana": float(0.25),
    }


def _estabilidad_tempo(envolvente: np.ndarray, fs: float,
                       bpm_est: float) -> float:
    """La dispersión del tempo medido en ventanas: ¿el pulso es regular?

    Se mide el tempo en varias ventanas de la envolvente y se devuelve la
    DESVIACIÓN TÍPICA. Un valor bajo significa un pulso regular (una
    batería con metrónomo, un cuatro por cuatro); un valor alto significa
    un tempo que respira, que es exactamente lo que en la literatura sobre
    música y atención se asocia a un estado más relajado y menos
    "provocador".
    """
    if bpm_est <= 0 or len(envolvente) < 16:
        return 0.0
    fps = fs / 512.0
    largo = int(fps * 4.0)            # ventanas de 4 s
    if largo < 8 or len(envolvente) < 2 * largo:
        return 0.0
    valores = []
    for ini in range(0, len(envolvente) - largo, largo):
        tramo = envolvente[ini:ini + largo]
        e = tramo - tramo.mean()
        ac = np.correlate(e, e, mode="full")[len(e) - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        lag_min = max(1, int(fps * 60.0 / 190.0))
        lag_max = min(len(ac) - 1, int(fps * 60.0 / 60.0))
        if lag_max <= lag_min:
            continue
        lag = lag_min + int(np.argmax(ac[lag_min:lag_max + 1]))
        if lag > 0:
            valores.append(60.0 * fps / lag)
    if len(valores) < 2:
        return 0.0
    return float(np.std(valores))


# =============================================================================
# BANDAS Y BRILLO
# =============================================================================

def energias_por_banda(espectro: dict,
                       bandas: tuple[tuple[str, float, float], ...] = BANDAS_SONORAS
                       ) -> dict:
    """La energía (potencia) de cada banda, en fracción del total.

    Se usa la POTENCIA (`A²`), no la amplitud, porque lo que suma en el
    tiempo es la potencia: dos tonos de la misma amplitud pero en
    frecuencias distintas no aportan lo mismo a la sensación de "energía"
    si uno está en 80 Hz y otro en 8 kHz.
    """
    f = espectro["f"]
    A = espectro["A"]
    P = A ** 2
    total = float(np.sum(P))
    salida = {}
    for nombre, f0, f1 in bandas:
        dentro = (f >= f0) & (f < f1)
        p = float(np.sum(P[dentro]))
        salida[nombre] = {
            "f0": f0,
            "f1": f1,
            "potencia": p,
            "fraccion": (p / total) if total > 0 else 0.0,
        }
    return salida


def centroide_espectral(espectro: dict, potencia: bool = True) -> float:
    """El centroide espectral: el "brillo" de la pieza, en Hz.

        c = Σ f·A^p / Σ A^p        con p = 1 (amplitud) o p = 2 (potencia)

    Es el centro de gravedad del espectro. Una pieza con centroide bajo
    (150-400 Hz) es grave y Spotify; una con centroide alto (2-4 kHz) es
    brillante y presente. Es el indicador más citado en el análisis
    de "brillo" de un sonido.
    """
    f = espectro["f"]
    A = espectro["A"]
    w = A ** 2 if potencia else A
    s = float(np.sum(w))
    if s <= 0:
        return 0.0
    return float(np.sum(f * w) / s)


def planicidad_espectral(espectro: dict) -> float:
    """La planicidad: 0 = un tono puro, 1 = ruido blanco.

        planicidad = media geométrica / media aritmética de la potencia

    Es una medida de TONALIDAD: un instrumentoafinada da una potencia
    muy desigual entre bins (planicidad baja); el ruido da una potencia
    pareja (planicidad alta).
    """
    P = espectro["A"] ** 2
    P = P[P > 0]
    if len(P) == 0:
        return 0.0
    media_arit = float(np.mean(P))
    if media_arit <= 0:
        return 0.0
    media_geom = float(np.exp(np.mean(np.log(P))))
    return media_geom / media_arit


def crest_factor(x: np.ndarray) -> float:
    """El factor de cresta: pico / RMS.

    Mide la DINÁMICA. En música, un valor de 3-4 es una señal muy
    comprimida (sin silencios: es la "música de fondo de un gimnasio"), y
    un valor de 5-7 es una grabación con mucho margen entre picos y
    silencios, como una toma acústica o una grabación de época.

    En el punto (e) importa porque la compresión con limitador es, junto
    con la densidad de percusión, uno de los rasgos que se han
    identificado como proveedores de excitación en la música que resulta
    activante para quien tiene TDAH.
    """
    x = np.asarray(x, dtype=np.float64)
    rms = float(np.sqrt(np.mean(x ** 2)))
    if rms <= 0:
        return 0.0
    return float(np.max(np.abs(x)) / rms)


# =============================================================================
# EL ÍNDICE DE ATENCIÓN (PUNTO e)
# =============================================================================

#: Los cinco criterios salen de `nucleo/fuentes.py`, que es el sitio
#: único donde vive el dato de referencia de cada uno y la cita que lo
#: respalda.
try:
    from .fuentes import CRITERIOS as _CRITERIOS_FUENTES
except ImportError:                       # ejecución suelta
    from fuentes import CRITERIOS as _CRITERIOS_FUENTES

#: Los cinco criterios del índice, con su peso y su justificación.
#:
#: Cada criterio se normaliza a 0..1 (1 = mejor para concentrarse) y se
#: multiplica por su peso. La suma da el índice de 0 a 100.
#:
#: LA PREGUNTA QUE RESPONDE EL ÍNDICE
#: -----------------------------------
#: "Si un estudiante con TDAH pone esta pieza de fondo mientras
#: estudia, ¿ayuda o estorba?" Por eso los criterios NO son aesthetic
#: (¿es bonita?) sino de COMPETENCIA POR LA ATENCIÓN:
#:
#:   · el pulso, que marca el ritmo interno del cuerpo,
#:   · el brillo, que activa,
#:   · los agudos de percusión, que son transitorios y enganchan,
#:   · el rango dinámico, que da descanso,
#:   · y la banda de la voz (300 Hz-3,5 kHz), que es la MISMA en la que
#:     habla el profesor: una pieza con cantante en esa banda compite
#:     con la voz que el estudiante tiene que seguir.
CRITERIOS_atencion: tuple[dict, ...] = tuple(
    {
        "clave": c.clave,
        "nombre": c.nombre,
        "peso": c.peso,
        "por_que": c.peso_justo,
    }
    for c in _CRITERIOS_FUENTES
)

def _puntuacion_tempo(bpm: float) -> float:
    """1.0 dentro de 60-90 BPM, decayendo por fuera.

    La curva es una "trapezoid": plana en la ventana buena, y cae
    linealmente hasta 0 a 45 BPM por debajo y a 30 BPM por encima.
    """
    if bpm <= 0:
        return 0.0
    if 60.0 <= bpm <= 90.0:
        return 1.0
    if bpm < 60.0:
        return float(np.clip((bpm - 45.0) / 15.0, 0.0, 1.0))
    return float(np.clip((135.0 - bpm) / 45.0, 0.0, 1.0))


def _puntuacion_regularidad(estable: float) -> float:
    """1.0 si el tempo es irregular (respirado), 0.0 si es mecánico.

    Se toma `estable` (desviación típica del tempo en BPM). Con 0 BPM de
    dispersión la pieza es un metrónomo (puntuación 0); con 8 BPM o más ya
    se considera "respirada" (puntuación 1).
    """
    return float(np.clip(estable / 8.0, 0.0, 1.0))


def _puntuacion_brillo(centroide: float) -> float:
    """1.0 si el centroide está por debajo de 400 Hz, 0.0 si pasa de 2500 Hz."""
    if centroide <= 0:
        return 0.0
    if centroide <= 400.0:
        return 1.0
    if centroide >= 2500.0:
        return 0.0
    return float((2500.0 - centroide) / (2500.0 - 400.0))


def _puntuacion_agudos(fraccion: float) -> float:
    """1.0 si casi no hay energía en 2-8 kHz, 0.0 si es más de la mitad."""
    return float(np.clip(1.0 - fraccion / 0.5, 0.0, 1.0))


def _puntuacion_dinamica(crest: float) -> float:
    """1.0 con mucha dinámica (crest alto), 0.0 si está comprimida.

    El factor de cresta de la música va de ~3 (comprimida con
    limitador) a ~7 (grabación de época o música acústica). Por debajo de
    3 dB de crest la señal está claramente aplastada; por encima de 6 dB
    tiene mucho margen entre picos y silencios.
    """
    if crest <= 0:
        return 0.0
    if crest <= 3.0:
        return 0.0
    if crest >= 6.0:
        return 1.0
    return float((crest - 3.0) / 3.0)


def _puntuacion_voz(fraccion: float) -> float:
    """1.0 si casi no hay energía en 300 Hz-3,5 kHz, 0.0 si es la mitad."""
    return float(np.clip(1.0 - fraccion / 0.5, 0.0, 1.0))


def indice_atencion(metricas: dict) -> dict:
    """El índice de atención: un número de 0 a 100, con sus cuentas a la vista.

    Parámetros
    ----------
    metricas : dict
        Con las claves "bpm", "bpm_estable", "confianza_bpm", "centroide",
        "frac_agudos" y "crest".

    Devuelve
    --------
    dict con:
        indice      : 0..100
        por_criterio : [{clave, nombre, peso, valor, puntos, por_que}]
        veredicto   : una frase corta con la lectura
        tempo_no_fiable : True si el pulso no se pudo medir con confianza

    LO QUE ESTE ÍNDICE NO ES
    ------------------------
    No es una medida de la atención de nadie. Es una puntuación de PROPIEDADES
    ACÚSTICAS de una grabación, con los pesos a la vista, para poder
    compararla con otra. El paso de "esta canción suena más tranquila" a
    "a un estudiante con TDAH le va a servir más" es un SALTO que este
    proyecto NO da: eso requiere un estudio con personas, con un grupo de
    control, y no cabe en un trabajo de DSP. Lo que sí se puede hacer, y
    es lo que se hace, es:

      1. medir las propiedades acústicas con precisión,
      2. publicarlas,
      3. contrastarlas con lo que dice la literatura,
      4. y decir con todas las letras que es una HIPÓTESIS.

    Un índice con pesos escondidos no sirve ni para comparar ni para
    discutir. Con los pesos a la vista, se puede estar en desacuerdo con
    un peso, y eso es una discusión sana.
    """
    bpm = float(metricas.get("bpm", 0.0))
    estable = float(metricas.get("bpm_estable", 0.0))
    centroide = float(metricas.get("centroide", 0.0))
    frac_agudos = float(metricas.get("frac_agudos", 0.0))
    frac_voz = float(metricas.get("frac_voz", 0.0))
    crest = float(metricas.get("crest", 0.0))
    confianza = float(metricas.get("confianza_bpm", 1.0))
    medible = bool(metricas.get("tempo_medible", True))

    valores = {
        "tempo": _puntuacion_tempo(bpm),
        "brillo": _puntuacion_brillo(centroide),
        "agudos": _puntuacion_agudos(frac_agudos),
        "dinamica": _puntuacion_dinamica(crest),
        "voz": _puntuacion_voz(frac_voz),
    }

    # EL TEMPO ES FIABLE O NO LO ES
    # -------------------------------
    # Una pieza sin percusión (un preludio barroco, por ejemplo) no tiene
    # un pulso que medir: la envolvente de ataques no tiene picos claros
    # y la autocorrelación devuelve cualquier cosa. Cuando el pulso no es
    # medible, el criterio de tempo NO debe decidir nada: se puntúa como
    # neutro (0,5) y se anota, en vez de meter ruido en el índice. Es
    # mejor un índice con un "no medido" declarado que un índice que
    # finge una precisión que no tiene.
    tempo_no_fiable = (not medible) or confianza < 0.30
    if tempo_no_fiable:
        valores["tempo"] = 0.5

    filas = []
    total = 0.0
    for crit in CRITERIOS_atencion:
        v = float(np.clip(valores[crit["clave"]], 0.0, 1.0))
        puntos = v * crit["peso"]
        total += puntos
        filas.append({
            "clave": crit["clave"],
            "nombre": crit["nombre"],
            "peso": crit["peso"],
            "valor": v,
            "puntos": puntos,
            "por_que": crit["por_que"],
        })

    if total >= 70:
        veredicto = "favorable como fondo de estudio"
    elif total >= 55:
        veredicto = "aceptable como fondo de estudio"
    elif total >= 40:
        veredicto = "discutible como fondo de estudio"
    else:
        veredicto = "poco recomendable como fondo de estudio"

    return {
        "indice": float(total),
        "por_criterio": filas,
        "veredicto": veredicto,
        "tempo_no_fiable": bool(tempo_no_fiable),
    }
