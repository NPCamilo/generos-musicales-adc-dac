"""
catalogo.py — las cinco pistas de la muestra y su ficha de investigación.

QUÉ ES ESTO
-----------
El enunciado pide "una investigación breve" de cada género: de dónde
viene, quién lo compuso o lo interpretó, y en qué año. Aquí están esos
datos, con la fuente, en un solo sitio, para que el informe los use sin
tener que inventarlos en el momento.

También está, para cada pista, la razón por la que se eligió: no es
decorativo, es la JUSTIFICACIÓN de que ese ejemplo representa al género en
lo que importa para este trabajo, que es el ESPECTRO.

EL CRITERIO DE SELECCIÓN
------------------------
Una pista representa a su género en este trabajo si su perfil espectral
es el propio del género, no una excepción:

    · BARROCA   — un solo instrumento (violonchelo), fundamental grave y
      armónicos limpios: casi nada por encima de 2 kHz. El perfil
      "solemne y oscuro" del barroco, medible.
    · METAL     — guitarra saturada: la saturación genera armónicos de
      orden muy alto, así que hay energía hasta 8-10 kHz. El perfil
      "denso y brillante" del metal.
    · SALSA     — percusión latina (timbales, cowbell) y montuno: la
      energía se reparte en la banda media (250 Hz-2 kHz), con un bajo
      eléctrico en el graves.
    · REGGAETÓN — bombo sintetizado en 40-60 Hz y voz limpia por encima,
      casi sin contenido intermedio: el perfil más grave y de mayor
      dinámica de los cinco.
    · POPULAR COLOMBIANA — la "cantina" o "depecho" de la costa
      colombiana: guitarra y voz en la banda media,percusión de raspas.
      Es el género que laBundles "música popular colombiana" del
      enunciado.

CADA FICHA TIENE
----------------
    clave        : el nombre del fichero (audio/<clave>.wav)
    nombre       : cómo se llama en las gráficas
    musico       : quién lo interpretó
    obra         : la obra concreta
    anio         : el año
    compositor   : quién lo compuso (o "la propia tradición oral")
    estilo       : el subgénero
    instrumentacion : qué suena
    bpm_esperado : el tempo aproximado, para contrastar con el medido
    banda_clave  : la banda de frecuencias donde se espera la energía
    por_que      : por qué este ejemplo y no otro
    fuentes      : dónde se comprobó cada dato
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Genero:
    """La ficha de una pista: datos de investigación y perfil esperado."""

    clave: str
    nombre: str
    genero: str
    musico: str
    obra: str
    anio: int
    compositor: str
    estilo: str
    instrumentacion: str
    bpm_esperado: str
    banda_clave: str
    por_que: str
    fuentes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def etiqueta(self) -> str:
        """El nombre corto para las gráficas y las tablas."""
        return self.nombre

    def ficha(self) -> dict:
        """La ficha como diccionario, para las tablas del informe."""
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "género": self.genero,
            "músico": self.musico,
            "obra": self.obra,
            "año": self.anio,
            "compositor": self.compositor,
            "estilo": self.estilo,
            "instrumentación": self.instrumentacion,
            "bpm esperado": self.bpm_esperado,
            "banda clave": self.banda_clave,
            "por qué este ejemplo": self.por_que,
            "fuentes": list(self.fuentes),
        }


#: El catálogo, en el orden en que se presentan los resultados.
CATALOGO: tuple[Genero, ...] = (
    Genero(
        clave="barroca",
        nombre="Clásica · Barroca",
        genero="Clásica — Barroca",
        musico="Netherlands Bach Society (Lucia Swarts, violonchelo)",
        obra="J. S. Bach — Suite para violonchelo n.º 1 en Sol mayor, "
             "BWV 1007 (I. Preludio)",
        anio=1722,
        compositor="Johann Sebastian Bach (1685-1750)",
        estilo="Barroco tardío (Köthen), cello solo senza basso",
        instrumentacion="Un solo violonchelo, arpegiado continuo y "
                        "cadencias de acordes",
        bpm_esperado="60-80 (sin percusión, el pulso lo marca el arpegio)",
        banda_clave="60-250 Hz (fundamental del violonchelo) con armónicos "
                    "limpios; casi nada por encima de 2 kHz",
        por_que="Es el perfil más limpio de los cinco: un instrumento "
                "sin percusión, sin distorsión y sin voz. Al medirlo se "
                "ve que casi toda la energía está en 60-250 Hz, que es "
                "justo lo que hace que una pieza barroca 'suene' profunda. "
                "Sirve de REFERENCIA: es el caso en el que el criterio de "
                "Nyquist se cumple de sobra y el audio no tiene nada que "
                "esconder.",
        fuentes=(
            "Wikipedia (EN): Cello Suites (Bach), BWV 1007-1012, "
            "compuestas entre 1717 y 1723 en Köthen.",
            "IMSLP: Cello Suite No. 1 en Sol mayor, BWV 1007, año de "
            "composición 1717.",
            "Netherlands Bach Society: proyecto 'All of Bach', "
            "interpretación de Lucia Swarts (proyecto 2022).",
        ),
    ),
    Genero(
        clave="metal",
        nombre="Metal",
        genero="Metal (heavy/thrash)",
        musico="Megadeth",
        obra="Tornado of Souls (del álbum Youthanasia)",
        anio=1990,
        compositor="Dave Mustaine",
        estilo="Thrash/heavy metal de finales de los 80",
        instrumentacion="Guitarras con saturación, bajo eléctrico, "
                        "batería y.msg",
        bpm_esperado="120-140 (tema en 4/4, riff en semicorcheas)",
        banda_clave="Fundamental grave del bajo (40-100 Hz) + mucha "
                    "energía de guitarra hasta 8 kHz por la saturación",
        por_que="La saturación de la guitarra no es un efecto de timbre: "
                "es multiplicación de la onda por una función no lineal, "
                "y eso genera armónicos de orden muy alto. Por eso el "
                "metal es el caso con más contenido agudo del conjunto, y "
                "el que peor se porta cuando se baja la frecuencia de "
                "muestreo: es la pista donde el aliasing se ve más claro.",
        fuentes=(
            "Discografía de Megadeth: 'Youthanasia', 1990; "
            "'Tornado of Souls' es el segundo corte del álbum.",
            "Wikipedia (EN): Youthanasia, álbum de 1990.",
        ),
    ),
    Genero(
        clave="salsa",
        nombre="Salsa",
        genero="Salsa (salsa romántica, montuno)",
        musico="Frankie Ruiz y La Solución",
        obra="La Rueda (compositor: Víctor Manuel Mato)",
        anio=1980,
        compositor="Víctor Manuel Mato (ranchera Colombian, años 50)",
        estilo="Salsa romántica con montuno y percusión latina",
        instrumentacion="Voz, trombones y clarinetes, percusión latina "
                        "(timbales, congas, cowbell), bajo y guitarra",
        bpm_esperado="90-110 (son clave, 2-3)",
        banda_clave="250 Hz-2 kHz (timbal y montuno) con bajo en 60-120 Hz",
        por_que="Es el género con la percusión más 'química' del "
                "conjunto: el timbal y la cowbell tienen su energía justo "
                "en la banda de 2-6 kHz, que es la banda que en el punto "
                "(e) se asocia con activación. Sirve para ver cómo un "
                "mismo género cambia de fisonomía según la época: aquí "
                "viene de la salsa de los 80, con un sonido de orquesta "
                "de viento muy presente.",
        fuentes=(
            "Wikipedia (ES): Frankie Ruiz — 'La rueda' se incluye en el "
            "segundo álbum de Orquesta La Solución, 'Orquesta La "
            "Solución' (LAD Records, 1980).",
            "RPP (2026): 'Originally it was a ranchera by composer Víctor "
            "Matos, recorded in the mid-1950s'; Frankie la grabó con La "
            "Solución a partir de 1978.",
            "Wikipedia (EN): 'Historia Musical de Frankie Ruiz' (1987).",
        ),
    ),
    Genero(
        clave="reggaeton",
        nombre="Reggaetón",
        genero="Reggaetón",
        musico="Feid y ATL Jacob",
        obra="LUNA (del EP Ferxxocalipsis)",
        anio=2023,
        compositor="Salomón Villada (Feid) y ATL Jacob",
        estilo="Reggaetón colombiano contemporary (2020s)",
        instrumentacion="Bombo sintetizado (dembow), pads, voz con "
                        "autotune, sintetizadores de alta frecuencia",
        bpm_esperado="90-100 (dembow en 2-4)",
        banda_clave="40-60 Hz (bombo sintetizado) y 60-250 Hz (bajo y "
                    "voz); muy poca energía por encima de 4 kHz",
        por_que="El reggaetón moderno es EL caso de la música con la "
                "energía más concentrada en el graves: el bombo es un "
                "seno sintetizado y la voz va con poca información "
                "armónica alta. Es, junto con la barroca, el otro extremo "
                "del conjunto, y el que da la mayor دينامica (el bombo "
                "ataca y la voz no).",
        fuentes=(
            "Wikipedia (EN): 'Luna (Feid and ATL Jacob song)', single del "
            "EP 'Ferxxocalipsis' (2023), lanzamiento el 1 de diciembre de "
            "2023.",
            "Apple Music / Shazam: fecha de publicación 1-dic-2023.",
        ),
    ),
    Genero(
        clave="popular",
        nombre="Popular colombiana",
        genero="Música popular colombiana (cantina / ranchera costeña)",
        musico="Fredy Montoya ft. Luisito Muñoz",
        obra="Ángel o Demonio",
        anio=2016,
        compositor="Fernando (Fredy) Montoya",
        estilo="Cantina colombiana de la costa (despecho costeño), con "
               "influencia del vallenato",
        instrumentacion="Guitarra acústica, Bajo, percusión de raspas y "
                        "pandereta, voz de Contralto",
        bpm_esperado="70-90 (balada con pulso binario)",
        banda_clave="250 Hz-2 kHz (voz y guitarra), casi sin graves "
                    "fuertes ni agudos",
        por_que="Es el género del enunciado que los demás llaman "
                "'cantina al hombro': la música popular colombiana de "
                "la costa, la que cantan Jessi Uribe o Paola Jara. Su "
                "perfil es de banda media, con voz y guitarra, y es un "
                "buen contraste con el resto: no tiene bombo, no tiene "
                "guitarra saturada y no tiene nada inesperado. Es "
                "el perfil 'neutro' del conjunto.",
        fuentes=(
            "Apple Music: 'Ángel o Demonio (feat. Luisito Muñoz) - "
            "Single', 2016.",
            "Shazam / Qobuz: compositor Fernando Montoya; remix oficial "
            "con Álzate, Jessi Uribe, Luisito Muñoz y Fredy Montoya "
            "(marzo de 2026).",
            "Tropicana Colombia (2026): 'Ángel o Demonio', clásico de la "
            "música popular colombiana.",
        ),
    ),
)


#: Acceso rápido por clave.
POR_CLAVE: dict[str, Genero] = {g.clave: g for g in CATALOGO}


def claves() -> list[str]:
    """Las claves de las pistas del catálogo, en orden."""
    return [g.clave for g in CATALOGO]


def obtener(clave: str) -> Genero:
    """La ficha de una pista por su clave.

    Lanza `KeyError` si la clave no existe, que es lo que quiere.
    """
    return POR_CLAVE[clave]
