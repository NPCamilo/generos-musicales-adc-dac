# GUION DE SUSTENTACIÓN — DSP aplicado a ADC-DAC sobre audio musical

> **⚠ Si sois un grupo de cuatro, usad [`GUION_CUATRO.md`](GUION_CUATRO.md).**
> Este documento es el guión completo de una persona; el de cuatro está
> repartido en tramos, con la señalización de qué tiene que estar en
> pantalla en cada momento, las transiciones entre ponentes y la
> distribución de las preguntas difíciles.
>
> **Cómo usar este documento.** El texto entre comillas es lo que se dice,
> palabra por palabra. Lo que va en *cursiva* son indicaciones de acción
> (qué hacer, dónde mirar, qué clic dar). Los **minutos** son la
> referencia: el bloque completo dura 75 minutos, y sobran 5 de margen en
> un turno de 80.
>
> **Antes de leer una línea más, mira el §0.** El día que no haya red, el
> día que el portátil no encienda el sonido o el día que el navegador no
> quiera cooperar, ahí está el plan B.

---

## 0. Antes de empezar (10 minutos antes)

**Prepara esto:**

| # | qué | cómo |
|---|---|---|
| 1 | La web | https://generos-musicales-adc-dac.vercel.app — **en una pestaña aparte**, no en la misma que vas a proyectar |
| 2 | El informe | `salida/informe.md` abierto en un editor, por si te preguntan por una cifra exacta |
| 3 | El plan B | `python manage.py runserver` **ya arrancado** en el portátil, con la URL `http://127.0.0.1:8000` en otra pestaña |
| 4 | El sonido | comprueba que los parlantes suenan: pon un audio de 8 bits y oye que se oye distinto. **Es la demo, no la puedes improvisar en el momento** |
| 5 | Las cifras | abre `docs/GUIA.md` §2 (la tabla de las cifras que hay que saber de memoria) en el móvil, por si te quedas en blanco |

**Los cuatro números que te repito hasta que se te graban:**

```
f_max de la barroca      1 881 Hz
f_s mínima del metal    23 332 Hz        (2·f_max)
y a 16 bits              3,052·10⁻⁵ V por nivel
mejor índice             80,1 / 100  →  Clásica · Barroca
```

**El verbo del proyecto, en una frase:** *caracterizar*.

---

## 1. Apertura (minuto 0-3)

*Abre la web en la portada. Saluda. No mires la pantalla todavía.*

> «Buenos días. Mi proyecto se titula **"DSP aplicado a ADC-DAC sobre audio
> musical"**, y la pregunta que responde es: **qué le pasa a una canción
> cuando la convierto a números y la vuelvo a convertir en sonido**.
>
> He tomado **cinco pistas** de cinco géneros distintos —barroca, metal,
> salsa, reggaetón y música popular colombiana—, les he pasado la cadena
> completa de conversión digital: **ADC, cuantizador y DAC**, les he
> aplicado el teorema de muestreo de **Nyquist-Shannon** medido sobre
> audio real, y las he comparado entre sí.
>
> Al final respondo a la pregunta del enunciado sobre el TDAH, y lo hago
> con las limitaciones declaradas: esto **caracteriza la música**, no
> mide la atención de ninguna persona. Y lo voy a ver, porque el mejor
> Convertidor del mundo es el que te deja **oír** la degradación.
>
> Empiezo por las cinco pistas.»

*Di la última frase mirando al profesor, no a la pantalla. Es lo que marca
la diferencia entre leer y presentar.*

---

## 2. Las cinco pistas y la investigación (minuto 3-10)

*Abre la portada. Señala las tarjetas de género.*

> «Cada pista es un fragmento de **12 segundos**, recortado con un
> criterio objetivo: el tramo de **mayor energía RMS** de la canción
> completa. No es arbitrario, y es el mismo criterio para los cinco, que
> es lo que hace que la comparación sea justa.
>
> El enunciado pide una investigación breve de cada género. Esta es:»

*Abre la ficha de cada género en la web, una a una, y di solo el dato
clave de cada una. No leas la tabla entera.*

| género | di esto |
|---|---|
| **Clásica · Barroca** | «Bach, Suite para violonchelo n.º 1 en Sol mayor, BWV 1007, de 1722. Un solo violonchelo, sin percusión, sin voz.» |
| **Metal** | «Megadeth, *Tornado of Souls*, del álbum *Youthanasia*, de 1990. Guitarra saturada.» |
| **Salsa** | «Frankie Ruiz y La Solución, *La Rueda*, de 1980, con La Solución. Percusión latina y montuno.» |
| **Reggaetón** | «Feid y ATL Jacob, *LUNA*, de 2023, del EP *Ferxxocalipsis*. Bombo sintetizado y voz limpia.» |
| **Popular colombiana** | «Fredy Montoya con Luisito Muñoz, *Ángel o Demonio*, de 2016. La cantina o depecho de la costa.» |

> «Y hay una razón por la que elegí **estos** temas y no otros, y es la
> que importa para un trabajo de DSP: **cada uno representa a su género
> en lo que aquí se mide, que es el espectro**.
>
> El metal, por ejemplo: la saturación de la guitarra no es un efecto de
> timbre, es **multiplicar la onda por una función no lineal**, y eso
> genera armónicos de orden muy alto. Por eso el metal es el caso con
> más contenido agudo del conjunto, y el que peor se porta cuando se
> baja la frecuencia de muestreo. No lo elegí porque suene duro: lo
> elegí porque su espectro lo delata.
>
> Lo mismo al revés con la barroca: un instrumento solo, sin percusión y
> sin voz, es el perfil más limpio de los cinco, y por eso la usé como
> **referencia**: el caso en el que no hay nada que esconder.»

---

## 3. La cadena ADC-DAC (minuto 10-20)

*Abre la ficha del metal. Baja a la figura de cuantización.*

> «Este es el corazón del proyecto: la cadena de conversión, con lo que
> se mide en cada paso.
>
> La cadena es esta:»

*Aplica con el cursor o con la mano la secuencia de la figura: señal →
filtro antialiasing → muestreo → cuantizador → DAC.*

> «**El filtro antialiasing** es lo que separa una reconstrucción
> correcta de un desastre, y su corte va al **45 % de f_s/2**, no al
> 100 %, porque un filtro real no cae en vertical: si el corte estuviera
> en f_s/2, parte del contenido original se metería en la banda nueva y
> el aliasing no desaparecería del todo.
>
> **El muestreo** toma las muestras en los instantes del reloj, sin
> interpolar nada, que es lo que hace un ADC de verdad.
>
> **El cuantizador** es uniforme, con los niveles en los **centros** de
> las celdas, y satura en los extremos. Y aquí está el resultado:»

*Señala la tabla de bits de la ficha.*

> «Con un fondo de escala de ±1 voltio, el **factor de escala** es

```
y = V_fs / 2^(b-1) = 1 / 2^15 = 3,052 · 10⁻⁵ voltios por nivel
```

> Es el paso entre niveles. En 16 bits son 65 536 niveles repartidos en
> 2 voltios, y el error de redondeo está **acotado a ±Δ/2**, o sea
> ±15,26 microvoltios.
>
> Y ahora, un detalle que es la diferencia entre un ADC y una cifra
> bonita: **los bits nominales no son los bits efectivos**. El SNR
> teórico de 16 bits son 98 decibelios, pero el **medido** en el metal
> es de 83. ¿Por qué? Porque la señal no llena el rango: está a
> −2,4 dBFS, y esa carga se paga. Los **bits efectivos** son 13,5, no
> 16. Un ADC de 16 bits al que le metes una señal que solo ocupa el 20 %
> del rango no te da 16 bits: te da menos. Eso está medido aquí, no
> supuesto.
>
> Y en la tabla de códigos binarios están las muestras con su código de
> 16 bits, que es lo que el convertidor entrega de verdad: un entero, no
> una tensión.»

*Abre la figura de la escalera de cuantización.*

> «Aquí se ve la escalera. Y fíjense en el panel del error, en
> microvoltios: son escalones de medio Δ, y nunca se salen de la banda.
> Eso es el error de cuantización: **acotado, determinista y no
> gaussiano**.»

*Abre la figura de la cadena (sección 5 de la ficha).*

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

## 4. Nyquist-Shannon sobre audio real (minuto 20-28)

*Abre la figura de muestreo del metal (la de la ficha).*

> «Y aquí está el teorema, medido. Esta gráfica es un barrido: se
> submuestrea la misma pista a distintas frecuencias y se mide el error
> de la reconstrucción, con y sin filtro antialiasing.
>
> La línea naranja es lo que pasa **sin** filtrar: el contenido que
> está por encima de f_s/2 se pliega dentro de la banda. Y el pliegue
> es **irreversible**: no hay ningún filtro que lo deshaga después,
> porque la información se mezcló al muestrear, no al filtrar.
>
> La línea verde es lo que pasa **con** filtro. Y el hueco entre las dos
> es, literalmente, **el precio de no filtrar**.
>
> Miren el eje de la derecha: el porcentaje de energía que queda por
> encima de f_s/2. Cuando esa energía es cero, el teorema se cumple y no
> hay aliasing posible. En el metal, con f_s = 11 666 Hz —la mitad de lo
> que hace falta— todavía queda un **1 % de la energía** fuera de banda,
> y el error de reconstrucción se multiplica por **tres**: del 1,2 % al
> 4,0 %. Ese 1 % de energía, al plegarse, aterriza en un sitio donde
> machaca el pico de la señal, y por eso el error crece mucho más que
> la energía.
>
> Una cosa que quiero decir aquí, porque es la diferencia entre un
> trabajo de DSP y un ejercicio: el error de aliasing **no baja de
> forma monótona** al subir f_s. Depende de **qué** contenido se pliega y
> **dónde** cae al plegarse. Un componente estrecho que cae en una zona
> silenciosa apenas se nota; un transitorio que cae justo encima de un
> pico, mucho. La tendencia general es clarísima, pero la curva tiene
> dientes, y decirlo de otra cosa sería mentir en la gráfica.»

---

## 5. Los resultados por género (minuto 28-36)

*Abre la comparativa. Señala la tabla.*

> «Aquí están los cinco, con todas las cifras. Recorro lo importante:
>
> **f_max**, la frecuencia hasta donde llega el contenido útil. La
> barroca llega a 1 881 Hz; el reggaetón a 7 943. Y aquí hay un matiz
> metodológico que publiqué en el informe: `f_max` **depende de un
> criterio**, y por eso el criterio está escrito y hay una tabla de
> sensibilidad. Con el criterio de energía acumulada en vez del de
> umbral, al reggaetón le sale 17 290 Hz. No es un error: son dos
> preguntas distintas —"¿hasta dónde llega el contenido significativo?"
> y "¿hasta dónde llega la energía?"— y aquí se publica la respuesta a
> las dos.
>
> **f_s mínima**, que es el doble de f_max. Para la pista más exigente,
> el metal, son 23 332 Hz, y para el reggaetón 15 887. **Los 44,1 kHz del
> CD sobran para las cinco**; lo que no alcanza es la mitad, 22,05 kHz,
> porque el contenido del metal, que llega a 11 666 Hz, ya no cabe y se
> plegaría. Por eso el CD se fijó en 44,1 kHz y no en 22,05.
>
> **Centroide espectral**, que es el brillo de la pieza: 290 Hz en la
> barroca frente a 1 116 Hz en la popular colombiana. Es la cifra que
> después va a decidir el punto (e).
>
> Y **factor de cresta**, que es pico/RMS, o sea la dinámica. 5,99 en la
> barroca frente a 2,81 en la popular. Aquí hay un aviso honesto que
> está en el informe: la compresión con limitador es una práctica de
> **estudio moderno**, así que ese criterio mide en parte la época de
> producción y no solo el género.»

---

## 6. El punto (e): la comparación y el veredicto (minuto 36-50)

*Abre la gráfica de los cinco espectros comparados (la de arriba).*

> «Esta es la gráfica que pide el punto (e): **los cinco espectros de
> magnitud en el mismo eje**. Cada uno normalizado a su propio pico y
> suavizado, para comparar las **formas** y no los niveles.
>
> Miren cómo se separan. La barroca, en azul, es una línea que cae en
> picado: a los 4 kHz ya está 37 dB por debajo, y a los 8 kHz, 48. El reggaetón, en rosa, es
> la que aguanta hasta 17 kHz. Y en la versión logarítmica, abajo, está
> sombreada **la banda de la voz humana, de 300 Hz a 3,5 kHz** —que
> es justo la banda en la que el estudiante tiene que seguir la voz del
> profesor.»

*Abre la figura de las bandas y luego la del índice.*

> «Y aquí está la comparación propiamente dicha, la energía por bandas.
> La popular colombiana tiene el 72 % de su energía en la banda de
> 250 Hz a 2 kHz, que es justo donde está la voz humana: es una canción
> con cantante, y el cantante está exactamente donde está la voz del
> profesor.
>
> Para ordenar los cinco construí un **índice de atención** con cinco
> criterios, y lo importante es que **los pesos están a la vista**, en la
> tabla. Un índice con pesos escondidos no sirve ni para comparar ni
> para discutir.»

*Abre la tabla de criterios en la web.*

> «Los cinco criterios, con su peso y su justificación:
>
> - **Tempo en la ventana de 60 a 90 BPM**, peso 25. La literatura
>   relaciona un tempo moderado con menor activación.
> - **Bajo centroide espectral**, peso 20. El contenido agudo activante
>   tapa la voz del profesor.
> - **Poca energía entre 2 y 8 kHz**, peso 20. Ahí viven las percusiones
>   de ataque: timbales, charles, platillos.
> - **Rango dinámico**, peso 20. Una señal comprimida no tiene silencios:
>   el oído no descansa.
> - **Poca energía en la banda de la voz**, peso 15. Es el criterio más
>   específico del contexto: la misma banda en la que hay que seguir al
>   profesor.
>
> Y el resultado es este:»

*Abre la figura del veredicto.*

> «**La barroca gana, con 80,1 de 100.** El metal queda segundo con 63,9,
> y las dos peores son la popular colombiana y la salsa: las dos tienen
> cantante.
>
> La razón es una sola y se ve en la gráfica: el espectro de la barroca
> es el más oscuro. Centroide de 290 Hz, casi nada por encima de 4 kHz.
> Deja libre la banda donde se mueve la voz del profesor. Eso es lo que
> significa 80,1 puntos.»

---

## 7. La honestidad: qué NO demuestra (minuto 50-58)

*Esta es la parte que más puntos suma. Dímela DESPUÉS del veredicto,
nunca antes, y míralo al profesor.*

> «Ahora, y esto es lo que más me importa decir: **qué es este trabajo y
> qué no es**.
>
> Este trabajo **caracteriza propiedades acústicas** de cinco grabaciones
> y las ordena con un criterio explícito y publicable. Eso es todo.
>
> Esto **no** es un estudio clínico. **No** he evaluado a ningún
> estudiante, **no** he medido su atención, y **no** puedo afirmar que
> una pieza mejore el TDAH de nadie. Ese paso —de "suena más tranquila"
> a "le va a mejor a una persona"— exige personas, un grupo de control y
> un protocolo, y eso no cabe en un trabajo de DSP. Si alguien me lo
> preguntara, la respuesta sería que es una **hipótesis fundamentada**,
> no una prescripción.
>
> Y hay una segunda analogía que no quiero que se me escape: en el
> informe aparecen unas bandas que se llaman delta, theta, alfa, beta y
> gamma, como las del EEG. **Son bandas sonoras.** Se calculan sobre el
> audio y se leen como "qué banda del sonido está activada". Atribuirles
> un significado cerebral sería inventar una equivalencia que no existe.
>
> Y una tercera limitación, la más incómoda: hay **una pista por
> género**. Con otra canción, el orden puede cambiar. Lo que sí comprobé
> es que las tres características que más pesan son robustas entre los
> cinco, y que el tempo no lo es: en la barroca, que no tiene percusión,
> el detector de tempo no encuentra pulso con confianza, y en vez de
> inventarse un número, ese criterio se puntúa como neutro y se dice
> que no es medible.»

---

## 8. La demostración en vivo (minuto 58-68)

*Abre la ficha de un género, con la música puesta de fondo en un volumen
bajo. Si puedes, pon el audio en el portátil y en la web a la vez.*

> «Y ahora, en vez de gráfica, **oído**. En la ficha del metal hay cuatro
> audios: el original, el cuantizado a 12 bits, el cuantizado a 8 bits y
> la cadena telefónica a 8 kHz.
>
> Primero el original.»

*Reproduce el original 5 segundos. Pausa.*

> «Ahora el mismo audio cuantizado a **8 bits**:»

*Reproduce el de 8 bits.*

> «Se oye el ruido de cuantización. Eso no es un efecto del programa:
> es el error del cuantizador, que es determinista y no gaussiano, y por
> eso se oye como un siseo y no como ruido blanco.
>
> Y ahora el **telefónico**: 8 kilohertz y 8 bits, que es lo que pasaba
> por una línea de teléfono analógica. Fíjense en que no solo suena más
> grave: **ha desaparecido toda la mitad del espectro**. Y el SNR de la
> cadena cae de 83 dB a 36 dB.
>
> Es la mejor forma de ver por qué el enunciado pide un factor de escala
> en voltios y en bits: no son dos formas de decir lo mismo. Los voltios
> son la escala física; los bits son cuántos niveles hay. Y entre las dos
> cosas está la resolución, que es lo que determina si el oyente
> distinguido nota la diferencia.»

---

## 9. El código y cómo está hecho (minuto 68-74)

*Abre el repositorio en GitHub, en otra pestaña. Muestra la estructura.*

> «Un minuto sobre cómo está construido, porque creo que es parte del
> trabajo.
>
> El proyecto es un **motor de cálculo** y una **aplicación web** por
> encima. El motor no depende de la web: se ejecuta solo, genera el
> informe y las figuras, y hay una suite de **164 comprobaciones
> automáticas** que verifican las cifras contra valores analíticos
> conocidos.
>
> Tres cosas que me parecen lo más interesante de haber resuelto:»

*Abre `nucleo/primitivas.py` en GitHub.*

> «**Una**: el parser de WAV está escrito desde cero, sin `soundfile` ni
> `librosa`, para no añadir dependencias. Soporta PCM de 8, 16, 24 y 32
> bits y coma flotante. Y al hacerlo se ve lo que hace de verdad un ADC:
> los bytes se convierten a enteros con signo y se dividen.
>
> **Dos**: este proyecto se despliega en **Vercel**, y Vercel no es un
> servidor: cada visita ejecuta una función con un límite de diez
> segundos y el disco de solo lectura. Eso obligó a pre-calcular los
> números y las figuras, y a hacer que el proyecto fuera
> **autosuficiente**. Y con esa restricción terminó siendo un proyecto
> mejor: ahora se clona y funciona en cualquier parte.
>
> **Tres**, y esta me gusta más porque es de las pruebas: las pruebas
> encontraron **siete errores reales** en mi propio código, y están
> documentados. El mejor fue que yo suavizaba el espectro **promediando
> decibelios**, y eso no es promediar potencias: el pico de un tono se
> "promediaba" a 92 decibelios por debajo, y mi medida de f_max daba
> **cero hercios** para un tono de 500. Lo encontré porque la prueba
> comparaba un tono sintético con el valor esperado. Ese tipo de
> error no se ve en una gráfica: se ve en una prueba.»

---

## 10. Cierre (minuto 74-78)

*Vuelve a la portada de la web. Pausa un segundo antes de hablar.*

> «Resumo.
>
> Cinco géneros, cinco perfiles espectrales distintos, medidos con la
> cadena completa de conversión digital y con el teorema de
> Nyquist-Shannon aplicado a audio real.
>
> El factor de escala de un convertidor de 16 bits con fondo de escala
> de ±1 voltio es **3,052 · 10⁻⁵ voltios por nivel**, con el error
> acotado a la mitad de eso, y los bits **efectivos** son menos que los
> nominales en cuanto la señal no llena el rango.
>
> Y del punto (e): con un índice de cinco criterios de pesos
> publicados, la mejor opción como música de fondo para estudiar es la
> **Clásica · Barroca**, con 80,1 de 100, porque su espectro es el más
> oscuro y deja libre la banda de la voz. Es una hipótesis con un
> criterio publicable, no una afirmación clínica, y el informe dice
> exactamente eso.
>
> Está todo en el repositorio, con el informe completo, las figuras y
> las 164 comprobaciones. Muchas gracias.»

*Si hay tiempo y preguntan: "el código y el informe están enlazados desde
aquí". Si no hay tiempo, para ahí. **No alargues el cierre.**

---

## 11. Preguntas: las 12 que te van a hacer, y la respuesta

### 1. «¿Por qué no usaste las bandas cerebrales?»

> «Las que aparecen en el informe son bandas **sonoras** con los mismos
> nombres, calculadas sobre el audio. Atribuirles un significado
> cerebral sería inventar una equivalencia que no existe: el EEG mide
> actividad electrical en el scalp, y un fragmento del audio no tiene nada que
> ver con eso. Se pueden comparar las bandas como analogía visual, pero
> no como medida cerebral. Y por eso el punto (e) no dice "se activa la
> banda alfa", sino "en qué banda del sonido está la energía".»

### 2. «¿La música cura el TDAH?»

> «No, y no lo afirmamos. La literatura de la que nos apoyamos habla de
> efectos **pequeños, inconsistentes y dependientes de la tarea**; el
> "efecto Mozart" es un ejemplo de efecto pequeño, y el antecedente más
> citado de la idea del contenido de baja frecuencia es el del ruido
> marrón a 60-70 Hz de Brown et al. (2001). Lo que este trabajo hace es
> caracterizar la música y publicar el criterio con el que la ordena. El
> resto es una hipótesis, y así está escrito en el informe.»

### 3. «¿Y si cambias los pesos del índice?»

> «El orden puede cambiar, y por eso los pesos están a la vista: un
> índice con pesos escondidos no sirve ni para comparar ni para
> discutir. Con los pesos actuales, la barroca gana por 16 puntos al
> segundo, y esa diferencia es demasiado grande para que un cambio
> razonable de pesos la dé vuelta. Lo único que la cambiaría es el
> criterio de tempo, y ese está medido como no medible en la barroca. Si
> usted quisiera, podemos probar otros pesos y ver qué pasa: es
> question de un minuto, con el código.»

### 4. «Una pista por género no es muy riguroso.»

> «Es la limitación más importante y está escrita en el informe, en la
> sección de condiciones. Con otra canción el orden puede cambiar. Lo
> que sí comprobé es que las tres características que más pesan —brillo,
> banda de la voz y rango dinámico— son robustas entre los cinco, y que
> el tempo no. Y el enunciado pide audios cortos, así que el
> fragmento de 12 segundos es lo que corresponde; lo que hice fue elegir
> el tramo con un criterio publicado —el de mayor energía RMS— en lugar
> de al azar.»

### 5. «¿Por qué f_max depende del criterio? Eso lo hace subjetivo.»

> «Depende de cualquier decisión, y prefiero que se vea. Mido dos
> cosas: el **umbral** —la frecuencia más alta que sigue estando 40 dB
> por debajo del pico— y la **energía acumulada** —el 99,9 % de la
> energía—. En el metal casi coinciden; en el reggaetón se separan
> mucho, porque el pico está en los graves y la energía de una
> masterización moderna se concentra abajo. Publico las dos y la tabla
> de sensibilidad al umbral. Un resultado con un criterio escondido no
> se puede discutir; este se puede discutir en cada número.»

### 6. «¿Y no es grave que la música moderne suene comprimida? ¿Eso no
falsea la comparaciónón?»

> «Sí lo es, y está anotado como sesgo del criterio. La compresión con
> limitador es una práctica de estudio moderno, así que el factor de
> cresta mide en parte la época de producción y no solo el género: por
> eso el reggaetón y la popular, que son de 2023 y 2016, tienen cresta
> baja, mientras que la barroca, grabada con otros criterios, tiene 5,99.
> Podría haber eliminado ese criterio, pero preferí publicarlo y
> señalarlo, porque un criterio que no se ve es donde se esconden las
> manipulaciones.»

### 7. «¿Por qué 12 segundos?»

> «Por dos razones. La primera es el enunciado: pide audios cortos. La
> segunda es de medida: doce segundos a 44,1 kHz dan una resolución en
> frecuencia de unos 0,08 Hz, muy por debajo de lo que hace falta para
> caracterizar el espectro, y caben en una figura legible. Y el corte
> no es al azar: se elige el tramo de mayor energía RMS, con el mismo
> criterio para los cinco.»

### 8. «¿Qué pasa si la canción tiene silencio al principio?»

> «Justo por eso el criterio es el de energía: el silencio no se
> analiza. Y hay un detalle técnico: el tramo se recorta antes de
> quitar la componente continua, porque si no, el offset de la
> grabación se cuela como una delta en cero y falsea la energía de la
> banda subgrave, que es justo una de las que comparo.»

### 9. «¿Cómo verificaste que los números son correctos?»

> «Con 164 comprobaciones automáticas, y no solo de que el código
> corre: comparan contra señales sintéticas de valor conocido. Por
> ejemplo, que un tono de amplitud 1 mida 1 en el espectro, que un
> metrónomo sintético a 120 BPM se detecte a 120 BPM, que un tono de
> 3 000 Hz muestreado a 4 000 se pliegue a 1 000, o que el cuantizador
> dé el SNR teórico. Y las fórmulas están justificadas en el código:
> el 6,02 dB por bit es `20·log10(2)`, y el 1,76 de plena escala sale
> de la potencia de la senoidal. Además, todo el DSP del proyecto viene
> del proyecto anterior de la asignatura, que ya tenía sus propias
> pruebas, y las cifras que dan las dos implementaciones son
> **idénticas** hasta la cuarta cifra decimal.»

### 10. «¿Por qué Django y no Streamlit, que ya usaste?»

> «Porque el enunciado pedía poder cargar audios, y subir un fichero
> y analizarlo es una operación de escritura. En Streamlit eso funciona,
> pero en el despliegue que hice en Vercel el disco es de solo lectura
> y hay que procesar el fichero en memoria. Con Django lo tengo
> managed: es la misma aplicación, pero con URLs propias, descarga de
> informes y el audio servido como ficheros de verdad. El motor de
> cálculo, que es la parte interesante, no depende de ninguno de los
> dos.»

### 11. «¿El proyecto está en GitHub? ¿Es open source?»

> «Sí, está en GitHub, con el informe completo, las figuras y las
> pruebas. Es un proyecto académico, sin licencia. Y los clips de audio
> son extractos de obras con derechos de autor, solo para el análisis, y
> no se redistribuyen: por eso el repositorio va a ponerse privado esta
> semana. Lo que sí es open source es todo el código.»

### 12. «Si tuvieras que mejorarlo, ¿qué harías?»

> «Dos cosas. La primera, **más de una pista por género**: con tres
> por género, el orden dejaría de depender tanto de la elección
> concreta, y podría publicar la varianza. Y la segunda, **un índice
> con pesos que se puedan discutir uno a uno**, con un análisis de
> sensibilidad que mostrara en qué pesos cambia el orden. El índice
> actual es transparente, pero es un solo número, y un solo número
> siempre se puede cuestionar. Lo que no haría es añadir más genres
> con una sola pista cada uno: eso da más apariencia de rigor sin
> darla.»

---

## 12. Plan B: si algo falla

| lo que falla | lo que haces |
|---|---|
| **No hay internet** | `python manage.py runserver` (ya lo tienes arrancado). Di: *"tengo también la versión local"*. |
| **El sonido no funciona** | las figuras y las tablas siguen sosteniendo toda la presentación; di: *"les muestro el error medido, que es lo que el trabajo demuestra"*. La demo de audio es el 15 % de la nota, no el 100 %. |
| **La web tarda o se cae** | vuelve a la pestaña local. |
| **Te preguntan una cifra que no tienes** | abre el informe y búscala. Es honesto y es mejor que inventar: *"lo tengo aquí en el informe, en la sección 3"*. |
| **Se te queda blanco** | las cuatro cifras del §0 y las tres ideas del §11. Mira el profesor y di *"vuelvo a la cifra"*. |
| **Te preguntan algo que no hiciste** | *"no está implementado, pero el módulo donde iría es X y necesitaría Y"*. |
| **El portátil se muere** | el repositorio está en GitHub y la web en Vercel: se levanta desde cualquier otro equipo con `git clone` y `python manage.py runserver`. |

---

## 13. Las tres ideas que tienes que poder decir en cualquier momento

1. **El aliasing es irreversible**: pliega el contenido dentro de la
   banda, y no hay filtro que lo deshaga después.
2. **El factor de escala en voltios y los bits son dos cosas
   distintas**: `y = V_fs/2^(b-1)` es la escala física, y los bits
   efectivos son los que la señal real consigue, no los del catálogo.
3. **Un índice con los pesos a la vista se puede discutir; uno con los
   pesos escondidos, no.** Y esto vale igual para el punto (e) del
   enunciado y para un proyecto entero.

---

## 14. La lista de un día antes

- [ ] `python construir.py` (por si has tocado algo) y `git push`
- [ ] `python nucleo/comprobar_todo.py` → 164/164 en verde
- [ ] Comprobar que la web responde: https://generos-musicales-adc-dac.vercel.app
- [ ] Probar la demo de audio (original vs 8 bits) con sonido
- [ ] Tener el informe abierto y `docs/GUIA.md` a mano
- [ ] Repasar las 4 cifras del §0 y las 12 preguntas del §11
- [ ] Repasar el §0 del GUIÓN (el plan B) por si acaso
- [ ] El viernes: recordatorio de poner el repositorio en privado