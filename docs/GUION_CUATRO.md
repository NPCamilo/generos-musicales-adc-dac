# GUION DE SUSTENTACIÓN EN CUATRO — DSP aplicado a ADC-DAC sobre audio musical

> **Cómo usar este documento.** El texto entre comillas es lo que se dice,
> palabra por palabra. Lo que va en *cursiva* son indicaciones de acción.
> El bloque **[PANTALLA]** de cada tramo dice **exactamente qué tiene que
> estar en la pantalla en ese momento**: si no está, el que habla tiene que
> tenerla preparada en otra pestaña.
>
> **Reparto:** Ángel, Mariano, Luis y Camilo (tú). 80 minutos de turno.
> **El reparto está en la §2, en una tabla.** Cada uno tiene su tramo, su
> minutaje y sus transiciones.
>
> **Antes de empezar, mira la §0** (preparación) y la §9 (plan B).

---

## 0. Antes de empezar (10 minutos antes)

| # | qué | cómo |
|---|---|---|
| 1 | **La web** | https://generos-musicales-adc-dac.vercel.app — abierta en **cuatro pestañas**: portada, comparativa, ficha del metal, ficha de la barroca |
| 2 | **La web en local** | `python manage.py runserver` **ya arrancado**, en http://127.0.0.1:8000 — es el plan B |
| 3 | **El informe** | `salida/informe.md` abierto, por si preguntan una cifra exacta |
| 4 | **El sonido** | comprobado: el audio de 8 bits se oye distinto del original. **La demo no se improvisa** |
| 5 | **Los papeles** | cada uno con su tramo del §2 y las 4 cifras de la §3 |
| 6 | **Quién va primero** | decidedlo antes. El que abre, abre: es el que presenta el problema |

**Regla de oro del reparto:** quien **entra** en su tramo dice su nombre y
el de quién sale. *"Yo soy Ángel y le paso a Mariano."* En un grupo de
cuatro, eso da la sensación de equipo sin ensayar.

---

## 1. El reparto en una tabla

| tramo | minutos | quién | de qué se ocupa | la pantalla |
|---|---|---|---|---|
| **1** | 0-8 | **Ángel** | Apertura: el problema y las cinco pistas (la investigación) | Portada de la web |
| **2** | 8-26 | **Mariano** | La cadena ADC-DAC: el factor de escala, los bits, el cuantizador | Ficha del **metal**, secciones 3-5 |
| **3** | 26-46 | **Luis** | Nyquist-Shannon sobre audio real y los resultados por género | Ficha del metal (barrido) + comparativa |
| **4** | 46-66 | **Camilo** (tú) | El punto (e): la gráfica única, el índice, el veredicto **y la honestidad** | Comparativa + veredicto |
| **5** | 66-80 | **todos** | La demo de audio, el código y el cierre | Ficha de un género (los audios) |

**Por qué este reparto y no otro:**

- **Ángel** abre porque tiene la voz más clara para el problema, y su
  tramo es el más ligero: son datos, no matemáticas.
- **Mariano** se queda con la parte más técnica (el cuantizador), que es
  donde están las fórmulas del enunciado (el punto d). Es el tramo con
  más números y el más fácil de sostener si se sabe la fórmula del
  factor de escala.
- **Luis** se queda con el teorema y los resultados, que es la parte
  más "de exhibition" (el barrido de f_s es la figura más bonita del
  proyecto).
- **Tú** te quedas con **el punto (e) y la honestidad**, que es la parte
  que decide la nota, y con la demo. Es lo que peor se puede delegar.

Si en la semana os repartís distinto, el **contenido** de cada tramo
está en el §2 de este documento, así que la estructura sirve igual.

---

## 2. El guion, tramo por tramo

### TRAMO 1 · ÁNGEL · 0-8 min · Apertura y las cinco pistas

**[PANTALLA: la portada de la web]**

> «Buenos días. Somos un grupo de cuatro y este es nuestro proyecto:
> **"DSP aplicado a ADC-DAC sobre audio musical"**.
>
> La pregunta que responde es: **qué le pasa a una canción cuando la
> convierto a números y la vuelvo a convertir en sonido**.
>
> Hemos tomado **cinco pistas** de cinco géneros —barroca, metal, salsa,
> reggaetón y música popular colombiana—, les hemos pasado la cadena
> completa de conversión digital —**ADC, cuantizador y DAC**—, les hemos
> aplicado el teorema de muestreo de **Nyquist-Shannon** medido sobre
> audio real, y las hemos comparado entre sí.
>
> Yo empiezo por las pistas; luego Mariano os contará la cadena de
> conversión, Luis el teorema y el punto del TDAH será el final, con la
> demo de audio.»

*Di esto mirando al profesor. El resto del grupo, de pie o al lado,
escuchando. Es la señal de que esto es un equipo.*

**[PANTALLA: la portada, las tarjetas de los cinco géneros]**

> «Cada pista es un fragmento de **12 segundos**, recortado con un
> criterio objetivo: el tramo de **mayor energía RMS** de la canción
> completa. No es arbitrario, y es el mismo para los cinco, que es lo que
> hace que la comparación sea justa.
>
> El enunciado pide una investigación breve de cada género. Esta es:»

*Señala cada tarjeta y di **solo el dato clave**, sin leer la tabla:*

| género | di esto | por qué ese tema |
|---|---|---|
| **Clásica · Barroca** | «Bach, Suite para violonchelo n.º 1 en Sol mayor, BWV 1007, de 1722.» | un solo violonchelo, sin percusión: el perfil más limpio |
| **Metal** | «Megadeth, *Tornado of Souls*, del álbum *Youthanasia*, de 1990.» | la guitarra saturada genera armónicos de orden altísimo |
| **Salsa** | «Frankie Ruiz y La Solución, *La Rueda*, de 1980.» | percusión latina: el timbal vive en los agudos |
| **Reggaetón** | «Feid y ATL Jacob, *LUNA*, de 2023.» | bombo sintetizado y voz limpia: casi todo graves |
| **Popular colombiana** | «Fredy Montoya con Luisito Muñoz, *Ángel o Demonio*, de 2016.» | la cantina de la costa: banda de la voz |

> «Y hay un criterio para elegir **estos** temas y no otros, y es el que
> importa en un trabajo de DSP: cada uno representa a su género **en el
> espectro**. El metal, por ejemplo: la saturación de la guitarra no es
> un efecto de timbre, es multiplicar la onda por una función no lineal, y
> eso genera armónicos de orden muy alto. No lo elegí porque suene duro:
> lo elegí porque su espectro lo delata.
>
> Con la investigación hecha, paso la palabra. Ángel, ¿empiezas tú o
> empiezo yo?»

*Si te toca abrir a ti, di la apertura que está arriba y cambia los
nombres. Si no, pasa el turno.*

---

### TRAMO 2 · MARIANO · 8-26 min · La cadena ADC-DAC

**[PANTALLA: la ficha del METAL, secciones 3, 4 y 5]**

> «Gracias. La cadena de conversión es el corazón de este proyecto, y es
> donde están las fórmulas que pide el enunciado.
>
> La cadena es esta:»

*Aplica con el cursor (o con la mano) la secuencia de la ficha:*

```
x(t) ──filtro AA──▶ ──muestreo──▶ ──cuantizador──▶ ──DAC──▶ x̂(t)
```

> «**El filtro antialiasing** recorta la banda de arriba del todo. Su
> corte va al **45 % de f_s/2**, no al 100 %, porque un filtro real no
> cae en vertical: si el corte estuviera justo en f_s/2, parte del
> contenido original se metería en la banda nueva y el aliasing no
> desaparecería del todo.
>
> **El muestreo** toma las muestras en los instantes del reloj, sin
> interpolar nada, que es lo que hace un ADC de verdad.
>
> **El cuantizador** es uniforme, con los niveles en los **centros** de
> las celdas, y satura en los extremos.
>
> Y **el DAC** lo implemento de dos formas: retenedor de orden cero (el
> DAC barato) y suma de senos cardinales, que es la reconstrucción
> exacta de Shannon.»

**[PANTALLA: en la misma ficha, la tabla de bits de la sección 4]**

> «Y aquí está el resultado, que es el **punto (d)** del enunciado: el
> **factor de escala**, en voltios y en bits.
>
> Con un fondo de escala de ±1 voltio:

```
y = V_fs / 2^(b-1) = 1 / 2^15 = 3,052 · 10⁻⁵ voltios por nivel
```

> Es el paso entre niveles. En 16 bits son 65 536 niveles repartidos en
> 2 voltios, y el error de redondeo está **acotado a ±Δ/2**, o sea
> ±15,26 microvoltios.
>
> Pero aquí está el detalle que es la diferencia entre un ADC y una cifra
> bonita: **los bits nominales no son los bits efectivos**. El SNR
> teórico de 16 bits son 98 decibelios, pero el **medido** en el metal
> es de 83. ¿Por qué? Porque la señal no llena el rango: está a
> −2,4 dBFS, y esa carga se paga. Los **bits efectivos** son 13,5, no
> 16. Un ADC de 16 bits al que le metes una señal que solo ocupa el 20 %
> del rango no te da 16 bits: te da menos. Y eso está medido aquí, no
> supuesto.»

**[PANTALLA: la figura de la escalera de cuantización, en la sección 4]**

> «Aquí se ve la escalera. Y fíjense en el panel del error, en
> microvoltios: son escalones de medio Δ, y nunca se salen de la banda.
> Eso es el error de cuantización: **acotado, determinista y no
> gaussiano**.»

**[PANTALLA: la tabla de códigos binarios, en la sección 4]**

> «Y estas son las muestras con su código de 16 bits, que es lo que el
> convertidor entrega de verdad: un entero, no una tensión. El error de
> cada una está en la última columna, en unidades de Δ.»

**[PANTALLA: la figura de la cadena, sección 5]**

> «Y aquí está la cadena completa, que es lo que más me costó entender a
> mí. Arriba están **las barras de degradación de cada etapa**:
> cuánto SNR se pierde en cada paso. La azul es la cadena nativa, a
> 44,1 kHz y 16 bits, y la naranja la telefónica, a 8 kHz y 8 bits.
>
> Cada barra mide SU etapa contra la anterior, y la última es el total
> acumulado contra la señal original. Por eso la última puede ser PEOR
> que las anteriores: **el error del filtro no se deshace**.
>
> Fíjense en la **cáda del filtro antialiasing**: en el metal se
> pierden 18 dB, y en la barroca 45. La diferencia no es del
> instrumento, es de la **masterización**: el reggaetón tiene contenido
> hasta 17 kHz y la barroca no pasa de 4 kHz. Por eso el filtro, que es
> la misma etapa en los cinco, cuesta cosas distintas.
>
> Abajo están los 20 milisegundos del error de cada etapa, y se ve la
> diferencia de textura: el filtro antialiasing deja un error que parece
> ruido, el retenedor de orden cero deja una onda suave, el cuantizador
> deja una franja acotada, y el total es la suma de todo.»

---

### TRAMO 3 · LUIS · 26-46 min · Nyquist-Shannon y los resultados

**[PANTALLA: la ficha del metal, la figura del barrido de muestreo]**

> «Gracias. El teorema de Nyquist-Shannon dice que si una señal no tiene
> contenido por encima de f_max y se muestrea a más de 2·f_max, se puede
> reconstruir **exactamente**. Y el punto es que en audio real, el f_max
> hay que **medirlo**: no hay fórmula, porque el audio no es periódico.
>
> Esta gráfica es un barrido: submuestreamos la misma pista del metal a
> distintas frecuencias y medimos el error de la reconstrucción, con y
> sin filtro antialiasing.
>
> La línea naranja es lo que pasa **sin** filtrar: el contenido que está
> por encima de f_s/2 se pliega dentro de la banda. Y el pliegue es
> **irreversible**: no hay ningún filtro que lo deshaga después, porque
> la información se mezcló al muestrear, no al filtrar.
>
> La línea verde es lo que pasa **con** filtro. Y el hueco entre las dos
> es, literalmente, **el precio de no filtrar**.
>
> Miren el eje de la derecha: el porcentaje de energía que queda por
> encima de f_s/2. Cuando esa energía es cero, el teorema se cumple. En
> el metal, bajando a la mitad de lo necesario, todavía queda un **1 %
> de la energía** fuera de banda, y el error se multiplica por **tres**:
> del 1,2 % al 4,0 %.»

**[PANTALLA: la comparativa, la tabla de las cinco cifras]**

> «Y esto es lo que sale al repetirlo con las cinco pistas. Las cinco
> cifras que se comparan:
>
> **f_max**, hasta dónde llega el contenido útil. La barroca llega a
> 1 881 Hz y el reggaetón a 7 943. Y aquí hay un matiz metodológico que
> publiqué en el informe: `f_max` **depende de un criterio**, y por eso
> el criterio está escrito y hay una tabla de sensibilidad. Con el
> criterio de energía acumulada en vez del del umbral, al reggaetón le
> sale 17 290 Hz. No es un error: son dos preguntas distintas —"¿hasta
> dónde llega el contenido significativo?" y "¿hasta dónde llega la
> energía?"— y se publica la respuesta a las dos.
>
> **f_s mínima**, el doble de f_max: para la pista más exigente, el
> metal, son 23 332 Hz. **Los 44,1 kHz del CD sobran para las cinco**;
> lo que no alcanza es la mitad, 22,05 kHz, porque el contenido del
> metal ya no cabe y se plegaría. Por eso el CD se fijó en 44,1 kHz.
>
> **Centroide espectral**, el brillo: 290 Hz en la barroca frente a
> 1 116 Hz en la popular colombiana.
>
> **Factor de cresta**, pico/RMS, la dinámica: 5,99 en la barroca frente
> a 2,81 en la popular. Y aquí va un aviso honesto que está en el
> informe: la compresión con limitador es una práctica de **estudio
> moderno**, así que ese criterio mide en parte la época de producción y
> no solo el género.
>
> Y el **tempo**: 101 BPM en la salsa, 100 en el reggaetón, 98 en el
> metal. Y en la barroca, **no es medible**: no hay percusión, así que el
> detector no encuentra pulso con confianza, y en vez de inventarse un
> número, ese criterio se puntúa como neutro y se dice que no es
> medible.»

---

### TRAMO 4 · CAMILO (tú) · 46-66 min · El punto (e) y la honestidad

**[PANTALLA: la comparativa, la gráfica de los cinco espectros]**

> «Gracias. Y ahora la pregunta que el enunciado hace en el último
> punto: **qué género aporta mejores frecuencias para un estudiante con
> TDAH**.
>
> Esta es la gráfica que pide: **los cinco espectros de magnitud en el
> mismo eje**, cada uno normalizado a su pico y suavizado, para comparar
> las formas y no los niveles.
>
> Miren cómo se separan. La barroca, en azul, es una línea que cae en
> picado: a los 4 kHz ya está 37 dB por debajo, y a los 8 kHz, 48. El
> reggaetón, en rosa, es el que aguanta hasta 17 kHz. Y abajo, en escala
> logarítmica, está sombreada **la banda de la voz humana, de 300 Hz a
> 3,5 kHz**.»

**[PANTALLA: la figura de la energía por bandas]**

> «Y aquí está la comparación propiamente dicha. La popular colombiana
> tiene el 72 % de su energía en la banda de 250 Hz a 2 kHz, que es
> justo donde está la voz humana: es una canción con cantante, y el
> cantante está exactamente donde está la voz del profesor.
>
> Para ordenar los cinco construí un **índice de atención** con cinco
> criterios, y lo importante es que **los pesos están a la vista** en las
> tablas. Un índice con pesos escondidos no sirve ni para comparar ni
> para discutir.»

**[PANTALLA: la tabla de criterios de la ficha de un género]**

> «Los cinco criterios, con su peso:
>
> - **Tempo en 60-90 BPM**, peso 25: la literatura relaciona un tempo
>   moderado con menor activación.
> - **Bajo centroide espectral**, peso 20: el contenido agudo activante
>   tapa la voz del profesor.
> - **Poca energía entre 2 y 8 kHz**, peso 20: ahí viven las percusiones
>   de ataque.
> - **Rango dinámico**, peso 20: una señal comprimida no tiene silencios.
> - **Poca energía en la banda de la voz**, peso 15: la misma banda en la
>   que hay que seguir al profesor.»

**[PANTALLA: la figura del veredicto]**

> «Y el resultado: **la barroca gana, con 80,1 de 100**. El metal queda
> segundo con 63,9, y las dos peores son la popular colombiana y la
> salsa: las dos tienen cantante.
>
> La razón es una sola y se ve en la gráfica: el espectro de la barroca
> es el más oscuro. Centroide de 290 Hz, casi nada por encima de 4 kHz.
> Deja libre la banda donde se mueve la voz del profesor. Eso son 80,1
> puntos.»

**[PANTALLA: la comparativa, la sección "Lo que este trabajo NO demuestra"]**

> «Y ahora, y esto es lo que más me importa decir: **qué es este trabajo
> y qué no es**.
>
> Este trabajo **caracteriza propiedades acústicas** de cinco grabaciones
> y las ordena con un criterio explícito y publicable. Eso es todo.
>
> Esto **no** es un estudio clínico. **No** hemos evaluado a ningún
> estudiante, **no** hemos medido su atención, y **no** podemos afirmar
> que una pieza mejore el TDAH de nadie. Ese paso —de "suena más
> tranquila" a "le va a mejor a una persona"— exige personas, un grupo de
> control y un protocolo, y eso no cabe en un trabajo de DSP. Si nos lo
> preguntaran, la respuesta sería: es una **hipótesis fundamentada**, no
> una prescripción.
>
> Y una segunda analogía que no quiero que se nos escape: en el informe
> aparecen unas bandas que se llaman delta, theta, alfa, beta y gamma,
> como las del EEG. **Son bandas sonoras.** Se calculan sobre el audio y
> se leen como "qué banda del sonido está activada". Atribuirles un
> significado cerebral sería inventar una equivalencia que no existe.
>
> Y una tercera limitación, la más incómoda: hay **una pista por
> género**. Con otra canción, el orden puede cambiar. Lo que sí
> comprobamos es que las tres características que más pesan son robustas
> entre los cinco, y que el tempo no lo es.
>
> Bien. Con esto cerramos la parte de measurements, y ahora sí: la
> parte que más se disfruta, que es **oírlo**.»

---

### TRAMO 5 · TODOS · 66-80 min · La demo, el código y el cierre

**[PANTALLA: la ficha de un género, la sección "Escúchalo"]**

*Que sea **una sola persona** la que maneje el audio (tú), y los otros
tres, de pie, escuchando. Se ve mejor.*

> «En la ficha de cada género hay cuatro audios: el original, el
> cuantizado a 12 bits, el cuantizado a 8 bits y la cadena telefónica a
> 8 kHz. Primero el original.»

*5 segundos. Pausa.*

> «Ahora el mismo audio cuantizado a **8 bits**:»

*Se oye el ruido de cuantización.*

> «Ese siseo no es un efecto del programa: es el error del cuantizador,
> que es determinista y no gaussiano, y por eso se oye como un siseo y
> no como ruido blanco.
>
> Y ahora el **telefónico**: 8 kHz y 8 bits, lo que pasaba por una línea
> de teléfono analógica. No solo suena más grave: **ha desaparecido toda
> la mitad del espectro**, y el SNR de la cadena cae de 83 dB a 36 dB.»

*(Si prefieréis, que lo diga Ángel o Mariano:)*

> «Es la mejor forma de ver por qué el enunciado pide el factor de
> escala en voltios **y** en bits: no son dos formas de decir lo mismo.
> Los voltios son la escala física; los bits son cuántos niveles hay.
> Entre las dos cosas está la resolución, que es lo que determina si el
> oyente distinguido nota la diferencia.»

**[PANTALLA: el repositorio en GitHub, la estructura de carpetas]**

> «Y un minuto sobre cómo está construido, que es parte del trabajo.
>
> Es un **motor de cálculo** y una **aplicación web** por encima. El
> motor no depende de la web: genera el informe y las figuras, y hay una
> suite de **164 comprobaciones automáticas** que verifican las cifras
> contra valores analíticos conocidos.
>
> Tres cosas que nos parecen lo más interesante de haber resuelto:
>
> **Una**: el parser de WAV está escrito desde cero, sin `soundfile` ni
> `librosa`, para no añadir dependencias. Soporta PCM de 8, 16, 24 y 32
> bits y coma flotante. Al hacerlo se ve lo que hace de verdad un ADC:
> los bytes se convierten a enteros con signo y se dividen.
>
> **Dos**: el proyecto está desplegado en **Vercel**, y Vercel no es un
> servidor: cada visita ejecuta una función con un límite de diez
> segundos y el disco de solo lectura. Eso obligó a pre-calcular los
> números y las figuras, y a hacer que el proyecto fuera
> **autosuficiente**. Con esa restricción terminó siendo un proyecto
> mejor: ahora se clona y funciona en cualquier parte.
>
> **Tres**, y esta es la que más nos gusta, porque viene de las pruebas:
> las pruebas encontraron **siete errores reales** en nuestro propio
> código. El mejor fue que suavizábamos el espectro **promediando
> decibelios**, y eso no es promediar potencias: el pico de un tono se
> "promediaba" a 92 decibelios por debajo, y nuestra medida de f_max
> daba **cero hercios** para un tono de 500. Lo encontramos porque la
> prueba comparaba un tono sintético con el valor esperado. Ese tipo de
> error no se ve en una gráfica: se ve en una prueba.»

**[PANTALLA: la portada de la web]**

> «Cerramos. Resumen:
>
> Cinco géneros, cinco perfiles espectrales, medidos con la cadena
> completa de conversión digital y con el teorema de Nyquist-Shannon
> aplicado a audio real.
>
> El factor de escala de un convertidor de 16 bits con fondo de escala de
> ±1 voltio es **3,052 · 10⁻⁵ voltios por nivel**, con el error acotado
> a la mitad de eso, y los bits **efectivos** son menos que los
> nominales en cuanto la señal no llena el rango.
>
> Y del punto (e): con un índice de cinco criterios de pesos publicados,
> la mejor opción como música de fondo para estudiar es la **Clásica ·
> Barroca**, con 80,1 de 100, porque su espectro es el más oscuro y
> deja libre la banda de la voz. Es una hipótesis con un criterio
> publicable, no una afirmación clínica, y el informe dice exactamente
> eso.
>
> Está todo en el repositorio, con el informe completo, las figuras y
> las 164 comprobaciones. Muchas gracias.»

---

## 3. Las cuatro cifras que hay que saber de memoria

```
f_max de la barroca      1 881 Hz
f_s mínima del metal    23 332 Hz        (2·f_max)
y a 16 bits              3,052·10⁻⁵ V por nivel
mejor índice             80,1 / 100  →  Clásica · Barroca
```

**Y el verbo del proyecto, en una frase:** *caracterizar*.

---

## 4. Las transiciones entre tramos (las cinco frases)

En un grupo de cuatro, las transiciones son la mitad del pulido. Estas
son exactas, y se dicen mirando al que entra:

| de → a | la frase |
|---|---|
| **1 → 2** | «Con la investigación hecha, paso la palabra. Ángel, ¿empiezas tú o empiezo yo?» / «Mariano, te toca la cadena de conversión.» |
| **2 → 3** | «Con esto ya se puede pasar a Luis, que nos va a enseñar qué pasa cuando bajamos la frecuencia de muestreo.» |
| **3 → 4** | «Gracias. Y ahora la pregunta que el enunciado hace en el último punto: qué género aporta mejores frecuencias para un estudiante con TDAH.» |
| **4 → 5** | «Bien. Con esto cerramos la parte de mediciones, y ahora sí: la parte que más se disfruta, que es **oírlo**.» |
| **cierre** | «Cerramos. Resumen:… Muchas gracias.» (el que cierra, el último) |

---

## 5. Qué pasa si alguien pregunta a la persona equivocada

| la pregunta | quién la sabe mejor | qué hacer |
|---|---|---|
| «¿Por qué elegiste estos temas?» | Ángel | que le repita la pregunta al que sabe |
| «¿Cuánto es el factor de escala?» | Mariano | ditad verbatim: `y = V_fs / 2^(b-1)` |
| «¿Y si bajas f_s?» | Luis | la figura del barrido |
| «¿Entonces la música cura el TDAH?» | **Camilo** | es la pregunta de la §6.1 |
| «¿Por qué Django y no Streamlit?» | Luis | lo cuenta él, es su parte del código |
| «¿Cuánto cuesta el despliegue?» | Luis | Vercel, funciones serverless, 10 s de límite |
| «¿Qué es lo que más costó?» | cualquiera | la verdad: el suavizado en dB, y las pruebas |

**Regla:** si no la sabes, **pásala**: *"Esa la tiene mejor Marian, te
la paso"*. No es debilidad, es lo que hace un equipo.

---

## 6. Las 12 preguntas difíciles, y a quién le tocan

### 6.1 Para todos (las que hay que saber sí o sí)

**P: «¿La música cura el TDAH?»**
> «No, y no lo afirmamos. La literatura de la que nos apoyamos habla de
> efectos **pequeños, inconsistentes y dependientes de la tarea**; el
> "efecto Mozart" es un ejemplo de efecto pequeño, y el antecedente más
> citado de la idea del contenido de baja frecuencia es el del ruido
> marrón a 60-70 Hz de Brown et al. (2001). Lo que este trabajo hace es
> caracterizar la música y publicar el criterio con el que la ordena. El
> resto es una hipótesis, y así está escrito en el informe.»

**P: «¿Y si cambias los pesos del índice?»**
> «El orden puede cambiar, y por eso los pesos están a la vista: un
> índice con pesos escondidos no sirve ni para comparar ni para
> discutir. Con los pesos actuales, la barroca gana por 16 puntos al
> segundo, y esa diferencia es demasiado grande para que un cambio
> razonable de pesos la dé vuelta. Lo único que la cambiaría es el
> criterio de tempo, y ese está medido como no medible en la barroca.»

**P: «Una pista por género no es muy riguroso.»**
> «Es la limitación más importante y está escrita en el informe, en la
> sección de condiciones. Con otra canción el orden puede cambiar. Lo que
> sí comprobamos es que las tres características que más pesan —brillo,
> banda de la voz y rango dinámico— son robustas entre los cinco, y que
> el tempo no. Y el enunciado pide audios cortos, así que el fragmento
> de 12 segundos es lo que corresponde; lo que hicimos fue elegir el
> tramo con un criterio publicado —el de mayor energía RMS— en lugar de
> al azar.»

**P: «¿Por qué f_max depende del criterio? Eso lo hace subjetivo.»**
> «Depende de cualquier decisión, y prefiero que se vea. Mido dos cosas:
> el **umbral** —la frecuencia más alta que sigue estando 40 dB por
> debajo del pico— y la **energía acumulada** —el 99,9 % de la
> energía—. En el metal casi coinciden; en el reggaetón se separan
> mucho, porque el pico está en los graves y la energía de una
> masterización moderna se concentra abajo. Publico las dos y la tabla
> de sensibilidad. Un resultado con un criterio escondido no se puede
> discutir; este se puede discutir en cada número.»

**P: «¿Y no es grave que la música moderne suene comprimida? ¿Eso no
falsea la comparación?»**
> «Sí lo es, y está anotado como sesgo del criterio. La compresión con
> limitador es una práctica de estudio moderno, así que el factor de
> cresta mide en parte la época de producción y no solo el género: por
> eso el reggaetón y la popular, de 2023 y 2016, tienen cresta baja,
> mientras que la barroca, grabada con otros criterios, tiene 5,99.
> Podríamos haber eliminado ese criterio, pero preferimos publicarlo y
> señalarlo, porque un criterio que no se ve es donde se esconden las
> manipulaciones.»

**P: «¿Por qué 12 segundos?»**
> «Por dos razones: el enunciado pide audios cortos, y doce segundos a
> 44,1 kHz dan una resolución en frecuencia de unos 0,08 Hz, muy por
> debajo de lo necesario. Y el corte no es al azar: se elige el tramo de
> mayor energía RMS, con el mismo criterio para los cinco.»

### 6.2 Para Mariano (la parte técnica)

**P: «¿Por qué 2^(b-1) y no 2^b en el factor de escala?»**
> «Porque un ADC de b bits tiene su código en el rango de −2^(b−1) a
> 2^(b−1)−1: el cero está en el centro, no en el extremo. Por eso el
> paso es Δ = 2·V_fs / 2^b = V_fs / 2^(b−1). Es el error de un bit
> entero, y es el error más común al hacer cuentas de cuantización a
> mano.»

**P: «¿Por qué los niveles en el centro de las celdas?»**
> «Porque si se usara x_q = Δ·round(x/Δ), aparecerían N+1 niveles en vez
> de N, y el cero no sería representable en un cuantizador con un número
> par de niveles. Lo comprobamos con una rampa densa: 8 bits dan 257
> niveles distintos en vez de 256.»

**P: «¿Qué es el dither?»**
> «Es ruido deliberado de muy baja amplitud que se suma antes de
> cuantizar. Convierte un error determinista y correlacionado con la
> señal —que produce armónicos espurios, que se oyen como un tono
> cantarín— en ruido blanco. Pero **empeora** el SNR: pierde unos dB a
> cambio de que el error no tenga estructura. Es un intercambio, no una
> mejora gratis.»

### 6.3 Para Luis (el teorema y el código)

**P: «¿Por qué Django y no Streamlit?»**
> «Porque el enunciado pedía poder cargar audios, y subir un fichero y
> analizarlo es una operación de escritura. En el despliegue que hicimos
> en Vercel el disco es de solo lectura, y hubo que procesar el fichero
> en memoria. Con Django lo tenemos resuelto: es la misma aplicación,
> con URLs propias, descarga de informes y el audio servido como
> ficheros de verdad. El motor de cálculo, que es la parte interesante,
> no depende de ninguno de los dos.»

**P: «¿Cómo verificasteis que los números son correctos?»**
> «Con 164 comprobaciones automáticas, y no solo de que el código corre:
> comparan contra señales sintéticas de valor conocido. Por ejemplo, que
> un tono de amplitud 1 mida 1 en el espectro, que un metrónomo
> sintético a 120 BPM se detecte a 120 BPM, o que un tono de 3 000 Hz
> muestreado a 4 000 se pliegue a 1 000. Y las fórmulas están
> justificadas en el código: el 6,02 dB por bit es 20·log10(2), y el 1,76
> de plena escala sale de la potencia de la senoidal. Además, el DSP
> viene del proyecto anterior de la asignatura, que ya tenía sus
> pruebas, y las dos implementaciones dan cifras **idénticas**.»

**P: «¿Por qué pre-calcular los datos si se puede calcular en el
servidor?»**
> «Porque Vercel no es un servidor: cada visita ejecuta una función con
> un límite de diez segundos, y analizar las cinco pistas tarda veinte.
> Con el pre-cálculo la web responde en milisegundos. Y el efecto
> secundario fue bueno: al no poder depender de nada externo, el
> proyecto quedó autosuficiente.»

### 6.4 Para Camilo (el punto e y la honestidad)

**P: «¿Por qué no usasteis las bandas cerebrales?»**
> «Las que aparecen en el informe son bandas **sonoras** con los mismos
> nombres, calculadas sobre el audio. Atribuirles un significado
> cerebral sería inventar una equivalencia que no existe: el EEG mide
> actividad eléctrica en el scalp, y un fragmento de audio no tiene nada
> que ver con eso. Se pueden comparar las bandas como analogía visual,
> pero no como medida cerebral.»

**P: «Si tuvierais que mejorarlo, ¿qué haríais?»**
> «Dos cosas. La primera, **más de una pista por género**: con tres por
> género, el orden dejaría de depender tanto de la elección concreta. Y
> la segunda, **un análisis de sensibilidad de los pesos**, que mostrara
> en qué pesos cambia el orden. El índice actual es transparente, pero
> es un solo número, y un solo número siempre se puede cuestionar. Lo
> que **no** haríamos es añadir más géneros con una sola pista cada
> uno: eso da más apariencia de rigor sin darla.»

**P: «¿El repositorio es open source?»**
> «Sí, con el informe completo, las figuras y las pruebas. Es un
> proyecto académico, sin licencia. Y los clips de audio son extractos
> de obras con derechos de autor, solo para el análisis, y no se
> redistribuyen: por eso el repositorio se pondrá privado esta semana.
> Lo que sí es open source es todo el código.»

---

## 7. El código: qué mostra cada persona si lo preguntan

| persona | qué puede abrir y explicar en 30 segundos |
|---|---|
| **Ángel** | `nucleo/catalogo.py`: las cinco fichas con la investigación. "Aquí está por qué elegimos cada tema." |
| **Mariano** | `nucleo/primitivas.py`: la función `cuantizar` y `factor_de_escala`. "Aquí está la fórmula del factor de escala, con el porqué del 2^(b−1)." |
| **Luis** | `nucleo/primitivas.py`: `reconstruir_sinc` (la suma de senos cardinales) y `nucleo/dsp_audio.py`: `antialias`. "Aquí está el teorema implementado." |
| **Camilo** | `nucleo/comparativa.py`: `CRITERIOS_atencion` y `indice_atencion`. "Aquí están los cinco pesos, y aquí se ve que son públicos." |

Los cuatro knows dónde está lo suyo: eso es lo que hace que un grupo de
cuatro funcione.

---

## 8. El plan B: si algo falla

| lo que falla | lo que hacéis |
|---|---|
| **No hay internet** | `python manage.py runserver` (ya arrancado): *"tenemos también la versión local"*. |
| **El sonido no funciona** | las figuras y las tablas sostienen la presentación: *"les muestro el error medido, que es lo que el trabajo demuestra"*. La demo es el 15 % de la nota, no el 100 %. |
| **La web tarda o se cae** | a la pestaña local, sin drama. |
| **Alguien pregunta una cifra que no tienes** | abre el informe y búscala: es honesto y es mejor que inventar. |
| **Te quedas en blanco** | las 4 cifras de la §3 y las 5 transiciones de la §4. Mira al profesor y di *"vuelvo a la cifra"*. |
| **Un compañero se atasca** | **tú entras y sigues**. No lo dejes solo: "Yo retomo desde aquí" es siempre mejor que un silencio. |
| **El portátil se muere** | el repositorio está en GitHub y la web en Vercel: se levanta desde cualquier otro equipo con `git clone` y `python manage.py runserver`. |

---

## 9. La lista de un día antes

- [ ] `python construir.py` y `git push` (por si habéis tocado algo)
- [ ] `python nucleo/comprobar_todo.py` → **164/164 en verde**
- [ ] Comprobar que la web responde: https://generos-musicales-adc-dac.vercel.app
- [ ] Probar la demo de audio (original vs 8 bits) **con sonido**
- [ ] Repartir el §2: cada uno con su tramo impreso
- [ ] Ensayar **solo las transiciones** (la §4), que es donde se corta
- [ ] Cada uno: las 4 cifras de la §3 y su pregunta del §6
- [ ] Acordar quién abre y quién cierra
- [ ] **El viernes: recordatorio de poner el repositorio en privado**