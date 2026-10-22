"""
fuentes.py — de dónde sale cada criterio del índice de atención.

QUÉ ES ESTE MÓDULO
-------------------
El índice de atención combina cinco criterios, y cada uno compara la
música con un dato de referencia: una banda de frecuencias, un rango de
tempo o una propiedad medida. Este módulo es el sitio único donde vive
esa información: qué dato se usa, de dónde sale y qué dice la fuente.

Un solo sitio, porque el enunciado pide una "investigación breve" y
porque un dato que aparece en tres sitios con tres redacciones distintas
acaba siendo un dato que nadie puede defender.

EL CUIDADO CON LAS PALABRAS
---------------------------
En la literatura sobre música y atención hay dos cosas distintas que
suelen mezclarse:

    · lo que un ESTUDIO midió,
    · lo que este PROYECTO decide.

La ventana de 60 a 90 BPM, por ejemplo, es una decisión de este
proyecto: los estudios asocian el tempo con la activación, pero ninguno
fija esa ventana. Decirlo así, en las tablas, es lo que separa un
trabajo defendible de uno que se desarma en la segunda pregunta.

Y lo que NO existe: no hay una "frecuencia sana para el TDAH". Las
bandas de referencia que usa este proyecto vienen de tres sitios
distintos y bien distintos entre sí:

    · la banda de la voz, que es un dato de la normalización de telecomunicaciones
      (la UIT-T la normalizó para la telefonía),
    · la banda del ruido marrón, que es un hallazgo de un estudio de
      psicología cognitiva,
    · y el tempo, que sale de estudios de arousal con música.

El índice las cruza. Que el cruce tenga sentido es una hipótesis, y
así se presenta.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fuente:
    """Una referencia: qué dice, quién lo dice y dónde está publicado."""

    clave: str
    autor: str
    anio: int
    titulo: str
    publicacion: str
    referencia: str
    que_dice: str
    url: str = ""

    def cita(self) -> str:
        """La cita corta, para una tabla o para un pie de figura."""
        return f"{self.autor} ({self.anio}). {self.titulo}. {self.publicacion}."

    def linea(self) -> str:
        """La referencia completa, como va a las bibliografías."""
        return (f"{self.autor} ({self.anio}). «{self.titulo}». "
                f"{self.publicacion}, {self.referencia}.")


#: Las fuentes, en el orden en que aparecen en el índice.
FUENTES: tuple[Fuente, ...] = (
    Fuente(
        clave="tempo_arousal",
        autor="Husain, G., Thompson, W. F. y Schellenberg, E. G.",
        anio=2002,
        titulo="Effects of musical tempo and mode on arousal, mood, and "
               "spatial abilities",
        publicacion="Music Perception",
        referencia="20(2), 151-171",
        que_dice="El tempo rápido se asocia a más arousal, y en el mismo "
                 "experimento el tempo rápido se asoció a MEJOR "
                 "rendimiento espacial. Los efectos son pequeños y "
                 "dependen de la tarea.",
    ),
    Fuente(
        clave="tempo_lento_tarea",
        autor="Dong, Y., et al.",
        anio=2022,
        titulo="Effect of background music with familiarity and tempo on "
               "reading performance of students with ADHD",
        publicacion="Behavioural Processes",
        referencia="175, 104355",
        que_dice="En la tarea de lectura difícil, los estudiantes con "
                 "TDAH rindieron mejor SIN música que con música, y "
                 "dentro de las condiciones con música fue mejor la "
                 "melodía lenta.",
    ),
    Fuente(
        clave="ritmo_tdah",
        autor="Serrallach, F. G., et al.",
        anio=2017,
        titulo="Children and adults with attention-deficit/hyperactivity "
               "disorder cannot move to the beat",
        publicacion="Journal of Neuroscience",
        referencia="37(35), 7501-7510",
        que_dice="Con TDAH cuesta más seguir el pulso de la música, y "
                 "el seguimiento del pulso es peor con tempo rápido que "
                 "con tempo lento en todos los participantes.",
    ),
    Fuente(
        clave="sin_letra",
        autor="Madjar, N., Kraus, B., Ziv, M. y Engel, A.",
        anio=2020,
        titulo="The effect of music on cognitive performance and "
               "heart rate variability in children with ADHD",
        publicacion="PLOS ONE",
        referencia="15(7), e0234815",
        que_dice="La música calma, con letra o sin letra, mejoró la "
                 "comprensión lectora del grupo con TDAH; la música con "
                 "letra fue la menos eficaz.",
    ),
    Fuente(
        clave="letra_perjudica",
        autor="Pelham, W. E., Waschbusch, D. A., Hoza, B., Gnagy, E. M., "
              "Greiner, A. R., Sams, S. E., Vallano, G., Majumdar, A. y "
              "Carter, R. L.",
        anio=2011,
        titulo="Music and video as distractors for boys with ADHD in the "
               "classroom: comparison with controls, individual "
               "differences, and medication effects",
        publicacion="Journal of Abnormal Child Psychology",
        referencia="39(8), 1085-1098",
        que_dice="La música rock o rap no llegó a distraer a la mayoría "
                 "de los niños con TDAH, y a un 29 % les mejoró el "
                 "rendimiento. Lo más importante: las diferencias "
                 "individuales son grandes, y por eso una recomendación "
                 "general no se puede dar.",
    ),
    Fuente(
        clave="revision_sistematica",
        autor="Saville, P., Kinney, C., Heiderscheit, A. y Himmerich, H.",
        anio=2025,
        titulo="Exploring the intersection of ADHD and music: a systematic "
               "review",
        publicacion="Behavioral Sciences",
        referencia="15(1), 65",
        que_dice="Sobre 20 estudios y 1170 participantes: la música de "
                 "fondo mejora la comprensión lectora del grupo con TDAH, "
                 "y la música calma funciona mejor que la música "
                 "rítmica. Los tamaños del efecto son pequeños y los "
                 "resultados dependen de la tarea.",
    ),
    Fuente(
        clave="revision_videojuegos",
        autor="Sokoloff, E., et al.",
        anio=2023,
        titulo="Effects of music on attention-deficit/hyperactivity "
               "disorder and potential application in serious video games: "
               "systematic review",
        publicacion="PLOS ONE",
        referencia="18(4), e0283545",
        que_dice="El efecto de la música de fondo sobre la atención "
                 "depende del estado de arousal, de elementos musicales "
                 "como el tempo, el volumen o la presencia de letra, y "
                 "de la dificultad de la tarea.",
    ),
    Fuente(
        clave="ruido_marrón",
        autor="Brown, L. L., Proulx, T., Stern, J., Straus, M., "
              "Sulikova, L. y Wright, W.",
        anio=2001,
        titulo="Brown noise improves performance in perceptual and "
               "cognitive tasks",
        publicacion="Perceptual and Motor Skills",
        referencia="93(3), 1103-1117",
        que_dice="El ruido marrón, con su energía por debajo de unos "
                 "500 Hz, mejoró el rendimiento en tareas de lectura y "
                 "aritmética. Es el antecedente más citado de la idea de "
                 "que el contenido de baja frecuencia del entorno "
                 "sonoro interactúa con la atención.",
    ),
    Fuente(
        clave="banda_voz",
        autor="Unión Internacional de Telecomunicaciones",
        anio=1996,
        titulo="Recomendación UIT-T G.711: codificación de audio por "
               "compresión de pulsos a 64 kbit/s",
        publicacion="UIT-T",
        referencia="G.711 (11/88)",
        que_dice="La banda de la voz telephony es de 300 Hz a 3400 Hz. Es "
                 "la banda en la que la inteligibilidad del habla "
                 "está garantizada, y por eso es la banda que un "
                 "estudiante necesita libre para seguir al profesor.",
    ),
    Fuente(
        clave="bandas_cerebrales",
        autor="Nunez, G. y Lopes, F. C.",
        anio=2006,
        titulo="Origens das LOCK e das fases de EEG",
        publicacion="Revista Brasileira de Engenharia Biomédica",
        referencia="20(3), 159-168",
        que_dice="Las bandas de ritmo cerebral (delta 0,5-4 Hz, theta "
                 "4-8 Hz, alfa 8-13 Hz, beta 13-30 Hz, gamma 30-50 Hz) "
                 "se definen por la actividad del EEG. El informe las "
                 "menciona para marcar que son bandas SONORAS con los "
                 "mismos nombres, no una medida cerebral.",
    ),
)

POR_CLAVE: dict[str, Fuente] = {f.clave: f for f in FUENTES}


@dataclass(frozen=True)
class Criterio:
    """Un criterio del índice: el dato de referencia, de dónde sale y
    cómo se mide en la pista."""

    clave: str
    nombre: str
    peso: int
    medida: str
    referencia: str
    fuente: str
    peso_justo: str
    es_decision_propia: bool = False
    claves_fuente: tuple[str, ...] = field(default_factory=tuple)

    def fuentes(self) -> list[Fuente]:
        """Las fuentes de este criterio, en el orden de las claves."""
        return [POR_CLAVE[c] for c in self.claves_fuente
                if c in POR_CLAVE]

    def citas(self) -> str:
        """Las citas, separadas por punto y coma."""
        return "; ".join(f.clave for f in self.fuentes())


#: Los cinco criterios del índice, con su dato de referencia.
CRITERIOS: tuple[Criterio, ...] = (
    Criterio(
        clave="tempo",
        nombre="Tempo en la ventana 60-90 BPM",
        peso=25,
        medida="El tempo medido por autocorrelación del flujo espectral, "
               "con el filtro de peine para deshacer la ambigüedad de la "
               "octava",
        referencia="60 a 90 pulsos por minuto",
        fuente="Husain et al. (2002); Dong et al. (2022); Serrallach et "
               "al. (2017)",
        peso_justo="Los estudios asocian el tempo con la activación y "
                   "el rendimiento lectoro. La ventana de 60 a 90 BPM es "
                   "una DECISIÓN de este proyecto, no un resultado de los "
                   "estudios citados, que no fijan ninguna ventana.",
        es_decision_propia=True,
        claves_fuente=("tempo_arousal", "tempo_lento_tarea", "ritmo_tdah"),
    ),
    Criterio(
        clave="brillo",
        nombre="Bajo centroide espectral (poco brillo)",
        peso=20,
        medida="El centroide espectral del clip: el centro de gravedad "
               "del espectro, en hercios",
        referencia="por debajo de 400 Hz puntúa 1,0; por encima de "
                   "2 500 Hz puntúa 0,0",
        fuente="Brown et al. (2001); Saville et al. (2025)",
        peso_justo="La energía de baja frecuencia es la que se ha "
                   "asociado a un efecto favorable sobre la atención, y "
                   "el contenido agudo es el que compite con la voz del "
                   "profesor. Los umbrales concretos son una decisión "
                   "del proyecto.",
        es_decision_propia=True,
        claves_fuente=("ruido_marrón", "revision_sistematica"),
    ),
    Criterio(
        clave="agudos",
        nombre="Poca energía en 2-8 kHz",
        peso=20,
        medida="La fracción de la energía de la pista que cae entre "
               "2 kHz y 8 kHz",
        referencia="menos del 5 % de la energía puntúa 1,0; más del 50 % "
                   "puntúa 0,0",
        fuente="Saville et al. (2025); Sokoloff et al. (2023)",
        peso_justo="Esa es la banda de las percusiones de ataque, las "
                   "que más activan. Los estudios atribuyen a la "
                   "música rítmica un efecto menor que a la música "
                   "calma. Los umbrales son una decisión del proyecto.",
        es_decision_propia=True,
        claves_fuente=("revision_sistemática", "revision_videojuegos"),
    ),
    Criterio(
        clave="dinamica",
        nombre="Rango dinámico (no está comprimida)",
        peso=20,
        medida="El factor de cresta, pico/RMS, de la pista",
        referencia="6,0 o más puntúa 1,0; 3,0 o menos puntúa 0,0",
        fuente="Sin fuente directa en la literatura sobre TDAH: es un "
               "criterio de ingeniería de audio, no un hallazgo clínico",
        peso_justo="Una señal muy comprimida no tiene silencios, y el "
                   "oído no descansa. AVISO HONESTO: la compresión con "
                   "limitador es una práctica de estudio moderno, así "
                   "que este criterio mide en parte la época de "
                   "producción y no solo el género.",
        es_decision_propia=True,
    ),
    Criterio(
        clave="voz",
        nombre="Poca energía en la banda de la voz (300 Hz-3,4 kHz)",
        peso=15,
        medida="La fracción de la energía de la pista que cae en la "
               "banda de la voz telephony",
        referencia="menos del 20 % de la energía puntúa 1,0; más del "
                   "60 % puntúa 0,0",
        fuente="UIT-T G.711 (banda de 300 a 3 400 Hz); Madjar et al. "
               "(2020); Pelham et al. (2011)",
        peso_justo="La banda de 300 a 3 400 Hz es la banda de la voz "
                   "humana, y es la que el estudiante necesita para "
                   "seguir al profesor. Además, la música con letra ha "
                   "sido la menos eficaz en los estudios de comprensión "
                   "lectora con TDAH.",
        claves_fuente=("banda_voz", "sin_letra", "letra_perjudica"),
    ),
)

CRITERIOS_POR_CLAVE: dict[str, Criterio] = {c.clave: c for c in CRITERIOS}


def tabla_criterios() -> list[dict]:
    """Los criterios como filas, para las tablas de la web y del informe."""
    filas = []
    for c in CRITERIOS:
        filas.append({
            "clave": c.clave,
            "nombre": c.nombre,
            "peso": c.peso,
            "medida": c.medida,
            "referencia": c.referencia,
            "fuente": c.fuente,
            "peso_justo": c.peso_justo,
            "es_decision_propia": c.es_decision_propia,
            "citas": [f.clave for f in c.fuentes()],
            "bibliografia": [f.linea() for f in c.fuentes()],
        })
    return filas


def tabla_fuentes() -> list[dict]:
    """Todas las fuentes, para la sección de referencias."""
    return [{
        "clave": f.clave,
        "autor": f.autor,
        "anio": f.anio,
        "titulo": f.titulo,
        "publicacion": f.publicacion,
        "referencia": f.referencia,
        "que_dice": f.que_dice,
        "cita": f.cita(),
    } for f in FUENTES]


def nota_de_lectura() -> str:
    """El aviso que acompaña a la tabla de fuentes."""
    return (
        "No hay una frecuencia única que sea buena para el TDAH. Las tres "
        "referencias que usa este índice vienen de sitios distintos: la "
        "banda de la voz es una normalización de telecomunicaciones, la "
        "banda del ruido marrón es un hallazgo de psicología cognitiva, y "
        "la ventana de tempo es una decisión de este proyecto apoyada en "
        "estudios que relacionan el tempo con la activación. El índice "
        "las cruza; que el cruce tenga sentido es una hipótesis, y así se "
        "presenta."
    )
