# Especificación del proyecto

> Este fichero es la especificación que el proyecto tiene que cumplir. Es
> el enunciado tal como se recibió, con las precisiones que se acordaron
> durante el desarrollo, y es la referencia contra la que se revisa el
> código.

## El enunciado, punto por punto

**Objetivo:** identificar e interiorizar el tema de DSP aplicado a ADC-DAC
sobre archivos WAV.

**Entrega:** jueves 22 de octubre de 2026, de 09:00 a 11:00.

### a. Cargar audios cortos en formato WAV

> Permita cargar audios cortos en formato Wav.

**Cómo se cumple:**

- `nucleo/wav_io.py` tiene un parser de WAV propio, sin dependencias
  externas, que admite PCM de 8, 16, 24 y 32 bits y coma flotante de 32
  y 64 bits, con downmix a mono.
- La web (página `/subir/`) acepta un WAV del usuario y lo analiza con
  el mismo instrumental que el catálogo.
- El parser funciona también sobre bytes en memoria, que es lo que
  necesita el despliegue en Vercel, donde el disco es de solo lectura.

### b. Cinco géneros, con investigación

> Cargar cinco tipos de género musical, en el cual serán libres de
> escoger el músico, clásico, opera, sinfónica, filarmónica, orquesta,
> banda, y de hacer manipulación de las variables.

**Cómo se cumple:**

- `nucleo/catalogo.py` tiene una ficha por género con el músico, la obra,
  el año, el compositor, la instrumentación, el tempo esperado, la banda
  característica, el motivo por el que ese tema representa al género en el
  espectro, y las fuentes consultadas.
- Los cinco géneros del enunciado, con el tema elegido para cada uno:
  Clásica-Barroca, Metal, Salsa, Popular colombiana (la "cantina") y
  Reggaetón.

### c. Graficar x(t), muestrear con FFT, Nyquist y espectro de magnitud

> Una vez cargados los archivos van a graficar la señal x(t), luego
> deberán aplicar la técnica del muestreo haciendo uso de [FFT] y del
> teorema Nyquist Shannon e incluya el espectro de magnitud.

**Cómo se cumple:**

- La señal x(t) se dibuja completa, con un detalle de 20 ms con las
  muestras marcadas.
- El espectro de magnitud se calcula con FFT de 2^20 bins y ventana
  Hann, corregida por ganancia coherente, y se dibuja en dB.
- `f_max` se mide, con un criterio publicado y con un control por
  energía acumulada.
- El teorema de Nyquist-Shannon se mide: barrido de cuatro frecuencias de
  muestreo, con y sin filtro antialiasing, reconstruyendo con la suma de
  senos cardinales.

### d. Cuantización, factor de escala y resolución

> Seguidamente aplicarán a dichas señales cargadas la técnica de
> cuantización para obtener el factor de escala (y) en (V) y en bits,
> sírvanse incluir en el muestreo x(n) los bits e identifiquen el valor
> de resolución para un ADC-DAC.

**Cómo se cumple:**

- El factor de escala se da en las dos unidades que pide el enunciado:
  `y = V_fs / 2^(b-1)` en voltios por nivel, y el número de bits.
- La tabla de códigos binarios muestra x(n) con sus bits, que es lo que
  el convertidor entrega de verdad.
- La resolución se da en voltios por nivel, en número de niveles, en SNR
  teórico, en SNR medido y en bits efectivos, para 8, 12, 16 y 24 bits.
- El presupuesto de error reparte la potencia del error entre las
  etapas de la cadena.

### e. Comparar las frecuencias de cada género y concluir para el TDAH

> Encuentre el valor de frecuencias de cada género musical, compárelos en
> una misma gráfica y determine según la gráfica qué género aporta
> mejores frecuencias en la patología del TDH de un estudiante.

**Cómo se cumple:**

- Los cinco espectros de magnitud están en una misma gráfica, y la
  energía por bandas en otra.
- El índice de atención ordena los cinco con cinco criterios cuyos pesos
  están publicados, y cada criterio apunta a su fuente. Las fuentes
  viven en `nucleo/fuentes.py`, y la portada de la web las muestra.
- El veredicto llega con sus condiciones y con los tres límites de lo
  que el trabajo no demuestra.

## Lo que el trabajo NO tiene que hacer, y sí dice que no hace

- No es un estudio clínico, y no mide la atención de ninguna persona.
- No afirma que una pieza mejore el TDAH de nadie.
- No usa las bandas cerebrales como medida cerebral: las que aparecen en
  el informe son bandas sonoras con los mismos nombres.

## Los criterios de aceptación

| criterio | cómo se comprueba |
|---|---|
| el código no depende de nada fuera del repositorio | `git clone` en limpio, `pip install -r requirements.txt`, `python -m nucleo.informe` |
| las cifras son correctas | `python nucleo/comprobar_todo.py` (164 comprobaciones) |
| la web funciona en un entorno serverless | despliegue en Vercel, con el disco de solo lectura y el límite de 10 s |
| el informe, las figuras, el PDF y la web dicen lo mismo | las cuatro salidas se generan desde el mismo análisis |
