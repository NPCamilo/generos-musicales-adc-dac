# GUÍA DE DEFENSA — DSP aplicado a ADC-DAC sobre audio musical

> Documento de estudio y de sustentación. Todo lo que sigue está comprobado
> contra el código de esta carpeta y contra `salida/informe.md`. Si aquí y el
> código discrepan, **manda el código**.

---

## 1. Qué es este proyecto, en un párrafo

Se toman **cinco pistas de música real** (una por género), se les aplica la
cadena completa de conversión digital **ADC → cuantizador → DAC**, se mide
el teorema de muestreo de **Nyquist-Shannon** sobre esas señales reales, se
caracteriza el **factor de escala** de cada convertidor en voltios y en bits
efectivos, y se comparan los cinco géneros con un **índice de atención**
cuyos pesos están publicados, para responder al punto (e) del enunciado.

**En una frase para la sustentación:** es el proyecto de Nyquist-Shannon que
ya tenías, aplicado a música de verdad, con una comparación entre géneros y
un veredicto honesto sobre el punto del TDAH.

**Lo que NO es** (importante para no defender de más):
- No es un estudio clínico, y no mide la atención de ninguna persona.
- No es un reproductor de audio: es una caracterización.
- No usa IA, ni aprendizaje automático, ni redes neuronales.

---

## 2. Las cifras que hay que saber de memoria

| cifra | valor | de dónde sale |
|---|---|---|
| pistas analizadas | 5 | `audio/*.wav` |
| duración de cada clip | 12 s | el tramo de mayor energía RMS |
| f_s de los archivos | 44 100 Hz | los WAV tal cual, sin re-muestrear |
| f_max de la barroca | 1 881 Hz | criterio del −40 dB |
| f_max del reggaetón | 7 943 Hz | criterio del −40 dB |
| f_s mínima del conjunto | 15 887 Hz | 2·f_max del reggaetón |
| factor de escala a 16 bits | 3,052·10⁻⁵ V/nivel | V_fs / 2^(b−1), con V_fs = 1 V |
| SNR medido a 16 bits | 81-94 dB | según la pista |
| bits efectivos a 12 bits | 9,4-11,0 | (SNR − 1,76) / 6,0206 |
| mejor índice de atención | 80,1 / 100 | Clásica · Barroca |
| género más desfavorable | 42,2 / 100 | Popular colombiana |
| comprobaciones automáticas | 164, en 4 suites | `python nucleo/comprobar_todo.py` |

El **ranking** que sale de la medición:

| puesto | género | índice | por qué |
|---|---|---|---|
| 1 | Clásica · Barroca | 80,1 | centroide 290 Hz, casi nada de agudos, dinámica de 5,99 |
| 2 | Metal | 63,9 | 20 % de energía en 2-8 kHz (la guitarra saturada) |
| 3 | Salsa | 62,6 | 66 % de energía en la banda de la voz |
| 4 | Reggaetón | 59,8 | comprimida (cresta 2,88) aunque sea muy grave |
| 5 | Popular colombiana | 42,2 | 72 % en la banda de la voz, y comprimida |

---

## 3. Las ocho ideas que tienes que poder decir de memoria

1. **`f_s ≥ 2·f_max`**, y por qué el 2 es un límite y no un objetivo.
2. **El aliasing es irreversible**: pliega el contenido dentro de la banda y
   no hay filtro que lo deshaga después.
3. **El filtro antialiasing es lo que separa la reconstrucción correcta del
   desastre**, y por eso su corte va al 45 % de f_s/2 y no al 100 %.
4. **El factor de escala en voltios** es `y = V_fs / 2^(b−1)`, y el error del
   cuantizador está acotado a `±Δ/2`.
5. **Los bits nominales no son los bits efectivos**: los efectivos salen del
   SNR medido, y la diferencia es la carga y el ruido.
6. **Un espectro de audio no es un EEG**: la analogía entre las bandas
   sonoras y las cerebrales es una analogía, y hay que decirlo.
7. **El criterio de `f_max` es una decisión**, y por eso se publica el
   criterio y se da la sensibilidad al umbral.
8. **Lo que este trabajo demuestra es una caracterización con un criterio
   publicable, no una afirmación clínica.**

---

## 4. El punto (e): cómo se defiende el veredicto del TDAH

Esta es la parte de la sustentación que más riesgo tiene, así que está
escrita de forma que puedas decir exactamente la respuesta.

### 4.1 Qué se afirma

> "Con el índice propuesto —cinco criterios ponderados, con los pesos
> publicados en las tablas—, la mejor opción como **música de fondo para
> estudiar** es la Clásica-Barroca, con 80,1 de 100. Su espectro es el más
> oscuro: centroide de 290 Hz y casi nada por encima de 4 kHz, de modo que
> deja libre la banda en la que se mueve la voz del profesor. La segunda es
> el Metal, y las dos peores son las dos piezas con cantante, porque
> compiten con la voz en la misma banda de frecuencias."

### 4.2 Qué NO se afirma, y hay que decirlo antes de que te lo pregunten

> "Esto **no** es un estudio clínico. No se ha evaluado a ningún estudiante,
> no se ha medido su atención y no podemos afirmar que una pieza mejore el
> TDAH de nadie. Lo que este trabajo hace es caracterizar **propiedades
> acústicas** de cinco grabaciones y ordenarlas con un criterio explícito.
> El paso de 'suena más tranquila' a 'le va a mejor a un estudiante' exige
> personas, un grupo de control y un protocolo, y eso no cabe en un trabajo
> de DSP."

### 4.3 Por qué esos cinco criterios

| criterio | peso | por qué (para poder soltarlo sin mirar la tabla) |
|---|---|---|
| Tempo en 60-90 BPM | 25 | La literatura sobre música y atención (Husain et al. 2002; Strayer & Perona 2006) relaciona un tempo moderado con menor activación. |
| Bajo centroide espectral | 20 | El contenido agudo es activante y tapa la voz del profesor. |
| Poca energía en 2-8 kHz | 20 | Ahí viven las percusiones de ataque (timbales, charles, platillos). |
| Rango dinámico | 20 | Una señal comprimida no tiene silencios: el oído no descansa. |
| Poca energía en 300 Hz-3,5 kHz | 15 | Es la banda de la voz humana: la misma en la que hay que seguir al profesor. |

### 4.4 Los honestos que hay que tener preparados

- **"Una pista por género"**: con otra canción, el orden puede cambiar. Lo
  que se comprobó es que las tres características que más pesan (brillo,
  banda de la voz, rango dinámico) son robustas entre los cinco, y que el
  tempo no lo es.
- **"El factor de cresta mezcla género y época"**: una masterización
  moderna comprimida con limitador tiene cresta baja, sea del género que
  sea. Está anotado como sesgo conocido del criterio.
- **"La barroca no tiene tempo medible"**: es un preludio sin percusión, así
  que el detector no encuentra pulso, y en el índice ese criterio se
  puntúa como neutro en vez de inventarse un valor.
- **"Un fragmento de 12 s no es la canción"**: lo pide el enunciado
  ("audios cortos"), pero el criterio de selección (el tramo de mayor
  energía RMS) es una decisión.

### 4.5 Las preguntas que te pueden hacer, y la respuesta

**P: ¿La música cura el TDAH?**
No, y no lo afirmamos. La literatura de la que nos apoyamos habla de
efectos **pequeños, inconsistentes y dependientes de la tarea** (el
"efecto Mozart" es un ejemplo de efecto pequeño; Brown et al. 2001 es el
antecedente más citado de la idea del contenido de baja frecuencia). Esto
es una hipótesis con un criterio publicable, no una prescripción.

**P: ¿Por qué no usaste las bandas cerebrales (delta, theta, alfa, beta)?**
Las que se muestran en el informe son **bandas sonoras** con los mismos
nombres, para que la comparación sea visual; se calculan sobre el audio y
se leen como "qué banda del sonido está activada". Atribuirles un
significado cerebral sería inventar una equivalencia que no existe.

**P: ¿Y si cambias los pesos?**
El orden puede cambiar, y por eso los pesos están a la vista: un índice con
pesos escondidos no sirve ni para comparar ni para discutir. Con el
criterio actual, el barroca gana por 16 puntos al segundo, y esa
diferencia es demasiado grande para que un cambio razonable de pesos la
dé vuelta: la únicahdr que lo cambia es el tempo, y ese está medido como
no medible en la barroca.

**P: ¿Y si el profe dice que el metal es mejor?**
Es una discusión legítima, y la respuesta es: "entonces cambiamos el peso
del brillo y lo vemos". El índice está hecho para eso.

---

## 5. Cómo está organizado el código

```
Generos_Musicales_ADC_DAC/
├── nucleo/                    el motor de cálculo (sin Django)
│   ├── wav_io.py              el parser de WAV, propio y sin dependencias
│   ├── primitivas.py          las primitivas de DSP: Shannon, cuantizador,
│   │                          métricas, dither, diagnóstico de Nyquist
│   ├── dsp_audio.py           espectro, f_max, antialiasing, tempo, el índice
│   ├── catalogo.py            las cinco fichas: músico, obra, año, fuentes
│   ├── analisis.py            el pipeline completo por pista
│   ├── comparativa.py         la comparación y el veredicto
│   ├── figuras.py             las figuras (matplotlib, 300 dpi)
│   ├── informe.py             el .md del entregable
│   ├── serializacion.py       el JSON con los números, para el despliegue
│   ├── descarga.py            bajar y recortar las pistas
│   ├── test_*.py              las comprobaciones
│   └── comprobar_todo.py      el runner
├── motor/                     la aplicación Django (vistas y plantillas)
├── dsp_web/                   el proyecto Django (settings, urls)
├── api/                       la entrada WSGI para Vercel
├── public/                    los ficheros estáticos
├── manage.py
├── construir.py               regenera el entregable y los datos
├── vercel.json                la configuración de Vercel
├── audio/                     los cinco WAV + descargas.json
├── salida/                    el entregable: informe.md, datos.json, 39 PNG
└── docs/                      GUIA.md (esta) y PUBLICAR.md
```

El grafo de dependencias es de una sola dirección:

```
wav_io ──┐
primitivas ┼──► analisis ──► comparativa ──► informe
dsp_audio ┘        │             │
                   ▼             ▼
                figuras ─────────┘
                   │
                   ▼
            motor/views.py  (Django)
```

Y el proyecto es **autosuficiente**: las primitivas de DSP vienen de
`nucleo/primitivas.py`, adaptadas del proyecto `Nyquist_Shannon/` (que
está en la carpeta de al lado y del que viene la metodología). Al
copiarlas, el repositorio se puede clonar y desplegar sin depender de
ninguna carpeta hermana, que es lo que hace falta para Vercel. Las cifras
que dan son exactamente las mismas: lo verifican las 164 comprobaciones.

---

## 6. Los bugs que se encontraron y se corrigieron (y que puedes citar)

Son errores REALES del código, encontrados por las pruebas. Citar them es
una muestra de rigor, y si alguien los encuentra por ti, es mejor que los
tengas tú:

1. **El suavizado del espectro se hacía en dB.** Promediar logaritmos no es
   promediar potencias: el pico de un tono (3 bins a 0 dB y el resto a −30,
   −60, −90) se "promediaba" a −92 dB, y el `f_max` de un tono puro de
   500 Hz daba **0 Hz**. Ahora el suavizado es una media móvil de la
   **potencia**, y el pico da 511 Hz.
2. **El suavizado usaba `np.convolve` con modo "same"**, que es O(N·M): con
   una FFT de 2²⁰ bins y una ventana de 250 Hz eran 6000 millones de
   operaciones por suavizado, y además en los bordes producía un pico
   fantasma en el bin de DC. Ahora es O(N) con sumas acumuladas.
3. **El umbral de `f_max` se medía respecto al pico SUAVIZADO**, que está
   una docena de dB por debajo del real. Ahora se mide respecto al pico
   CRUDO, que es el dato.
4. **El detector de tempo daba un tempo falso a las senoidales**, con una
   confianza de 0,86: la fuga del bin hace que el flujo espectral de un
   tono tenga una periodicidad espuria. Ahora el tempo solo se declara
   medible si además la envolvente de ataques tiene crestas (cresta ≥ 3).
5. **El experimento de aliasing medía también el efecto del filtro**, porque
   la referencia era el filtro del 45 %. Con la referencia correcta (el
   muro de ladrillo en f_s/2), el error de aliasing es exactamente el
   contenido plegado.
6. **El presupuesto de error contaba la energía de la cuantización dos
   veces** (una en la etapa del cuantizador y otra en la del DAC), porque
   el error del DAC se medía contra la señal original en vez de contra la
   ya cuantizada.
7. **El factor de cresta estaba mal interpretado**: con la definición
   pico/RMS de la música (3 a 7), los umbrales de la puntuación estaban
   calculados como si el rango fuera de 0,25 a 0,8.

---

## 7. Limitaciones que debes saber (para que no te pillen de sorpresa)

- **Una pista por género.** Es la limitación más importante y ya está
  escrita en el informe.
- **`f_max` depende del criterio.** Con −30 dB y con −50 dB salen cifras
  distintas; por eso está publicado y hay una tabla de sensibilidad.
- **El factor de cresta mezcla género y época de producción.**
- **Un fragmento de 12 s no es la canción.**
- **La analogía con las bandas cerebrales es una analogía.**
- **Los clips son de YouTube**, descargados y recortados con el mismo
  criterio para los cinco (el tramo de mayor energía RMS). Son extracts
  para análisis académico: **no se redistribuyen**.

---

## 8. Plan de la sustentación (2 horas el jueves)

| minuto | qué haces | qué proyectas |
|---|---|---|
| 0-5 | El problema: cinco géneros, una cadena ADC-DAC, dos preguntas | la portada de la web |
| 5-15 | La cadena y el factor de escala: qué es y en qué se equivoca | la figura de cuantización de una pista |
| 15-25 | Nyquist-Shannon sobre audio real: el barrido de f_s | la figura de muestreo del metal |
| 25-35 | Los resultados por género: la tabla | la web, la ficha del metal |
| 35-50 | **El punto (e)**: la gráfica única, el índice, el veredicto | la comparativa de la web |
| 50-60 | **La honestidad**: qué no demuestra y por qué | la sección de límites |
| 60-70 | **La demo**: el audio de 8 bits y el de 8 kHz, que se oyen | el reproductor de la ficha |
| 70-80 | Las preguntas | — |

**El momento que más impresiona**: poner el audio original y el de 8 bits a
continuación, y que se note. Es el momento en que el proyecto deja de ser
un ejercicio de DSP y se convierte en algo que demuestra el sistema de
conversión entero.

---

## 9. Cómo ejecutar todo

```bash
# el motor de cálculo, sin la web
python -m nucleo.informe            # el informe y las 39 figuras
python -m nucleo.comparativa        # la comparación por consola
python -m nucleo.descarga           # (re)bajar las pistas

# la aplicación web
python manage.py runserver          # http://127.0.0.1:8000

# las comprobaciones
python nucleo/comprobar_todo.py     # 164 en verde
```

## 10. Glosario

| símbolo | significado |
|---|---|
| `f_max` | la frecuencia máxima útil de la señal, medida con un criterio |
| `f_s,min` | `2·f_max`, la tasa de muestreo mínima según Nyquist |
| `Δ` | el paso del cuantizador, `V_fs / 2^(b−1)` |
| `y` | el factor de escala, en V por nivel (el LSB) |
| ENOB | los bits efectivos, `(SNR − 1,76) / 6,0206` |
| dBFS | el nivel respecto a plena escala |
| cresta | pico/RMS: la dinámica de la grabación |
| centroide | el centro de gravedad del espectro: el brillo |
| NRMSE | el error RMS dividido por el recorrido de la señal |
| OSR | el sobremuestreo, `f_s / (2·f_max)` |
