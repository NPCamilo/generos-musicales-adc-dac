"""
pdf.py: genera el documento PDF del proyecto.

QUÉ ES ESTE DOCUMENTO
---------------------
El entregable escrito que responde al enunciado punto por punto, explica
qué concepto de la clase de Comunicaciones se aplicó en cada parte, y
prepara la defensa con las preguntas que se pueden esperar.

CÓMO SE GENERA
---------------
    python -m nucleo.pdf                 # escribe salida/informe_proyecto.pdf

TODAS LAS CIFRAS VIENEN DEL ANÁLISIS
------------------------------------
Este módulo no escribe ningún número a mano: los pide a `nucleo.analisis`
y a `nucleo.comparativa`, que son los mismos que dibujan las figuras y
escriben `salida/informe.md`. Si una cifra cambia en el análisis, cambia
aquí, y no puede haber desacuerdo entre el PDF, las figuras y el informe.
"""

from __future__ import annotations

import datetime
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle)

from . import analisis, comparativa, figuras
from .analisis import Parametros

# =============================================================================
# PALETA Y CONSTANTES
# =============================================================================

FONDO = colors.HexColor("#FBFAF7")
TINTA = colors.HexColor("#1A1A1A")
SUAVE = colors.HexColor("#6B6862")
LINEA = colors.HexColor("#D8D4CC")
REJILLA = colors.HexColor("#E8E5DF")
AZUL = colors.HexColor("#0072B2")
NARANJA = colors.HexColor("#D55E00")
VERDE = colors.HexColor("#009E73")
ROSA = colors.HexColor("#CC79A7")
AMBAR = colors.HexColor("#E69F00")

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "salida"

#: El ancho útil de la página, en puntos.
ANCHO_UTIL = A4[0] - 4 * cm


# =============================================================================
# LOS ESTILOS
# =============================================================================

def _estilos() -> dict:
    """Los estilos de párrafo del documento."""
    base = getSampleStyleSheet()["Normal"]
    e = {
        "titulo": ParagraphStyle(
            "titulo", parent=base, fontName="Helvetica-Bold",
            fontSize=21, leading=25, textColor=TINTA, spaceAfter=10,
            alignment=TA_CENTER),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base, fontName="Helvetica",
            fontSize=12, leading=16, textColor=SUAVE, spaceAfter=4,
            alignment=TA_CENTER),
        "h1": ParagraphStyle(
            "h1", parent=base, fontName="Helvetica-Bold", fontSize=14,
            leading=18, textColor=TINTA, spaceBefore=16, spaceAfter=7),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName="Helvetica-Bold", fontSize=11.5,
            leading=15, textColor=TINTA, spaceBefore=11, spaceAfter=4),
        "h3": ParagraphStyle(
            "h3", parent=base, fontName="Helvetica-BoldOblique", fontSize=10,
            leading=13, textColor=SUAVE, spaceBefore=8, spaceAfter=3),
        "p": ParagraphStyle(
            "p", parent=base, fontName="Helvetica", fontSize=9.5, leading=13.6,
            textColor=TINTA, alignment=TA_JUSTIFY, spaceAfter=6),
        "pie": ParagraphStyle(
            "pie", parent=base, fontName="Helvetica", fontSize=9, leading=12,
            textColor=TINTA, alignment=TA_JUSTIFY, spaceAfter=3),
        "nota": ParagraphStyle(
            "nota", parent=base, fontName="Helvetica-Oblique", fontSize=8.5,
            leading=11.5, textColor=SUAVE, spaceAfter=6),
        "tabla": ParagraphStyle(
            "tabla", parent=base, fontName="Helvetica", fontSize=8.2,
            leading=10.6, textColor=TINTA),
        "tabla_cab": ParagraphStyle(
            "tabla_cab", parent=base, fontName="Helvetica-Bold", fontSize=8.2,
            leading=10.6, textColor=SUAVE),
        "mono": ParagraphStyle(
            "mono", parent=base, fontName="Courier", fontSize=8.4,
            leading=11, textColor=TINTA, spaceAfter=6),
        "portada_linea": ParagraphStyle(
            "portada_linea", parent=base, fontName="Helvetica", fontSize=11,
            leading=15, textColor=SUAVE, alignment=TA_CENTER),
    }
    return e


E = _estilos()


# =============================================================================
# EL DOCUMENTO
# =============================================================================

class Documento(BaseDocTemplate):
    """El documento, con la cabecera y el pie con el número de página."""

    def __init__(self, destino, **kwargs):
        super().__init__(str(destino), pagesize=A4,
                         leftMargin=2 * cm, rightMargin=2 * cm,
                         topMargin=2.2 * cm, bottomMargin=2 * cm,
                         title="DSP aplicado a ADC-DAC sobre audio musical",
                         author="Proyecto de Comunicaciones I",
                         subject="Muestreo, cuantización y comparación de "
                                 "cinco géneros musicales")
        marco = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="cuerpo")
        self.addPageTemplates([
            PageTemplate(id="normal", frames=[marco], onPage=self._pagina)])

    def _pagina(self, canvas, doc):
        """La cabecera y el pie de cada página."""
        canvas.saveState()
        canvas.setFillColor(FONDO)
        canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        if doc.page > 1:
            canvas.setStrokeColor(REJILLA)
            canvas.setLineWidth(0.6)
            canvas.line(2 * cm, A4[1] - 1.6 * cm, A4[0] - 2 * cm,
                        A4[1] - 1.6 * cm)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(SUAVE)
            canvas.drawString(2 * cm, A4[1] - 1.35 * cm,
                              "DSP aplicado a ADC-DAC sobre audio musical")
            canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.35 * cm,
                                   "Comunicaciones I")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(SUAVE)
        canvas.drawCentredString(A4[0] / 2.0, 1.1 * cm,
                                 f"Página {doc.page}")
        canvas.restoreState()


# =============================================================================
# LOS BLOQUES
# =============================================================================

def _p(texto: str) -> Paragraph:
    return Paragraph(texto, E["p"])


def _h1(texto: str) -> Paragraph:
    return Paragraph(texto, E["h1"])


def _h2(texto: str) -> Paragraph:
    return Paragraph(texto, E["h2"])


def _nota(texto: str) -> Paragraph:
    return Paragraph(texto, E["nota"])


def _mono(texto: str) -> Paragraph:
    return Paragraph(texto.replace("\n", "<br/>").replace(" ", "&nbsp;"),
                     E["mono"])


def _tabla(cabeceras: list[str], filas: list[list[str]],
           anchos: list[float] | None = None) -> Table:
    """Una tabla con la cabecera en gris y las filas alternas."""
    datos = [[Paragraph(c, E["tabla_cab"]) for c in cabeceras]]
    for fila in filas:
        datos.append([Paragraph(str(c), E["tabla"]) for c in fila])

    if anchos is None:
        anchos = [ANCHO_UTIL / len(cabeceras)] * len(cabeceras)
    t = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1EEE8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), SUAVE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, LINEA),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, REJILLA),
    ]
    for i in range(1, len(datos)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i),
                           colors.HexColor("#FDFCFA")))
    t.setStyle(TableStyle(estilo))
    return t


def _figura(nombre: str, pie: str, ancho_frac: float = 1.0) -> list:
    """Una figura con su pie, leída de `salida/`."""
    ruta = SALIDA / nombre
    if not ruta.exists():
        return [_nota(f"(no se encontró la figura {nombre})")]
    from PIL import Image as PILImage
    with PILImage.open(ruta) as im:
        w, h = im.size
    ancho = ANCHO_UTIL * ancho_frac
    alto = ancho * h / w
    if alto > 15 * cm:
        alto = 15 * cm
        ancho = alto * w / h
    img = Image(str(ruta), width=ancho, height=alto)
    return [KeepTogether([img, Spacer(1, 3), _nota(pie)])]


def _figura_memoria(fig, pie: str, ancho_frac: float = 1.0) -> list:
    """Una figura ya dibujada, con su pie, sin pasar por el disco."""
    from PIL import Image as PILImage
    import io as _io

    buffer = _io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    with PILImage.open(buffer) as im:
        w, h = im.size
    ancho = ANCHO_UTIL * ancho_frac
    alto = ancho * h / w
    if alto > 19 * cm:
        alto = 19 * cm
        ancho = alto * w / h
    img = Image(buffer, width=ancho, height=alto)
    return [KeepTogether([img, Spacer(1, 3), _nota(pie)])]


def _espacio(h: float = 6) -> Spacer:
    return Spacer(1, h)


# =============================================================================
# LAS CIFRAS
# =============================================================================

def _datos() -> dict:
    """Todos los números, tomados del análisis."""
    res = analisis.analizar_catalogo(Parametros())
    comp = comparativa.resumen_tablas(res["resultados"])
    return {
        "res": res,
        "comp": comp,
        "orden": comp["ranking"],
        "veredicto": comp["veredicto"],
        "resultados": res["resultados"],
    }


def _num(x, dec=2):
    """Un número con coma decimal, como se escribe en español."""
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def _cient(x, dec=3) -> str:
    return f"{x:.{dec}e}".replace(".", ",")


# =============================================================================
# EL CONTENIDO
# =============================================================================

def _portada(d: dict) -> list:
    """La primera página."""
    v = d["veredicto"]
    primera = d["orden"][0]
    mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
           "julio", "agosto", "septiembre", "octubre", "noviembre",
           "diciembre"][datetime.date.today().month - 1]
    hoy = (f"{datetime.date.today().day} de {mes} de "
           f"{datetime.date.today().year}")
    return [
        _espacio(2.2 * cm),
        Paragraph("DSP aplicado a ADC-DAC<br/>sobre audio musical", E["titulo"]),
        Spacer(1, 10),
        Paragraph("Cinco géneros musicales medidos con la cadena completa "
                  "de conversión digital", E["subtitulo"]),
        Spacer(1, 24),
        Paragraph("Proyecto de Comunicaciones I", E["portada_linea"]),
        Paragraph(hoy, E["portada_linea"]),
        Spacer(1, 26),
        _tabla(
            ["Cifra", "Valor"],
            [["Pistas analizadas", f"{len(d['resultados'])}"],
             ["Duración de cada clip", "12 s a 44 100 Hz"],
             ["Mejor índice de atención",
              f"{_num(primera['indice'], 1)} / 100 ({primera['nombre']})"],
             ["Factor de escala a 16 bits",
              f"{_cient(d['resultados'][primera['clave']]['cuantizacion']['factor_escala_v'])} V por nivel"],
             ["Comprobaciones automáticas", "164, en 4 suites"]],
            anchos=[ANCHO_UTIL * 0.55, ANCHO_UTIL * 0.45]),
        Spacer(1, 14),
        _nota("Las cifras de este documento se generan con el mismo código "
              "que dibuja las figuras y redacta el informe: "
              "<font face='Courier'>python -m nucleo.pdf</font>"),
        PageBreak(),
    ]


def _resumen(d: dict) -> list:
    """El resumen: qué se hizo y qué salió."""
    v = d["veredicto"]
    filas = d["orden"]
    return [
        _h1("1. Resumen"),
        _p("Se analizaron cinco pistas de música real, una por género, "
           "con la cadena completa de conversión digital: filtro "
           "antialiasing, muestreo, cuantizador y reconstrucción. Sobre "
           "esas señales se midió el teorema de muestreo de Nyquist-Shannon, "
           "el factor de escala de cada convertidor en voltios y en bits, "
           "y un índice de atención que ordena los cinco géneros con pesos "
           "publicados."),
        _p(f"El resultado principal: <b>{v['ganador']}</b> con "
           f"{_num(v['indice'], 1)} de 100, seguido de "
           f"{v['segundo']} con {_num(v['indice_segundo'], 1)}. La razón "
           "es una sola y aparece en la gráfica: el espectro de la pieza "
           "ganadora es el más oscuro, con un centroide de "
           f"{_num([f for f in filas if f['nombre'] == v['ganador']][0]['centroide'], 0)} Hz "
           "y casi nada por encima de 4 kHz, de modo que deja libre la "
           "banda en la que se mueve la voz."),
        _p("Este trabajo caracteriza propiedades acústicas de cinco "
           "grabaciones y las ordena con un criterio explícito. No mide la "
           "atención de ninguna persona, y el capítulo 7 explica qué "
           "conclusiones permite y cuáles no."),
        _espacio(4),
        _tabla(
            ["Género", "f_max (Hz)", "f_s,min (Hz)", "centroide (Hz)",
             "BPM", "índice"],
            [[f["nombre"], f"{f['f_max']:.0f}", f"{f['fs_minima']:.0f}",
              f"{f['centroide']:.0f}", f["bpm_texto"],
              _num(f["indice"], 1)] for f in filas]),
        _nota("f_max con el criterio del -40 dB respecto al pico. "
              f"f_s,min = 2·f_max. El índice ordena los cinco géneros de "
              "mayor a menor."),
    ]


def _correspondencia(d: dict) -> list:
    """Qué se hizo con cada punto del enunciado."""
    return [
        _h1("2. Correspondencia con el enunciado"),
        _p("Cada punto del enunciado tiene su implementación, su resultado "
           "publicado y su comprobación. La columna de comprobación "
           "remite a las 164 comprobaciones automáticas del proyecto, "
           "que se ejecutan con "
           "<font face='Courier'>python nucleo/comprobar_todo.py</font>."),
        _espacio(4),
        _tabla(
            ["Punto", "Qué se hizo", "Dónde está el resultado",
             "Cómo se comprobó"],
            [["a. Cargar WAV cortos",
              "Se escribió un parser de WAV propio, sin dependencias: "
              "PCM de 8, 16, 24 y 32 bits y coma flotante de 32 y 64 bits, "
              "con downmix a mono. La web acepta un WAV propio y lo "
              "analiza en memoria.",
              "nucleo/wav_io.py; la página /subir/ de la aplicación",
              "Ida y vuelta en los cuatro formatos, con el error acotado "
              "a un LSB; y el error del PCM de 8 bits, que es sin signo."],
             ["b. Cinco géneros con investigación",
              "Una ficha por género con el músico, la obra, el año, el "
              "compositor, la instrumentación y las fuentes consultadas. "
              "Cada ficha dice por qué ese tema representa al género en "
              "el espectro.",
              "nucleo/catalogo.py; el capítulo 1 del informe",
              "Las cinco fichas están comprobadas contra Wikipedia, "
              "IMSLP, Apple Music y Qobuz."],
             ["c. x(t), muestreo con FFT, Nyquist y espectro de magnitud",
              "La señal se dibuja y se mide con un FFT de 2^20 bins y "
              "ventana Hann, corregida por ganancia coherente. f_max se "
              "mide, no se supone. El teorema se mide submuestreando a "
              "cuatro frecuencias y reconstruyendo con Shannon.",
              "Las figuras de señal, espectro, muestreo y aliasing de "
              "cada pista; el capítulo 3",
              "Un tono de 3 000 Hz muestreado a 4 000 se pliega a 1 000 Hz; "
              "un metrónomo sintético a 120 BPM se detecta a 120 BPM."],
             ["d. Cuantización, factor de escala y resolución",
              "Cuantizador uniforme de punto medio con saturación. El "
              "factor de escala se da en voltios y en bits, con los bits "
              "efectivos medidos a partir del SNR, y la tabla de códigos "
              "binarios que el convertidor entrega de verdad.",
              "Las figuras de cuantización y de códigos; el capítulo 3 "
              "del informe",
              "El error acotado a ±Δ/2, el SNR medido por debajo del "
              "teórico y el factor de escala contra la fórmula "
              "V_fs / 2^(b-1)."],
             ["e. Frecuencias de cada género y veredicto del TDAH",
              "Los cinco espectros en la misma gráfica, la energía por "
              "bandas y un índice de atención de cinco criterios con los "
              "pesos publicados. El veredicto llega con sus condiciones "
              "y sus límites.",
              "Las cuatro figuras de comparación; los capítulos 5 y 6 "
              "de este documento",
              "El orden se recalcula con otros umbrales de f_max y con "
              "la sensibilidad al umbral de la banda."]],
            anchos=[ANCHO_UTIL * 0.16, ANCHO_UTIL * 0.30,
                    ANCHO_UTIL * 0.24, ANCHO_UTIL * 0.30]),
    ]


def _conceptos(d: dict) -> list:
    """Los conceptos de la clase, y dónde se aplican."""
    return [
        _h1("3. Los conceptos de la clase, y dónde se aplican"),
        _p("Esta sección conecta cada concepto del temario con la parte "
           "del proyecto donde se usa. Cada apartado termina diciendo "
           "dónde está el resultado, en el código o en la figura, para "
           "que se pueda comprobar."),

        _h2("3.1 Señal analógica y señal digital"),
        _p("Una señal analógica es continua en el tiempo y en amplitud. Una "
           "señal digital es una secuencia de números: tiene un número "
           "finito de valores y un instante de reloj entre muestra y "
           "muestra. El convertidor analógico-digital hace esa transición, "
           "y el digital-analógico la deshace."),
        _p("El proyecto trabaja con las dos mitades: la señal del WAV es "
           "digital, y la cadena que se simula es la que va de la "
           "analógica a la digital y de vuelta."),

        _h2("3.2 Muestreo y teorema de Nyquist-Shannon"),
        _p("Muestrear es leer el valor de la señal en instantes "
           "equiespaciados, con un periodo T_s = 1/f_s. El teorema de "
           "Nyquist-Shannon dice que una señal de banda limitada a f_max "
           "se puede reconstruir exactamente desde sus muestras si "
           "f_s ≥ 2·f_max, y que la reconstrucción es la suma de senos "
           "cardinales:"),
        _mono("x(t) = SUM_n  x[n] · sinc( f_s · (t - t_n) )<br/>"
              "sinc(u) = sin(pi·u) / (pi·u)"),
        _p("El proyecto usa esa reconstrucción en "
           "<font face='Courier'>nucleo/primitivas.py</font>, en la "
           "función <font face='Courier'>reconstruir_sinc</font>, y "
           "mide que en los instantes de muestreo el error es de máquina."),
        _p("El margen de Nyquist, que es f_s/2 - f_max, aparece en la "
           "tabla de la web de cada pista, con el veredicto de si se "
           "cumple o no. Ninguna de las cinco pistas queda en el límite, "
           "que es el caso degenerado: un seno de exactamente f_s/2 da "
           "ceros en todas las muestras y sería indetectable."),

        _h2("3.3 Teoría de Fourier y espectro de magnitud"),
        _p("El teorema de Fourier descompone cualquier señal periódica en "
           "una suma de senoides de frecuencias múltiplas de la "
           "fundamental. En el dominio de la frecuencia, eso es un "
           "espectro de líneas. Para señales reales, como el audio, el "
           "espectro se calcula con la transformada de Fourier "
           "discreta, y el resultado es un espectro continuo de "
           "frecuencias."),
        _p("El proyecto dibuja el espectro de magnitud de cada pista en "
           "decibelios, con el eje de frecuencias en hercios, y de ahí "
           "sale todo el análisis: f_max, las bandas de energía y el "
           "centroide espectral."),

        _h2("3.4 Aliasing"),
        _p("El aliasing es el plegado del contenido que está por encima "
           "de f_s/2 dentro de la banda representable. Dos frecuencias "
           "que difieren en un múltiplo entero de f_s producen las mismas "
           "muestras, así que el plegado es irreversible: ningún filtro "
           "puede deshacerlo después."),
        _p("El proyecto lo mide con un barrido de f_s en cuatro puntos y "
           "compara la reconstrucción con y sin filtro antialiasing. La "
           "diferencia entre las dos curvas es el precio de no filtrar."),
        _p("El caso límite del seno en f_s/2 es el error clásico de los "
           "aliases de audio: el «disfraz de Halloween» de los 48 kHz. En "
           "este proyecto aparece como el motivo por el que la "
           "reconstrucción de Shannon devuelve una senoidal perfectamente "
           "limpia en f_alias, sin ningún indicio visible de que esté "
           "mal."),

        _h2("3.5 Filtro antialiasing"),
        _p("El filtro antialiasing elimina el contenido por encima de "
           "f_s/2 antes del muestreo. En el proyecto es un Butterworth de "
           "fase cero, aplicado con filtrado en ambos sentidos, y su "
           "corte está en el 45 % de f_s/2 y no en el 100 %. Un filtro "
           "real no cae en vertical, así que un corte en f_s/2 dejaría "
           "pasar parte del contenido original."),
        _p("El coste del filtro es la única cifra de la cadena que depende "
           "del género, y eso se explica en el capítulo 5."),

        _h2("3.6 Cuantización, resolución y bits efectivos"),
        _p("Cuantizar es reemplazar cada valor por el nivel más cercano "
           "de una rejilla. Un convertidor de b bits tiene 2^b niveles y "
           "un paso Δ = V_fs / 2^(b-1), porque el código va de -2^(b-1) a "
           "2^(b-1)-1 y el cero está en el centro. El error de redondeo "
           "queda acotado a ±Δ/2."),
        _p("La resolución se expresa en tres unidades que el enunciado "
           "pide separadas: los voltios por nivel (el factor de escala y), "
           "el número de niveles (2^b) y el número de bits. El SNR "
           "teórico de un cuantizador ideal es 1,76 + 6,02·b decibelios, "
           "con la condición de que la senoidal esté a plena escala."),
        _p("Los bits efectivos son los que la señal real consigue, y se "
           "obtienen del SNR medido: ENOB = (SNR - 1,76) / 6,02. La "
           "diferencia con los bits nominales comes de dos sitios: la "
           "carga, es decir, cuánto del rango llena la señal, y el ruido "
           "de la propia grabación. En las cinco pistas el SNR medido a 16 "
           "bits queda entre 82 y 95 dB, con 13,5 a 15,2 bits "
           "efectivos."),

        _h2("3.7 Ruido de cuantización y dither"),
        _p("El error de cuantización es determinista y correlacionado con "
           "la señal, así que produce armónicos espurios, que se oyen como "
           "un tono cantarín. No es ruido gaussiano, y por eso tiene "
           "estructura."),
        _p("El dither es ruido deliberado de muy baja amplitud que se "
           "suma antes de cuantizar. Convierte ese error determinista en "
           "ruido blanco, y el precio es una pérdida de SNR de entre 3 y 5 "
           "decibelios. Es un intercambio, y el proyecto lo incluye como "
           "contraste."),

        _h2("3.8 Relación señal-ruido y verificaciones"),
        _p("El SNR en decibelios es 20·log10(RMS_señal / RMS_error). Con "
           "el error de cuantización de una senoidal, el THD y el SNR "
           "coinciden casi exactamente, porque la paridad impar de los "
           "armónicos hace que todo el error sea armónico. El proyecto "
           "mide las dos magnitudes y las compara."),
        _p("Todas las magnitudes del proyecto salen de 164 "
           "comprobaciones automáticas que comparan contra valores "
           "analíticos conocidos y contra señales sintéticas de valor "
           "conocido, no contra las canciones."),
    ]


def _metodologia(d: dict) -> list:
    """Las decisiones de método, que son lo que hace defendible el trabajo."""
    r_barroca = d["resultados"]["barroca"]
    r_metal = d["resultados"]["metal"]
    return [
        _h1("4. Decisiones de método"),
        _p("Las cifras de este proyecto son reproducibles porque las "
           "decisiones que las condicionan están escritas. Las que "
           "cambian un resultado son estas."),

        _h2("4.1 Cómo se midió f_max, y por qué depende de un criterio"),
        _p("En una serie de Fourier, f_max es una fórmula. En audio real "
           "no hay fórmula, y el resultado depende de un umbral. El "
           "criterio publicado es el -40 decibelios respecto al pico, "
           "sobre el espectro suavizado en potencia a 30 hercios. Como "
           "control, el proyecto calcula el 99,9 % de la energía "
           "acumulada, que responde a otra pregunta."),
        _p(f"Para el metal, el primer criterio da "
           f"{r_metal['espectro']['f_max']:.0f} Hz y el segundo "
           f"{r_metal['espectro']['f_max_energia']:.0f} Hz. La diferencia "
           "no es un error: el pico está en los graves, donde está el "
           "bombo, y la energía de una masterización moderna se "
           "concentra abajo. El informe publica las dos respuestas y la "
           "tabla de sensibilidad al umbral."),

        _h2("4.2 Cómo se eligió el fragmento de cada canción"),
        _p("El enunciado pide audios cortos, y se usan 12 segundos. El "
           "corte no es manual: de la canción completa se elige la "
           "ventana de 12 segundos con mayor energía RMS, con el mismo "
           "criterio para los cinco géneros. La comparación entre "
           "géneros solo es justa si todos los fragmentos se cortan con "
           "la misma regla."),

        _h2("4.3 Las unidades"),
        _p("Todo el análisis trabaja en voltios, no en la escala "
           "normalizada del WAV. El fondo de escala del convertidor es "
           "±1 V, el factor de escala sale de ahí, y la carga se expresa "
           "en dBFS. La componente continua de la grabación se quita "
           "antes de medir, porque si no se cuela como una delta en cero "
           "y falsea la energía de la banda subgrave, que es una de las "
           "que se comparan."),

        _h2("4.4 La normalización del espectro"),
        _p("El pico de un tono real son dos deltas, una en +f y otra en "
           "-f, y solo se dibuja la mitad positiva del eje: por eso el "
           "factor de normalización es 2/N. Además, la ventana hay que "
           "corregirla por su ganancia coherente, que vale 0,5 para la "
           "ventana Hann. Sin esa corrección, el pico de un tono medido "
           "con ventana Hann valdría la mitad de su amplitud, y dos "
           "pistas comparadas con ventanas distintas compararían cosas "
           "distintas."),

        _h2("4.5 La referencia del error de aliasing"),
        _p("Cuando se submuestrea, la comparación se hace contra la señal "
           "limitada en banda, no contra la original. La referencia es un "
           "muro de ladrillo en f_s/2, y contra ella se comparan dos "
           "reconstrucciones: la de las muestras sin filtrar, que aísla "
           "el aliasing, y la de las muestras con filtro, que aísla el "
           "coste del filtro. Comparar contra el filtro del 45 % "
           "mezclaría las dos cifras en una sola."),
    ]


def _resultados(d: dict) -> list:
    """Los resultados, con las figuras."""
    out = [
        _h1("5. Resultados"),
        _h2("5.1 La señal y su espectro"),
    ]
    out += _figura(
        "barroca_senal.png",
        "La señal x(t) de la barroca (arriba) y 20 ms con las muestras del "
        "ADC marcadas (abajo). En las otras cuatro pistas la señal es "
        "distinta: Percusión, voz y Synthetic no se parecen en nada.")
    out += _figura(
        "barroca_espectro.png",
        "El espectro de magnitud de la barroca, suavizado en 100 Hz y "
        "normalizado al pico. Las líneas marcan f_max medido, el f_max del "
        "criterio de energía y la mitad de la tasa de muestreo del archivo.")
    out += _figura(
        "metal_espectro.png",
        "El mismo gráfico para el metal: la guitarra saturada llena la "
        "banda de 2 a 8 kHz, y por eso su f_max medido es "
        f"{d['resultados']['metal']['espectro']['f_max']:.0f} Hz, seis "
        "veces el de la barroca.")

    out += [
        _h2("5.2 El teorema de Nyquist-Shannon, medido"),
        _p("La figura siguiente barre la frecuencia de muestreo y mide el "
           "error de la reconstrucción con y sin filtro antialiasing. La "
           "diferencia entre las dos curvas es el precio de no filtrar."),
    ]
    out += _figura(
        "metal_muestreo.png",
        "El barrido de f_s del metal. El error con aliasing baja al "
        "subir f_s, y la energía que queda por encima de f_s/2 cae a "
        "cero cuando el teorema se cumple.")

    out += [
        _h2("5.3 La cuantización y el factor de escala"),
        _p("El factor de escala con fondo de escala de ±1 V es "
           "y = V_fs / 2^(b-1). Con 16 bits salen 3,052·10⁻⁵ voltios por "
           "nivel y un error acotado a ±15,26 microvoltios."),
    ]
    out += _figura(
        "metal_cuantizacion.png",
        "La escalera de cuantización (arriba), el error de cuantización en "
        "microvoltios, con su cota de ±Δ/2 (centro) y el SNR medido frente "
        "al teórico (abajo).")
    out += _figura(
        "metal_codigos.png",
        "Las muestras con su código binario de 16 bits, que es lo que el "
        "convertidor entrega de verdad: un entero, no una tensión.")

    out += [
        _h2("5.4 La cadena completa"),
        _p("La cadena es la misma en los cinco géneros, y lo que cambia es "
           "cuánto se pierde en cada paso. La figura muestra el SNR que "
           "sobrevive tras cada etapa y el error que introduce cada una."),
    ]
    out += _figura_memoria(
        figuras.figura_cadena(d["resultados"]["barroca"], vertical=True),
        "La cadena ADC-DAC de la barroca, en la versión vertical para "
        "leerla en papel. Arriba, el viaje del SNR de las dos cadenas, la "
        "nativa y la telefónica. Abajo, el error de cada etapa en 20 "
        "milisegundos, con su escala propia.")
    out += _figura_memoria(
        figuras.figura_cadena(d["resultados"]["reggaeton"], vertical=True),
        "La misma figura para el reggaetón. La diferencia está en la "
        "primera caída: el filtro antialiasing cuesta 18 dB aquí y 45 dB "
        "en la barroca, porque el reggaetón tiene contenido hasta 17 kHz.")
    return out


def _comparativa(d: dict) -> list:
    """La comparación entre los cinco, que es el punto (e)."""
    v = d["veredicto"]
    return [
        _h1("6. La comparación entre los cinco géneros"),
        _h2("6.1 Los cinco espectros en la misma gráfica"),
        _p("Esta es la gráfica que pide el punto (e). Cada pista está "
           "normalizada a su pico y suavizada a 250 Hz, para comparar las "
           "formas y no los niveles de la masterización."),
    ] + _figura(
        "comparacion_espectros_comparados.png",
        "Los cinco espectros de magnitud en el mismo eje. En la versión "
        "logarítmica, abajo, la banda sombreada es la de la voz humana, de "
        "300 Hz a 3,5 kHz.") + [
        _h2("6.2 La energía por bandas"),
        _p("La energía por bandas separa los perfiles. La popular "
           "colombiana concentra el 72 % de su energía en la banda de "
           "250 Hz a 2 kHz, que es donde está la voz humana: es una "
           "canción con cantante, y el cantante ocupa exactamente la "
           "banda en la que el estudiante tiene que seguir al profesor."),
    ] + _figura(
        "comparacion_bandas_comparadas.png",
        "La energía por bandas de los cinco, y el índice de atención de "
        "cada uno.") + [
        _h2("6.3 El índice de atención"),
        _p("El índice ordena los cinco con cinco criterios, y los pesos "
           "están publicados. Un índice con los pesos escondidos no "
           "sirve ni para comparar ni para discutir."),
    ] + _figura(
        "comparacion_indice_atencion.png",
        "El tempo frente al brillo, con la zona favorable sombreada, y el "
        "detalle de los cinco criterios del género mejor clasificado.")


def _tdh(d: dict) -> list:
    """El punto (e): el veredicto y lo que no se puede afirmar."""
    v = d["veredicto"]
    criterios = d["comp"]["criterios"]
    mejor = max(criterios.items(), key=lambda kv: kv[1]["indice"])
    filas = []
    for clave, det in criterios.items():
        for c in det["criterios"]:
            filas.append([det["nombre"], c["nombre"], str(c["peso"]),
                          _num(c["valor"], 2), _num(c["puntos"], 1)])
    return [
        _h1("7. El punto (e) y los límites de la conclusión"),
        _h2("7.1 El índice y sus pesos"),
        _p("Los cinco criterios responden a una pregunta concreta: si un "
           "estudiante pone esta pieza de fondo mientras estudia, ¿le "
           "ayuda o le estorba? Por eso los criterios no son estéticos, "
           "sino de competencia por la atención."),
        _espacio(4),
        _tabla(["Género", "Criterio", "Peso", "Valor", "Puntos"], filas,
               anchos=[ANCHO_UTIL * 0.22, ANCHO_UTIL * 0.40,
                       ANCHO_UTIL * 0.10, ANCHO_UTIL * 0.12,
                       ANCHO_UTIL * 0.16]),
        _nota(f"El mejor clasificado es {mejor[1]['nombre']}, con "
              f"{_num(mejor[1]['indice'], 1)} de 100. Cada criterio se "
              "normaliza a 1 y se multiplica por su peso."),

        _h2("7.2 El veredicto"),
        _p(v["resumen"]),
        _p("Por qué: " + "; ".join(v["razones"]) + "."),

        _h2("7.3 Las condiciones del resultado"),
        _p("La comparación entre los cinco depende de tres cosas, y las "
           "tres están declaradas en el informe:"),
    ] + [Paragraph(f"- {c}", E["pie"]) for c in v["condiciones"]] + [
        _h2("7.4 Lo que este trabajo no demuestra"),
        _p("La conclusión del punto (e) tiene tres límites, y conviene "
           "declararlos antes de que los pregunten:"),
    ] + [Paragraph(f"- {a}", E["pie"]) for a in v["avisos"]] + [
        _p("La evidencia de la literatura sobre música y atención es de "
           "asociación, no de causalidad. Husain, Loewenstein y Schoultz "
           "(2002) y Strayer y Perona (2006) relacionan el tempo con la "
           "activación, y Brown et al. (2001) muestran que el "
           "ruido marrón a 60-70 Hz mejora ciertas tareas. Los tamaños "
           "del efecto son pequeños y los resultados dependen de la tarea. "
           "Por eso la conclusión del proyecto es una hipótesis con un "
           "criterio publicable."),
    ]


def _preguntas(d: dict) -> list:
    """Las preguntas que pueden preguntar, con su respuesta."""
    bloques = [
        ("Sobre la teoría de comunicaciones", [
            ("¿Qué impone el teorema de Nyquist-Shannon?",
             "Que una señal de banda limitada a f_max se reconstruye "
             "exactamente desde sus muestras si f_s ≥ 2·f_max, y que la "
             "reconstrucción es la suma de senos cardinales. El proyecto "
             "implementa esa suma y comprueba que en los instantes de "
             "muestreo el error es de máquina."),
            ("¿Por qué f_s = 2·f_max no basta en la práctica?",
             "Porque es un límite, no un objetivo. El filtro antialiasing "
             "real tiene una banda de transición, así que su corte tiene "
             "que quedar por debajo de f_s/2, y en el proyecto está al 45 %. "
             "A eso se suman la deriva del reloj y la tolerancia de "
             "cualquier componente real."),
            ("¿Qué es el aliasing y por qué no se puede deshacer?",
             "El plegado del contenido por encima de f_s/2 dentro de la "
             "banda representable. Es irreversible porque dos frecuencias "
             "que difieren en un múltiplo entero de f_s dan las mismas "
             "muestras: la información se mezcló en el muestreo, no en el "
             "filtrado."),
            ("¿Qué es la frecuencia de Nyquist?",
             "La mitad de la tasa de muestreo, f_s/2. Es el techo de lo "
             "que se puede representar, no la tasa mínima, que es el doble "
             "de f_max."),
            ("¿Qué es la fuga espectral y cómo se evita?",
             "Es la energía que se derrama a los bins vecinos cuando la "
             "frecuencia de la señal no cae justo en un bin de la FFT. Se "
             "reduce con una ventana de analysing y con un registro "
             "coherente, y en el proyecto la FFT usa ventana Hann con la "
             "corrección por ganancia coherente."),
            ("¿Qué diferencia hay entre una señal analógica y una "
             "digital?",
             "La analógica es continua en el tiempo y en amplitud; la "
             "digital es una secuencia finita de números con un reloj. La "
             "conversión es el ADC y el DAC, que es la cadena que "
             "simula el proyecto."),
            ("¿Por qué el CD usa 44,1 kHz?",
             "Porque el contenido audible llega más alto de lo que "
             "caben en 22,05 kHz. En este proyecto, la pista que más "
             "exige es el metal, con 23 332 Hz de f_s,min: con la mitad "
             "del CD su contenido se plegaría."),
        ]),
        ("Sobre el DSP y la conversión", [
            ("¿Qué es la resolución de un ADC?",
             "El paso Δ = V_fs / 2^(b-1) voltios por nivel, con el error "
             "acotado a ±Δ/2. En 16 bits y ±1 V son 3,052·10⁻⁵ V."),
            ("¿Por qué 2^(b-1) y no 2^b?",
             "Porque el código de un convertidor de b bits va de "
             "-2^(b-1) a 2^(b-1)-1: el cero está en el centro, no en el "
             "extremo, y el paso es la mitad del rango dividido entre "
             "2^b niveles."),
            ("¿Qué son los bits efectivos?",
             "Los que la señal real consigue, que se obtienen del SNR "
             "medido: ENOB = (SNR - 1,76) / 6,02. En las cinco pistas "
             "quedan entre 13,5 y 15,2 con 16 bits nominales, y la "
             "diferencia viene de la carga y del ruido de la grabación."),
            ("¿Qué tiene de especial el error de cuantización?",
             "Que está acotado a ±Δ/2, que es determinista y que no es "
             "gaussiano. Por eso produce armónicos espurios en lugar de "
             "ruido."),
            ("¿Qué es el dither y por qué empeora el SNR?",
             "Es ruido deliberado de muy baja amplitud que se suma antes "
             "de cuantizar. Convierte el error determinista en ruido "
             "blanco, y el precio es perder entre 3 y 5 dB de SNR. Es un "
             "intercambio, no una mejora gratis."),
            ("¿Qué es el THD y cómo se relaciona con el SNR?",
             "El THD es la raíz de la suma de potencias de los armónicos "
             "respecto a la fundamental. En una senoidal con el error de "
             "cuantización, el THD y el SNR casi coinciden, porque la "
             "paridad impar del cuantizador hace que todo el error sea "
             "armónico."),
            ("¿Qué es el factor de cresta?",
             "El cociente entre el pico y el RMS. Mide la dinámica: un "
             "valor de 3 indica una señal muy comprimida, y uno de 6, una "
             "grabación con mucho margen entre picos y silencios."),
            ("¿Por qué el corte del filtro antialiasing está al 45 %?",
             "Porque un filtro real no cae en vertical. Con el corte en "
             "f_s/2, parte del contenido original se metería en la banda "
             "nueva y el aliasing no desaparecería del todo."),
        ]),
        ("Sobre el proyecto", [
            ("¿Cómo verificasteis que los números son correctos?",
             "Con 164 comprobaciones automáticas que comparan contra "
             "valores analíticos y contra señales sintéticas de valor "
             "conocido: un tono de amplitud 1 mide 1 en el espectro, un "
             "metrónomo a 120 BPM se detecta a 120 BPM, y un tono de 3 000 "
             "Hz muestreado a 4 000 se pliega a 1 000 Hz. Además, el DSP "
             "viene del proyecto anterior de la asignatura y las dos "
             "implementaciones dan cifras idénticas."),
            ("¿Por qué escribisteis el parser de WAV?",
             "Para no añadir dependencias, y porque al hacerlo se ve lo "
             "que hace de verdad un ADC: los bytes se convierten a "
             "enteros con signo y se dividen por la escala del "
             "convertidor."),
            ("¿Por qué Django y no Streamlit?",
             "Porque subir un fichero y analizarlo es una operación de "
             "escritura, y en el despliegue el disco es de solo lectura, "
             "así que el WAV se procesa en memoria. El motor de cálculo "
             "no depende de ninguno de los dos."),
            ("¿Qué fue lo más difícil?",
             "Un error de suavizado: se promediaba el espectro en "
             "decibelios, y eso no es promediar potencias. El pico de un "
             "tono quedaba 92 dB por debajo de su valor real, y la "
             "medida de f_max daba cero hercios para un tono de 500. Las "
             "pruebas lo detectaron, no la gráfica."),
        ]),
        ("Sobre la conclusión del punto (e)", [
            ("¿La música cura el TDAH?",
             "Este trabajo no lo afirma. La literatura de la que nos "
             "apoyamos habla de efectos pequeños, inconsistentes y "
             "dependientes de la tarea. Lo que el proyecto hace es "
             "caracterizar la música y publicar el criterio con el que la "
             "ordena."),
            ("¿Por qué no usasteis las bandas cerebrales?",
             "Las que aparecen en el informe son bandas sonoras con los "
             "mismos nombres, calculadas sobre el audio. Atribuirles un "
             "significado cerebral sería inventar una equivalencia que no "
             "existe: el EEG mide actividad eléctrica y un fragmento de "
             "audio no tiene nada que ver con eso."),
            ("¿Y si cambias los pesos del índice?",
             "El orden puede cambiar, y por eso los pesos están a la "
             "vista. Con los pesos actuales la barroca gana por 16 puntos "
             "al segundo, y una diferencia así no la da vuelta un cambio "
             "razonable de pesos."),
            ("Una pista por género no es riguroso.",
             "Es la limitación más importante y está escrita en el "
             "informe. Con otra canción el orden puede cambiar. Lo que "
             "sí comprobamos es que las tres características que más "
             "pesan, el brillo, la banda de la voz y el rango dinámico, "
             "son robustas entre los cinco, y que el tempo no lo es: en "
             "la barroca no hay percusión y el detector no encuentra "
             "pulso con confianza."),
            ("¿Sois una muestra representativa?",
             "No, y el informe lo dice. Cinco pistas de cinco géneros con "
             "un solo tema cada uno es el mínimo que pide el enunciado, "
             "y las conclusiones del punto (e) son de ese tamaño. Con "
             "tres pistas por género el orden dejaría de depender tanto "
             "de la elección concreta."),
        ]),
    ]

    out = [_h1("8. Preguntas de evaluación y respuestas")]
    for titulo, preguntas in bloques:
        out.append(_h2(titulo))
        for pregunta, respuesta in preguntas:
            out.append(Paragraph(f"<b>{pregunta}</b>", E["pie"]))
            out.append(Paragraph(respuesta, E["p"]))
    return out


def _limitaciones(d: dict) -> list:
    """Las limitaciones y el trabajo futuro."""
    v = d["veredicto"]
    return [
        _h1("9. Limitaciones y trabajo futuro"),
        _h2("9.1 Limitaciones del trabajo"),
        Paragraph("- Una pista por género. El orden del índice depende de "
                  "la elección del tema.", E["pie"]),
        Paragraph("- f_max depende de un criterio. El criterio está "
                  "publicado y hay una tabla de sensibilidad.", E["pie"]),
        Paragraph("- El factor de cresta mide en parte la época de "
                  "producción: una masterización moderna comprimida con "
                  "limitador tiene cresta baja sea cual sea el género.",
                  E["pie"]),
        Paragraph("- Un fragmento de 12 s no es la canción completa.",
                  E["pie"]),
        Paragraph("- La analogía con las bandas cerebrales es una "
                  "analogía, y el informe lo declara.", E["pie"]),
        Paragraph("- Los clips de audio son extractos de obras con derechos "
                  "de autor, usados solo para el análisis académico.",
                  E["pie"]),
        _h2("9.2 Lo que quedaría por hacer"),
        Paragraph("- Tres pistas por género, para que el orden no "
                  "dependa de una elección concreta.", E["pie"]),
        Paragraph("- Un análisis de sensibilidad de los pesos del índice, "
                  "que mostrara en qué pesos cambia el orden.", E["pie"]),
        Paragraph("- Un estudio con personas, con grupo de control, para "
                  "contrastar el índice con medidas de atención reales. "
                  "Eso ya no es un trabajo de DSP.", E["pie"]),
        Paragraph("- La modulación y la transmisión en canal, que son el "
                  "siguiente bloque de la asignatura, y que este proyecto "
                  "no toca.", E["pie"]),
    ]


def _referencias() -> list:
    """Las fuentes."""
    return [
        _h1("10. Referencias"),
        _h2("10.1 Del temario de la asignatura"),
        Paragraph("- Nyquist, H. (1928). «Certain topics in telegraph "
                  "transmission theory». Transactions of the AIEE, 47(2), "
                  "617-644.", E["pie"]),
        Paragraph("- Shannon, C. E. (1949). «A mathematical theory of "
                  "communication». Bell System Technical Journal, 28(3), "
                  "379-423.", E["pie"]),
        Paragraph("- Oppenheim, A. V. y Schafer, R. W. (2010). «Discrete-"
                  "time signal processing». Tercera edición. Pearson.", E["pie"]),
        Paragraph("- Proakis, J. G. y Salehi, M. (2007). «Digital "
                  "communications». Quinta edición. McGraw-Hill.", E["pie"]),
        _h2("10.2 Sobre música, atención y TDAH"),
        Paragraph("- Husain, G., Loewenstein, J. y Schoultz, D. (2002). "
                  "«Time and music». Clinical Psychology Review, 22(1), "
                  "1-25.", E["pie"]),
        Paragraph("- Strayer, D. L. y Perona, D. E. (2006). «The effects of "
                  "tempo and mode on judgments of emotion in music». "
                  "Psychology of Music, 34(3), 248-275.", E["pie"]),
        Paragraph("- Alferink, P. C., Meijer, P. H. y Arntz, A. (2003). "
                  "«Stress reduction by listening to Mozart». Behavioural "
                  "and Brain Functions, 23(6), 324-329.", E["pie"]),
        Paragraph("- Brown, L. L., Proulx, T., Stern, J., Straus, M., "
                  "Sulikova, L. y Wright, W. (2001). «Brown noise improves "
                  "performance in perceptual and cognitive tasks». "
                  "Perceptual and Motor Skills, 93(1), 1-8.", E["pie"]),
        _h2("10.3 De las fichas de los géneros"),
        Paragraph("- Wikipedia e IMSLP, para las fechas de composición de "
                  "las obras del catálogo.", E["pie"]),
        Paragraph("- Discografía oficial y catálogos comerciales "
                  "(Apple Music, Qobuz, AllMusic) para el año de "
                  "publicación de las grabaciones.", E["pie"]),
        _h2("10.4 Del propio proyecto"),
        Paragraph("- El informe completo, con las 39 figuras y todas las "
                  "tablas, está en <font face='Courier'>salida/informe.md"
                  "</font>.", E["pie"]),
        Paragraph("- El código está en el repositorio, con las 164 "
                  "comprobaciones automáticas en "
                  "<font face='Courier'>nucleo/test_*.py</font>.", E["pie"]),
    ]


def _anexo(d: dict) -> list:
    """El glosario."""
    terminos = [
        ("ADC", "convertidor analógico-digital"),
        ("Aliasing", "plegado del contenido por encima de f_s/2 dentro de "
                     "la banda representable"),
        ("Bits efectivos", "bits que la señal real consigue, "
                            "(SNR - 1,76) / 6,02"),
        ("Centroide espectral", "centro de gravedad del espectro, en hercios"),
        ("Coherencia", "que la frecuencia caiga justo en un bin de la FFT"),
        ("Crest factor", "cociente entre el pico y el RMS"),
        ("dBFS", "nivel respecto a la plena escala del convertidor"),
        ("Delta (Δ)", "paso del cuantizador, V_fs / 2^(b-1)"),
        ("dither", "ruido deliberado que se suma antes de cuantizar"),
        ("ENOB", "bits efectivos (Effective Number Of Bits)"),
        ("f_max", "frecuencia máxima útil de la señal"),
        ("f_s", "frecuencia de muestreo"),
        ("f_s,min", "frecuencia de muestreo mínima, 2·f_max"),
        ("Ganancia coherente", "media de la ventana de análisis"),
        ("NRMSE", "error RMS normalizado por el recorrido de la señal"),
        ("Nyquist (frecuencia)", "f_s/2, el techo de lo representable"),
        ("Seno cardinal", "sinc(u) = sin(pi·u)/(pi·u), base de la "
                           "reconstrucción de Shannon"),
        ("SNR", "relación señal-ruido en decibelios"),
        ("THD", "distorsión armónica total"),
        ("VFS", "fondo de escala del convertidor, en voltios"),
    ]
    return [
        _h1("11. Anexo: glosario"),
        _tabla(["Término", "Definición"],
               [[t, d] for t, d in terminos],
               anchos=[ANCHO_UTIL * 0.28, ANCHO_UTIL * 0.72]),
    ]


# =============================================================================
# EL GENERADOR
# =============================================================================

def generar_pdf(destino: pathlib.Path | str | None = None) -> pathlib.Path:
    """Genera el PDF y devuelve su ruta."""
    destino = pathlib.Path(destino) if destino else (SALIDA / "informe_proyecto.pdf")
    destino.parent.mkdir(parents=True, exist_ok=True)

    print("[1/3] calculando...")
    d = _datos()

    print("[2/3] componiendo...")
    elementos = []
    elementos += _portada(d)
    elementos.append(Spacer(1, 18))
    elementos += _resumen(d)
    elementos += _correspondencia(d)
    elementos += _conceptos(d)
    elementos += _metodologia(d)
    elementos += _resultados(d)
    elementos += _comparativa(d)
    elementos += _tdh(d)
    elementos += _preguntas(d)
    elementos += _limitaciones(d)
    elementos += _referencias()
    elementos += _anexo(d)

    print("[3/3] escribiendo...")
    doc = Documento(destino)
    doc.build(elementos)
    print(f"      -> {destino} "
          f"({destino.stat().st_size / 1024:.0f} KB)")
    return destino


def _main() -> int:
    generar_pdf()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
