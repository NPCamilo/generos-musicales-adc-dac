# Graph Report - Generos_Musicales_ADC_DAC  (2026-10-27)

## Corpus Check
- 146 files · ~89,873 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .css 2, .zip 1)

## Summary
- 554 nodes · 1111 edges · 28 communities (20 shown, 8 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 23
- Community 24
- Community 25

## God Nodes (most connected - your core abstractions)
1. `analizar_pista()` - 29 edges
2. `Parametros` - 21 edges
3. `generar_pdf()` - 20 edges
4. `main()` - 18 edges
5. `_construir_texto()` - 17 edges
6. `_experimentos_de_muestreo()` - 15 edges
7. `_cadena_adc_dac()` - 14 edges
8. `_analisis_de_cuantizacion()` - 13 edges
9. `_cadena_telefonica()` - 13 edges
10. `analizar_catalogo()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `analizar_catalogo()`  [EXTRACTED]
  construir.py → nucleo/analisis.py
- `main()` --calls--> `Parametros`  [EXTRACTED]
  construir.py → nucleo/analisis.py
- `main()` --calls--> `resumen_tablas()`  [EXTRACTED]
  construir.py → nucleo/comparativa.py
- `main()` --calls--> `generar_informe()`  [EXTRACTED]
  construir.py → nucleo/informe.py
- `main()` --calls--> `generar_pdf()`  [EXTRACTED]
  construir.py → nucleo/pdf.py

## Import Cycles
- None detected.

## Communities (28 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (32): _anexo(), _cient(), _comparativa(), _conceptos(), _correspondencia(), _datos(), Documento, _enob_max() (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (18): main(), bajar(), cargar_registro(), convertir_a_wav(), descargar_todas(), escribir_wav(), guardar_registro(), leer_wav_mono() (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (18): a_png(), _aplicar_tema(), _encabezado(), figura_aliasing_detalle(), figura_bandas(), figura_cadena(), figura_codigos(), figura_cuantizacion() (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (19): ancho_banda_ocupado(), antialias(), bpm(), centroide_espectral(), crest_factor(), energias_por_banda(), envolvente_de_ataques(), espectro_magnitud() (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (16): _coma(), detalle_criterios(), _main(), ranking(), resumen_tablas(), tabla_comparativa(), veredicto_tdh(), construir_todas() (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (17): _aa_max(), _aa_min(), _cientifico(), _comp_centroide(), _comp_crest(), _comp_fmax(), _comp_fmax_energia(), _comp_mas_exigente() (+9 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (11): chk(), main(), _seccion(), _decodificar(), escribir_wav(), factor_de_escala(), leer_pista(), leer_wav() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): _analisis_de_cuantizacion(), analizar_pista(), _bits_a_codigo(), _cadena_adc_dac(), _cadena_telefonica(), _energia_fuera_de_banda(), _experimentos_de_muestreo(), _fraccion_voz() (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (14): _telefonica_en_vivo(), bits_efectivos(), cuantizar(), diagnostico_nyquist(), dither(), factor_carga(), parametros_cuantiizador(), plena_escala() (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (5): _correr(), main(), chk(), main(), _seccion()

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (21): runs-on, steps, strategy, jobs, build, python-version, name, on (+13 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (7): descarga_figuras(), descarga_pdf(), estilo(), informe(), np_arange(), publico_archivo(), subir()

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (4): analizar_catalogo(), claves(), Genero, obtener()

### Community 13 - "Community 13"
Cohesion: 0.18
Nodes (5): portada(), r_cuant(), nota_de_lectura(), tabla_criterios(), tabla_fuentes()

### Community 14 - "Community 14"
Cohesion: 0.21
Nodes (6): api_datos(), catalogo_analizado(), comparativa(), comparativa_calculada(), datos_precalculados(), genero()

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (6): indice_atencion(), _puntuacion_agudos(), _puntuacion_brillo(), _puntuacion_dinamica(), _puntuacion_tempo(), _puntuacion_voz()

### Community 17 - "Community 17"
Cohesion: 0.29
Nodes (4): audio(), _cuantizar_en_vivo(), np_int16(), _wav_en_bytes()

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (3): analisis_completo(), figura(), _figura_en_disco()

### Community 20 - "Community 20"
Cohesion: 0.40
Nodes (4): builds, routes, $schema, version

### Community 21 - "Community 21"
Cohesion: 0.50
Nodes (3): interface, display_name, short_description

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Parametros` connect `Community 7` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.058385093167701865 - nodes in this community are weakly interconnected._
- **Why does `analizar_pista()` connect `Community 7` to `Community 3`, `Community 4`, `Community 6`, `Community 8`, `Community 11`, `Community 12`, `Community 15`, `Community 25`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07716701902748414 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.10359408033826638 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.09988385598141696 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.07657657657657657 - nodes in this community are weakly interconnected._