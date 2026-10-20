"""
construir.py — prepara el proyecto para desplegarlo.

QUÉ HACE
-------
Regenera, en este orden:

    1. el informe (`salida/informe.md`) y las 39 figuras,
    2. el JSON con los datos precalculados (`salida/datos.json`),
    3. la copia de la hoja de estilos en `public/`.

POR QUÉ HACE FALTA
------------------
En un despliegue *serverless* (Vercel) la función tiene un límite de
tiempo y el disco es de solo lectura, así que no se puede analizar ni
dibujar en cada visita. La solución es calcular ANTES y subir al
repositorio el resultado: el JSON con los números y los PNG con las
figuras.

Este script es el que se ejecuta antes de subir los cambios:

    python construir.py
    git add salida/datos.json salida/*.png public/estilo.css
    git commit -m "números y figuras al día"
    git push

Y en el panel de Vercel, el "Build Command" puede ser este mismo
script, para que se ejecute en cada despliegue.

    python construir.py
"""

from __future__ import annotations

import pathlib
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo import analisis, comparativa, informe, serializacion  # noqa: E402
from nucleo.analisis import Parametros                        # noqa: E402


def main() -> int:
    print("=" * 70)
    print("construir.py — preparando el despliegue")
    print("=" * 70)

    # 1. el informe y las figuras
    print("[1/4] el informe y las figuras...")
    informe.generar_informe(Parametros())

    # 2. los datos precalculados
    print("[2/4] los datos precalculados...")
    res = analisis.analizar_catalogo(Parametros())
    comp = comparativa.resumen_tablas(res["resultados"])
    ruta = serializacion.guardar_datos(res, informe.SALIDA / "datos.json",
                                       extra=comp)
    print(f"      -> {ruta} "
          f"({ruta.stat().st_size / 1024:.0f} KB)")

    # 3. la hoja de estilos en `public/`
    print("[3/4] la hoja de estilos...")
    origen = RAIZ / "motor" / "static" / "motor" / "estilo.css"
    destino = RAIZ / "public" / "estilo.css"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.exists() and origen.resolve() != destino.resolve():
        shutil.copyfile(origen, destino)
        print(f"      -> {destino}")
    else:
        print("      (ya estaba)")

    # 4. el resumen
    print("[4/4] el resumen...")
    n_figuras = len(list(informe.SALIDA.glob("*.png")))
    print(f"      {len(res['resultados'])} pistas · {n_figuras} figuras · "
          f"datos.json listo")
    if res["faltantes"]:
        print(f"      AVISO: faltan pistas: {res['faltantes']}")
    print()
    print("Listo. Ahora hay que subir `salida/` y `public/` al repositorio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
