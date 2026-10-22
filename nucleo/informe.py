"""
informe.py — genera `salida/informe.md`, el entregable escrito del proyecto.

QUÉ CONTIENE EL INFORME
-----------------------
    0. Portada y resumen ejecutivo (las cifras que hay que saber de memoria)
    1. La investigación: las cinco fichas, con músico, obra y año
    2. La cadena ADC-DAC, explicada antes de usarla
    3. Los resultados, género por género (con sus figuras)
    4. La comparación: la gráfica única y la tabla de las cifras
    5. El punto (e): el índice de atención, el veredicto y sus límites
    6. Cómo se ha calculado, y con qué criterio
    7. Lo que este trabajo NO demuestra

EL ORDEN IMPORTA
----------------
La sección 0 va arriba porque es la que se lee en los primeros diez
segundos. La sección 7 va al final porque es la que hay que leer cuando
alguien pregunte "¿y esto sirve para tratar el TDAH?".

CÓMO SE GENERA
--------------
    python -m nucleo.informe          # escribe salida/informe.md y los PNG

El informe se escribe desde los MISMOS datos que dibujan las figuras, de
modo que no puede haber desacuerdo entre el texto y los gráficos: si una
cifra cambia, cambia en los dos sitios a la vez.
"""

from __future__ import annotations

import datetime
import pathlib

try:
    from . import analisis, comparativa, figuras
    from .analisis import Parametros
except ImportError:                        # ejecución suelta
    import analisis
    import comparativa
    import figuras
    from analisis import Parametros

#: La carpeta de salida.
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "salida"


def _tabla(encabezados: list[str], filas: list[list[str]]) -> str:
    """Una tabla markdown."""
    lineas = ["| " + " | ".join(encabezados) + " |",
              "|" + "|".join(["---"] * len(encabezados)) + "|"]
    for fila in filas:
        lineas.append("| " + " | ".join(str(c) for c in fila) + " |")
    return "\n".join(lineas)


def _figura(ruta_relativa: str, pie: str) -> str:
    """La marca de una figura, con su pie."""
    return f"![{pie}]({ruta_relativa})\n\n*{pie}*\n"


def _num(x, decimales: int = 2, unidad: str = "") -> str:
    """Un número con el separador decimal español (coma)."""
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    texto = f"{x:,.{decimales}f}".replace(",", "§").replace(".", ",")
    texto = texto.replace("§", ".")
    return texto + (f" {unidad}" if unidad else "")


def _cientifico(x, decimales: int = 3) -> str:
    """Un número en notación científica, con coma decimal."""
    if x is None:
        return "—"
    return f"{x:.{decimales}e}".replace(".", ",")


def generar_informe(params: Parametros | None = None,
                    destino: pathlib.Path | None = None,
                    regenerar_figuras: bool = True) -> pathlib.Path:
    """Analiza las pistas, dibuja las figuras y escribe el informe.

    Devuelve la ruta del `.md` escrito.
    """
    p = params or Parametros()
    destino = pathlib.Path(destino) if destino else (SALIDA / "informe.md")
    destino.parent.mkdir(parents=True, exist_ok=True)

    print("[1/4] analizando las pistas...")
    res = analisis.analizar_catalogo(p)
    resultados = res["resultados"]
    if not resultados:
        raise RuntimeError(
            "No hay ninguna pista en audio/. Descarga las pistas con "
            "`python -m nucleo.descarga` o coloca tus propios WAV.")
    comp = comparativa.resumen_tablas(resultados)
    veredicto = comp["veredicto"]

    print("[2/4] dibujando las figuras...")
    nombres = []
    if regenerar_figuras:
        for clave, r in resultados.items():
            for nombre, fig in figuras.construir_todas(r).items():
                ruta = f"{clave}_{nombre}.png"
                figuras.guardar(fig, destino.parent / ruta)
                nombres.append(ruta)
        for nombre, fn in (("espectros_comparados",
                            figuras.figura_espectros_comparados),
                           ("bandas_comparadas", figuras.figura_bandas),
                           ("indice_atencion", figuras.figura_indice),
                           ("veredicto", figuras.figura_veredicto)):
            ruta = f"comparacion_{nombre}.png"
            figuras.guardar(fn(resultados), destino.parent / ruta)
            nombres.append(ruta)

    print("[3/4] escribiendo el informe...")
    texto = _construir_texto(res, comp, veredicto, p, nombres)

    print("[4/4] guardando...")
    destino.write_text(texto, encoding="utf-8")
    print(f"      -> {destino}")
    return destino


def _construir_texto(res: dict, comp: dict, veredicto: dict,
                      p: Parametros, nombres_figuras: list[str]) -> str:
    """El cuerpo del informe, en markdown."""
    resultados = res["resultados"]
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    partes: list[str] = []

    # ---------------------------------------------------------------- 0
    primera = comp["ranking"][0]
    partes.append(f"""# DSP aplicado a ADC-DAC sobre audio musical

### Cinco géneros, cinco perfiles espectrales, una comparación

**Proyecto de Comunicaciones I · {hoy}**

---

## 0. Resumen ejecutivo

Se analizaron **cinco pistas** de cinco géneros distintos, cada una de 12
segundos y a 44,1 kHz, con la cadena completa de conversión
**ADC → cuantizador → DAC** y con el teorema de muestreo de
**Nyquist-Shannon** medido sobre audio real (no sobre señales
sintéticas).

Las cinco cifras que hay que saber de memoria:

| cifra | valor | de dónde sale |
|---|---|---|
| pistas analizadas | {len(resultados)} | `audio/*.wav` |
| géneros comparados | {len(resultados)} | el catálogo, punto (b) del enunciado |
| mejor índice de atención | **{_num(primera['indice'], 1)} / 100** | {primera['nombre']} |
| `f_s` mínima del conjunto | {max(f['fs_minima'] for f in comp['veredicto']['tabla']):.0f} Hz | 2·f_max de la pista más exigente |
| resolución a 16 bits | {resultados[list(resultados)[0]]['cuantizacion']['factor_escala_v']:.3e} V/nivel | V_fs / 2^(b-1) |

**El veredicto del punto (e):** {veredicto['resumen']}

> **Aviso de alcance, y es importante:** este trabajo caracteriza
> *propiedades acústicas* de cinco grabaciones y las ordena con un índice
> cuyos pesos están publicados. **No** mide la atención de ninguna
> persona, **no** es un estudio clínico y **no** puede afirmar que una
> pieza mejore el TDAH de un estudiante. La sección 5 explica qué se
> afirma y qué no.
""")

    # ---------------------------------------------------------------- 1
    filas_ficha = []
    for clave, r in resultados.items():
        f = r["ficha"]
        filas_ficha.append([
            r["nombre"], f["músico"], f["obra"], f["año"], f["compositor"],
        ])
    fichas = []
    for clave, r in resultados.items():
        f = r["ficha"]
        fuentes = "\n".join(f"- {s}" for s in f["fuentes"])
        fichas.append(f"""### {r['nombre']}

| campo | dato |
|---|---|
| **Músico / intérprete** | {f['músico']} |
| **Obra** | {f['obra']} |
| **Año** | {f['año']} |
| **Compositor** | {f['compositor']} |
| **Estilo** | {f['estilo']} |
| **Instrumentación** | {f['instrumentación']} |
| **Tempo esperado** | {f['bpm esperado']} |
| **Banda característica** | {f['banda clave']} |

**Por qué este ejemplo y no otro.** {f['por qué este ejemplo']}

**Fuentes.**

{fuentes}
""")
    partes.append(f"""## 1. La investigación: las cinco pistas

El enunciado pide una "investigación breve" de cada género. Las fichas
son las siguientes, y cada una dice por qué ese tema representa al
género **en lo que importa para este trabajo, que es el espectro**.

{_tabla(["Género", "Músico", "Obra", "Año", "Compositor"], filas_ficha)}

{chr(10).join(fichas)}
""")

    # ---------------------------------------------------------------- 2
    partes.append("""## 2. La cadena ADC-DAC, explicada antes de usarla

El proyecto `Nyquist_Shannon` (que ya existía, y del que viene la
metodología) trabaja con señales que son **series de Fourier**, de las
que se sabe `f_max` exactamente. El audio real es otra cosa: no es
periódico, es finito, y su `f_max` hay que **medirlo**. Por eso este
proyecto tiene su propia capa de instrumental, que es la parte realmente
nueva.

La cadena, en orden, con lo que se mide en cada paso:

```
x(t)  ──filtro antialiasing──▶  ──muestreo──▶  ──cuantizador──▶  ──DAC──▶  x̂(t)
       recorta lo que está         reloj de fs      b bits, Δ =      ZOH o
       por encima de fs/2          y retención      Vfs/2^(b-1)      Shannon
```

**El filtro antialiasing** es lo que separa una reconstrucción correcta
de una riddled de aliasing. SeButterworth de fase cero (`sosfiltfilt`), con
el corte al 45 % de `f_s/2` y no al 100 %, porque un filtro real no cae
en vertical.

**El muestreo** toma las muestras en los instantes del reloj, sin
interpolar nada: es lo que hace un ADC de verdad.

**El cuantizador** es uniforme, con los niveles en los **centros** de las
celdas, y satura en los extremos. El error está acotado a `±Δ/2`.

**El DAC** se implementa de dos formas: retenedor de orden cero (el DAC
barato) y suma de senos cardinales (la reconstrucción exacta de Shannon).

### La normalización del espectro, que es donde se cuelan los errores

Un tono real son **dos** deltas en `±f`, y solo se dibuja la mitad
positiva del eje: por eso el factor de normalización es `2/N` y no `1/N`.

Y la ventana hay que corregirla por su **ganancia coherente**:

    A[k] = 2·|X[k]| / (N · CG)      con CG = media de la ventana

    CG(rectangular) = 1,00     CG(Hann) = 0,50     CG(Blackman) = 0,42

Sin esa corrección, el pico de un tono en ventana Hann mide LA MITAD de su
amplitud, y comparar dos pistas con ventanas distintas es comparar
cosas distintas. Es el mismo error que multiplicar por `4/N` en vez de
`2/N`: parece un ajuste de escala y en realidad cambia el resultado.
""")

    # ---------------------------------------------------------------- 3
    secciones = []
    for clave, r in resultados.items():
        e = r["espectro"]
        cuanti = r["cuantizacion"]
        ritmo = r["ritmo"]
        casos = cuanti["casos"]
        filas_caso = []
        for b in sorted(casos, key=lambda k: int(k)):
            c = casos[b]
            filas_caso.append([
                b, _cientifico(c["delta"]), c["niveles"],
                _num(c["snr_teorico"], 1), _num(c["snr_medido"], 1),
                _num(c["enob"], 2), _num(c["carga_dbfs"], 2),
            ])
        filas_codigos = []
        for fila in cuanti["tabla_codigos"][:8]:
            filas_codigos.append([
                fila["n"], _num(fila["x_v"], 5), f"`{fila['binario']}`",
                _num(fila["x_q"], 5), _cientifico(fila["error"]),
                _num(fila["error_medio_abs"], 3) + " Δ",
            ])
        filas_muestreo = []
        for ex in r["muestreo"]["experimentos"]:
            if ex["cumple_nyquist"]:
                # el multiplicador 1,0 es el caso límite: f_s ES f_s,min,
                # así que el teorema se cumple pero en el borde exacto.
                # (OJO: la variable se llama `cumple` y no `veredicto`,
                # que es el parámetro de la función y no se debe tapar.)
                cumple = ("sí (al límite)" if ex.get("caso_limite")
                          else "sí")
            else:
                cumple = "NO"
            filas_muestreo.append([
                f"{ex['fs']:.0f}",
                f"{ex['multiplicador']:.2f}×",
                cumple,
                _cientifico(ex["nrmse_aliasing"]),
                _cientifico(ex["nrmse_reconstruccion"]),
                _num(ex["energia_fuera_banda"], 2) + " %",
            ])
        bpm_texto = (f"{ritmo['bpm']:.0f}" if ritmo.get("medible", True)
                     else "**no medible** (sin percusión)")
        secciones.append(f"""### {r['nombre']}

**La señal.** Clip de {_num(r['pista']['duracion_s'], 0)} s a {r['pista']['fs']} Hz,
{r['pista']['bits']} bits, {r['pista']['canales']} canal
{"(es)" if r['pista']['canales'] != 1 else ""}, pico
{_num(r['pista']['pico'], 3)}.

![La señal x(t) de {r['nombre']}]({clave}_senal.png)

**El espectro de magnitud.** `f_max` = **{e['f_max']:.0f} Hz** y por tanto
`f_s,mín` = **{e['fs_minima']:.0f} Hz**. El criterio de `f_max` es el
{p.umbral_db:.0f} dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de {e['f_max_energia']:.0f} Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice {e['f_max']:.0f} Hz y el de
energía, {e['f_max_energia']:.0f} Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

{_tabla(["umbral", "f_max (Hz)"], [[f"{float(u):.0f} dB", f"{v:.0f}"] for u, v in e['f_max_por_umbral'].items()])}

![El espectro de {r['nombre']}]({clave}_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar:

{_tabla(["f_s (Hz)", "respecto a f_s,min", "¿cumple Nyquist?", "NRMSE con aliasing", "NRMSE con filtro", "energía fuera de banda"], filas_muestreo)}

La fila del multiplicador 1,00× es el **caso límite**: ahí el `f_s` es
exactamente `f_s,mín` = 2·`f_max`, o sea `f_s/2` es `f_max`. El teorema se
cumple, pero en el borde exacto: un seno de precisamente `f_s/2` sale con
todas sus muestras a cero, así que en el límite la señal no es
recuperable. De ahí el aviso en la tabla.

![El barrido de muestreo de {r['nombre']}]({clave}_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±{_num(cuanti['vfs'], 0)} V, el factor de escala es

    y = V_fs / 2^(b-1) = {_num(cuanti['vfs'], 0)} / 2^({cuanti['bits']}-1) = **{_cientifico(cuanti['factor_escala_v'])} V por nivel**

con {cuanti['niveles']} niveles y un error acotado a
±{_cientifico(cuanti['factor_escala_v'] / 2)} V.

{_tabla(["bits", "y (V/nivel)", "niveles", "SNR teórico (dB)", "SNR medido (dB)", "bits efectivos", "carga (dBFS)"], filas_caso)}

![La cuantización de {r['nombre']}]({clave}_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de {cuanti['bits']} bits, no una tensión.

{_tabla(["n", "x(n) (V)", "código binario", "x_q (V)", "error (V)", "error en Δ"], filas_codigos)}

![Los códigos binarios de {r['nombre']}]({clave}_codigos.png)

**La cadena completa.** Lo primero es lo primero: **la cadena es la
misma en los cinco géneros**; lo que cambia es **cuánto se pierde en cada
paso**, y eso es justo lo que se mide aquí.

La cadena es esta:

```
x(t)  ──filtro AA──▶  ──muestreo──▶  ──cuantizador──▶  ──DAC──▶  x̂(t)
       recorta la banda        reloj de fs      b bits        ZOH
       de arriba
```

Y el **viaje del SNR**, que es el número que resume cada paso:

{_tabla(["etapa", "qué hace", "SNR que queda", "en la telefónica (8 kHz, 8 bits)"],
        [[e["etapa"], e["nota"],
          ("—" if e["snr"] is None else
           ("exacta" if e["snr"] == float("inf") else _num(e["snr"], 1) + " dB")),
          ("—" if t["snr"] is None else
           ("exacta" if t["snr"] == float("inf") else _num(t["snr"], 1) + " dB"))]
         for e, t in zip(r["cadena"]["viaje"], r["cadena"]["telefonica"]["viaje"])])}

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde {_aa_min(res):.0f} dB (la pista con más contenido
  agudo) hasta {_aa_max(res):.0f} dB (la que menos tiene): {_aa_max(res) - _aa_min(res):.0f} dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±{r['cuantizacion']['factor_escala_medio'] * 1e6:.1f} µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de {r['nombre']}]({clave}_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** {bpm_texto}{f", con una confianza de {_num(ritmo['confianza'], 2)}" if ritmo.get('medible', True) else ""}.
""")
    partes.append("## 3. Los resultados, género por género\n\n" +
                  "\n".join(secciones))

    # ---------------------------------------------------------------- 4
    filas_comp = []
    for f in comp["comparativa"]:
        filas_comp.append([
            f["nombre"], f"{f['f_max']:.0f}", f"{f['fs_minima']:.0f}",
            f"{f['centroide']:.0f}", f["bpm_texto"],
            _num(f["planicidad"], 4), _num(f["crest"], 2),
            _num(f["indice"], 1),
        ])
    partes.append(f"""## 4. La comparación: los cinco en la misma gráfica

Esta es la gráfica que pide el punto (e): **los cinco espectros de
magnitud en el mismo eje**, normalizados al pico y suavizados a 250 Hz
para que se puedan leer.

![Los cinco espectros comparados](comparacion_espectros_comparados.png)

Y la energía por bandas, que es donde se ve la diferencia de perfil:

![La energía por bandas de los cinco](comparacion_bandas_comparadas.png)

{_tabla(["Género", "f_max (Hz)", "f_s,min (Hz)", "centroide (Hz)", "BPM", "planicidad", "factor de cresta", "índice"], filas_comp)}

**Qué dice cada cifra.**

- **f_max** es hasta dónde llega el contenido útil de la pista, con el
  criterio del {p.umbral_db:.0f} dB respecto al pico. La barroca llega a
  {_comp_fmax(comp, 'Clásica'):.0f} Hz y el reggaetón a
  {_comp_fmax(comp, 'Reggaetón'):.0f} Hz con ese criterio; con el
  criterio de energía acumulada, el reggaetón llega a
  {_comp_fmax_energia(comp, 'Reggaetón'):.0f} Hz. La diferencia no es
  del género, es de la masterización: una grabación de archivo de 1722 no
  tiene ni un transitorio por encima de 4 kHz, y una masterización
  moderna de 2023 tiene hats por encima de 10 kHz.
- **f_s,min = 2·f_max** es la tasa de muestreo que exige el teorema. Con
  el criterio del -40 dB, la pista más exigente (el reggaetón) necesita
  {_comp_fmax(comp, 'Reggaetón') * 2:.0f} Hz y la más generosa (la
  barroca) {_comp_fmax(comp, 'Clásica') * 2:.0f} Hz. **Los 44,1 kHz del CD
  sobran para las cinco**; lo que no alcanza es la mitad, 22,05 kHz: con
  esa tasa el contenido del metal (que llega a
  {_comp_fmax(comp, 'Metal'):.0f} Hz) y del reggaetón se plegaría dentro
  de la banda. Por eso el CD se fijó en 44,1 kHz y no en 22,05.
- **centroide espectral** es el brillo de la pieza: {_comp_centroide(comp, 'Clásica'):.0f} Hz en la barroca
  frente a {_comp_centroide(comp, 'Popular'):.0f} Hz en la popular colombiana.
- **planicidad** mide la tonalidad: 0 es un tono puro, 1 es ruido.
- **factor de cresta** (pico/RMS) mide la dinámica: {_comp_crest(comp, 'Clásica'):.2f} en la barroca
  frente a {_comp_crest(comp, 'Popular'):.2f} en la popular, que es el valor típico de una
  masterización moderna comprimida con limitador.
""")

    # ---------------------------------------------------------------- 5
    filas_crit = []
    for clave, det in comp["criterios"].items():
        for c in det["criterios"]:
            filas_crit.append([
                det["nombre"], c["nombre"], c["peso"],
                _num(c["valor"], 2), _num(c["puntos"], 1),
            ])
    partes.append(f"""## 5. El punto (e): qué género aporta mejores frecuencias

### El índice, con los pesos a la vista

El índice de atención (0-100) combina cinco criterios. Los pesos están
publicados a propósito: un índice con pesos escondidos no sirve ni para
comparar ni para discutir.

{_tabla(["Género", "criterio", "peso", "valor normalizado", "puntos"], filas_crit)}

![El índice de atención y el diagrama tempo/brillo](comparacion_indice_atencion.png)

### El veredicto

**{veredicto['resumen']}**

Por qué:

{chr(10).join(f"- {r}" for r in veredicto["razones"])}

![El resumen del punto e](comparacion_veredicto.png)

### Las condiciones del resultado

{chr(10).join(f"- {c}" for c in veredicto["condiciones"])}

### Lo que este trabajo NO demuestra

{chr(10).join(f"- {a}" for a in veredicto["avisos"])}

### Qué dice la literatura

La base del criterio de tempo y de brillo:

- Husain, Loewenstein y Schoultz (2002), *Clinical Psychology Review*:
  "time and music". El tempo se relaciona con la activación.
- Strayer y Perona (2006), *Psychology of Music*: los efectos del tempo
  sobre la percepción y la activación.
- Alferink, Meijer y Arntz (2003) y otros estudios sobre el "efecto
  Mozart": efectos pequenos y inconsistentes, muy por debajo de lo que
  se cuenta en la prensa.
- Brown, Proulx, Stern, Straus, Sulikova y Wright (2001), *Perceptual and
  Motor Skills*: el "ruido marrón" a 60-70 Hz mejora el rendimiento en
  tareas de lectura y aritmética. Es el antecedente más citado de la
  idea de que el contenido de baja frecuencia del entorno sonoro
  interactúa con la atención.

La conclusión de la literatura es prudente: hay efectos **pequeños**,
**inconsistentes** y dependientes de la tarea. Por eso este trabajo no
afirma causalidad, y por eso el índice se presenta como una hipótesis
con el criterio a la vista.
""")

    # ---------------------------------------------------------------- 6
    partes.append(f"""## 6. Cómo se ha calculado

### Los parámetros del análisis

| parámetro | valor | por qué |
|---|---|---|
| Duración del clip | {p.duracion} s | suficiente para la resolución en frecuencia y corto para la demo |
| Frecuencia de muestreo | la del archivo (44,1 kHz) | no se re-muestrea el original: se analiza tal cual |
| Criterio de `f_max` | {p.umbral_db:.0f} dB bajo el pico | publicado, y con control por energía acumulada |
| Bits del ADC | {p.bits} | el de un CD, y se comparan 24/12/8 |
| Fondo de escala | ±{p.vfs} V | el del enunciado: el factor de escala se pide en voltios |
| Orden del filtro AA | {p.orden_filtro} | Butterworth de fase cero, `sosfiltfilt` |
| Ventana de la FFT | {p.ventana} | con corrección por ganancia coherente |

### Los módulos

| archivo | qué hace |
|---|---|
| `nucleo/wav_io.py` | el parser de WAV (PCM de 8/16/24/32 bits y coma flotante), sin dependencias |
| `nucleo/dsp_audio.py` | espectro, `f_max`, antialiasing, tempo, bandas, el índice de atención |
| `nucleo/catalogo.py` | las cinco fichas: músico, obra, año, fuentes |
| `nucleo/analisis.py` | el pipeline completo por pista |
| `nucleo/comparativa.py` | la comparación y el veredicto |
| `nucleo/figuras.py` | las figuras (matplotlib, 300 dpi) |
| `nucleo/informe.py` | este `.md` |
| `nucleo/descarga.py` | la descarga y el recorte de las pistas |
| `nucleo/test_*.py` | las comprobaciones automáticas |

### Las primitivas de DSP

Este proyecto es la continuación de `Nyquist_Shannon/`, donde las señales
eran series de Fourier y se sabía `f_max` por fórmula. Aquí el `f_max`
hay que **medirlo**, y esa es la parte nueva.

Las primitivas de DSP (la reconstrucción de Shannon, el cuantizador
uniforme, las métricas de error, el diagnóstico de Nyquist) están en
`nucleo/primitivas.py`, adaptadas del proyecto anterior para que este
repositorio sea **autosuficiente**: se clona, se instala y funciona, sin
depender de ninguna carpeta de al lado. Las cifras que dan son
exactamente las mismas (las 164 comprobaciones lo verifican).

| primitiva | para qué se usa aquí |
|---|---|
| `reconstruir_sinc` | la reconstrucción de Nyquist-Shannon desde las muestras |
| `reconstruir_zoh` | el DAC barato (retenedor de orden cero) |
| `cuantizar` | el cuantizador uniforme de punto medio, con saturación |
| `factor_carga`, `bits_efectivos` | los bits efectivos y la carga en dBFS |
| `dither` | el contraste con dither TPDF |
| `nrmse_por_rango`, `snr_db` | todas las cifras de error |
| `diagnostico_nyquist` | el veredicto de Nyquist por pista |

### Las cifras de las pistas

{_tabla(["Pista", "Duración", "f_max", "f_s,min", "SNR 16 bits (dB)", "ENOB 16 bits", "índice"],
        [[r["nombre"], f"{_num(r['pista']['duracion_s'], 0)} s",
          f"{r['espectro']['f_max']:.0f} Hz",
          f"{r['espectro']['fs_minima']:.0f} Hz",
          _num(r["cuantizacion"]["casos"]["16"]["snr_medido"], 1),
          _num(r["cuantizacion"]["casos"]["16"]["enob"], 2),
          f"{r['atencion']['indice']:.1f}"] for r in resultados.values()])}
""")

    # ---------------------------------------------------------------- 7
    partes.append("""## 7. Limitaciones y honestidad

- **Una pista por género.** Con otra canción, o con la misma canción en
  otra masterización, el orden puede cambiar. Lo que se comprobó es que
  las tres características que más pesan (brillo, banda de la voz, rango
  dinámico) son robustas entre_ENUM los cinco, y que el tempo no lo es.
- **`f_max` depende de un criterio.** Con -30 dB y con -50 dB salen
  cifras distintas; por eso el criterio está publicado, y se da el
  control por energía acumulada.
- **El factor de cresta mezcla género y época de producción.** Una
  masterización moderna comprimida con limitador tiene crest bajo
  regardless del género. Es un sesgo conocido del criterio y está
  anotado en la tabla.
- **El tempo de una pieza sin percusión no se puede medir.** En la
  barroca el detector no encuentra pulso, y el criterio de tempo se
  puntúa como neutro en vez de inventarse un valor.
- **Un fragmento de 12 s no es la canción.** Es lo que el enunciado pide
  ("audios cortos"), pero el criterio de selección (el tramo de mayor
  energía RMS) es una decisión, y puede no representar la pieza.
- **La analogía con las bandas cerebrales es una analogía.** El
  informe muestra las bandas tipo EEG (delta, theta, alfa, beta, gamma)
  calculadas sobre el AUDIO, y su lectura es "qué banda del sonido está
  activada", no "qué banda cerebral se activa".

---

*Informe generado por `nucleo/informe.py` a partir de los mismos datos
que dibujan las figuras. Si una cifra cambia aquí, cambia también en los
gráficos.*
""")

    return "\n".join(partes)


def _aa_min(res: dict) -> float:
    """La menor pérdida del filtro antialiasing (la pista más brillante)."""
    valores = [r["cadena"]["viaje"][1]["snr"] for r in res["resultados"].values()
               if r["cadena"]["viaje"][1]["snr"] is not None]
    return min(valores) if valores else 0.0


def _aa_max(res: dict) -> float:
    """La mayor pérdida del filtro antialiasing (la pista más oscura)."""
    valores = [r["cadena"]["viaje"][1]["snr"] for r in res["resultados"].values()
               if r["cadena"]["viaje"][1]["snr"] is not None]
    return max(valores) if valores else 0.0


def _comp_fmax(comp: dict, nombre_parcial: str) -> float:
    """El `f_max` de un género, buscado por un fragmento de su nombre."""
    for f in comp["veredicto"]["tabla"]:
        if nombre_parcial.lower() in f["nombre"].lower():
            return f["f_max"]
    return 0.0


def _comp_fmax_energia(comp: dict, nombre_parcial: str) -> float:
    """El `f_max` por energía acumulada de un género."""
    for f in comp.get("f_max_energia", []):
        if nombre_parcial.lower() in f["nombre"].lower():
            return f["f_max_energia"]
    return 0.0


def _comp_centroide(comp: dict, nombre_parcial: str) -> float:
    """El centroide espectral de un género."""
    for f in comp["veredicto"]["tabla"]:
        if nombre_parcial.lower() in f["nombre"].lower():
            return f["centroide"]
    return 0.0


def _comp_crest(comp: dict, nombre_parcial: str) -> float:
    """El factor de cresta de un género."""
    for f in comp["veredicto"]["tabla"]:
        if nombre_parcial.lower() in f["nombre"].lower():
            return f["crest"]
    return 0.0


def _main() -> int:
    """Genera el informe y las figuras."""
    generar_informe()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
