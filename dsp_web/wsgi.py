"""La entrada WSGI: la que usa el servidor de desarrollo de Django."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsp_web.settings")

application = get_wsgi_application()
