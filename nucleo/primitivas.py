"""
primitivas.py — las primitivas de DSP que usa el proyecto.

POR QUÉ ESTE MÓDULO EXISTE
---------------------------
La primera versión de este proyecto importaba estas funciones del
proyecto `Nyquist_Shannon/`, que está en la carpeta de al lado. Funcionaba
en local, pero **no se podía desplegar**: en Vercel (y en cualquier
repositorio) solo se sube ESTE proyecto, y la carpeta hermana no está
ahí. La aplicación fallaba al arrancar con un `ModuleNotFoundError`.

Así que aquí están las primitivas, adaptadas del proyecto anterior (es
tuño, del mismo trabajo de Comunicaciones) y escritas para que este
proyecto sea **autosuficiente**: se clona, se instala y funciona, sin
depender de ninguna carpeta de al lado.

Lo que hay aquí
---------------
    · las métricas de error (RMSE, NRMSE, SNR),
    · el cuantizador uniforme de punto medio, con saturación,
    · la carga, los bits efectivos y el SNR teórico,
    · el dither uniforme y el triangular (TPDF),
    · la reconstrucción de Shannon (suma de senos cardinales),
    · el retenedor de orden cero (el DAC barato),
    · el diagnóstico de Nyquist.

NINGÚN NÚMERO "MÁGICO"
----------------------
Todos los coeficientes (6.0206, 1.76, 2^bits) están justificados en su
docstring, y todos se pueden comprobar numéricamente con las pruebas de
`nucleo/test_analisis.py`.
"""

from __future__ import annotations

import numpy as np

#: La ganancia en dB por bit: `20·log10(2)`.
DB_POR_BIT = 6.0206

#: La penalización de plena escala: `20·log10(2^B·√2 / 2^(B+1))`.
PENALIZACION_PLENA_ESCALA = 1.76

#: Por debajo de este valor una amplitud se considera exactamente cero.
UMBRAL_ACTIVO = 1e-12


# =============================================================================
# LAS MÉTRICAS DE ERROR
# =============================================================================

def rmse(x_real: np.ndarray, x_hat: np.ndarray) -> float:
    """El error cuadrático medio, sin normalizar.

        RMSE = sqrt( mean( (x - x_hat)^2 ) )

    Es la métrica base de la que salen casi todas las demás: el NRMSE es
    el RMSE dividido por algo, y el SNR sale de la relación entre la
    energía de la señal y la del error.

    POR QUÉ EL CUADRADO, Y POR QUÉ LA RAÍZ
    --------------------------------------
    El cuadrado penaliza mucho más los errores grandes que los pequeños:
    un error de 0.1 aporta 0.01, uno de 1.0 aporta 1.0. Eso es lo que
    quiero: un pico de 2 voltios equivocado arruina más una señal que
    mil errores de 1 mV.

    La raíz devuelve a las unidades originales, para que el número se
    pueda comparar con la amplitud de la señal sin tener que hacer
    cuentas. Sin la raíz, el RMSE sería potencia y no amplitud, y
    compararlo con la amplitud daría un error de √2.
    """
    x_real = np.asarray(x_real, dtype=float)
    x_hat = np.asarray(x_hat, dtype=float)
    if x_real.shape != x_hat.shape:
        raise ValueError(
            f"Las señales tienen distinta forma: {x_real.shape} vs "
            f"{x_hat.shape}. No se puede comparar punto a punto.")
    if x_real.size == 0:
        raise ValueError("No se puede medir el error de una señal vacía")
    return float(np.sqrt(np.mean((x_real - x_hat) ** 2)))


def nrmse_por_rango(x_real: np.ndarray, x_hat: np.ndarray) -> float:
    """NRMSE normalizado por el RANGO de la señal real.

        NRMSE = RMSE / (max(x) - min(x))

    Divide por el rango y no por el RMS de la señal porque así un offset
    grande NO puede disimular el error: dividir por el RMS de una señal
    con mucho DC infla el denominador y achica el error hasta hacerlo
    invisible. El rango depende solo de la amplitud, no del nivel.

    Si la señal real es constante (rango 0), no hay escala contra la cual
    medir, y se devuelve el RMSE puro.
    """
    x_real = np.asarray(x_real, dtype=float)
    rango = float(x_real.max() - x_real.min())
    base = rmse(x_real, x_hat)
    return base / rango if rango > 0 else base


def snr_db(x_real: np.ndarray, x_err: np.ndarray) -> float:
    """La relación señal/error en decibelios.

        SNR_dB = 20·log10( RMS(x) / RMS(x_err) )

    Es lo mismo que `10·log10(P_señal/P_error)`, solo que escrito con
    amplitudes.

    POR QUÉ DECIBELES Y NO UNA RAZÓN
    ---------------------------------
    Porque las razones de potencia se comprimen mal: pasar de 1 a 10 es
    multiplicar por 10, y de 100 a 1000 también. En dB, lo primero son
    10 dB y lo segundo otros 10 dB.

    LA CONVENCIÓN: positivo = la señal domina = bien. Negativo = el error
    es mayor que la señal.

    CASOS DEGENERADOS, QUE HAY QUE PROTEGER
    ---------------------------------------
    · error = 0    ->  +inf (la reconstrucción es perfecta).
    · señal = 0    ->  -300 dB en vez de -inf, porque un -inf rompe el
                      formato de las tablas y no aporta información.
    · ambos = 0    ->  0.0 (no hay nada que comparar).
    """
    x_real = np.asarray(x_real, dtype=float)
    x_err = np.asarray(x_err, dtype=float)
    if x_real.shape != x_err.shape:
        raise ValueError(
            f"La señal y el error tienen formas distintas: "
            f"{x_real.shape} y {x_err.shape}. El SNR se define sobre el "
            f"MISMO conjunto de puntos.")
    if x_real.size == 0:
        raise ValueError("La señal está vacía")
    p_senal = float(np.sqrt(np.mean(x_real ** 2)))
    p_error = float(np.sqrt(np.mean(x_err ** 2)))

    if p_error == 0.0 and p_senal == 0.0:
        return 0.0
    if p_error == 0.0:
        return float("inf")
    if p_senal == 0.0:
        return -300.0
    return float(20.0 * np.log10(p_senal / p_error))


# =============================================================================
# EL CUANTIZADOR
# =============================================================================

def parametros_cuantiizador(bits: int, rango: float) -> dict:
    """Los números de un cuantizador uniforme de `bits` bits sobre `rango`.

    `rango` es el recorrido de pico a pico, es decir 2·V (para una
    senoidal de amplitud V el recorrido es justo 2V). Los niveles son 2^B,
    el paso es

        Δ = rango / 2^B

    y el error de redondeo está acotado a Δ/2.
    """
    if bits < 1:
        raise ValueError(f"Hacen falta bits >= 1, recibí {bits}")
    if rango <= 0:
        raise ValueError(f"El rango debe ser positivo, recibí {rango}")
    niveles = 2 ** bits
    delta = rango / niveles
    return {
        "bits": bits,
        "niveles": niveles,
        "rango": rango,
        "delta": delta,
        "error_maximo": delta / 2.0,
        "varianza_teorica": delta ** 2 / 12.0,
        "snr_teorico_db": snr_teorico_cuanti(bits),
        "paso_por_segundo": DB_POR_BIT,
    }


def cuantizar(x: np.ndarray, bits: int, rango: float,
              saturar: bool = True) -> np.ndarray:
    """Cuantizador uniforme de punto medio con redondeo al más próximo.

        x_q = -rango/2 + (k + 0.5)·Δ,   k = floor((x + rango/2)/Δ)

    Los `2**bits` niveles son los CENTROS de las celdas, no los bordes. La
    diferencia importa:

        x_q = Δ·round(x/Δ)          ->  N+1 niveles, y NO son centros
        x_q = -rango/2 + (k+0.5)·Δ  ->  N niveles, sí son centros

    Comprobado con una rampa densa: 8 bits dan 257 niveles distintos en
    vez de 256, y 3 bits dan 9 en vez de 8, con la primera fórmula.

    El nivel más alto tampoco está en ±rango/2 sino en ±(rango/2 - Δ/2),
    porque es el centro de la última celda. Con 8 bits y rango 2 V son
    ±0.99609375 V, no ±1 V.

    Con `saturar=False` lo que sale del rango se mantiene, que no existe
    en un ADC real pero sirve para separar "me equivoqué de rango" de
    "hay clipping".
    """
    x = np.asarray(x, dtype=float)
    p = parametros_cuantiizador(bits, rango)
    delta = p["delta"]
    n = int(p["niveles"])
    k = np.floor((x + rango / 2.0) / delta)
    if saturar:
        k = np.clip(k, 0.0, n - 1.0)
    return -rango / 2.0 + (k + 0.5) * delta


def factor_carga(x: np.ndarray, rango: float) -> dict:
    """Cuánta parte del rango del convertidor usa realmente la señal.

    El SNR de 6.02·B dB es para una señal a PLENA ESCALA. Si el pico de x
    es una fracción `c` de la mitad del rango, la potencia de señal baja
    c² y el SNR baja `20·log10(1/c)` dB. Es la causa número uno de "mi ADC
    de 16 bits no me da 98 dB".

    Comprobado: con 8 bits, una senoidal a −20 dBFS da 29.78 dB en vez de
    49.92 dB. Se pierden 20.14 dB, que es el −20 dBFS de la entrada.
    """
    x = np.asarray(x, dtype=float)
    if rango <= 0:
        raise ValueError(f"El rango debe ser positivo, recibí {rango}")
    if x.size == 0:
        raise ValueError("La señal está vacía")
    pico = float(np.max(np.abs(x)))
    mitad = rango / 2.0
    carga = min(pico / mitad, 1.0) if mitad > 0 else 0.0
    dbfs = 20.0 * np.log10(carga) if carga > UMBRAL_ACTIVO else -np.inf
    return {
        "pico": pico,
        "rango": rango,
        "mitad_rango": mitad,
        "carga": carga,
        "dbfs": dbfs,
        "perdida_db": -dbfs if np.isfinite(dbfs) else np.inf,
        "satura": pico > mitad,
    }


def bits_efectivos(x: np.ndarray, bits: int, rango: float) -> float:
    """Cuántos bits quedan de verdad, después de contar la carga.

        bits_efectivos = bits - perdida_db / 6.02

    Es la cifra que hay que citar cuando alguien pregunta "¿cuánta
    resolución tiene mi medida?".
    """
    c = factor_carga(x, rango)
    if not np.isfinite(c["perdida_db"]):
        return 0.0
    return max(0.0, bits - c["perdida_db"] / DB_POR_BIT)


def snr_teorico_cuanti(bits: int) -> float:
    """`1,76 + 6,02·B` dB: el SNR de un cuantizador ideal con senoidal a
    plena escala.

    El +1.76 no es un adorno: sale de la potencia de la senoidal, A²/2
    con A = rango/2, dividida por Δ²/12.

        SNR = 10·log10( (R²/8) / (R²/(2^B)²/12) ) = 1.76 + 6.02·B

    Y el "6 dB por bit" tampoco es aproximado: cada bit duplica los
    niveles, o sea divide el error entre 2, o sea multiplica el SNR por
    4, o sea son `10·log10(4) = 6,02` dB exactos.

    LA CONDICIÓN QUE SE OLVIDA: la senoidal tiene que estar A PLENA
    ESCALA. Ver `factor_carga`.
    """
    if bits < 1:
        raise ValueError(f"Hacen falta bits >= 1, recibí {bits}")
    return PENALIZACION_PLENA_ESCALA + DB_POR_BIT * bits


def plena_escala(bits: int, rango: float) -> float:
    """Amplitud de la señal más grande que el convertidor representa.

    No es `rango/2`, es `rango/2 - Δ/2`: los niveles de un cuantizador de
    punto medio son los CENTROS de las celdas, así que el último está
    medio paso por debajo del borde. Con 8 bits y rango 2 V, plena escala
    son 0.99609375 V, no 1 V.
    """
    if bits < 1:
        raise ValueError(f"Hacen falta bits >= 1, recibí {bits}")
    if rango <= 0:
        raise ValueError(f"El rango debe ser positivo, recibí {rango}")
    return rango / 2.0 - parametros_cuantiizador(bits, rango)["delta"] / 2.0


def dither(n: int, delta: float, tipo: str = "uniforme", semilla: int = 0,
           amplitud: float = 1.0) -> np.ndarray:
    """Ruido de dither para desdoblar el error de cuantización.

    tipo
        "uniforme"  ruido uniforme de pico a pico 2·amplitud·Δ.
        "tpdf"       suma de dos uniformes, o sea triangular. Es la
                     recomendación clásica y la que realmente separa dos
                     niveles.

    LO QUE HACE Y LO QUE NO
    -----------------------
    Convierte un error DETERMINISTA y correlacionado con la señal (que
    produce armónicos espurios) en ruido BLANCO independiente de la
    señal.

    Lo que NO hace es mejorar el SNR: lo empeora. El intercambio es
    perder unos dB de SNR a cambio de que el error no tenga estructura.
    Para audio, eso casi siempre vale la pena.
    """
    if delta <= 0:
        raise ValueError(f"El paso Δ debe ser positivo, recibí {delta}")
    if n < 0:
        raise ValueError(f"n no puede ser negativo, recibí {n}")
    if tipo not in ("uniforme", "tpdf"):
        raise ValueError(
            f"Dither desconocido: {tipo!r}. Opciones: 'uniforme', 'tpdf'")
    if amplitud <= 0:
        raise ValueError(f"La amplitud debe ser positiva, recibí {amplitud}")

    rng = np.random.default_rng(semilla)
    pico_a_pico = 2.0 * amplitud * delta
    if tipo == "uniforme":
        return (rng.random(n) - 0.5) * pico_a_pico
    return ((rng.random(n) - 0.5) + (rng.random(n) - 0.5)) * amplitud * delta


def varianza_teorica_dither(tipo: str, delta: float, amplitud: float) -> float:
    """La varianza que el dither AÑADE al error de cuantización.

    uniforme: p-p = 2·a·Δ  ->  var = (2aΔ)²/12
    tpdf:     p-p = 2·a·Δ  ->  var = (2aΔ)²/24
    """
    if delta <= 0:
        raise ValueError(f"El paso Δ debe ser positivo, recibí {delta}")
    pico_a_pico = 2.0 * amplitud * delta
    base = pico_a_pico ** 2 / 12.0
    return base if tipo == "uniforme" else base / 2.0


# =============================================================================
# LA RECONSTRUCCIÓN
# =============================================================================

#: Cuántos senos cardinales se suman por defecto en la reconstrucción.
N_PULSOS_POR_DEFECTO = 64


def _vecindario(t_m: np.ndarray, t_eval: np.ndarray, n_pulsos: int):
    """Los índices de las `n_pulsos` muestras relevantes para cada `t`.

    Devuelve (índices, máscara de validez).

    POR QUÉ LA VENTANA SE CENTRA EN LA MUESTRA MÁS CERCANA
    -------------------------------------------------------
    La suma de Shannon usa los senos cardinales alrededor del instante
    evaluado. En los instantes de muestreo exactos, el único término que
    no se anula es el central (`sinc(0) = 1`), así que la ventana tiene
    que incluirlo: con una ventana descentrada, la reconstrucción
    devolvería ~0 en vez de `x[n]`.

    Y EL BORDE: la suma usa índices negativos, que no existen. Esos
    términos se ponen a CERO (la muestra no existe, luego no aporta),
    en vez de recortarse: si se recortaran, la misma muestra aparecería
    varias veces en la suma y se inventarían datos.
    """
    N = len(t_m)
    p = int(max(1, min(n_pulsos, N)))
    if N == 1:
        centro = np.zeros(len(t_eval), dtype=int)
    else:
        pos = np.clip(np.searchsorted(t_m, t_eval), 1, N - 1)
        izquierda = t_m[pos - 1]
        derecha = t_m[pos]
        centro = np.where((t_eval - izquierda) <= (derecha - t_eval),
                          pos - 1, pos).astype(int)
    centro = np.clip(centro, 0, N - 1)
    idx = centro[:, None] + (np.arange(p) - p // 2)[None, :]
    return idx, (idx >= 0) & (idx < N)


def reconstruir_sinc(t: np.ndarray, t_m: np.ndarray, x_m: np.ndarray,
                     fs: float | None = None,
                     n_pulsos: int = N_PULSOS_POR_DEFECTO) -> np.ndarray:
    """La reconstrucción EXACTA de Nyquist-Shannon por senos cardinales.

        x_hat(t) = SUM_n  x[n] · sinc( f_s · (t - t_n) )

    con `sinc(u) = sin(pi·u)/(pi·u)`, el NORMALIZADO (que es el que
    brings `np.sinc`).

    Lo que garantiza: en los instantes de muestreo, `x_hat(t_n) = x[n]`
    con error de máquina (~1e-16), incluso con aliasing. Entre muestras,
    la suma FINITA de `n_pulsos` términos no da error de máquina: da del
    orden de 1e-2 en las zonas de borde, decreciendo hacia el interior.

    Y LOS DOS ERRORES, QUE SON DISTINTOS
    -------------------------------------
    1. COLA DEL SINC: al quedarnos con `n_pulsos` términos dejamos fuera
       los más lejanos. Se arregla subiendo `n_pulsos`.
    2. TRUNCAMIENTO DE LA VENTANA: en el primer y el último 5 % del
       registro no hay muestras de un lado, y la serie no converge ahí.
       NO se arregla con más pulsos: es inherente a un registro finito.
    """
    t = np.asarray(t, dtype=float)
    x_m = np.asarray(x_m, dtype=float)
    if len(x_m) == 0:
        return np.zeros_like(t)
    if fs is None or fs <= 0:
        if len(t_m) < 2:
            raise ValueError(
                "No se puede deducir f_s: hacen falta 2 muestras o pasar fs")
        fs = float(1.0 / (t_m[1] - t_m[0]))

    idx, valido = _vecindario(t_m, t, n_pulsos)
    seguro = np.clip(idx, 0, len(x_m) - 1)
    u = fs * (t[:, None] - t_m[seguro])
    aporte = np.where(valido, x_m[seguro], 0.0)
    return np.sum(aporte * np.sinc(u), axis=1)


def reconstruir_zoh(t: np.ndarray, t_m: np.ndarray,
                    x_m: np.ndarray) -> np.ndarray:
    """Retenedor de orden cero: se mantiene el valor hasta la siguiente.

        x_hat(t) = x[n]  para  t_n <= t < t_{n+1}

    Es lo que hace un DAC muy barato. Introduce un retardo de hasta
    T_s/2 y un error grande: sirve para mostrar el otro extremo de los
    métodos de reconstrucción.
    """
    t = np.asarray(t, dtype=float)
    x_m = np.asarray(x_m, dtype=float)
    if len(x_m) == 0:
        return np.zeros_like(t)
    idx = np.clip(np.searchsorted(t_m, t, side="right") - 1, 0, len(x_m) - 1)
    return x_m[idx]


# =============================================================================
# EL DIAGNÓSTICO DE NYQUIST
# =============================================================================

def diagnostico_nyquist(fmax: float, fs: float, tol: float = 1e-9) -> dict:
    """Todos los números que resumen si se cumple el teorema.

    Devuelve
    --------
    {"f_nyquist", "fs_minima", "margen_hz", "margen_rel", "cumple",
     "caso_limite", "veredicto"}

    SOBRE EL CASO LÍMITE
    --------------------
    Se usa `f_s/2 >= f_max` (no `>`). En la igualdad el teorema sigue
    siendo válido para un coseno, pero la igualdad es una trampa: un
    SENO de exactamente `f_s/2` da ceros en todas las muestras
    (`sen(pi·n) = 0`), así que es indetectable. De ahí el caso_limite.
    """
    fn = fs / 2.0
    fs_min = 2.0 * fmax
    margen = fn - fmax
    cumple = margen >= -tol
    limite = abs(margen) <= max(tol, 1e-9 * max(fn, fmax, 1.0))
    if limite:
        veredicto = "LÍMITE (f_s = 2·f_max): al borde, no lo hagas"
    elif cumple:
        veredicto = f"CUMPLE (margen {margen:.3g} Hz)"
    else:
        veredicto = f"NO CUMPLE (faltan {-margen:.3g} Hz)"
    return {
        "f_nyquist": fn,
        "fs_minima": fs_min,
        "margen_hz": margen,
        "margen_rel": (fs / fs_min) if fs_min > 0 else float("inf"),
        "cumple": bool(cumple),
        "caso_limite": bool(limite),
        "veredicto": veredicto,
    }
