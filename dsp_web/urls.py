"""
urls.py — las URLs del proyecto.

    /                      la portada: el resumen y el veredicto
    /genero/<clave>/       la ficha de un género, con sus figuras y su audio
    /comparativa/          los cinco juntos (el punto e)
    /subir/                subir tu propio WAV y analizarlo
    /informe/              descargar el informe y las figuras
    /estilo.css            la hoja de estilos (en local; en Vercel la
                            sirve `public/` directamente)
    /figura/<clave>/<n>.png   las figuras, servidas como imagen
    /audio/<clave>/<n>.wav    los WAV generados (cuantizados, telefónicos)
"""

from django.urls import path

from motor import views

urlpatterns = [
    path("", views.portada, name="portada"),
    path("genero/<str:clave>/", views.genero, name="genero"),
    path("comparativa/", views.comparativa, name="comparativa"),
    path("subir/", views.subir, name="subir"),
    path("informe/", views.informe, name="informe"),
    path("estilo.css", views.estilo, name="estilo"),
    path("publico/<str:nombre>", views.publico_archivo, name="publico_archivo"),
    path("descargas/informe.md", views.descarga_informe, name="descarga_informe"),
    path("descargas/informe_proyecto.pdf", views.descarga_pdf,
         name="descarga_pdf"),
    path("descargas/figuras.zip", views.descarga_figuras, name="descarga_figuras"),
    path("figura/<str:clave>/<str:nombre>.png", views.figura, name="figura"),
    path("figura-subida/<str:token>/<str:nombre>.png", views.figura_subida,
         name="figura_subida"),
    path("audio/<str:clave>/<str:variante>.wav", views.audio, name="audio"),
    # Sirve cualquier archivo de public/ en local (Vercel lo sirve directamente en su ruta)
    path("<str:nombre>", views.publico_archivo, name="publico_archivo"),
]

