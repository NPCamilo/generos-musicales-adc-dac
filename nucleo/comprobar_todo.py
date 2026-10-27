"""
comprobar_todo.py — pasa todas las suites y resume.

    python comprobar_todo.py              # todas
    python comprobar_todo.py test_wav_io  # solo esa

Cada suite se ejecuta en un PROCESO NUEVO, con un tiempo máximo, y se
lee su salida con dos expresiones regulares. Un proceso por suite es lo
correcto aquí: las suites modifican el `rcParams` de Matplotlib y el
caché de Django, y si compartieran proceso una suite podría tapar el
fallo de otra.

Salida: 0 si todo está en verde, 1 si algún fallo, 2 si no existe el
fichero de una suite.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent

#: Las suites, en el orden en que conviene correrlas.
SUITES = (
    "test_wav_io",
    "test_dsp_audio",
    "test_analisis",
)

#: Las pruebas de la web, que necesitan Django.
SUITES_WEB = ("test_web",)

RE_PRUEBAS = re.compile(r"(\d+)\s*/\s*(\d+)\s*comprobaciones en verde")
RE_FALLOS = re.compile(r"^\s*·\s*(.+)$", re.MULTILINE)


def _correr(nombre: str, timeout: int = 1800) -> dict:
    """Ejecuta una suite en un proceso nuevo y devuelve su resumen."""
    ruta = RAIZ / f"{nombre}.py"
    if not ruta.exists():
        return {"suite": nombre, "ok": False, "pruebas": 0, "fallos": 1,
                "detalle": f"no existe {ruta.name}", "codigo": 2}

    inicio = time.time()
    # La consola de Windows abre en cp1252, que no tiene el símbolo Δ ni
    # las rayas Unicode. Sin esto, la suite aborta con un
    # UnicodeEncodeError en una consola normal y el resumen miente.
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        proceso = subprocess.run(
            [sys.executable, str(ruta)],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, cwd=str(RAIZ),
            env=entorno,
        )
    except subprocess.TimeoutExpired:
        return {"suite": nombre, "ok": False, "pruebas": 0, "fallos": 1,
                "detalle": f"se pasó del límite de {timeout} s", "codigo": 1}

    salida = (proceso.stdout or "") + (proceso.stderr or "")
    m = RE_PRUEBAS.search(salida)
    if m:
        pruebas = int(m.group(1))
        total = int(m.group(2))
        fallos = total - pruebas
        detalle = "; ".join(RE_FALLOS.findall(salida)[:6])
    else:
        pruebas = 0
        total = 0
        fallos = 1
        detalle = salida.strip().splitlines()[-1] if salida.strip() else "sin salida"

    return {
        "suite": nombre,
        "ok": proceso.returncode == 0 and fallos == 0,
        "pruebas": pruebas,
        "total": total,
        "fallos": fallos,
        "detalle": detalle,
        "codigo": proceso.returncode,
        "segundos": round(time.time() - inicio, 1),
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if argv:
        suites = list(argv)
    else:
        suites = list(SUITES) + list(SUITES_WEB)

    print("=" * 78)
    print("comprobar_todo.py — las comprobaciones de este proyecto")
    print("=" * 78)

    resultados = []
    for nombre in suites:
        print(f"  ejecutando {nombre}...", flush=True)
        res = _correr(nombre)
        resultados.append(res)
        marca = "OK  " if res["ok"] else "FALLA"
        total = res.get("total", 0)
        print(f"  {marca} {nombre}: {res['pruebas']}/{total} "
              f"({res['segundos']} s)")

    print()
    print("=" * 78)
    total_pruebas = sum(r["pruebas"] for r in resultados)
    total_fallos = sum(r["fallos"] for r in resultados)
    print(f"{total_pruebas - total_fallos}/{total_pruebas} comprobaciones "
          f"en verde, en {len(resultados)} suites")
    if total_fallos:
        print()
        for r in resultados:
            if not r["ok"]:
                print(f"  · {r['suite']}: {r['detalle']}")
    print("=" * 78)

    if any(r["codigo"] == 2 for r in resultados):
        return 2
    return 1 if total_fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
