"""
Los filtros de plantilla de la aplicación.

HAY UN SOLO FILTRO, `num`, Y HACE UNA COSA
-----------------------------------------
Escribe los números como se escriben en español: con punto para los
miles y con COMA para los decimales.

    {{ 23332|num }}      ->  23.332
    {{ 11666.5|num }}   ->  11.666,5
    {{ 290|num:0 }}     ->  290

Django no trae nada para esto (el filtro `intcomma` de `humanize` usa el
convención inglesa, con la coma para los miles), y en un informe con
cifuras de frecuencia mixing las dos convenciones es justo lo que hace
que un número parezca otro.

Aparte, `recorta` quita los decimales inútiles de un valor que viene
redondeado (un índice que sale 80,0999999 se muestra como 80,1).
"""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter(name="num")
def num(valor, decimales=None) -> str:
    """Un número con la convención española: miles con punto, coma decimal."""
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if decimales is None:
        decimales = 0 if abs(n - round(n)) < 1e-9 else 2
    try:
        d = int(decimales)
    except (TypeError, ValueError):
        d = 2
    texto = f"{n:,.{d}f}"
    # se cambia el separador de miles por un punto y la coma decimal por
    # una coma: en el formato de Python el millar es la coma y el decimal
    # el punto, así que el cambio se hace en un solo paso
    partes = texto.split(".")
    entero = partes[0].replace(",", ".")
    if len(partes) > 1:
        return f"{entero},{partes[1]}"
    return entero


@register.filter(name="recorta")
def recorta(valor, decimales=1) -> str:
    """Un número con los decimales indicados, sin ceros de más."""
    return num(valor, decimales)
