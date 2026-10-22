"""
analisis.py — el pipeline completo de una pista: del WAV al veredicto.

CONTINUACIÓN DE `Nyquist_Shannon/`
----------------------------------
El proyecto anterior (`Nyquist_Shannon/`, en la carpeta de al lado) trabaja
con señales que son SERIES DE FOURIER, de las que se sabe `f_max`
exactamente. El audio real es otra cosa: no es periódico, es finito, y
su `f_max` hay que **medirlo**. Eso es lo nuevo aquí.

Las primitivas de DSP que hacen falta (reconstrucción de Shannon,
cuantizador, métricas) están en `nucleo/primitivas.py`, adaptadas del
proyecto anterior para que este repositorio sea **autosuficiente**: se
clona, se instala y funciona, sin depender de ninguna carpeta de al lado.
Las cifras que dan son exactamente las mismas.

QUÉ HACE, PASO A PASO
---------------------
Para cada archivo de `audio/` este módulo recorre la cadena entera del
enunciado, y deja todas las cifras en un diccionario:

    1. LECTURA        `wav_io.leer_pista` + mono + sin DC
    2. TIEMPO         x(t) del clip y un zoom con las muestras marcadas
    3. ESPECTRO       magnitud en dB, `f_max` medido, bandas, centroide
    4. NYQUIST        `f_s,min = 2·f_max` y cuatro experimentos de muestreo
    5. CUANTIZACIÓN   el factor de escala en V y en bits, el SNR, los
                      bits efectivos, y la tabla de códigos binarios
    6. CADENA ADC-DAC cuantizar → reconstruir → medir
    7. RITMO          el tempo, por autocorrelación del flujo espectral
    8. ATENCIÓN       el índice del punto (e), con sus pesos a la vista

LA CADENA ADC-DAC, EN ORDEN
---------------------------
    x(t)  --filtro AA-->  --muestreo-->  --cuantizador-->  --DAC-->  x̂(t)

y en cada etapa se mide el error que introduce, para poder decir QUIÉN se
equivoca. Es el mismo espíritu que el "presupuesto de error" del proyecto
Nyquist_Shannon, pero aplicado a audio real.

EL ERROR DE ALIASING, MEDIDO CONTRA ALGO
-----------------------------------------
Cuando se submuestrea, la comparación hay que hacerla contra la señal
FILTRADA, no contra la original: si se compara contra la original, el
error del filtro antialiasing se cuenta como error de muestreo y no se
puede distinguir una cosa de la otra.

Así que la referencia es:

    ref(f_s) = x filtrada a 0,45 · f_s/2

y se comparan DOS reconstrucciones contra ella:

    · la de las muestras SIN filtrar (con aliasing): aísla el aliasing,
    · la de las muestras CON filtro: aísla el error de reconstrucción.

Las dos usan el mismo reconstructor (Shannon), de modo que la diferencia
entre ellas es exactamente el coste de no filtrar.

EL FACTOR DE ESCALA, Y POR QUÉ HAY DOS VERSIONES
------------------------------------------------
El enunciado pide el factor de escala (y) "en V" y "en bits":

    · EN VOLTIOS:  y = V_fs / 2^(b-1)      [V por nivel, el LSB]
    · EN BITS:     b nominal frente a los BITS EFECTIVOS (ENOB) medidos

No es lo mismo. El número de bits del convertidor es una decisión de
diseño; los bits efectivos son lo que la señal REAL consigue, y salen
del SNR medido:

    ENOB = (SNR_medido - 1,76) / 6,0206

La diferencia entre los dos es lo que se pierde por no llenar el rango
(carga) y por el ruido. Un ADC de 16 bits al que se le mete una señal
que solo ocupa el 20 % del rango no da 16 bits útiles: da menos, y este
proyecto lo mide en vez de suponerlo.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import numpy as np

try:
    from . import dsp_audio as dsp
    from . import primitivas
    from . import wav_io
    from .catalogo import Genero, obtener
except ImportError:
    import dsp_audio as dsp
    import primitivas
    import wav_io
    from catalogo import Genero, obtener


# =============================================================================
# PARÁMETROS
# =============================================================================

@dataclass
class Parametros:
    """Los ajustes del análisis. Todos tienen valor por defecto."""

    #: Fondo de escala del convertidor, en voltios (±).
    vfs: float = 1.0
    #: Bits del ADC que se simula en la cadena principal.
    bits: int = 16
    #: Bits extra que se cuantizan además, para la tabla comparativa.
    bits_extra: tuple[int, ...] = (24, 12, 8)
    #: Umbral (dB bajo el pico) para medir `f_max`.
    umbral_db: float = -40.0
    #: Umbrales alternativos, para mostrar de qué depende la medida.
    umbrales_alternativos: tuple[float, ...] = (-30.0, -50.0)
    #: Duración del clip analizado, en segundos.
    duracion: float = 12.0
    #: Orden del filtro antialiasing.
    orden_filtro: int = 8
    #: Semilla del ruido (para el dither).
    semilla: int = 0
    #: Número de muestras que se muestran en la tabla de códigos binarios.
    n_muestras_tabla: int = 12
    #: Multiplicadores de `f_s,min` en los experimentos de muestreo.
    multiplicadores_fs: tuple[float, ...] = (0.5, 1.0, 1.5, 2.0)
    #: Ventana de la FFT.
    ventana: str = "hann"
    #: Si se hace el diagnóstico de dither en la cadena completa.
    con_dither: bool = False


# =============================================================================
# UTILIDADES
# =============================================================================

def _bits_a_codigo(valor: float, delta: float, rango: float,
                   bits: int) -> int:
    """El código entero de una muestra, como lo daría un ADC.

        código = floor((x + rango/2) / Δ)   recortado a [0, 2^b - 1]

    Es la misma cuenta que hace `primitivas.cuantizar`, pero devolviendo el
    CÓDIGO y no la tensión: lo que sale del convertidor es un entero, y
    ese entero es lo que se quiere ver escrito en binario.
    """
    niveles = 2 ** bits
    c = int(np.floor((valor + rango / 2.0) / delta))
    return int(np.clip(c, 0, niveles - 1))


def _tabla_codigos(x_v: np.ndarray, delta: float, rango: float,
                   bits: int, n: int) -> list[dict]:
    """Una tabla de `n` muestras con su código binario y su error.

    Se eligen las muestras de la zona de mayor señal (donde el error de
    cuantización es más visible) y se escriben en binario, que es como
    un ADC entrega la muestra: un número entero de `b` bits.
    """
    if len(x_v) == 0:
        return []
    centro = int(np.argmax(np.abs(x_v)))
    inicio = max(0, min(centro - n // 2, len(x_v) - n))
    filas = []
    for i in range(inicio, min(inicio + n, len(x_v))):
        codigo = _bits_a_codigo(x_v[i], delta, rango, bits)
        reconstruido = -rango / 2.0 + (codigo + 0.5) * delta
        filas.append({
            "n": i,
            "x_v": float(x_v[i]),
            "codigo": codigo,
            "binario": format(codigo, f"0{bits}b"),
            "x_q": float(reconstruido),
            "error": float(reconstruido - x_v[i]),
            "error_medio_abs": abs(reconstruido - x_v[i]) / delta,
        })
    return filas


def _rejilla_densa(duracion: float, fs: float, n: int = 4001) -> np.ndarray:
    """La rejilla de evaluación: densa, y NO múltiplo de la de muestreo.

    Es la misma decisión que en el proyecto Nyquist_Shannon: si la
    rejilla de evaluación coincidiera con la de muestreo, la tabla de
    errores sería una tabla de ceros y no distinguiría nada.
    """
    return np.linspace(0.0, duracion, int(n))


# =============================================================================
# EL ANÁLISIS DE UNA PISTA
# =============================================================================

def analizar_pista(entrada, params: Parametros | None = None,
                   genero: Genero | None = None) -> dict:
    """Analiza un WAV completo y devuelve todas las cifras.

    Parámetros
    ----------
    entrada : str, pathlib.Path o wav_io.Pista
        El WAV a analizar. También se puede pasar una `Pista` ya leída,
        que es lo que hace la vista web cuando el usuario sube un
        fichero: en un despliegue *serverless* el disco es de solo
        lectura, así que el audio se procesa en memoria.
    params : Parametros
        Los ajustes; si no se pasan, se usan los de por defecto.
    genero : Genero
        La ficha del catálogo, si se conoce; si no, se busca por el
        nombre del fichero.

    Devuelve
    --------
    dict
        Con las secciones "pista", "tiempo", "espectro", "muestreo",
        "cuantizacion", "cadena", "ritmo" y "atencion".
    """
    p = params or Parametros()
    if isinstance(entrada, wav_io.Pista):
        pista = wav_io.recortar(entrada, duracion=p.duracion)
    else:
        pista = wav_io.leer_pista(entrada, duracion=p.duracion)
    if genero is None:
        genero = obtener(pista.etiqueta)

    x = dsp.quitar_dc(pista.x)
    fs = pista.fs

    # ---------------------------------------------------------------- tiempo
    tiempo = {
        "t": np.arange(len(x)) / fs,
        "x": x,
        "zoom": _zoom_con_muestras(x, fs),
    }

    # -------------------------------------------------------------- espectro
    esp = dsp.espectro_magnitud(x, fs, ventana=p.ventana)
    f_max_umbral = dsp.f_max_umbral(esp, p.umbral_db)
    f_max_energia = dsp.f_max_energia(esp, 0.999)
    # El f_max DE TRABAJO es el menor de los dos criterios. Motivo: en
    # una.masterización moderna con mucho brillo, el ruido de la
    # grabación llega hasta el final de la banda, y el criterio de
    # umbral devuelve fs/2 (que no es información: es el techo del
    # convertidor). El criterio de energía acumulada, en cambio, no
    # depende del suelo de ruido y sí discrimina.
    f_max = min(f_max_umbral, f_max_energia)
    f_max_por_umbral = {
        str(u): dsp.f_max_umbral(esp, u)
        for u in (p.umbral_db,) + tuple(p.umbrales_alternativos)
    }
    bandas = dsp.energias_por_banda(esp)
    bandas_eeg = dsp.energias_por_banda(esp, dsp.BANDAS_EEG)
    centroide = dsp.centroide_espectral(esp)
    planicidad = dsp.planicidad_espectral(esp)
    crest = dsp.crest_factor(x)

    fs_min = dsp.fs_minima_nyquist(f_max)
    diag_nyquist = primitivas.diagnostico_nyquist(f_max, fs)

    espectro = {
        "espectro": esp,
        "f_max": f_max,
        "f_max_umbral": f_max_umbral,
        "f_max_energia": f_max_energia,
        "f_max_por_umbral": f_max_por_umbral,
        "umbral_db": p.umbral_db,
        "bandas": bandas,
        "bandas_eeg": bandas_eeg,
        "centroide": centroide,
        "planicidad": planicidad,
        "crest": crest,
        "fs_minima": fs_min,
        "nyquist": diag_nyquist,
        "ancho_banda": dsp.ancho_banda_ocupado(esp, p.umbral_db),
        "pico_hz": esp["pico_hz"],
    }

    # -------------------------------------------------------------- muestreo
    muestreo_ = {
        "fs_minima": fs_min,
        "experimentos": _experimentos_de_muestreo(x, fs, fs_min, p),
    }

    # ---------------------------------------------------------- cuantización
    cuanti = _analisis_de_cuantizacion(x, p)

    # ------------------------------------------------------------- la cadena
    cadena = _cadena_adc_dac(x, fs, p)

    # ---------------------------------------------------------------- ritmo
    ritmo = dsp.bpm(x, fs)

    # ------------------------------------------------------------- atención
    atencion = dsp.indice_atencion({
        "bpm": ritmo["bpm"],
        "bpm_estable": ritmo["bpm_estable"],
        "confianza_bpm": ritmo["confianza"],
        "tempo_medible": ritmo["medible"],
        "centroide": centroide,
        "frac_agudos": bandas["agudo"]["fraccion"],
        "frac_voz": _fraccion_voz(esp),
        "crest": crest,
    })

    return {
        "clave": genero.clave,
        "nombre": genero.nombre,
        "ficha": genero.ficha(),
        "pista": pista.resumen(),
        "parametros": {
            "vfs": p.vfs, "bits": p.bits, "umbral_db": p.umbral_db,
            "duracion": p.duracion, "ventana": p.ventana,
            "orden_filtro": p.orden_filtro,
        },
        "tiempo": tiempo,
        "espectro": espectro,
        "muestreo": muestreo_,
        "cuantizacion": cuanti,
        "cadena": cadena,
        "ritmo": ritmo,
        "atencion": atencion,
    }


def _zoom_con_muestras(x: np.ndarray, fs: float,
                       duracion_zoom: float = 0.02) -> dict:
    """Un trozo corto con los instantes de muestreo marcados.

    Es la figura que responde al punto (c) del enunciado: "van a graficar
    la señal x(t)". Se dibuja el tramo entero del clip y, debajo, 20 ms
    con las muestras encima, que es donde se ve de verdad el muestreo.
    """
    n_zoom = max(8, int(duracion_zoom * fs))
    n_zoom = min(n_zoom, len(x))
    t = np.arange(n_zoom) / fs
    return {
        "t": t,
        "x": x[:n_zoom],
        "fs": fs,
        "n_zoom": n_zoom,
    }


def _experimentos_de_muestreo(x: np.ndarray, fs: float, fs_min: float,
                              p: Parametros) -> list[dict]:
    """Submuestrea a varias frecuencias y mide el error de aliasing.

    Para cada `f_s` del barrido se hacen DOS muestreos:

        · SIN filtro  → el contenido por encima de f_s/2 se pliega (aliasing)
        · CON filtro  → el contenido se elimina antes de muestrear

    y se reconstruye ambos con Shannon (senos cardinales) sobre una
    rejilla densa, comparando contra la señal de banda limitada ideal.
    Así:

        NRMSE(aliasing)  =  el contenido de arriba de f_s/2, plegado
        NRMSE(filtro)    =  lo que le cuesta al filtro real de 0,45·f_s/2

    que es la cifra que demuestra el teorema de Nyquist-Shannon sobre
    audio real.

    EL ERROR DE ALIASING NO BAJA DE FORMA MONÓTONA
    ----------------------------------------------
    El error de aliasing depende de QUÉ contenido se pliega y DÓNDE cae
    al plegarse. Un componente estrecho que se pliega en una zona
    silenciosa apenas se nota; un transitorio broadband que se pliega
    justo encima de un pico, mucho. Por eso la tendencia general es
    clara (al bajar f_s, el error crece) pero la curva no es
    estrictamente monótona, y decirlo de otra cosa sería mentir en la
    gráfica.

    POR QUÉ UN EXTRACTO DE 1 SEGUNDO Y NO EL CLIP ENTERO
    ----------------------------------------------------
    La referencia (la señal filtrada) hay que evaluarla en la rejilla
    densa donde se compara con la reconstrucción. Si esa rejilla es
    gruesa (3 ms en un clip de 12 s), la interpolación de la referencia
    mete un error del orden del 7 % en un componente de 10 kHz, y ese
    error se mezclaría con el del aliasing, que es justo lo que se quiere
    medir.

    Con un extracto de 1 s y una rejilla de 20 001 puntos (50 µs de
    separación), el error de interpolación de la referencia baja a
    ~3·10⁻⁶: despreciable frente a los errores que se miden, que son de
    orden 10⁻².
    """
    fs_pruebas = []
    for mult in p.multiplicadores_fs:
        f = fs_min * mult
        if f >= 200.0 and f < fs * 0.999:
            fs_pruebas.append(float(f))
    fs_pruebas = sorted(set(round(f, 3) for f in fs_pruebas))

    n_ex = int(min(1.0 * fs, len(x)))
    x_e = x[:n_ex]
    duracion = n_ex / fs
    t_ref = _rejilla_densa(duracion, fs, n=20001)

    filas = []
    for f_s in fs_pruebas:
        # LA REFERENCIA: la señal con TODO lo que pasa de f_s/2 eliminado,
        # es decir, la señal de banda limitada ideal que una f_s de
        # muestreo podría representar sin pérdida. Se hace con un
        # Butterworth de orden 12 aplicado dos veces (filtfilt), que a
        # efectos prácticos es un muro de ladrillo.
        #
        # EL CORTE VA EN f_s/2, Y NO EN f_s/4
        # ------------------------------------------
        # El corte del filtro es `f_s/2` multiplicado por 1,10, no por
        # 0,5. Con el 0,5 la referencia se quedaba en f_s/4, es decir
        # en la mitad de la banda que el muestreo SÍ puede representar,
        # y la diferencia con la reconstrucción sin filtro no era el
        # aliasing: era la mitad de la banda útil que la referencia se
        # había comido. Medido sobre la barroca, a f_s = f_s,min (donde
        # por definición no puede haber aliasing) el error salía 2,27 %
        # en vez del 1,10 % que corresponde a la truncadura de la
        # ventana del sinc.
        #
        # El 1,10 de margen por encima de f_s/2 es para que el propio
        # filtro de referencia no se coma el borde de la banda: un
        # Butterworth de orden 12 tiene una transición de unos pocos
        # por ciento de f_s.
        #
        # Esto es lo que separa las dos cifras:
        #
        #   · contra esta referencia, la reconstrucción SIN filtro tiene
        #     el error del ALIASING (el contenido de arriba de f_s/2,
        #     plegado dentro de la banda);
        #   · la reconstrucción CON filtro tiene el error del FILTRO
        #     (la banda de 0,45·f_s/2 a f_s/2 que el filtro real se
        #     come, y la fuga por encima de f_s/2).
        ref_full = dsp._filtro_pasabajos(x_e, fs, 1.10 * f_s / 2.0, 12)
        ref = np.interp(t_ref, np.arange(n_ex) / fs, ref_full)

        # (a) muestreo SIN filtro antialiasing
        x_alias = dsp.muestrear(x_e, fs, f_s, con_filtro=False)
        t_m = np.arange(len(x_alias)) / f_s
        xhat_alias = primitivas.reconstruir_sinc(t_ref, t_m, x_alias, fs=f_s)

        # (b) muestreo CON filtro antialiasing (el del 45 %)
        x_limpio = dsp.antialias(x_e, fs, f_s, orden=p.orden_filtro)
        xhat_limpio = primitivas.reconstruir_sinc(t_ref, t_m, x_limpio, fs=f_s)

        # (c) reconstrucción con retenedor de orden cero (el DAC barato)
        xhat_zoh = primitivas.reconstruir_zoh(t_ref, t_m, x_limpio)

        filas.append({
            "fs": f_s,
            "fs_minima": fs_min,
            "multiplicador": f_s / fs_min if fs_min else 0.0,
            "n_muestras": int(len(x_alias)),
            "cumple_nyquist": bool(f_s >= fs_min - 1e-9),
            "nrmse_aliasing": primitivas.nrmse_por_rango(ref, xhat_alias),
            "nrmse_reconstruccion": primitivas.nrmse_por_rango(ref, xhat_limpio),
            "nrmse_zoh": primitivas.nrmse_por_rango(ref, xhat_zoh),
            "snr_aliasing": primitivas.snr_db(ref, ref - xhat_alias),
            "snr_reconstruccion": primitivas.snr_db(ref, ref - xhat_limpio),
            "energia_fuera_banda": _energia_fuera_de_banda(x_e, fs, f_s, p),
            "ref": ref,
            "x_alias": x_alias,
            "x_limpio": x_limpio,
            "t_ref": t_ref,
            "xhat_alias": xhat_alias,
            "xhat_limpio": xhat_limpio,
        })
    return filas


def _energia_fuera_de_banda(x: np.ndarray, fs: float, f_s: float,
                            p: Parametros) -> float:
    """La fracción de energía que queda por encima de f_s/2 (en %).

    Es la medida "previolación de Nyquist": si se submuestrea a f_s, ¿qué
    tanto de la energía original estaba por encima de f_s/2? Si es cero,
    el teorema se cumple y no hay aliasing posible; si es mucho, el
    contenido se pliega.

    Se mide sobre el espectro, sin ventana, para no contaminar con el
    lóbulo principal de la ventana.
    """
    esp = dsp.espectro_magnitud(x, fs, ventana="rectangular")
    P = esp["A"] ** 2
    f = esp["f"]
    total = float(np.sum(P))
    if total <= 0:
        return 0.0
    fuera = float(np.sum(P[f > f_s / 2.0]))
    return 100.0 * fuera / total


def _fraccion_voz(espectro: dict) -> float:
    """La fracción de energía en la banda de la voz humana: 300-3500 Hz.

    Es la banda de la primera formante, donde está la inteligibilidad del
    habla. Una pieza con cantante tiene mucha energía ahí, y esa es
    exactamente la banda que necesita el estudiante para seguir la voz
    del profesor.
    """
    f = espectro["f"]
    P = espectro["A"] ** 2
    total = float(np.sum(P))
    if total <= 0:
        return 0.0
    dentro = (f >= 300.0) & (f < 3500.0)
    return float(np.sum(P[dentro]) / total)


def _analisis_de_cuantizacion(x: np.ndarray, p: Parametros) -> dict:
    """El punto (d) del enunciado: cuantizar, factor de escala y bits.

    Devuelve, para el número de bits principal y para los alternativos:

        · el factor de escala y en VOLTIOS (V por nivel),
        · el factor de escala en BITS (nominal y efectivo),
        · el SNR medido y el teórico,
        · la carga (dBFS) y los bits perdidos por no llenar el rango,
        · una tabla de códigos binarios de las muestras más grandes.
    """
    vfs = p.vfs
    rango = 2.0 * vfs
    x_v = wav_io.a_voltios(x, vfs)          # la señal, en voltios
    escala = wav_io.factor_de_escala(vfs, p.bits)
    carga = primitivas.factor_carga(x_v, rango)
    parametros = primitivas.parametros_cuantiizador(p.bits, rango)

    casos = {}
    for bits in (p.bits,) + tuple(bits_extra for bits_extra in p.bits_extra
                                  if bits_extra != p.bits):
        esc = wav_io.factor_de_escala(vfs, bits)
        xq = primitivas.cuantizar(x_v, bits, rango, saturar=True)
        e = xq - x_v
        snr = primitivas.snr_db(x_v, e)
        enob = (snr - 1.76) / 6.0206
        carga_b = primitivas.factor_carga(x_v, rango)
        bits_ef = primitivas.bits_efectivos(x_v, bits, rango)
        casos[str(bits)] = {
            "bits": bits,
            "factor_escala_v": esc["y_voltios"],
            "delta": esc["delta"],
            "niveles": esc["niveles"],
            "snr_teorico": esc["snr_teorico_db"],
            "snr_medido": float(snr),
            "enob": float(enob),
            "bits_efectivos": float(bits_ef),
            "carga_dbfs": carga_b.get("dbfs"),
            "perdida_por_carga": float(bits) - float(bits_ef),
            "x_q": xq,
            "error": e,
        }

    principal = casos[str(p.bits)]
    tabla = _tabla_codigos(x_v, principal["delta"], rango, p.bits,
                           p.n_muestras_tabla)

    return {
        "vfs": vfs,
        "rango_v": rango,
        "bits": p.bits,
        "factor_escala_v": escala["y_voltios"],
        "factor_escala_voltios": escala["y_voltios"],
        "factor_escala_medio": escala["y_voltios"] / 2.0,
        "niveles": escala["niveles"],
        "snr_teorico": escala["snr_teorico_db"],
        "parametros": parametros,
        "carga": carga,
        "casos": casos,
        "tabla_codigos": tabla,
        "x_v": x_v,
    }


def _cadena_adc_dac(x: np.ndarray, fs: float, p: Parametros) -> dict:
    """La cadena completa: ADC → cuantizador → DAC, y el error de cada paso.

    EL RECORRIDO ETAPA POR ETAPA
    ---------------------------
    Además del presupuesto, se calcula el **viaje del SNR**: cuánto SNR
    queda después de cada paso. La clave es que el error **se acumula**:

        original           ideal
        filtro AA          se pierde la banda de arriba del todo
        muestreo           se pierde lo que no cabe en f_s/2 (el aliasing)
        cuantizador        se pierde el error de redondeo
        DAC                el retenedor de orden cero añade su retardo

    Cada etapa se mide contra la **salida de la etapa anterior**, y el
    error de la cadena completa es la suma de todos. Antes, cada etapa se
    medía contra una referencia distinta y el filtro antialiasing no
    entraba en el total: la curva subía de 45 dB a 82 dB entre dos
    etapas, lo que no tiene sentido. Con el error acumulado, la curva
    solo puede bajar.
    """
    vfs = p.vfs
    rango = 2.0 * vfs
    x_v = wav_io.a_voltios(x, vfs)               # la señal, en voltios
    escala = wav_io.factor_de_escala(vfs, p.bits)

    # DOS REJILLAS: la de las muestras y la de los puntos medios
    # -------------------------------------------------------
    # El retenedor de orden cero mantiene cada muestra durante un
    # periodo entero, así que su error NO se ve en los instantes de
    # muestreo (allí reproduce el valor exacto) sino a medio camino
    # entre muestra y muestra. Medirlo en los nodos daba un error
    # EXACTAMENTE NULO, que era un error de medición disfrazado de
    # resultado.
    t = np.arange(len(x_v)) / fs
    t_mid = (np.arange(len(x_v)) + 0.5) / fs

    # --- etapa 1: el filtro antialiasing -------------------------------
    # A la tasa nativa no hace falta filtrar (no hay nada por encima de
    # f_s/2 que se pueda doblar), pero el filtro real de una cadena de
    # conversión sí recorta la banda de arriba, y esa pérdida SÍ es
    # distinta en cada pista: un reggaetón masterizado tiene contenido
    # hasta 17 kHz y una barroca nada por encima de 4 kHz.
    fc_aa = 0.45 * fs / 2.0
    x_filtrada = dsp._filtro_pasabajos(x, fs, fc_aa, p.orden_filtro)
    x_filtrada_v = wav_io.a_voltios(x_filtrada, vfs)
    e_filtro = x_filtrada_v - x_v
    snr_filtro = primitivas.snr_db(x_v, e_filtro)

    # --- etapa 2: el muestreo (el reloj y la retención) ----------------
    # El retenedor de orden cero sobre las muestras de la señal
    # filtrada, comparado con esa misma señal en los puntos medios.
    x_filtrada_mid = np.interp(t_mid, t, x_filtrada_v)
    e_muestreo = x_filtrada_v - x_filtrada_mid
    snr_muestreo = primitivas.snr_db(x_filtrada_v, e_muestreo)

    # --- etapa 3: el cuantizador ---------------------------------------
    # La cuantización se aplica sobre la señal YA FILTRADA, que es lo que
    # hace un convertidor real, y su error se mide contra ella.
    xq = primitivas.cuantizar(x_filtrada_v, p.bits, rango, saturar=True)
    e_cuanti = xq - x_filtrada_v

    # --- etapa 4: el DAC -----------------------------------------------
    # El retenedor de orden cero sobre las muestras cuantizadas,
    # comparado con la señal cuantizada en los puntos medios.
    xq_mid = np.interp(t_mid, t, xq)
    e_dac = xq - xq_mid

    # --- etapa 5: la cadena entera -------------------------------------
    # El error total se mide en los instantes de muestreo, que es donde
    # la salida de la cadena es exacta: incluye la pérdida de banda del
    # filtro y el error de cuantización.
    error_total = xq - x_v
    snr_cadena = primitivas.snr_db(x_v, error_total)

    # el DAC con dither: el error se dispersa (y el SNR empeora)
    xq_dither = xq
    if p.con_dither:
        d = primitivas.dither(len(x_v), escala["delta"], tipo="tpdf",
                             semilla=p.semilla, amplitud=1.0)
        xq_dither = primitivas.cuantizar(x_v + d, p.bits, rango, saturar=True)

    etapas = {
        "filtro_aa": {
            "rmse": float(np.sqrt(np.mean(e_filtro ** 2))),
            "max_abs": float(np.max(np.abs(e_filtro))),
            "snr": snr_filtro,
            "error": e_filtro,
        },
        "muestreo": {
            "rmse": float(np.sqrt(np.mean(e_muestreo ** 2))),
            "max_abs": float(np.max(np.abs(e_muestreo))),
            "snr": snr_muestreo,
            "error": e_muestreo,
        },
        "cuantizador": {
            "rmse": float(np.sqrt(np.mean(e_cuanti ** 2))),
            "max_abs": float(np.max(np.abs(e_cuanti))),
            "snr": primitivas.snr_db(x_filtrada_v, e_cuanti),
            "error": e_cuanti,
        },
        "dac_zoh": {
            "rmse": float(np.sqrt(np.mean(e_dac ** 2))),
            "max_abs": float(np.max(np.abs(e_dac))),
            "snr": primitivas.snr_db(xq, e_dac),
            "error": e_dac,
        },
    }
    if p.con_dither:
        e_d = xq_dither - x_v
        etapas["dither"] = {
            "rmse": float(np.sqrt(np.mean(e_d ** 2))),
            "max_abs": float(np.max(np.abs(e_d))),
            "snr": primitivas.snr_db(x_v, e_d),
            "error": e_d,
        }

    # el presupuesto: qué tanto del error total aporta cada etapa
    # ---------------------------------------------------------------
    # SOLO entran las etapas cuyo error se SUMA al error total, que se
    # mide en los instantes de muestreo: el filtro antialiasing y el
    # cuantizador. El error del retenedor de orden cero NO entra, porque
    # en los instantes de muestreo es cero: se ve a medio camino entre
    # muestra y muestra, y se reporta aparte, en el SNR de su etapa.
    potencia_total = float(np.mean(error_total ** 2))
    presupuesto = {}
    for nombre in ("filtro_aa", "cuantizador"):
        p_etapa = float(np.mean(etapas[nombre]["error"] ** 2))
        presupuesto[nombre] = {
            "potencia": p_etapa,
            "porcentaje": (100.0 * p_etapa / potencia_total
                           if potencia_total > 0 else 0.0),
        }

    # EL RECORRIDO DEL SNR: cuánto queda después de cada etapa
    # ---------------------------------------------------------------
    # Cada barra mide la degradación de UNA etapa, contra la salida de la
    # etapa anterior, y la última barra es el total acumulado contra la
    # señal original. Por eso la última puede ser MUCHO peor que las
    # anteriores: en la cadena nativa, el filtro antialiasing se lleva
    # la banda de arriba del todo y ese error ya no se puede deshacer,
    # de modo que las etapas siguientes no pueden mejorar el total.
    #
    # La figura es un gráfico de barras y no una curva escalonada a
    # propósito: una curva sugiere que el SNR se acumula de una etapa a
    # otra, y no es lo que pasa.
    snr_cadena = primitivas.snr_db(x_v, error_total)
    viaje = [
        {"etapa": "x(t) original", "snr": None, "error": None,
         "error_acumulado": None,
         "nota": "la señal de entrada, sin error"},
        {"etapa": "filtro antialiasing", "snr": snr_filtro,
         "error": e_filtro, "error_acumulado": x_filtrada_v - x_v,
         "nota": f"recorta por encima de {fc_aa:.0f} Hz"},
        {"etapa": "muestreo", "snr": snr_muestreo,
         "error": e_muestreo, "error_acumulado": None,
         "nota": f"a {fs:.0f} Hz, sin aliasing posible"},
        {"etapa": "cuantizador",
         "snr": primitivas.snr_db(x_filtrada_v, e_cuanti),
         "error": e_cuanti, "error_acumulado": xq - x_v,
         "nota": f"{p.bits} bits, Δ = {escala['delta']:.2e} V".replace(".", ",")},
        {"etapa": "cadena completa", "snr": snr_cadena,
         "error": error_total, "error_acumulado": error_total,
         "nota": "acumulado, contra la señal original"},
    ]

    return {
        "etapas": etapas,
        "presupuesto": presupuesto,
        "viaje": viaje,
        "snr_cadena": snr_cadena,
        "nrmse_cadena": primitivas.nrmse_por_rango(x_v, xq),
        "x_v": x_v,
        "x_filtrada": x_filtrada_v,
        "x_muestreada": xq,
        "x_q": xq,
        "x_zoh": xq,
        "xq_dither": xq_dither,
        "telefonica": _cadena_telefonica(x, fs, p),
    }


#: La tasa de muestreo de la telefonía analógica: 8 kHz, banda de 300 Hz
#: a 3,4 kHz. Es el caso en el que la cadena ADC-DAC se nota de verdad.
FS_TELEFONICA = 8000.0


def _cadena_telefonica(x: np.ndarray, fs: float, p: Parametros) -> dict:
    """La misma cadena, pero como una llamada telefónica: 8 kHz.

    A 44,1 kHz y 16 bits, el error de cuantización es tan pequeño que
    desaparece al lado del error del retenedor de orden cero, y el
    presupuesto queda aburrido. Bajando a 8 kHz (la tasa de la
    telefonía analógica) las cosas se ponen interesantes:

        · el filtro antialiasing recorta la banda a 4 kHz, y se pierde
          toda la información de 4 kHz hacia arriba,
        · el muestreo a 8 kHz no puede representar más de 4 kHz,
        · el cuantizador de 8 bits (el de un codecs de voz de la época)
          introduce un error audible.

    Es el experimento que hace tangible por qué la música por teléfono
    suena peor, y es la mejor forma de mostrar la cadena completa.
    """
    vfs = p.vfs
    rango = 2.0 * vfs
    fs_o = FS_TELEFONICA

    n = int(len(x) * fs_o / fs)
    x8 = dsp.antialias(x, fs, fs_o, orden=p.orden_filtro)[:n]
    x8_v = wav_io.a_voltios(x8, vfs)

    xq8 = primitivas.cuantizar(x8_v, 8, rango, saturar=True)
    e_cuanti = xq8 - x8_v
    t8 = np.arange(len(xq8)) / fs_o
    # el DAC sobre una rejilla densa, por el mismo motivo que en la
    # cadena nativa: en los nodos el error del retenedor es cero
    t8_densa = (np.arange(len(xq8)) + 0.5) / fs_o
    x8_zoh = primitivas.reconstruir_zoh(t8_densa, t8, xq8)
    e_dac = x8_zoh - xq8

    # la referencia "correcta": la señal con la banda de 4 kHz eliminada
    ref = dsp._filtro_pasabajos(x, fs, 0.45 * fs_o / 2.0, p.orden_filtro)
    ref = np.interp(np.arange(len(x8)) / fs_o,
                    np.arange(len(x)) / fs, ref)

    error_total = x8_zoh - x8_v
    potencia_total = float(np.mean(error_total ** 2))
    etapas = {
        "cuantizador_8b": {
            "rmse": float(np.sqrt(np.mean(e_cuanti ** 2))),
            "snr": primitivas.snr_db(x8_v, e_cuanti),
            "error": e_cuanti,
        },
        "dac_zoh_8k": {
            "rmse": float(np.sqrt(np.mean(e_dac ** 2))),
            "snr": primitivas.snr_db(xq8, e_dac),
            "error": e_dac,
        },
    }
    presupuesto = {}
    for nombre, dato in etapas.items():
        p_etapa = float(np.mean(dato["error"] ** 2))
        presupuesto[nombre] = {
            "potencia": p_etapa,
            "porcentaje": (100.0 * p_etapa / potencia_total
                           if potencia_total > 0 else 0.0),
        }

    # el recorrido del SNR de la cadena telefónica, para poder comparar
    # las dos series en la MISMA figura. Lleva las mismas cinco etapas
    # que la nativa, para que las dos se lean sobre el mismo eje.
    #
    # La referencia de las etapas digitales es la señal YA limitada a la
    # banda del canal (3,6 kHz), porque es lo que un canal Telefónico
    # entrega: el recorte de banda es previo al enlace digital, no un
    # error de él. Por eso la etapa del filtro se mide contra la señal
    # original, y las demás contra la señal ya filtrada.
    x_v = wav_io.a_voltios(x, vfs)
    x_aa_full = dsp._filtro_pasabajos(x, fs, 0.45 * fs_o / 2.0, p.orden_filtro)
    # la señal de referencia de las etapas digitales es la propia x8_v:
    # ya está limitada a la banda del canal y remuestreada a 8 kHz, que
    # es exactamente lo que entra al enlace digital.
    x8_aa = x8_v
    e_aa_tel = wav_io.a_voltios(x_aa_full, vfs) - x_v

    t8 = np.arange(len(x8_v)) / fs_o
    t8_mid = (np.arange(len(x8_v)) + 0.5) / fs_o
    e_muestreo_tel = x8_v - np.interp(t8_mid, t8, x8_v)
    e_dac_tel = xq8 - np.interp(t8_mid, t8, xq8)
    # el TOTAL de la cadena telefónica se mide contra la señal ORIGINAL,
    # igual que el de la nativa, para que las dos cifras sean
    # comparables. La salida de 8 kHz se lleva a la rejilla original con
    # interpolación lineal, que es una reconstrucción suave de un
    # staircase de 8 kHz.
    e_total_tel = np.interp(np.arange(len(x_v)) / fs, t8, x8_zoh) - x_v
    snr_tel = primitivas.snr_db(x_v, e_total_tel)
    snr_tel_total = primitivas.snr_db(x8_aa, error_total)
    viaje = [
        {"etapa": "x(t) original", "snr": None, "error": None,
         "error_acumulado": None,
         "nota": "la señal de entrada"},
        {"etapa": "filtro antialiasing",
         "snr": primitivas.snr_db(x_v, e_aa_tel),
         "error": e_aa_tel, "error_acumulado": None,
         "nota": f"la banda del canal: recorta por encima de "
                 f"{0.45 * fs_o / 2:.0f} Hz"},
        {"etapa": "muestreo",
         "snr": primitivas.snr_db(x8_aa, e_muestreo_tel),
         "error": e_muestreo_tel, "error_acumulado": None,
         "nota": f"a {fs_o:.0f} Hz, sin aliasing posible"},
        {"etapa": "cuantizador",
         "snr": primitivas.snr_db(x8_aa, xq8 - x8_aa),
         "error": e_cuanti, "error_acumulado": None,
         "nota": "8 bits, 256 niveles"},
        {"etapa": "cadena completa", "snr": snr_tel,
         "error": e_total_tel, "error_acumulado": None,
         "nota": "acumulado, contra la señal original"},
    ]

    return {
        "fs": fs_o,
        "bits": 8,
        "n_muestras": int(len(x8)),
        "etapas": etapas,
        "presupuesto": presupuesto,
        "viaje": viaje,
        "snr_cadena": snr_tel,
        "nrmse_cadena": primitivas.nrmse_por_rango(x8_v, x8_zoh),
        "nrmse_sobre_banda_completa": primitivas.nrmse_por_rango(ref, x8_zoh),
        "x_v": x8_v,
        "x_q": xq8,
        "x_zoh": x8_zoh,
        "ref": ref,
    }


# =============================================================================
# EL CONJUNTO
# =============================================================================

def analizar_catalogo(params: Parametros | None = None,
                       claves: list[str] | None = None,
                       directorio: str | pathlib.Path | None = None
                       ) -> dict:
    """Analiza las pistas que haya en `audio/` y devuelve un dict por clave.

    Las pistas que falten se saltan (y se avisa), para que el programa
    funcione con un subconjunto: es lo que pasa cuando se sube un WAV
    propio desde la interfaz web.
    """
    p = params or Parametros()
    if directorio is None:
        directorio = pathlib.Path(__file__).resolve().parent.parent / "audio"
    directorio = pathlib.Path(directorio)

    resultados = {}
    faltantes = []

    try:
        from .catalogo import CATALOGO
    except ImportError:                    # ejecución suelta
        from catalogo import CATALOGO
    seleccion = claves if claves is not None else [g.clave for g in CATALOGO]
    for clave in seleccion:
        ruta = directorio / f"{clave}.wav"
        if not ruta.exists():
            faltantes.append(clave)
            continue
        ficha = obtener(clave)
        resultados[clave] = analizar_pista(ruta, p, ficha)

    return {"resultados": resultados, "faltantes": faltantes,
            "parametros": p}
