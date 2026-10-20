# DSP aplicado a ADC-DAC sobre audio musical

Cinco géneros musicales (Clásica-Barroca, Metal, Salsa, Popular colombiana
y Reggaetón) analizados con la cadena completa de conversión digital
**ADC → cuantizador → DAC**, el teorema de muestreo de **Nyquist-Shannon**
medido sobre audio real, y una comparación entre los cinco con un índice
de atención cuyos pesos están publicados.

Es el proyecto de Nyquist-Shannon (`../Nyquist_Shannon/`) aplicado a
**música de verdad**: allí las señales eran series de Fourier y se sabía
`f_max` por fórmula; aquí el `f_max` hay que **medirlo**, y esa es la
parte nueva.

## Qué hay dentro

| carpeta | qué es |
|---|---|
| `nucleo/` | el motor de cálculo: parser de WAV, DSP, análisis, comparativa, figuras e informe. No depende de Django. |
| `motor/` | la aplicación web (vistas y plantillas de Django). |
| `dsp_web/` | el proyecto Django (settings, urls). |
| `api/` | la entrada WSGI para Vercel. |
| `public/` | los ficheros estáticos que el servidor sirve tal cual. |
| `audio/` | las cinco pistas (12 s cada una) y `descargas.json`, con la procedencia de cada una. |
| `salida/` | el entregable: `informe.md`, `datos.json` y 39 figuras en PNG a 300 dpi. |
| `docs/` | `GUIA.md` (la guía de defensa) y `PUBLICAR.md` (cómo desplegarlo). |

## Se ejecuta así

```bash
# el motor, sin la web
python -m nucleo.informe         # escribe salida/informe.md y las figuras
python -m nucleo.comparativa     # la comparación por consola
python -m nucleo.descarga        # (re)baja las cinco pistas

# la web
python manage.py runserver       # http://127.0.0.1:8000

# las comprobaciones
python nucleo/comprobar_todo.py  # 164 comprobaciones, en 4 suites

# preparar el despliegue
python construir.py               # regenera el informe, las figuras y datos.json
```

## Publicarlo en GitHub + Vercel

La guía completa está en **[`docs/PUBLICAR.md`](docs/PUBLICAR.md)**. El
resumen:

1. `python construir.py` — deja el informe, las figuras y
   `salida/datos.json` listos para subirlos.
2. `git add . && git commit && git push` — el repositorio **tiene que
   llevar `salida/`**, porque en Vercel no se puede calcular nada en cada
   visita (la función tiene 10 s y el disco es de solo lectura).
3. En Vercel: *Add New → Project*, importar el repositorio, y en
   *Environment Variables* poner `DJANGO_SECRET_KEY`.

> **Los clips de `audio/` tienen derechos de autor.** Si el repositorio
> es público, comenta `audio/*.wav` en el `.gitignore` antes de subirlo.
> La web sigue funcionando; solo se pierde la parte de "escúchalo".

## Requisitos

`numpy`, `scipy`, `matplotlib` (ya están en el entorno) y, para la web,
`django`. Para descargar las pistas: `yt-dlp` y `imageio-ffmpeg`
(este último da el `ffmpeg` que hace falta para convertir a WAV).

La biblioteca `Nyquist_Shannon/`, que está un nivel más arriba, se usa
desde `nucleo/_rutas.py`, que la añade al `sys.path`: este proyecto **no
reimplementa** el DSP, lo toma prestado.

## Lo que hace cada módulo

| módulo | qué hace |
|---|---|
| `nucleo/wav_io.py` | el parser de WAV, propio y sin dependencias: PCM de 8, 16, 24 y 32 bits y coma flotante de 32 y 64. |
| `nucleo/dsp_audio.py` | el espectro con la normalización correcta, la medida de `f_max`, el filtro antialiasing, la reconstrucción, el tempo por autocorrelación y el índice de atención. |
| `nucleo/catalogo.py` | las cinco fichas: músico, obra, año, instrumentación y fuentes. |
| `nucleo/analisis.py` | el pipeline por pista: señal, espectro, muestreo, cuantización, cadena ADC-DAC, ritmo y atención. |
| `nucleo/comparativa.py` | la comparación entre los cinco y el veredicto del punto (e), con sus condiciones y sus avisos. |
| `nucleo/figuras.py` | las 39 figuras, con el tema visual del proyecto `Laboratorio_ADC_DAC`. |
| `nucleo/informe.py` | el `salida/informe.md`, escrito desde los mismos datos que dibujan las figuras. |

## Una nota sobre las pistas

Los clips son extracts de 12 segundos de obras con derechos de autor,
descargados **solo para el análisis académico** de este trabajo. No se
redistribuyen: el repositorio los trae para poder repetir las medidas, y
`audio/descargas.json` deja constancia de cuál es cada una.
