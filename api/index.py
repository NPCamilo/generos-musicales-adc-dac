"""
api/index.py — la entrada de la aplicación en Vercel.

QUÉ ES ESTO
-----------
Vercel no es un servidor: es una plataforma *serverless*. Cada visita
ejecuta una función, en una máquina que se enciende y se apaga, con un
disco de solo lectura y un límite de tiempo.

Para una aplicación de Django, el truco esışý exponer la aplicación WSGI
como una función de Python. Vercel busca en este fichero una variable
llamada `app` (o `application`) y la usa como manejador.

    app = application

LA RAÍZ DEL PROYECTO
--------------------
Vercel ejecuta el comando desde la RAÍZ del repositorio. Este proyecto
vive en una subcarpeta (`Generos_Musicales_ADC_DAC/`) dentro de
`COMUNICACIONES I/`, y el proyecto Django (`dsp_web`) y el motor
(`nucleo`) están dentro de esa subcarpeta.

Por eso, cuando subas el repositorio a GitHub, la raíz de Vercel tiene
que ser la carpeta del proyecto. En el panel de Vercel, en
*Settings → Root Directory*, se pone `Generos_Musicales_ADC_DAC` (o la
ruta que corresponda). Y en GitHub, el repositorio puede ser la carpeta
del proyecto directamente.

SI EL REPOSITORIO TIENE LA ESTRUCTURA COMPLETA
-----------------------------------------------
Si en GitHub subes la carpeta `COMUNICACIONES I/` completa, la raíz de
Vercel debe ser `COMUNICACIONES I/Generos_Musicales_ADC_DAC` y este
fichero es el mismo. No hay que cambiar nada más.

LO QUE HAY QUE TENER EN CUENTA
------------------------------
1. **El límite de tiempo.** La función tiene 10 segundos (plan gratuito).
   Por eso la web usa los datos PRECALCULADOS (`salida/datos.json`) y las
   figuras ya dibujadas: responder es leer un fichero. Si el JSON no
   está, la web calcula todo al vuelo y puede agotar el tiempo.
2. **El disco es de solo lectura.** No se puede escribir en `salida/`
   durante la visita. Por eso las figuras se generan antes de desplegar
   (con `python construir.py`) y se suben al repositorio.
3. **Sin base de datos.** Esta aplicación no usa ninguna: no hay
   modelos, ni sesiones, ni usuarios. Las sesiones de Django se
   desactivaron precisamente para no necesitar una.
4. **Los ficheros grandes.** Los WAV de `audio/` (5 MB en total) se suben
   al repositorio. Vercel no tiene problema con eso, pero conviene
   tenerlo en cuenta si el repositorio es público y los audios tienen
   derechos de autor.
"""

import os
import sys
import pathlib

# La raíz de este fichero es `.../Generos_Musicales_ADC_DAC/api/`, así que
# la raíz del proyecto es un nivel más arriba. Añadirla al `sys.path` es
# lo que hace que `import dsp_web.settings` y `from nucleo import ...`
# funcionen.
RAIZ = pathlib.Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsp_web.settings")

from dsp_web.wsgi import application  # noqa: E402

# Vercel busca `app` (y acepta `application`).
app = application
