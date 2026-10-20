#!/usr/bin/env python
"""El gestor de Django de este proyecto.

    python manage.py runserver        -> la aplicación web
    python manage.py test              -> las pruebas de Django

La carpeta `nucleo/` (el motor de cálculo) está en el mismo directorio, así
que se importa como `from nucleo import analisis`. Y la biblioteca
`Nyquist_Shannon`, que está un nivel más arriba, se añade al `sys.path`
desde `nucleo/_rutas.py`.
"""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsp_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Falta Django. Instálalo con: pip install django"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
