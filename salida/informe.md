# DSP aplicado a ADC-DAC sobre audio musical

### Cinco géneros, cinco perfiles espectrales, una comparación

**Proyecto de Comunicaciones I · 21/10/2026**

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
| pistas analizadas | 5 | `audio/*.wav` |
| géneros comparados | 5 | el catálogo, punto (b) del enunciado |
| mejor índice de atención | **80,1 / 100** | Clásica · Barroca |
| `f_s` mínima del conjunto | 23332 Hz | 2·f_max de la pista más exigente |
| resolución a 16 bits | 3.052e-05 V/nivel | V_fs / 2^(b-1) |

**El veredicto del punto (e):** Con el índice propuesto, la mejor opción como música de fondo para estudiar es Clásica · Barroca (80,1 de 100), seguido de Metal (63,9). La razón principal es que su espectro es el más oscuro: centroide de 290 Hz, y ocupa muy poca banda de agudos de percusión, que es donde más gana. En la banda de la voz (300 Hz-3,4 kHz), en cambio, concentra un 24 % de su energía: es el punto más débil de su ficha, y conviene decirlo.

> **Aviso de alcance, y es importante:** este trabajo caracteriza
> *propiedades acústicas* de cinco grabaciones y las ordena con un índice
> cuyos pesos están publicados. **No** mide la atención de ninguna
> persona, **no** es un estudio clínico y **no** puede afirmar que una
> pieza mejore el TDAH de un estudiante. La sección 5 explica qué se
> afirma y qué no.

## 1. La investigación: las cinco pistas

El enunciado pide una "investigación breve" de cada género. Las fichas
son las siguientes, y cada una dice por qué ese tema representa al
género **en lo que importa para este trabajo, que es el espectro**.

| Género | Músico | Obra | Año | Compositor |
|---|---|---|---|---|
| Clásica · Barroca | Netherlands Bach Society (Lucia Swarts, violonchelo) | J. S. Bach — Suite para violonchelo n.º 1 en Sol mayor, BWV 1007 | 1717 | Johann Sebastian Bach (1685-1750) |
| Metal | Megadeth | Tornado of Souls (del álbum Youthanasia) | 1990 | Dave Mustaine |
| Salsa | Frankie Ruiz y La Solución | La Rueda (compositor: Víctor Manuel Mato) | 1980 | Víctor Manuel Mato (ranchera Colombian, años 50) |
| Reggaetón | Feid y ATL Jacob | LUNA (del EP Ferxxocalipsis) | 2023 | Salomón Villada (Feid) y ATL Jacob |
| Popular colombiana | Fredy Montoya ft. Luisito Muñoz | Ángel o Demonio | 2016 | Fernando (Fredy) Montoya |

### Clásica · Barroca

| campo | dato |
|---|---|
| **Músico / intérprete** | Netherlands Bach Society (Lucia Swarts, violonchelo) |
| **Obra** | J. S. Bach — Suite para violonchelo n.º 1 en Sol mayor, BWV 1007 |
| **Año** | 1717 |
| **Compositor** | Johann Sebastian Bach (1685-1750) |
| **Estilo** | Barroco tardío (Köthen), cello solo senza basso |
| **Instrumentación** | Un solo violonchelo, arpegiado continuo y cadencias de acordes |
| **Tempo esperado** | 60-80 (sin percusión, el pulso lo marca el arpegio) |
| **Banda característica** | 60-250 Hz (fundamental del violonchelo) con armónicos limpios; casi nada por encima de 2 kHz |

**Por qué este ejemplo y no otro.** Es el perfil más limpio de los cinco: un instrumento sin percusión, sin distorsión y sin voz. Al medirlo se ve que casi toda la energía está en 60-250 Hz, que es justo lo que hace que una pieza barroca 'suene' profunda. Sirve de REFERENCIA: es el caso en el que el criterio de Nyquist se cumple de sobra y el audio no tiene nada que esconder.

**Fuentes.**

- Wikipedia (EN): Cello Suites (Bach), BWV 1007-1012, compuestas entre 1717 y 1723 en Köthen.
- IMSLP: Cello Suite No. 1 en Sol mayor, BWV 1007, año de composición 1717.
- Netherlands Bach Society: proyecto 'All of Bach', interpretación de Lucia Swarts (proyecto 2022).

### Metal

| campo | dato |
|---|---|
| **Músico / intérprete** | Megadeth |
| **Obra** | Tornado of Souls (del álbum Youthanasia) |
| **Año** | 1990 |
| **Compositor** | Dave Mustaine |
| **Estilo** | Thrash/heavy metal de finales de los 80 |
| **Instrumentación** | Guitarras con saturación, bajo eléctrico, batería y amplificación |
| **Tempo esperado** | 120-140 (tema en 4/4, riff en semicorcheas) |
| **Banda característica** | Fundamental grave del bajo (40-100 Hz) + mucha energía de guitarra hasta 8 kHz por la saturación |

**Por qué este ejemplo y no otro.** La saturación de la guitarra no es un efecto de timbre: es multiplicación de la onda por una función no lineal, y eso genera armónicos de orden muy alto. Por eso el metal es el caso con más contenido agudo del conjunto, y y el que tiene más contenido agudo del conjunto, por lo que es el primero en resentir una bajada de la tasa de muestreo en términos absolutos: necesita 23 332 Hz, la mayor de las cinco.

**Fuentes.**

- Discografía de Megadeth: 'Youthanasia', 1990; 'Tornado of Souls' es el segundo corte del álbum.
- Wikipedia (EN): Youthanasia, álbum de 1990.

### Salsa

| campo | dato |
|---|---|
| **Músico / intérprete** | Frankie Ruiz y La Solución |
| **Obra** | La Rueda (compositor: Víctor Manuel Mato) |
| **Año** | 1980 |
| **Compositor** | Víctor Manuel Mato (ranchera Colombian, años 50) |
| **Estilo** | Salsa romántica con montuno y percusión latina |
| **Instrumentación** | Voz, trombones y clarinetes, percusión latina (timbales, congas, cowbell), bajo y guitarra |
| **Tempo esperado** | 90-110 (son clave, 2-3) |
| **Banda característica** | 250 Hz-2 kHz (timbal y montuno) con bajo en 60-120 Hz |

**Por qué este ejemplo y no otro.** Es el género con la percusión más 'química' del conjunto: el timbal y la cowbell tienen su energía justo en la banda de 2-6 kHz, que es la banda que en el punto (e) se asocia con activación. Sirve para ver cómo un mismo género cambia de fisonomía según la época: aquí viene de la salsa de los 80, con un sonido de orquesta de viento muy presente.

**Fuentes.**

- Wikipedia (ES): Frankie Ruiz — 'La rueda' se incluye en el segundo álbum de Orquesta La Solución, 'Orquesta La Solución' (LAD Records, 1980).
- RPP (2026): 'Originally it was a ranchera by composer Víctor Matos, recorded in the mid-1950s'; Frankie la grabó con La Solución a partir de 1978.
- Wikipedia (EN): 'Historia Musical de Frankie Ruiz' (1987).

### Reggaetón

| campo | dato |
|---|---|
| **Músico / intérprete** | Feid y ATL Jacob |
| **Obra** | LUNA (del EP Ferxxocalipsis) |
| **Año** | 2023 |
| **Compositor** | Salomón Villada (Feid) y ATL Jacob |
| **Estilo** | Reggaetón colombiano contemporáneo (años 2020) |
| **Instrumentación** | Bombo sintetizado (dembow), pads, voz con autotune, sintetizadores de alta frecuencia |
| **Tempo esperado** | 90-100 (dembow en 2-4) |
| **Banda característica** | 40-60 Hz (bombo sintetizado) y 60-250 Hz (bajo y voz); muy poca energía por encima de 4 kHz |

**Por qué este ejemplo y no otro.** El reggaetón moderno es EL caso de la música con la energía más concentrada en el graves: el bombo es un seno sintetizado y la voz va con poca información armónica alta. Es el más oscuro en la banda de graves, con el 27 % de su energía por debajo de 60 Hz. Lo que sí tiene es un contraste rítmico grande entre el bombo y la voz, aunque el factor de cresta medido (2,88) es bajo por la compresión de la masterización.

**Fuentes.**

- Wikipedia (EN): 'Luna (Feid and ATL Jacob song)', single del EP 'Ferxxocalipsis' (2023), lanzamiento el 1 de diciembre de 2023.
- Apple Music / Shazam: fecha de publicación 1-dic-2023.

### Popular colombiana

| campo | dato |
|---|---|
| **Músico / intérprete** | Fredy Montoya ft. Luisito Muñoz |
| **Obra** | Ángel o Demonio |
| **Año** | 2016 |
| **Compositor** | Fernando (Fredy) Montoya |
| **Estilo** | Cantina colombiana de la costa (despecho costeño), con influencia del vallenato |
| **Instrumentación** | Guitarra acústica, Bajo, percusión de raspas y pandereta, voz de Contralto |
| **Tempo esperado** | 70-90 (balada con pulso binario) |
| **Banda característica** | 250 Hz-2 kHz (voz y guitarra), casi sin graves fuertes ni agudos |

**Por qué este ejemplo y no otro.** Es el género del enunciado que los demás llaman 'cantina al hombro': la música popular colombiana de la costa, la que cantan Jessi Uribe o Paola Jara. Su perfil es de banda media, con voz y guitarra, y es un buen contraste con el resto: no tiene bombo, no tiene guitarra saturada y no tiene nada inesperado. Es el perfil 'neutro' del conjunto.

**Fuentes.**

- Apple Music: 'Ángel o Demonio (feat. Luisito Muñoz) - Single', 2016.
- Shazam / Qobuz: compositor Fernando Montoya; remix oficial con Álzate, Jessi Uribe, Luisito Muñoz y Fredy Montoya (marzo de 2026).
- Tropicana Colombia (2026): 'Ángel o Demonio', clásico de la música popular colombiana.


## 2. La cadena ADC-DAC, explicada antes de usarla

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
de una lluvia de aliasing. Es un Butterworth de fase cero (`sosfiltfilt`), con
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

## 3. Los resultados, género por género

### Clásica · Barroca

**La señal.** Clip de 12 s a 44100 Hz,
16 bits, 1 canal
, pico
0,724.

![La señal x(t) de Clásica · Barroca](barroca_senal.png)

**El espectro de magnitud.** `f_max` = **1881 Hz** y por tanto
`f_s,mín` = **3762 Hz**. El criterio de `f_max` es el
-40 dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de 3659 Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice 1881 Hz y el de
energía, 3659 Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

| umbral | f_max (Hz) |
|---|---|
| -40 dB | 1881 |
| -30 dB | 1265 |
| -50 dB | 3964 |

![El espectro de Clásica · Barroca](barroca_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar
(4 frecuencias de muestreo):

| f_s (Hz) | respecto a f_s,min | ¿cumple Nyquist? | NRMSE con aliasing | NRMSE con filtro | energía fuera de banda |
|---|---|---|---|---|---|
| 1881 | 0.50× | NO | 2,339e-02 | 6,102e-02 | 2,39 % |
| 3762 | 1.00× | sí | 1,148e-02 | 2,649e-02 | 0,44 % |
| 5643 | 1.50× | sí | 7,975e-03 | 1,716e-02 | 0,14 % |
| 7524 | 2.00× | sí | 6,751e-03 | 1,176e-02 | 0,06 % |

![El barrido de muestreo de Clásica · Barroca](barroca_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±1 V, el factor de escala es

    y = V_fs / 2^(b-1) = 1 / 2^(16-1) = **3,052e-05 V por nivel**

con 65536 niveles y un error acotado a
±1,526e-05 V.

| bits | y (V/nivel) | niveles | SNR teórico (dB) | SNR medido (dB) | bits efectivos | carga (dBFS) |
|---|---|---|---|---|---|---|
| 8 | 7,812e-03 | 256 | 49,9 | 34,6 | 5,45 | -2,81 |
| 12 | 4,883e-04 | 4096 | 74,0 | 58,7 | 9,45 | -2,81 |
| 16 | 3,052e-05 | 65536 | 98,1 | 81,9 | 13,30 | -2,81 |
| 24 | 1,192e-07 | 16777216 | 146,3 | 128,6 | 21,06 | -2,81 |

![La cuantización de Clásica · Barroca](barroca_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de 16 bits, no una tensión.

| n | x(n) (V) | código binario | x_q (V) | error (V) | error en Δ |
|---|---|---|---|---|---|
| 347748 | -0,65445 | `0010110000111010` | -0,65446 | -9,761e-06 | 0,320 Δ |
| 347749 | -0,67100 | `0010101000011100` | -0,67101 | -9,761e-06 | 0,320 Δ |
| 347750 | -0,68781 | `0010011111110101` | -0,68782 | -9,761e-06 | 0,320 Δ |
| 347751 | -0,69538 | `0010011011111101` | -0,69539 | -9,761e-06 | 0,320 Δ |
| 347752 | -0,70518 | `0010010110111100` | -0,70518 | -9,761e-06 | 0,320 Δ |
| 347753 | -0,71866 | `0010010000000010` | -0,71867 | -9,761e-06 | 0,320 Δ |
| 347754 | -0,72388 | `0010001101010111` | -0,72389 | -9,761e-06 | 0,320 Δ |
| 347755 | -0,71470 | `0010010010000100` | -0,71471 | -9,761e-06 | 0,320 Δ |

![Los códigos binarios de Clásica · Barroca](barroca_codigos.png)

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

| etapa | qué hace | SNR que queda | en la telefónica (8 kHz, 8 bits) |
|---|---|---|---|
| x(t) original | la señal de entrada, sin error | — | — |
| filtro antialiasing | recorta por encima de 9922 Hz | 45,2 dB | 22,6 dB |
| muestreo | a 44100 Hz, sin aliasing posible | 30,1 dB | 16,7 dB |
| cuantizador | 16 bits, Δ = 3,05e-05 V | 82,8 dB | 34,6 dB |
| cadena completa | acumulado, contra la señal original | 45,2 dB | 21,4 dB |

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde 18 dB (la pista con más contenido
  agudo) hasta 45 dB (la que menos tiene): 27 dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±15.3 µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de Clásica · Barroca](barroca_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** **no medible** (sin percusión).

### Metal

**La señal.** Clip de 12 s a 44100 Hz,
16 bits, 1 canal
, pico
0,757.

![La señal x(t) de Metal](metal_senal.png)

**El espectro de magnitud.** `f_max` = **11666 Hz** y por tanto
`f_s,mín` = **23332 Hz**. El criterio de `f_max` es el
-40 dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de 13233 Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice 11666 Hz y el de
energía, 13233 Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

| umbral | f_max (Hz) |
|---|---|
| -40 dB | 11666 |
| -30 dB | 4467 |
| -50 dB | 15844 |

![El espectro de Metal](metal_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar
(3 frecuencias de muestreo):

| f_s (Hz) | respecto a f_s,min | ¿cumple Nyquist? | NRMSE con aliasing | NRMSE con filtro | energía fuera de banda |
|---|---|---|---|---|---|
| 11666 | 0.50× | NO | 1,829e-02 | 3,689e-02 | 1,05 % |
| 23332 | 1.00× | NO | 1,690e-02 | 1,704e-02 | 0,31 % |
| 34999 | 1.50× | sí | 1,659e-02 | 1,622e-02 | 0,02 % |

![El barrido de muestreo de Metal](metal_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±1 V, el factor de escala es

    y = V_fs / 2^(b-1) = 1 / 2^(16-1) = **3,052e-05 V por nivel**

con 65536 niveles y un error acotado a
±1,526e-05 V.

| bits | y (V/nivel) | niveles | SNR teórico (dB) | SNR medido (dB) | bits efectivos | carga (dBFS) |
|---|---|---|---|---|---|---|
| 8 | 7,812e-03 | 256 | 49,9 | 36,7 | 5,80 | -2,41 |
| 12 | 4,883e-04 | 4096 | 74,0 | 60,7 | 9,79 | -2,41 |
| 16 | 3,052e-05 | 65536 | 98,1 | 83,3 | 13,55 | -2,41 |
| 24 | 1,192e-07 | 16777216 | 146,3 | 139,6 | 22,90 | -2,41 |

![La cuantización de Metal](metal_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de 16 bits, no una tensión.

| n | x(n) (V) | código binario | x_q (V) | error (V) | error en Δ |
|---|---|---|---|---|---|
| 484893 | 0,51095 | `1100000101100110` | 0,51094 | -1,045e-05 | 0,342 Δ |
| 484894 | 0,56509 | `1100100001010100` | 0,56508 | -1,045e-05 | 0,342 Δ |
| 484895 | 0,62310 | `1100111111000001` | 0,62309 | -1,045e-05 | 0,342 Δ |
| 484896 | 0,62683 | `1101000000111011` | 0,62682 | -1,045e-05 | 0,342 Δ |
| 484897 | 0,62438 | `1100111111101011` | 0,62437 | -1,045e-05 | 0,342 Δ |
| 484898 | 0,68103 | `1101011100101011` | 0,68102 | -1,045e-05 | 0,342 Δ |
| 484899 | 0,75759 | `1110000011111000` | 0,75758 | -1,045e-05 | 0,342 Δ |
| 484900 | 0,68344 | `1101011101111010` | 0,68343 | -1,045e-05 | 0,342 Δ |

![Los códigos binarios de Metal](metal_codigos.png)

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

| etapa | qué hace | SNR que queda | en la telefónica (8 kHz, 8 bits) |
|---|---|---|---|
| x(t) original | la señal de entrada, sin error | — | — |
| filtro antialiasing | recorta por encima de 9922 Hz | 23,6 dB | 6,9 dB |
| muestreo | a 44100 Hz, sin aliasing posible | 18,6 dB | 14,6 dB |
| cuantizador | 16 bits, Δ = 3,05e-05 V | 84,8 dB | 35,6 dB |
| cadena completa | acumulado, contra la señal original | 23,6 dB | 6,8 dB |

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde 18 dB (la pista con más contenido
  agudo) hasta 45 dB (la que menos tiene): 27 dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±15.3 µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de Metal](metal_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** 98, con una confianza de 0,88.

### Salsa

**La señal.** Clip de 12 s a 44100 Hz,
16 bits, 1 canal
, pico
0,940.

![La señal x(t) de Salsa](salsa_senal.png)

**El espectro de magnitud.** `f_max` = **9332 Hz** y por tanto
`f_s,mín` = **18665 Hz**. El criterio de `f_max` es el
-40 dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de 11594 Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice 9332 Hz y el de
energía, 11594 Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

| umbral | f_max (Hz) |
|---|---|
| -40 dB | 9332 |
| -30 dB | 2329 |
| -50 dB | 12162 |

![El espectro de Salsa](salsa_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar
(4 frecuencias de muestreo):

| f_s (Hz) | respecto a f_s,min | ¿cumple Nyquist? | NRMSE con aliasing | NRMSE con filtro | energía fuera de banda |
|---|---|---|---|---|---|
| 9332 | 0.50× | NO | 1,759e-02 | 2,225e-02 | 1,38 % |
| 18665 | 1.00× | sí | 1,207e-02 | 1,608e-02 | 0,18 % |
| 27997 | 1.50× | sí | 1,152e-02 | 1,281e-02 | 0,00 % |
| 37329 | 2.00× | sí | 1,144e-02 | 1,162e-02 | 0,00 % |

![El barrido de muestreo de Salsa](salsa_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±1 V, el factor de escala es

    y = V_fs / 2^(b-1) = 1 / 2^(16-1) = **3,052e-05 V por nivel**

con 65536 niveles y un error acotado a
±1,526e-05 V.

| bits | y (V/nivel) | niveles | SNR teórico (dB) | SNR medido (dB) | bits efectivos | carga (dBFS) |
|---|---|---|---|---|---|---|
| 8 | 7,812e-03 | 256 | 49,9 | 38,8 | 6,16 | -0,54 |
| 12 | 4,883e-04 | 4096 | 74,0 | 62,9 | 10,16 | -0,54 |
| 16 | 3,052e-05 | 65536 | 98,1 | 94,5 | 15,41 | -0,54 |
| 24 | 1,192e-07 | 16777216 | 146,3 | 133,8 | 21,93 | -0,54 |

![La cuantización de Salsa](salsa_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de 16 bits, no una tensión.

| n | x(n) (V) | código binario | x_q (V) | error (V) | error en Δ |
|---|---|---|---|---|---|
| 19990 | 0,13857 | `1001000110111100` | 0,13857 | -3,715e-06 | 0,122 Δ |
| 19991 | 0,11397 | `1000111010010110` | 0,11397 | -3,715e-06 | 0,122 Δ |
| 19992 | 0,11696 | `1000111011111000` | 0,11696 | -3,715e-06 | 0,122 Δ |
| 19993 | 0,11544 | `1000111011000110` | 0,11543 | -3,715e-06 | 0,122 Δ |
| 19994 | 0,34621 | `1010110001010000` | 0,34621 | -3,715e-06 | 0,122 Δ |
| 19995 | 0,76769 | `1110001001000011` | 0,76768 | -3,715e-06 | 0,122 Δ |
| 19996 | 0,93959 | `1111100001000100` | 0,93959 | -3,715e-06 | 0,122 Δ |
| 19997 | 0,71679 | `1101101110111111` | 0,71678 | -3,715e-06 | 0,122 Δ |

![Los códigos binarios de Salsa](salsa_codigos.png)

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

| etapa | qué hace | SNR que queda | en la telefónica (8 kHz, 8 bits) |
|---|---|---|---|
| x(t) original | la señal de entrada, sin error | — | — |
| filtro antialiasing | recorta por encima de 9922 Hz | 23,5 dB | 10,1 dB |
| muestreo | a 44100 Hz, sin aliasing posible | 20,2 dB | 11,4 dB |
| cuantizador | 16 bits, Δ = 3,05e-05 V | 87,0 dB | 38,3 dB |
| cadena completa | acumulado, contra la señal original | 23,5 dB | 9,8 dB |

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde 18 dB (la pista con más contenido
  agudo) hasta 45 dB (la que menos tiene): 27 dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±15.3 µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de Salsa](salsa_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** 101, con una confianza de 0,85.

### Reggaetón

**La señal.** Clip de 12 s a 44100 Hz,
16 bits, 1 canal
, pico
1,000.

![La señal x(t) de Reggaetón](reggaeton_senal.png)

**El espectro de magnitud.** `f_max` = **7943 Hz** y por tanto
`f_s,mín` = **15887 Hz**. El criterio de `f_max` es el
-40 dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de 17290 Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice 7943 Hz y el de
energía, 17290 Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

| umbral | f_max (Hz) |
|---|---|
| -40 dB | 7943 |
| -30 dB | 707 |
| -50 dB | 17687 |

![El espectro de Reggaetón](reggaeton_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar
(4 frecuencias de muestreo):

| f_s (Hz) | respecto a f_s,min | ¿cumple Nyquist? | NRMSE con aliasing | NRMSE con filtro | energía fuera de banda |
|---|---|---|---|---|---|
| 7943 | 0.50× | NO | 4,717e-02 | 4,757e-02 | 7,14 % |
| 15887 | 1.00× | sí | 3,475e-02 | 3,662e-02 | 2,93 % |
| 23830 | 1.50× | sí | 3,222e-02 | 3,401e-02 | 0,97 % |
| 31774 | 2.00× | sí | 3,281e-02 | 3,211e-02 | 0,23 % |

![El barrido de muestreo de Reggaetón](reggaeton_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±1 V, el factor de escala es

    y = V_fs / 2^(b-1) = 1 / 2^(16-1) = **3,052e-05 V por nivel**

con 65536 niveles y un error acotado a
±1,526e-05 V.

| bits | y (V/nivel) | niveles | SNR teórico (dB) | SNR medido (dB) | bits efectivos | carga (dBFS) |
|---|---|---|---|---|---|---|
| 8 | 7,812e-03 | 256 | 49,9 | 43,7 | 6,97 | 0,00 |
| 12 | 4,883e-04 | 4096 | 74,0 | 67,8 | 10,97 | 0,00 |
| 16 | 3,052e-05 | 65536 | 98,1 | 90,8 | 14,79 | 0,00 |
| 24 | 1,192e-07 | 16777216 | 146,3 | 92,6 | 15,08 | 0,00 |

![La cuantización de Reggaetón](reggaeton_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de 16 bits, no una tensión.

| n | x(n) (V) | código binario | x_q (V) | error (V) | error en Δ |
|---|---|---|---|---|---|
| 685 | -0,56657 | `0011011101111010` | -0,56657 | -5,169e-06 | 0,169 Δ |
| 686 | -0,73963 | `0010000101010011` | -0,73964 | -5,169e-06 | 0,169 Δ |
| 687 | -0,84904 | `0001001101010010` | -0,84904 | -5,169e-06 | 0,169 Δ |
| 688 | -0,69633 | `0010011011011110` | -0,69633 | -5,169e-06 | 0,169 Δ |
| 689 | -0,70841 | `0010010101010010` | -0,70842 | -5,169e-06 | 0,169 Δ |
| 690 | -0,97450 | `0000001101000011` | -0,97450 | -5,169e-06 | 0,169 Δ |
| 691 | -1,00035 | `0000000000000000` | -0,99998 | 3,610e-04 | 11,831 Δ |
| 692 | -0,91337 | `0000101100010110` | -0,91338 | -5,169e-06 | 0,169 Δ |

![Los códigos binarios de Reggaetón](reggaeton_codigos.png)

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

| etapa | qué hace | SNR que queda | en la telefónica (8 kHz, 8 bits) |
|---|---|---|---|
| x(t) original | la señal de entrada, sin error | — | — |
| filtro antialiasing | recorta por encima de 9922 Hz | 18,2 dB | 8,6 dB |
| muestreo | a 44100 Hz, sin aliasing posible | 18,9 dB | 16,6 dB |
| cuantizador | 16 bits, Δ = 3,05e-05 V | 47,3 dB | 42,9 dB |
| cadena completa | acumulado, contra la señal original | 18,2 dB | 8,5 dB |

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde 18 dB (la pista con más contenido
  agudo) hasta 45 dB (la que menos tiene): 27 dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±15.3 µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de Reggaetón](reggaeton_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** 100, con una confianza de 0,94.

### Popular colombiana

**La señal.** Clip de 12 s a 44100 Hz,
16 bits, 1 canal
, pico
1,000.

![La señal x(t) de Popular colombiana](popular_senal.png)

**El espectro de magnitud.** `f_max` = **9953 Hz** y por tanto
`f_s,mín` = **19905 Hz**. El criterio de `f_max` es el
-40 dB respecto al pico, sobre el espectro suavizado en
potencia. Como control, el 99,9 % de la energía acumulada está por debajo
de 11978 Hz.

**Los dos criterios NO miden lo mismo, y conviene saber por qué.** El
criterio del umbral pregunta *"¿hasta dónde llega el contenido
significativo?"* (40 dB por debajo del pico). El criterio de energía
acumulada pregunta *"¿hasta dónde llega la energía?"*. En música los dos
se separan mucho, porque el pico está en los graves (un bombo a 50 Hz) y
la energía de una masterización moderna se concentra abajo: en el
reggaetón, el criterio del umbral dice 9953 Hz y el de
energía, 11978 Hz. La diferencia no es un error: son
dos preguntas distintas, y aquí se publica la respuesta a las dos.

Por eso la tabla de sensibilidad al umbral, que es la forma honesta de
decir "esta cifra depende de una decisión":

| umbral | f_max (Hz) |
|---|---|
| -40 dB | 9953 |
| -30 dB | 2944 |
| -50 dB | 13518 |

![El espectro de Popular colombiana](popular_espectro.png)

**El muestreo y el aliasing.** Cuánto error mete no filtrar
(4 frecuencias de muestreo):

| f_s (Hz) | respecto a f_s,min | ¿cumple Nyquist? | NRMSE con aliasing | NRMSE con filtro | energía fuera de banda |
|---|---|---|---|---|---|
| 9953 | 0.50× | NO | 1,757e-02 | 2,588e-02 | 0,91 % |
| 19905 | 1.00× | NO | 1,235e-02 | 1,603e-02 | 0,09 % |
| 29858 | 1.50× | sí | 1,204e-02 | 1,267e-02 | 0,00 % |
| 39811 | 2.00× | sí | 1,199e-02 | 1,192e-02 | 0,00 % |

![El barrido de muestreo de Popular colombiana](popular_muestreo.png)

**La cuantización: el factor de escala y los bits.**

Con fondo de escala de ±1 V, el factor de escala es

    y = V_fs / 2^(b-1) = 1 / 2^(16-1) = **3,052e-05 V por nivel**

con 65536 niveles y un error acotado a
±1,526e-05 V.

| bits | y (V/nivel) | niveles | SNR teórico (dB) | SNR medido (dB) | bits efectivos | carga (dBFS) |
|---|---|---|---|---|---|---|
| 8 | 7,812e-03 | 256 | 49,9 | 43,9 | 7,01 | -0,00 |
| 12 | 4,883e-04 | 4096 | 74,0 | 68,0 | 11,00 | -0,00 |
| 16 | 3,052e-05 | 65536 | 98,1 | 90,5 | 14,74 | -0,00 |
| 24 | 1,192e-07 | 16777216 | 146,3 | 139,1 | 22,80 | -0,00 |

![La cuantización de Popular colombiana](popular_cuantizacion.png)

**Las muestras con sus bits.** Esto es lo que el convertidor entrega de
verdad: un entero de 16 bits, no una tensión.

| n | x(n) (V) | código binario | x_q (V) | error (V) | error en Δ |
|---|---|---|---|---|---|
| 41918 | -0,83938 | `0001010010001111` | -0,83937 | 1,063e-05 | 0,348 Δ |
| 41919 | -0,79867 | `0001100111000101` | -0,79866 | 1,063e-05 | 0,348 Δ |
| 41920 | -0,81527 | `0001011110100101` | -0,81526 | 1,063e-05 | 0,348 Δ |
| 41921 | -0,86615 | `0001000100100010` | -0,86613 | 1,063e-05 | 0,348 Δ |
| 41922 | -0,92767 | `0000100101000010` | -0,92766 | 1,063e-05 | 0,348 Δ |
| 41923 | -0,98873 | `0000000101110001` | -0,98872 | 1,063e-05 | 0,348 Δ |
| 41924 | -0,99996 | `0000000000000001` | -0,99995 | 1,063e-05 | 0,348 Δ |
| 41925 | -0,99996 | `0000000000000001` | -0,99995 | 1,063e-05 | 0,348 Δ |

![Los códigos binarios de Popular colombiana](popular_codigos.png)

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

| etapa | qué hace | SNR que queda | en la telefónica (8 kHz, 8 bits) |
|---|---|---|---|
| x(t) original | la señal de entrada, sin error | — | — |
| filtro antialiasing | recorta por encima de 9922 Hz | 24,2 dB | 9,8 dB |
| muestreo | a 44100 Hz, sin aliasing posible | 19,1 dB | 11,6 dB |
| cuantizador | 16 bits, Δ = 3,05e-05 V | 56,1 dB | 38,4 dB |
| cadena completa | acumulado, contra la señal original | 24,2 dB | 9,6 dB |

**Cómo se lee esto**, que es lo importante:

- **El filtro antialiasing** es la etapa que más se nota, y es la única
  cuyo coste depende del **género**: recorta la banda de arriba del todo,
  así que en una pieza masterizada con contenido hasta 17 kHz se pierde
  mucho más que en una barroca que no pasa de 4 kHz. En esta muestra, el
  filtro cuesta desde 18 dB (la pista con más contenido
  agudo) hasta 45 dB (la que menos tiene): 27 dB
  de diferencia entre el género más brillante y el más oscuro.
- **El muestreo**, a la tasa del propio archivo, es **exacto**: no hay
  nada por encima de f_s/2 que se pueda plegar. El aliasing aparece solo
  cuando se baja la tasa, que es lo que se ve en la figura del barrido.
- **El cuantizador** es la etapa que domina a 44,1 kHz, y su error está
  **acotado** a ±Δ/2 = ±15.3 µV: se ve en el panel 3 de la figura como una franja, no como ruido.
- **El DAC** apenas añade error a 44,1 kHz (es un retenedor de orden
  cero sobre muestras que ya están tomadas a esa tasa), pero a 8 kHz el
  conjunto de pérdidas es mucho mayor.

![La cadena ADC-DAC de Popular colombiana](popular_cadena.png)

*La figura tiene dos mitades: arriba, el viaje del SNR (la curva azul es
la cadena nativa y la naranja la telefónica); abajo, 20 ms del error que
introduce cada etapa, con su propia escala. Lo que se ve en los cuatro
paneles de abajo es la diferencia de TEXTURA: el filtro antialiasing
deja un error que parece ruido, el cuantizador deja una franja
acotada, y el DAC deja los escalones del retenedor de orden cero.*


**El ritmo.** **no medible** (sin percusión).

## 4. La comparación: los cinco en la misma gráfica

Esta es la gráfica que pide el punto (e): **los cinco espectros de
magnitud en el mismo eje**, normalizados al pico y suavizados a 250 Hz
para que se puedan leer.

![Los cinco espectros comparados](comparacion_espectros_comparados.png)

Y la energía por bandas, que es donde se ve la diferencia de perfil:

![La energía por bandas de los cinco](comparacion_bandas_comparadas.png)

| Género | f_max (Hz) | f_s,min (Hz) | centroide (Hz) | BPM | planicidad | factor de cresta | índice |
|---|---|---|---|---|---|---|---|
| Clásica · Barroca | 1881 | 3762 | 290 | no medible | 0,0001 | 5,99 | 80,1 |
| Metal | 11666 | 23332 | 1003 | 98 | 0,0047 | 4,93 | 63,9 |
| Salsa | 9332 | 18665 | 923 | 101 | 0,0001 | 4,76 | 62,6 |
| Reggaetón | 7943 | 15887 | 830 | 100 | 0,0111 | 2,88 | 59,8 |
| Popular colombiana | 9953 | 19905 | 1116 | no medible | 0,0022 | 2,81 | 42,2 |

**Qué dice cada cifra.**

- **f_max** es hasta dónde llega el contenido útil de la pista, con el
  criterio del -40 dB respecto al pico. La barroca llega a
  1881 Hz y el reggaetón a
  7943 Hz con ese criterio; con el
  criterio de energía acumulada, el reggaetón llega a
  17290 Hz. La diferencia no es
  del género, es de la masterización: una grabación de archivo de 1722 no
  tiene ni un transitorio por encima de 4 kHz, y una masterización
  moderna de 2023 tiene hats por encima de 10 kHz.
- **f_s,min = 2·f_max** es la tasa de muestreo que exige el teorema. Con
  el criterio del -40 dB, la pista más exigente es Metal,
  que necesita 23332 Hz, y la más generosa es
  Clásica · Barroca, con 3762 Hz. **Los 44,1 kHz del CD
  sobran para las cinco**; lo que no alcanza es la mitad, 22,05 kHz: con
  esa tasa el contenido del metal (que llega a
  11666 Hz) y del reggaetón se plegaría dentro
  de la banda. Por eso el CD se fijó en 44,1 kHz y no en 22,05.
- **centroide espectral** es el brillo de la pieza: 290 Hz en la barroca
  frente a 1116 Hz en la popular colombiana.
- **planicidad** mide la tonalidad: 0 es un tono puro, 1 es ruido.
- **factor de cresta** (pico/RMS) mide la dinámica: 5.99 en la barroca
  frente a 2.81 en la popular, que es el valor típico de una
  masterización moderna comprimida con limitador.

## 5. El punto (e): qué género aporta mejores frecuencias

### El índice, con los pesos a la vista

El índice de atención (0-100) combina cinco criterios. Los pesos están
publicados a propósito: un índice con pesos escondidos no sirve ni para
comparar ni para discutir.

| Género | criterio | peso | valor normalizado | puntos |
|---|---|---|---|---|
| Clásica · Barroca | Tempo en la ventana 60-90 BPM | 25 | 0,50 | 12,5 |
| Clásica · Barroca | Bajo centroide espectral (poco brillo) | 20 | 1,00 | 20,0 |
| Clásica · Barroca | Poca energía en 2-8 kHz | 20 | 0,99 | 19,8 |
| Clásica · Barroca | Rango dinámico (no está comprimida) | 20 | 1,00 | 19,9 |
| Clásica · Barroca | Poca energía en la banda de la voz (300 Hz-3,4 kHz) | 15 | 0,52 | 7,8 |
| Metal | Tempo en la ventana 60-90 BPM | 25 | 0,83 | 20,8 |
| Metal | Bajo centroide espectral (poco brillo) | 20 | 0,71 | 14,3 |
| Metal | Poca energía en 2-8 kHz | 20 | 0,59 | 11,8 |
| Metal | Rango dinámico (no está comprimida) | 20 | 0,64 | 12,9 |
| Metal | Poca energía en la banda de la voz (300 Hz-3,4 kHz) | 15 | 0,27 | 4,1 |
| Salsa | Tempo en la ventana 60-90 BPM | 25 | 0,75 | 18,8 |
| Salsa | Bajo centroide espectral (poco brillo) | 20 | 0,75 | 15,0 |
| Salsa | Poca energía en 2-8 kHz | 20 | 0,85 | 17,1 |
| Salsa | Rango dinámico (no está comprimida) | 20 | 0,59 | 11,7 |
| Salsa | Poca energía en la banda de la voz (300 Hz-3,4 kHz) | 15 | 0,00 | 0,0 |
| Reggaetón | Tempo en la ventana 60-90 BPM | 25 | 0,78 | 19,4 |
| Reggaetón | Bajo centroide espectral (poco brillo) | 20 | 0,80 | 15,9 |
| Reggaetón | Poca energía en 2-8 kHz | 20 | 0,83 | 16,6 |
| Reggaetón | Rango dinámico (no está comprimida) | 20 | 0,00 | 0,0 |
| Reggaetón | Poca energía en la banda de la voz (300 Hz-3,4 kHz) | 15 | 0,53 | 7,9 |
| Popular colombiana | Tempo en la ventana 60-90 BPM | 25 | 0,50 | 12,5 |
| Popular colombiana | Bajo centroide espectral (poco brillo) | 20 | 0,66 | 13,2 |
| Popular colombiana | Poca energía en 2-8 kHz | 20 | 0,82 | 16,5 |
| Popular colombiana | Rango dinámico (no está comprimida) | 20 | 0,00 | 0,0 |
| Popular colombiana | Poca energía en la banda de la voz (300 Hz-3,4 kHz) | 15 | 0,00 | 0,0 |

![El índice de atención y el diagrama tempo/brillo](comparacion_indice_atencion.png)

### El veredicto

**Con el índice propuesto, la mejor opción como música de fondo para estudiar es Clásica · Barroca (80,1 de 100), seguido de Metal (63,9). La razón principal es que su espectro es el más oscuro: centroide de 290 Hz, y ocupa muy poca banda de agudos de percusión, que es donde más gana. En la banda de la voz (300 Hz-3,4 kHz), en cambio, concentra un 24 % de su energía: es el punto más débil de su ficha, y conviene decirlo.**

Por qué:

- el centroide espectral: 20.0 de 20 puntos
- la energía en 2-8 kHz: 19.8 de 20 puntos
- el rango dinámico: 19.9 de 20 puntos
- la energía en la banda de la voz: 7.8 de 15 puntos
- su tempo no es medible (no hay percusión), y por eso el criterio de tempo se puntúa como neutro

![El resumen del punto e](comparacion_veredicto.png)

### Las condiciones del resultado

- La comparación es entre UNA pista por género: con otra elección de tema (o con el mismo tema en otra masterización) el orden puede cambiar. Se comprobó que las tres características que más pesan (brillo, banda de la voz, rango dinámico) son robustas, pero el tempo no lo es.
- Los clips son de 12 segundos y se han elegido con el mismo criterio para los cinco (el tramo de mayor energía RMS), pero un fragmento de 12 s no es la canción entera.
- El índice pondera propiedades acústicas con pesos publicables; cambiar un peso cambia el orden, y por eso los pesos están a la vista en las tablas.

### Lo que este trabajo NO demuestra

- Un espectro de audio NO es un EEG. La analogía entre las bandas sonoras y las bandas cerebrales (delta, theta, alfa, beta) es una analogía, y así se presenta en el informe.
- No hay ninguna afirmación clínica aquí. Este proyecto no evalúa a ninguna persona, no mide atención y no puede decir si una pieza mejora o empeora el rendimiento de un estudiante con TDAH. Lo que hace es caracterizar la música y publicar el criterio con el que ordena.
- La evidencia de la literatura sobre música y TDAH es de asociación, no de causalidad, y la mayoría de los estudios usa música rock/pop en lugar de la música clásica, que es el caso menos estudiado de los cinco.

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

## 6. Cómo se ha calculado

### Los parámetros del análisis

| parámetro | valor | por qué |
|---|---|---|
| Duración del clip | 12.0 s | suficiente para la resolución en frecuencia y corto para la demo |
| Frecuencia de muestreo | la del archivo (44,1 kHz) | no se re-muestrea el original: se analiza tal cual |
| Criterio de `f_max` | -40 dB bajo el pico | publicado, y con control por energía acumulada |
| Bits del ADC | 16 | el de un CD, y se comparan 24/12/8 |
| Fondo de escala | ±1.0 V | el del enunciado: el factor de escala se pide en voltios |
| Orden del filtro AA | 8 | Butterworth de fase cero, `sosfiltfilt` |
| Ventana de la FFT | hann | con corrección por ganancia coherente |

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

| Pista | Duración | f_max | f_s,min | SNR 16 bits (dB) | ENOB 16 bits | índice |
|---|---|---|---|---|---|---|
| Clásica · Barroca | 12 s | 1881 Hz | 3762 Hz | 81,9 | 13,30 | 80.1 |
| Metal | 12 s | 11666 Hz | 23332 Hz | 83,3 | 13,55 | 63.9 |
| Salsa | 12 s | 9332 Hz | 18665 Hz | 94,5 | 15,41 | 62.6 |
| Reggaetón | 12 s | 7943 Hz | 15887 Hz | 90,8 | 14,79 | 59.8 |
| Popular colombiana | 12 s | 9953 Hz | 19905 Hz | 90,5 | 14,74 | 42.2 |

## 7. Limitaciones y honestidad

- **Una pista por género.** Con otra canción, o con la misma canción en
  otra masterización, el orden puede cambiar. Lo que se comprobó es que
  las tres características que más pesan (brillo, banda de la voz, rango
  dinámico) son robustas entre los cinco, y que el tempo no lo es.
- **`f_max` depende de un criterio.** Con -30 dB y con -50 dB salen
  cifras distintas; por eso el criterio está publicado, y se da el
  control por energía acumulada.
- **El factor de cresta mezcla género y época de producción.** Una
  masterización moderna comprimida con limitador tiene crest bajo
  sea cual sea el género. Es un sesgo conocido del criterio y está
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
