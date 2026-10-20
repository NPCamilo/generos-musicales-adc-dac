# Publicar el proyecto: GitHub + Vercel

> Esta guía explica cómo dejar el proyecto en GitHub y con la web
> desplegada en Vercel, sin servidor propio y sin pagar nada.

---

## 1. Las tres ideas que hay que tener claras antes de empezar

**1. Vercel no es un servidor: es una plataforma *serverless*.**
Cada visita a la web ejecuta una función en una máquina que se enciende,
atiende la petición y se apaga. Tres consecuencias:

| | en un servidor normal | en Vercel |
|---|---|---|
| tiempo de una función | sin límite práctico | **10 s** (plan gratuito) |
| disco | de lectura y escritura | **solo lectura** |
| memoria entre peticiones | sí | **no** |

**2. Por eso el análisis se calcula ANTES de desplegar.**
Analizar las cinco pistas tarda unos 20 segundos: en Vercel no cabría en
una función. La solución es la de siempre en estos casos: **calcular
antes y servir después**. El script `construir.py` deja el resultado en
dos sitios:

- `salida/datos.json` → los números (102 KB)
- `salida/*.png` → las 39 figuras, ya dibujadas

y la web los lee. Así, una visita responde en **1-7 milisegundos**.

**3. El repositorio tiene que llevar los resultados.**
`salida/` y `public/` se suben a GitHub. Eso es lo que hace que la web
funcione: no depende de que haya una máquina con SciPy y 5 MB de audio
preparados.

---

## 2. Qué se sube a GitHub y qué no

| sí | no | por qué |
|---|---|---|
| `nucleo/`, `motor/`, `dsp_web/`, `api/` | `__pycache__/`, `*.pyc` | están en el `.gitignore` |
| `salida/` (el informe y las figuras) | `db.sqlite3` | no hay base de datos |
| `public/estilo.css` | `audio/subido_*` | son de las pruebas |
| `vercel.json`, `requirements.txt`, `construir.py` | `nucleo/test_*.py` en el despliegue | no hacen falta en el servidor (están en `.vercelignore`) |
| `docs/`, `README.md` | | |
| **`audio/*.wav` — decide tú** | | **ver el aviso de abajo** |

> ### ⚠ Los audios tienen derechos de autor
>
> Los cinco clips son extractos de 12 s de obras comerciales (Black
> Sabbath, Frankie Ruiz, Feid, Fredy Montoya) más una grabación de Bach.
> **Subirlos a un repositorio PÚBLICO es redistribuir material con
> derechos de autor**, y queda en tu nombre.
>
> Tienes tres salidas, y las tres son válidas:
>
> 1. **Repositorio privado.** Es lo más simple y no hay ningún problema.
>    Vercel tiene un plan gratuito que se puede conectar a un repo
>    privado.
> 2. **Repositorio público sin los audios.** Comenta la línea
>    `audio/*.wav` del `.gitignore`. La web sigue funcionando (los
>    números y las figuras están en `salida/`), y solo se pierde la
>    parte de "escúchalo". Para recuperarla en tu máquina, se vuelven a
>    bajar con `python -m nucleo.descarga`.
> 3. **Repositorio público con audios que sí se puedan redistribuir.**
>    La grabación de Bach de la Netherlands Bach Society es de dominio
>    público (proyecto "All of Bach"), así que esa sí. Para las otras
>    cuatro, hay substitutes con licencia libre en Wikimedia Commons o
>    en Internet Archive; el programa no cambia, solo los ficheros.
>
> La decisión es tuya, pero que sea consciente.

---

## 3. Los pasos

### 3.1 Preparar el proyecto

```bash
cd "COMUNICACIONES I/Generos_Musicales_ADC_DAC"

# regenerar el informe, las figuras y los datos precalculados
python construir.py

# comprobar que todo está en verde
python nucleo/comprobar_todo.py
```

### 3.2 El repositorio en GitHub

Lo más limpio es que **el repositorio sea la carpeta del proyecto**:

```bash
cd "COMUNICACIONES I/Generos_Musicales_ADC_DAC"
git init
git add .
git status              # revisa qué se va a subir
git commit -m "DSP aplicado a ADC-DAC sobre audio musical"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/REPO.git
git push -u origin main
```

Si lo que quieres es subir **la carpeta `COMUNICACIONES I/` completa**
(para que el repositorio tenga los cuatro proyectos), entonces el
repositorio es esa carpeta y hay que decidir si se sube el resto. En
ese caso, la raíz de Vercel tiene que ser
`Generos_Musicales_ADC_DAC` (ver el punto 3.4).

> Ojo con `git add .` en `COMUNICACIONES I/`: ahí están los proyectos
> anteriores, con sus `__pycache__` y sus salidas. Si subes la carpeta
> completa, el repositorio puede pesar bastante y conviene limpiar los
> `__pycache__` antes.

### 3.3 Conectar Vercel

1. Entra en [vercel.com](https://vercel.com) y entra con la cuenta de
   GitHub.
2. **Add New → Project** → importa el repositorio.
3. En **Framework Preset**, deja **Other** (Vercel detecta el
   `vercel.json` y usa `@vercel/python`).
4. Deja la **Root Directory** como el directorio del proyecto
   (`Generos_Musicales_ADC_DAC` si el repositorio es la carpeta
   completa).
5. En **Environment Variables**, añade:
   - `DJANGO_SECRET_KEY` → una cadena larga y aleatoria. Se genera con
     `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
   - (opcional) `DJANGO_ALLOWED_HOSTS` → el dominio de Vercel, separados
     por comas. No es estrictamente necesario con `ALLOWED_HOSTS = ["*"]`.
6. **Deploy**.

Vercel instalará las dependencias de `requirements.txt` (Django, NumPy,
SciPy, Matplotlib), y eso tarda un poco la primera vez: son unos
120 MB de ruedas. Las siguientes son más rápidas.

> **El `vercel.json` y el orden de las rutas.** El `{"handle":
> "filesystem"}` de la primera ruta es lo que hace que los ficheros
> estáticos de `public/` (la hoja de estilos) se sirvan directamente,
> sin pasar por la función. Sin esa línea, todo iría a Django, que
> también funciona, pero es más lento.

### 3.4 Si el repositorio es la carpeta `COMUNICACIONES I/` completa

En el panel de Vercel, *Settings → Root Directory*:

```
Generos_Musicales_ADC_DAC
```

y el `vercel.json` y el `api/index.py` se leen desde ahí. Todo lo demás
igual.

### 3.5 El Build Command (opcional pero recomendado)

En *Settings → Build & Development Settings → Build Command*:

```
python construir.py
```

Con esto, cada vez que se sube un cambio, Vercel vuelve a analizar las
pistas y regenera el JSON y las figuras **dentro del entorno de
despliegue**. Es lo correcto si el despliegue tiene los audios (porque
si no, el script no encuentra pistas y falla).

Con la alternativa —calcular en local y subir `salida/`— el build
command se deja vacío, y hay que acordarse de ejecutar `python
construir.py` y hacer `git add salida/` antes de cada `git push`.

> **Recomendación:** si el repositorio es público y sin los audios, deja
> el Build Command **vacío** y sube `salida/` ya calculado. Si el
> repositorio es privado y tiene los audios, pon `python construir.py`
> y todo se mantiene solo.

---

## 4. Comprobar que funciona

En la URL que te dé Vercel (`https://TU-REPO.vercel.app`):

| página | qué tiene que pasar |
|---|---|
| `/` | la portada con las cifras y el veredicto |
| `/comparativa/` | los cinco espectros y la tabla |
| `/genero/metal/` | la ficha con las figuras y los cuatro audios |
| `/subir/` | subir un WAV propio y que lo analice |
| `/descargas/informe.md` | se descarga el informe |
| `/descargas/figuras.zip` | se descargan las 39 figuras |

Y el audio: en la ficha de un género, el reproductor de "Cuantizado a 8
bits" tiene que sonar **distinto** del original. Si suena igual, no se
está cuantizando (y hay que mirar que los WAV estén en `audio/`).

---

## 5. Si algo falla

| síntoma | causa probable | solución |
|---|---|---|
| `ModuleNotFoundError: dsp_web` | la Root Directory de Vercel está mal | ponerla a `Generos_Musicales_ADC_DAC` |
| 500 en todas las páginas | falta `DJANGO_SECRET_KEY` | añadirla en las variables de entorno |
| La web tarda mucho o da timeout | no está `salida/datos.json` | ejecutar `python construir.py` y subir `salida/` |
| Las figuras no salen | no está `salida/*.png` | lo mismo |
| Los audios no suenan | no están los WAV en `audio/` | subirlos, o quitarlos de la web |
| El CSS no se aplica | falta `public/estilo.css` | ejecutar `python construir.py` y subir `public/` |
| La construcción falla con 120 MB | el límite de tamaño de Vercel | comprobar `.vercelignore` y que no se suben los `__pycache__` |

---

## 6. La alternativa: Render (más simple, sin precalcular)

Si lo de Vercel se complica, **Render** es más directo: es un contenedor
normal, con disco de verdad y sin límite de tiempo.

- `render.yaml` en la raíz del proyecto:

```yaml
services:
  - type: web
    name: dsp-adc-dac
    runtime: python
    buildCommand: pip install -r requirements.txt && python construir.py
    startCommand: gunicorn dsp_web.wsgi:application
    envVars:
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: "3.12.6"
```

- En `requirements.txt` hay que añadir `gunicorn`.
- En el panel de Render: *New → Web Service → Connect repo*.

Con Render, `construir.py` corre en cada despliegue, y la web calcula
en vivo si hace falta. La única diferencia es que la primera visita tras
un despliegue tarda unos segundos (el análisis), y a partir de ahí va
rápido.

Render apaga el servicio tras 15 minutos sin visitas (en el plan
gratuito), así que la primera visita después de un rato tarda en
arrancar. **Vercel no tiene ese problema** (arranca en milisegundos),
que es su ventaja principal para una demo delante de un profesor.

---

## 7. Resumen: qué hace cada plataforma

| | Vercel | Render | GitHub Pages |
|---|---|---|---|
| Django | sí, con `@vercel/python` | sí, con gunicorn | no |
| Coste | 0 | 0 (con sueño de 15 min) | 0 |
| Arranque en frío | instantáneo | lento | — |
| Datos precalculados | **necesarios** | opcionales | — |
| Subir tu propio WAV | sí | sí | no |

Para una sustentación, Vercel es mejor: no hay sorpresas de arranque en
frente al profesor. Y como el cálculo ya está hecho, el riesgo es
prácticamente cero.
