"""
settings.py — la configuración de la aplicación.

Es un proyecto de una sola aplicación (`motor`) sobre el motor de cálculo
(`nucleo`), que es una biblioteca pura de Python: la web es una CAPA
encima, no el centro.

LO QUE ESTÁ HECHO PARA PODER DESPLEGAR EN VERCEL
-------------------------------------------------
Vercel no es un servidor: es una plataforma *serverless*. Cada visita
ejecuta una función en una máquina que se enciende y se apaga, con el
disco en solo lectura, sin base de datos y con un límite de tiempo. Las
decisiones que de aquí salen son todas por eso:

    · `DEBUG` sale de una variable de entorno, y en producción es False.
    · `SECRET_KEY` sale de una variable de entorno (`DJANGO_SECRET_KEY`).
    · NO hay base de datos: la aplicación no usa modelos, ni sesiones, ni
      usuarios. Se quitan las apps que la necesitarían, y con ellas el
      problema de tener una SQLite en un disco de solo lectura.
    · Los ficheros estáticos se sirven desde `public/`, que es la carpeta
      que Vercel publica tal cual. En local, la vista `estilo` los sirve
      para que la misma URL funcione en los dos sitios.
    · `DATA_UPLOAD_MAX_MEMORY_SIZE` está acotado, porque en un entorno
      serverless la memoria es el recurso que se paga.

El detalle de cómo se despliega está en `docs/PUBLICAR.md`.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

#: ¿Estamos en un despliegue real? (Vercel pone VERCEL=1 en el entorno)
EN_VERCEL = bool(os.environ.get("VERCEL"))

# La clave secreta de un proyecto académico. En producción se pone una
# de verdad en la variable de entorno `DJANGO_SECRET_KEY`; aquí, si no
# está, se usa la de desarrollo.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-generos-musicales-adc-dac-proyecto-utp-2026")

# En un despliegue real, DEBUG a False. En local, a True (para ver los
# errores sin consultar el registro).
DEBUG = not EN_VERCEL and os.environ.get("DJANGO_DEBUG", "1") == "1"

# El host del proyecto en Vercel y subdominios dinámicos.
HOST_PROYECTO = "generos-musicales-adc-dac.vercel.app"

#: Permitir todos los dominios de Vercel (producción y previews) y desarrollo local.
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://generos-musicales-adc-dac.vercel.app",
    "http://localhost",
    "http://127.0.0.1",
]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "motor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dsp_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "motor" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dsp_web.wsgi.application"

# Sin base de datos: esta aplicación no guarda nada. Se deja el motor de
# SQLite configurado por si alguien añade un modelo más adelante, pero
# no se usa ninguna migración.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Tegucigalpa"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "motor" / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#: Los ficheros de audio que se pueden subir, y su tamaño máximo (20 MB).
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

#: En un despliegue real, la lista de hosts permitidos se toma de una
#: variable de entorno. Si no hay variable, se usa el host del proyecto,
#: nunca `*`.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

