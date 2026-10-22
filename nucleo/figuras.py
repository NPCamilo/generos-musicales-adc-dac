"""
figuras.py — las figuras del proyecto, en matplotlib.

POR QUÉ SE REUTILIZA EL TEMA DEL LABORATORIO ANTERIOR
-------------------------------------------------------
El proyecto `Laboratorio_ADC_DAC` (carpeta hermana) ya tiene un módulo
`tema.py` con una paleta que funciona con daltonismo (la de Okabe-Ito),
tipografías y un montoncito de ayudas de dibujo. Reutilizarlo hace que
este proyecto se vea como parte de la misma línea de trabajo, y evita
mantener dos paletas distintas.

Si `Laboratorio_ADC_DAC` no está disponible, el módulo funciona igual con
un tema propio mínimo: el resto del proyecto no depende de que el tema
esté.

QUÉ FIGURAS SALEN
-----------------
Por cada género (cinco):

    1  La señal x(t) y el detalle con las muestras
    2  El espectro de magnitud y el criterio de f_max
    3  El muestreo: el barrido de f_s y el aliasing
    4  La cuantización: la escalera, el error y los códigos en binario
    5  La cadena ADC-DAC y el presupuesto de error

Y del conjunto (comparación, que es el punto e del enunciado):

    6  Los cinco espectros de magnitud en una misma gráfica
    7  La energía por bandas de los cinco géneros
    8  El índice de atención y el diagrama tempo/brillo
    9  El detalle de los criterios, género por género
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

try:
    from Laboratorio_ADC_DAC import tema
except ImportError:                       # pragma: no cover
    # El tema del proyecto hermano no está: el proyecto tiene que
    # funcionar solo, así que se usa un tema propio mínimo.
    tema = None

try:
    from . import dsp_audio as dsp
except ImportError:                       # ejecución suelta
    import dsp_audio as dsp

#: Los colores de las cinco pistas, en el orden del catálogo.
COLORES = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")

#: El color de la referencia, del error y del original.
COLOR_ORIGINAL = "#1A1A1A"
COLOR_REFERENCIA = "#009E73"
COLOR_ERROR = "#D55E00"
COLOR_CUANTIZADA = "#CC79A7"


def _aplicar_tema() -> None:
    """Aplica el tema visual (el del laboratorio anterior, si está)."""
    if tema is not None:
        tema.aplicar()
        return
    plt.rcParams.update({
        "figure.facecolor": "#FBFAF7",
        "axes.facecolor": "#FBFAF7",
        "axes.edgecolor": "#D8D4CC",
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#E8E5DF",
        "text.color": "#1A1A1A",
        "axes.labelcolor": "#6B6862",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Segoe UI", "Arial"],
        "figure.dpi": 100,
        "savefig.dpi": 300,
    })


def _titulo(ax, sobretitulo: str, titulo: str) -> None:
    """El rótulo y el título de un panel, encima del eje.

    Se escriben como texto en coordenadas de eje (y > 1) y no con
    `set_title`, por dos razones:

      · el rótulo va ENCIMA del título (al revés de lo que hace
        `tema.encabezado`, que pone el título arriba y el rótulo debajo),
      · así el título no se parte en dos líneas cuando es largo, que con
        el layout restringido ocurre y descuadra el panel.
    """
    ax.set_title("")
    ax.text(0.0, 1.10, sobretitulo, transform=ax.transAxes,
            fontsize=8.5, color="#6B6862", va="bottom", ha="left",
            fontweight="bold")
    ax.text(0.0, 1.015, titulo, transform=ax.transAxes,
            fontsize=11.5, color="#1A1A1A", va="bottom", ha="left",
            fontweight="semibold")


def _encabezado(ax, sobretitulo: str, titulo: str) -> None:
    """Alias de `_titulo`, para no cambiar todas las llamadas."""
    _titulo(ax, sobretitulo, titulo)


def _nota(ax, texto: str, x: float = 0.0, y: float = -0.16) -> None:
    """La nota al pie del panel, DEBAJO del eje.

    Antes iba dentro del área de plotting (abajo a la derecha), y con las
    señales de audio —que viven en la parte baja del panel— se leía
    encima de los datos. Debajo del eje no se cruza con nada.
    """
    ax.text(x, y, texto, transform=ax.transAxes, fontsize=8.5,
            color="#6B6862", ha="left", va="top")


def _marca_vertical(ax, x: float, texto: str, color: str,
                     alineacion: str = "left") -> None:
    """Una línea vertical con su etiqueta, arriba del panel.

    La etiqueta va en coordenadas de eje (y = 0,97) y no en coordenadas
    de datos, porque en datos quedaría pegada al suelo y, con el
    espectro, se iría fuera de la figura.
    """
    ax.axvline(x, color=color, linewidth=1.2, linestyle="--", alpha=0.9)
    if alineacion == "left":
        ax.text(x, 0.97, f" {texto}", transform=ax.get_xaxis_transform(),
                fontsize=8.5, color=color, va="top", ha="left",
                bbox=dict(facecolor="#FBFAF7", edgecolor="none", alpha=0.7,
                          pad=1.0))
    else:
        ax.text(x, 0.97, f" {texto}", transform=ax.get_xaxis_transform(),
                fontsize=8.5, color=color, va="top", ha="right",
                bbox=dict(facecolor="#FBFAF7", edgecolor="none", alpha=0.7,
                          pad=1.0))


def _limpiar(ax) -> None:
    if tema is not None:
        tema.limpiar_eje(ax)


# =============================================================================
# 1 — LA SEÑAL
# =============================================================================

def figura_senal(r: dict) -> plt.Figure:
    """La señal x(t) del clip, y un detalle con las muestras marcadas."""
    _aplicar_tema()
    t = r["tiempo"]["t"]
    x = r["tiempo"]["x"]
    zoom = r["tiempo"]["zoom"]
    fs = r["pista"]["fs"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 6.4), height_ratios=[1, 1],
                                   layout="constrained")

    ax1.plot(t, x, color=COLOR_ORIGINAL, linewidth=0.7)
    ax1.set_xlim(0, t[-1] if len(t) else 1)
    ax1.set_ylabel("amplitud")
    _encabezado(ax1, r["nombre"].upper(), "La señal x(t) del clip")
    _nota(ax1, f"{r['pista']['canales']} canal(es) · {fs} Hz · "
               f"{r['pista']['bits']} bits · {r['pista']['duracion_s']} s")

    ax2.plot(zoom["t"], zoom["x"], color=COLOR_ORIGINAL, linewidth=1.2,
             label="x(t)")
    ax2.plot(zoom["t"], zoom["x"], linestyle="none", marker="o",
             markersize=4.5, color="#D55E00", label="muestras x[n]")
    ax2.set_xlabel("tiempo (s)")
    ax2.set_ylabel("amplitud")
    ax2.legend(loc="upper right")
    _encabezado(ax2, "DETALLE", "20 ms con las muestras del ADC encima")
    _nota(ax2, f"una muestra cada {1000.0 / fs:.3f} ms "
               f"({fs} Hz)")

    return fig


# =============================================================================
# 2 — EL ESPECTRO
# =============================================================================

def figura_espectro(r: dict) -> plt.Figure:
    """El espectro de magnitud, con el criterio de `f_max` dibujado.

    Se dibuja el espectro SUAVIZADO (media móvil de 100 Hz en potencia) y
    no el crudo: con la rejilla fina de la FFT (2^20 bins para un clip de
    12 s) el espectro crudo es una mancha negra ilegible, y de lo que se
    trata aquí es de ver la FORMA del espectro y de ubicar `f_max`.
    """
    _aplicar_tema()
    esp = r["espectro"]["espectro"]
    f = esp["f"]
    db = dsp.suavizar_db(esp["db"], f, 100.0)
    f_max = r["espectro"]["f_max"]
    f_max_umbral = r["espectro"]["f_max_umbral"]
    fs_min = r["espectro"]["fs_minima"]
    fs = r["pista"]["fs"]

    fig, ax = plt.subplots(figsize=(9.4, 4.8), layout="constrained")
    # el espectro se NORMALIZA a su propio máximo: al suavizar en
    # potencia, la energía de un pico se reparte en la ventana y el
    # máximo baja una docena de dB, de modo que la gráfica quedaría
    # medio vacía y no se vería la FORMA, que es lo que importa aquí.
    db = db - float(np.max(db))
    ax.plot(f, db, color=COLOR_ORIGINAL, linewidth=1.0)

    _marca_vertical(ax, f_max, f"f_max = {f_max:.0f} Hz", "#D55E00")
    if abs(f_max_umbral - f_max) > 1.0:
        _marca_vertical(ax, f_max_umbral, f"{f_max_umbral:.0f} Hz", "#6B6862",
                        alineacion="right")
    _marca_vertical(ax, fs / 2.0, f"f_s/2 del archivo = {fs / 2.0:.0f} Hz",
                    "#0072B2", alineacion="right")

    ax.set_xlim(0, min(fs / 2.0, 22000))
    ax.set_ylim(-80, 5)
    ax.set_xlabel("frecuencia (Hz)")
    ax.set_ylabel("magnitude relativa (dB)")
    _titulo(ax, r["nombre"].upper(),
            "El espectro de magnitud y el criterio de f_max")
    _nota(ax, f"ventana {esp['ventana']} · ganancia coherente "
               f"{esp['ganancia_coherente']:.2f} · suavizado de 100 Hz · "
               f"normalizado al pico · f_max por energía acumulada "
               f"{r['espectro']['f_max_energia']:.0f} Hz")
    return fig


# =============================================================================
# 3 — EL MUESTREO Y EL ALIASING
# =============================================================================

def figura_muestreo(r: dict) -> plt.Figure:
    """El barrido de f_s: cuánto error mete el aliasing y cuánto la reconstrucción."""
    _aplicar_tema()
    exps = r["muestreo"]["experimentos"]
    fs_min = r["muestreo"]["fs_minima"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.4),
                                   layout="constrained")

    fs = [e["fs"] for e in exps]
    ax1.plot(fs, [max(e["nrmse_aliasing"], 1e-6) for e in exps], "o-",
             color=COLOR_ERROR, linewidth=1.6, label="sin filtro (aliasing)")
    ax1.plot(fs, [max(e["nrmse_reconstruccion"], 1e-6) for e in exps], "s--",
             color=COLOR_REFERENCIA, linewidth=1.6,
             label="con filtro antialiasing")
    ax1.axvline(fs_min, color="#6B6862", linewidth=1.1, linestyle=":")
    ax1.text(fs_min, 0.02, f" f_s,min = {fs_min:.0f} Hz",
             transform=ax1.get_xaxis_transform(), color="#6B6862",
             fontsize=8.5, va="bottom", ha="left")
    ax1.set_yscale("log")
    ax1.set_xlabel("f_s de muestreo (Hz)")
    ax1.set_ylabel("NRMSE")
    ax1.set_title("El coste de no filtrar", loc="left",
                  fontsize=11.5, fontweight="semibold", pad=14)
    ax1.legend(loc="lower left", fontsize=9)

    ax2.plot(fs, [e["energia_fuera_banda"] for e in exps], "o-",
             color="#0072B2", linewidth=1.6)
    ax2.axvline(fs_min, color="#6B6862", linewidth=1.1, linestyle=":")
    ax2.set_xlabel("f_s de muestreo (Hz)")
    ax2.set_ylabel("energía fuera de banda (%)")
    ax2.set_title("Cuánta energía se pliega", loc="left",
                  fontsize=11.5, fontweight="semibold")

    fig.suptitle(f"{r['nombre']} — el teorema de Nyquist-Shannon medido",
                 x=0.01, ha="left", fontsize=13, fontweight="semibold")
    return fig


def figura_aliasing_detalle(r: dict, indice: int = -1) -> plt.Figure:
    """El detalle: la referencia, la reconstrucción con aliasing y sin ella."""
    _aplicar_tema()
    exps = r["muestreo"]["experimentos"]
    if not exps:
        return figura_senal(r)
    e = exps[indice]
    t = e["t_ref"]
    t0 = t[-1] / 6.0

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 6.0), sharex=True,
                                   layout="constrained")
    ax1.plot(t, e["ref"], color=COLOR_REFERENCIA, linewidth=1.4,
             label="referencia (filtrada a f_s/2)")
    ax1.plot(t, e["xhat_alias"], color=COLOR_ERROR, linewidth=1.0,
             alpha=0.9, label="reconstruida SIN filtro (con aliasing)")
    ax1.set_xlim(t0, t0 + t[-1] / 6.0)
    ax1.set_ylabel("amplitud")
    ax1.legend(loc="upper right")
    _encabezado(ax1, r["nombre"].upper(),
                f"Sin filtro antialiasing, a f_s = {e['fs']:.0f} Hz")

    ax2.plot(t, e["ref"] - e["xhat_alias"], color=COLOR_ERROR, linewidth=1.0)
    ax2.set_xlim(t0, t0 + t[-1] / 6.0)
    ax2.set_xlabel("tiempo (s)")
    ax2.set_ylabel("error")
    _encabezado(ax2, "ERROR", "El error que introduce el aliasing")
    _nota(ax2, f"NRMSE aliasing {e['nrmse_aliasing']:.3e} · "
               f"NRMSE con filtro {e['nrmse_reconstruccion']:.3e}")
    return fig


# =============================================================================
# 4 — LA CUANTIZACIÓN
# =============================================================================

def figura_cuantizacion(r: dict) -> plt.Figure:
    """La escalera de cuantización, el error y la escala en voltios."""
    _aplicar_tema()
    cuanti = r["cuantizacion"]
    x_v = cuanti["x_v"]
    delta = cuanti["factor_escala_v"]
    bits = cuanti["bits"]
    caso = cuanti["casos"][str(bits)]
    x_q = caso["x_q"]
    error = caso["error"]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9.4, 8.2),
                                        height_ratios=[1.1, 1, 0.9],
                                        layout="constrained")

    # (1) la escalera de cuantización sobre un trozo corto
    centro = int(np.argmax(np.abs(x_v)))
    ini = max(0, centro - 60)
    fin = min(len(x_v), ini + 120)
    t = np.arange(ini, fin) / r["pista"]["fs"]
    ax1.plot(t, x_v[ini:fin], color=COLOR_ORIGINAL, linewidth=1.1,
             label="x(t) original")
    ax1.plot(t, x_q[ini:fin], color=COLOR_CUANTIZADA, linewidth=1.4,
             linestyle="--", label="x_q(t) cuantizada")
    ax1.set_ylabel("amplitud")
    ax1.legend(loc="upper right")
    _encabezado(ax1, r["nombre"].upper(),
                f"La escalera de cuantización ({bits} bits)")

    # (2) el error, acotado a ±Δ/2, en MICROVOLTIOS
    # En voltios el error de 16 bits (15 µV) no se ve: el panel vacío no
    # informa de nada. En microvoltios se ve la escalera de niveles, que
    # es justamente lo que hay que enseñar.
    ax2.plot(t, error[ini:fin] * 1e6, color=COLOR_ERROR, linewidth=1.2)
    ax2.axhline(delta / 2.0 * 1e6, color="#6B6862", linewidth=0.9,
                linestyle=":")
    ax2.axhline(-delta / 2.0 * 1e6, color="#6B6862", linewidth=0.9,
                linestyle=":")
    ax2.set_ylabel("error (µV)")
    _encabezado(ax2, "ERROR DE CUANTIZACIÓN",
                f"El error está acotado a ±Δ/2 = ±{delta / 2.0 * 1e6:.1f} µV")

    # (3) el SNR frente al número de bits, con el teórico
    casos = cuanti["casos"]
    claves = sorted(casos, key=lambda k: int(k))
    bits_lista = [int(k) for k in claves]
    medidos = [casos[k]["snr_medido"] for k in claves]
    teoricos = [casos[k]["snr_teorico"] for k in claves]
    ax3.plot(bits_lista, teoricos, "o--", color="#6B6862", linewidth=1.3,
             label="SNR teórico (1,76 + 6,02·b)")
    ax3.plot(bits_lista, medidos, "s-", color="#0072B2", linewidth=1.6,
             label="SNR medido")
    for b, m in zip(bits_lista, medidos):
        ax3.annotate(f"{m:.0f}", (b, m), textcoords="offset points",
                     xytext=(4, -12), fontsize=8, color="#0072B2")
    ax3.set_xlabel("bits del convertidor")
    ax3.set_ylabel("SNR (dB)")
    ax3.legend(loc="upper left")
    _encabezado(ax3, "RESOLUCIÓN",
                "El factor de escala y lo que cuesta cada bit")

    fig.suptitle(f"Cuantización: y = {delta:.3e} V por nivel "
                 f"({cuanti['niveles']} niveles en "
                 f"±{cuanti['vfs']} V)",
                 x=0.01, ha="left", fontsize=12, fontweight="semibold")
    return fig


def figura_codigos(r: dict) -> plt.Figure:
    """Las muestras con su código binario: lo que el ADC entrega de verdad."""
    _aplicar_tema()
    cuanti = r["cuantizacion"]
    tabla = cuanti["tabla_codigos"]
    bits = cuanti["bits"]
    if not tabla:
        return figura_cuantizacion(r)

    n = len(tabla)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 6.2), height_ratios=[1, 1.1],
                                   layout="constrained")

    indices = [f["n"] for f in tabla]
    x = np.arange(n)
    ax1.bar(x, [f["x_v"] for f in tabla], color=COLOR_ORIGINAL, width=0.6)
    ax1.plot(x, [f["x_q"] for f in tabla], "o", color=COLOR_CUANTIZADA,
             markersize=6, label="valor reconstruido")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(i) for i in indices], fontsize=8)
    ax1.set_ylabel("amplitud (V)")
    ax1.legend(loc="upper right")
    _encabezado(ax1, r["nombre"].upper(),
                f"x(n) y su código de {bits} bits")

    # el código binario, leído como bits
    for i, fila in enumerate(tabla):
        bits_texto = fila["binario"]
        for j, bit in enumerate(bits_texto):
            ax2.text(i, -j - 1, bit, ha="center", va="center",
                     fontsize=9, family="monospace",
                     color=COLOR_ORIGINAL if bit == "1" else "#C9C5BD")
    ax2.set_xlim(-0.6, n - 0.4)
    ax2.set_ylim(-bits - 0.5, 0.6)
    ax2.set_yticks([])
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(i) for i in indices], fontsize=8)
    _encabezado(ax2, "CÓDIGOS", "El mismo número, en binario")
    _nota(ax2, f"MSB a la izquierda · el error está acotado a "
               f"±{cuanti['factor_escala_v'] / 2:.3e} V")
    return fig


# =============================================================================
# 5 — LA CADENA COMPLETA
# =============================================================================

def figura_cadena(r: dict, vertical: bool = False) -> plt.Figure:
    """La cadena ADC-DAC explicada: qué pasa en cada etapa y cuánto cuesta.

    POR QUÉ ESTA FIGURA ESTA HECHA ASÍ
    -----------------------------------
    La primera versión de esta figura era un diagrama de barras con el
    presupuesto de error: dos barras, el 100 % y el 0 %, una para cada
    etapa. Era idéntica en los cinco géneros y no explicaba nada. Se
    rehízo con dos ideas:

    · **ARRIBA, EL VIAJE DEL SNR**: una curva escalonada que dice cuánto
      SNR queda después de cada etapa, y dos curvas: la cadena nativa y la
      telefónica. Esta es la parte que explica la cadena, y **sí cambia
      de un género a otro**, porque la pérdida del filtro antialiasing
      depende de cuánto contenido hay por encima del corte.

    · **ABAJO, EL ERROR DE CADA ETAPA**: 20 milisegundos del error que
      introduce cada paso, con su propia escala. Se ve la diferencia de
      TEXTURA: el filtro antialiasing quita una banda y deja un error que
      parece ruido; el cuantizador deja un error acotado a ±Δ/2, una
      franja; el DAC deja los escalones del retenedor de orden cero.

    Con esto, la figura cuenta una historia y no solo reparte un
    porcentaje.

    LA VARIANTE VERTICAL
    --------------------
    En horizontal (13,2 × 7,6 pulgadas) la figura va bien en una
    pantalla, pero impresa en un A4 los cuatro paneles de abajo quedan
    ilegibles. Con `vertical=True` se rehace en 5 filas: el viaje del SNR
    arriba a todo el ancho, y las cuatro etapas debajo, una por fila. Es
    la versión que usa el PDF.
    """
    _aplicar_tema()
    cadena = r["cadena"]
    tel = cadena["telefonica"]
    fs = r["pista"]["fs"]

    if vertical:
        fig = plt.figure(figsize=(9.6, 9.2), layout="constrained")
        rejilla = fig.add_gridspec(5, 1, height_ratios=[1.35, 1, 1, 1, 1])
        fila_viaje, filas_error = 0, [1, 2, 3, 4]
    else:
        fig = plt.figure(figsize=(13.2, 7.6), layout="constrained")
        rejilla = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.0])
        fila_viaje, filas_error = 0, [1, 1, 1, 1]

    # ---------------------------------------------------------------- arriba
    ax = fig.add_subplot(rejilla[fila_viaje, :])
    etapas_nativas = [e["etapa"] for e in cadena["viaje"]]
    etapas_tel = [e["etapa"] for e in tel["viaje"]]
    assert len(etapas_nativas) == len(etapas_tel), \
        "los dos viajes tienen que tener las mismas etapas"

    def _puntos(viaje):
        """Los valores del viaje, con el primero y los infinitos acotados.

        A la tasa nativa, muestrear a 44,1 kHz una señal que ya está a
        44,1 kHz es exacto, y el SNR de esa etapa da infinito. En la
        gráfica se dibuja acotado, y se rotula como "exacta": es más
        honesto que dejar un `inf` en un eje.
        """
        x = np.arange(len(viaje))
        y = []
        for v in viaje:
            s = v["snr"]
            if s is None or np.isinf(s):
                y.append(160.0)
            else:
                y.append(min(s, 160.0))
        return x, y

    xn, yn = _puntos(cadena["viaje"])
    xt, yt = _puntos(tel["viaje"])
    ax.step(xn, yn, "o-", color="#0072B2", linewidth=2.0, markersize=7,
            where="post", label=f"nativa: {fs:.0f} Hz, "
            f"{r['cuantizacion']['bits']} bits")
    ax.step(xt, yt, "s--", color="#D55E00", linewidth=1.8, markersize=6,
            where="post", label="telefónica: 8 kHz, 8 bits")

    for x, y, viaje, dy in ((xn, yn, cadena["viaje"], 9),
                            (xt, yt, tel["viaje"], -16)):
        for xi, yi, etapa in zip(x, y, viaje):
            if etapa["snr"] is None:
                continue
            texto = ("exacta" if np.isinf(etapa["snr"])
                     else f"{etapa['snr']:.0f} dB")
            ax.annotate(texto, (xi, yi), textcoords="offset points",
                        xytext=(0, dy), fontsize=8.5, ha="center",
                        color="#6B6862")

    etiquetas = ["original", "filtro AA", "muestreo", "cuantizador",
                 "cadena"]
    ax.set_xticks(range(len(etiquetas)))
    ax.set_xticklabels(etiquetas, fontsize=9.5)
    ax.set_ylabel("SNR después de la etapa (dB)")
    ax.set_ylim(0, 175)
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(axis="x", visible=False)
    _titulo(ax, "EL VIAJE DE LA SEÑAL",
            "Cuánto SNR sobrevive a cada paso de la cadena")
    _nota(ax, "la banda que se pierde es la de arriba del todo: por eso el "
              "filtro antialiasing cuesta 45 dB en la barroca y 18 dB en el "
              "reggaetón, que tiene contenido hasta 17 kHz")

    # ---------------------------------------------------------------- abajo
    ventana = 0.02
    n_vent = int(ventana * fs)
    # la ventana se elige por RMS máximo, NO por el pico: en el pico hay
    # saturación, y un solo pico de recorte aplasta el resto del error,
    # que es justo lo que hay que ver
    if len(cadena["x_v"]) > n_vent:
        energia = np.convolve(cadena["x_v"] ** 2,
                              np.ones(n_vent) / n_vent, mode="valid")
        ini = int(np.argmax(energia))
    else:
        ini = 0
    t = (np.arange(ini, ini + n_vent)) / fs

    paneles = [
        ("1 · filtro antialiasing", cadena["viaje"][1], "#6B6862"),
        ("2 · muestreo y DAC", cadena["viaje"][2], "#0072B2"),
        ("3 · cuantizador", cadena["viaje"][3], "#CC79A7"),
        ("4 · cadena completa", cadena["viaje"][4], "#D55E00"),
    ]
    for k, (titulo, etapa, color) in enumerate(paneles):
        if vertical:
            axk = fig.add_subplot(rejilla[filas_error[k], :])
        else:
            axk = fig.add_subplot(rejilla[1, k])
        error = etapa["error"]
        if error is None:
            axk.axis("off")
            continue
        e = error[ini:ini + n_vent] * 1e6          # en microvoltios
        axk.axhline(0, color="#C9C5BD", linewidth=0.8)
        maximo = float(np.max(np.abs(e))) if len(e) else 0.0
        nota = etapa["nota"]

        if maximo < 1e-6:
            # la etapa no introduce error (a la tasa nativa no hay nada
            # por encima de f_s/2, así que no hay aliasing posible)
            axk.set_ylim(-1.0, 1.0)
            axk.text(0.5, 0.42, "error nulo\na esta tasa no hay\n"
                                "contenido que plegar",
                     transform=axk.transAxes, ha="center", va="center",
                     fontsize=9, color="#6B6862")
        else:
            axk.plot(t, e, color=color, linewidth=0.8)
            rms = float(np.sqrt(np.mean(e ** 2)))
            # escala robusta: un solo pico de saturación no puede
            # aplastar el resto del error, que es lo que hay que ver
            p995 = float(np.percentile(np.abs(e), 99.5))
            lim = max(3.0 * rms, p995, 1e-9) * 1.15
            axk.set_ylim(-lim, lim)
            if maximo > lim:
                nota += " · escala recortada"

        axk.set_xlim(t[0], t[-1])
        snr_texto = "exacta" if np.isinf(etapa["snr"]) \
            else f"{etapa['snr']:.0f} dB"
        axk.set_title(f"{titulo}\nSNR {snr_texto}", fontsize=9.5,
                      loc="left", color="#1A1A1A")
        axk.set_xlabel("tiempo (s)", fontsize=8.5)
        if k == 0:
            axk.set_ylabel("error (µV)", fontsize=9)
        axk.tick_params(labelsize=8)
        # la nota va DENTRO del panel, arriba: abajo se cruzaba con el
        # pie de la figura
        axk.text(0.5, 0.965, nota, transform=axk.transAxes,
                  ha="center", va="top", fontsize=8, color="#6B6862",
                  bbox=dict(facecolor="#FBFAF7", edgecolor="none",
                             alpha=0.85, pad=1.5))

    fig.suptitle(f"{r['nombre']} — la cadena ADC-DAC, etapa por etapa",
                 x=0.01, ha="left", fontsize=13, fontweight="semibold")
    return fig


# =============================================================================
# 6-9 — LAS FIGURAS DE COMPARACIÓN
# =============================================================================

def figura_espectros_comparados(resultados: dict) -> plt.Figure:
    """LOS CINCO ESPECTROS EN UNA MISMA GRÁFICA (el punto e del enunciado).

    Para que la comparación sea legible se hacen dos cosas, y las dos son
    necesarias:

      · se SUAVIZA el espectro (media móvil de 250 Hz), porque con la
        rejilla fina de la FFT las cinco curvas son un ruido de picos y
        no se ve nada;
      · se NORMALIZA cada pista a su propio pico (0 dB), para comparar
        la FORMA de los espectros y no sus niveles, que son los de la
        masteredización de cada canción y no del género.
    """
    _aplicar_tema()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.2, 7.2), height_ratios=[1, 1],
                                   layout="constrained")

    for i, (clave, r) in enumerate(resultados.items()):
        esp = r["espectro"]["espectro"]
        f = esp["f"]
        db = dsp.suavizar_db(esp["db"], f, 250.0)
        db = db - float(np.max(db))
        ax1.plot(f, db, color=COLORES[i % len(COLORES)], linewidth=1.3,
                 label=r["nombre"])
        ax1.axvline(r["espectro"]["f_max"], color=COLORES[i % len(COLORES)],
                    linewidth=0.9, linestyle=":", alpha=0.9)
    ax1.set_xlim(0, 22000)
    ax1.set_ylim(-80, 5)
    ax1.set_xlabel("frecuencia (Hz)")
    ax1.set_ylabel("magnitude relativa (dB)")
    ax1.legend(loc="upper right", ncol=2)
    _encabezado(ax1, "COMPARACIÓN",
                "El espectro de magnitud de los cinco, normalizado al pico")
    _nota(ax1, "suavizado de 250 Hz · las líneas de puntos son el f_max")

    # la misma comparación pero en escala logarítmica de frecuencia, que
    # es donde se ven las diferencias de la banda de la voz
    for i, (clave, r) in enumerate(resultados.items()):
        esp = r["espectro"]["espectro"]
        f = esp["f"]
        db = dsp.suavizar_db(esp["db"], f, 250.0)
        db = db - float(np.max(db))
        m = f > 20
        ax2.semilogx(f[m], db[m], color=COLORES[i % len(COLORES)], linewidth=1.3,
                     label=r["nombre"])
    ax2.set_xlim(20, 22000)
    ax2.set_ylim(-80, 5)
    ax2.set_xlabel("frecuencia (Hz, escala logarítmica)")
    ax2.set_ylabel("magnitude relativa (dB)")
    ax2.legend(loc="upper right", ncol=2)
    _encabezado(ax2, "ESCALA LOGARÍTMICA",
                "La banda de la voz (300 Hz-3,5 kHz) es la sombreada")
    ax2.axvspan(300, 3500, color="#E69F00", alpha=0.10)
    return fig


def figura_bandas(resultados: dict) -> plt.Figure:
    """La energía por bandas de los cinco géneros."""
    _aplicar_tema()
    nombres_banda = ("subgrave", "grave", "medio", "agudo", "muy agudo")
    etiquetas = ("20-60 Hz", "60-250 Hz", "250 Hz-2 kHz", "2-8 kHz", "8-20 kHz")
    claves = list(resultados.keys())
    n = len(claves)
    ancho = 0.8 / n

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6),
                                   layout="constrained")

    x = np.arange(len(nombres_banda))
    for i, (clave, r) in enumerate(resultados.items()):
        b = r["espectro"]["bandas"]
        valores = [b[nb]["fraccion"] * 100 for nb in nombres_banda]
        ax1.bar(x + i * ancho - 0.4 + ancho / 2, valores, width=ancho,
                color=COLORES[i % len(COLORES)], label=r["nombre"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, fontsize=9)
    ax1.set_ylabel("energía (% del total)")
    ax1.legend(loc="upper right", ncol=2)
    _encabezado(ax1, "ENERGÍA POR BANDAS",
                "Dónde está la energía de cada género")

    # el índice de atención
    valores = [resultados[c]["atencion"]["indice"] for c in claves]
    colores = [COLORES[i % len(COLORES)] for i in range(n)]
    ax2.barh(range(n), valores, color=colores, height=0.6)
    for i, v in enumerate(valores):
        ax2.text(v + 1, i, f"{v:.1f}", va="center", fontsize=9.5)
    ax2.set_yticks(range(n))
    ax2.set_yticklabels([resultados[c]["nombre"] for c in claves], fontsize=9.5)
    ax2.set_xlim(0, 105)
    ax2.set_xlabel("índice de atención (0-100)")
    _encabezado(ax2, "ÍNDICE DE ATENCIÓN",
                "Más alto = mejor como fondo de estudio")
    return fig


def figura_indice(resultados: dict) -> plt.Figure:
    """El diagrama tempo/brillo y el detalle de los criterios."""
    _aplicar_tema()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.8),
                                   layout="constrained")

    for i, (clave, r) in enumerate(resultados.items()):
        ritmo = r["ritmo"]
        centroide = r["espectro"]["centroide"]
        medible = ritmo.get("medible", True)
        ax1.scatter([ritmo["bpm"]], [centroide], s=190,
                    color=COLORES[i % len(COLORES)],
                    alpha=0.9 if medible else 0.30,
                    edgecolors=COLOR_ORIGINAL, linewidths=0.8, zorder=3)
        # si el tempo no es medible, se dice: un punto translúcido sin
        # explicación parece un error, y no lo es
        etiqueta = r["nombre"] if medible else f"{r['nombre']} (tempo no medible)"
        ax1.annotate(etiqueta, (ritmo["bpm"], centroide),
                     textcoords="offset points", xytext=(10, 4), fontsize=9,
                     color=COLOR_ORIGINAL if medible else "#6B6862",
                     style="normal" if medible else "italic")
    ax1.axvspan(60, 90, color="#009E73", alpha=0.10)
    ax1.axhspan(0, 400, color="#009E73", alpha=0.08)
    ax1.set_xlabel("tempo (BPM)")
    ax1.set_ylabel("centroide espectral (Hz)")
    _titulo(ax1, "TEMPO Y BRILLO",
            "La zona verde es la favorable (60-90 BPM, poco brillo)")
    _nota(ax1, "en cursiva y translúcido, las pistas cuyo tempo no es medible")

    # el detalle de los criterios, para el género con mejor índice
    mejor = max(resultados.items(), key=lambda kv: kv[1]["atencion"]["indice"])
    filas = mejor[1]["atencion"]["por_criterio"]
    ax2.barh(range(len(filas)), [f["puntos"] for f in filas],
             color="#0072B2", height=0.6)
    for i, f in enumerate(filas):
        ax2.text(f["puntos"] + 0.4, i, f"{f['puntos']:.1f}/{f['peso']}",
                 va="center", fontsize=9)
    ax2.set_yticks(range(len(filas)))
    ax2.set_yticklabels([f["nombre"] for f in filas], fontsize=9)
    ax2.set_xlim(0, 27)
    ax2.set_xlabel("puntos")
    _titulo(ax2, f"EL MEJOR: {mejor[1]['nombre'].upper()}",
            "Los cinco criterios, con sus pesos")
    return fig


def figura_veredicto(resultados: dict) -> plt.Figure:
    """El veredicto del punto (e): la tabla que lo resume todo."""
    _aplicar_tema()
    fig, ax = plt.subplots(figsize=(9.4, 4.4), layout="constrained")
    ax.axis("off")

    filas = []
    for clave, r in resultados.items():
        e = r["espectro"]
        a = r["atencion"]
        ritmo = r["ritmo"]
        bpm = f"{ritmo['bpm']:.0f}" if ritmo.get("medible", True) else "n. medible"
        filas.append([
            r["nombre"],
            f"{e['f_max']:.0f}",
            f"{e['fs_minima']:.0f}",
            f"{e['centroide']:.0f}",
            bpm,
            f"{a['indice']:.1f}",
        ])

    cabeceras = ["Género", "f_max (Hz)", "f_s,min (Hz)", "centroide (Hz)",
                 "BPM", "índice"]
    tabla = ax.table(cellText=filas, colLabels=cabeceras, loc="center",
                     cellLoc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9.5)
    tabla.scale(1, 1.7)
    for (fila, _), celda in tabla.get_celld().items():
        celda.set_edgecolor("#D8D4CC")
        if fila == 0:
            celda.set_text_props(weight="semibold", color="#6B6862")
    ax.set_title("El resumen del punto (e)", loc="left", fontsize=13,
                 fontweight="semibold")
    return fig


# =============================================================================
# GUARDADO
# =============================================================================

def guardar(fig: plt.Figure, ruta) -> str:
    """Guarda la figura en PNG a 300 dpi y la cierra."""
    import pathlib
    ruta = pathlib.Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return str(ruta)


def a_png(fig: plt.Figure) -> bytes:
    """La figura como bytes PNG (para servirla desde la web)."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return buffer.getvalue()


#: Las figuras de una pista, por nombre.
FIGURAS_PISTA = {
    "senal": figura_senal,
    "espectro": figura_espectro,
    "muestreo": figura_muestreo,
    "aliasing": figura_aliasing_detalle,
    "cuantizacion": figura_cuantizacion,
    "codigos": figura_codigos,
    "cadena": figura_cadena,
}


def construir_todas(r: dict) -> dict:
    """Las figuras de una pista, por nombre."""
    salida = {}
    for nombre, fn in FIGURAS_PISTA.items():
        try:
            salida[nombre] = fn(r)
        except Exception as exc:                    # pragma: no cover
            print(f"  (figura {nombre} no se pudo construir: {exc})")
    return salida
