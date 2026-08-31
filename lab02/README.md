# Laboratorio 02 — Análisis de un dataset de pacientes con presupuesto de memoria

Sesión 02 · Python para Biomedicina: Estructuras de Datos y Pandas

Análisis de un dataset sintético tipo EHR midiendo el costo en memoria de cada decisión
de carga, tipado y agregación, y comparación de tres motores de procesamiento sobre el
mismo pipeline.

## Datos

Generados con [Synthea](https://github.com/synthetichealth/synthea), jar
`synthea-with-dependencies.jar` del tag `master-branch-latest`:

```bash
java -jar synthea-with-dependencies.jar -p 20001 \
    --exporter.csv.export true \
    --exporter.fhir.export false
```

- `--exporter.csv.export true` activa la exportación a CSV, apagada por defecto en
  `synthea.properties`.
- `--exporter.fhir.export false` desactiva FHIR, que no se usa en este laboratorio y
  triplica el tiempo de generación.

**Volumen resultante: 23 018 pacientes.** El parámetro `-p 20001` fija la población
**viva** al final de la simulación; Synthea además simula a los pacientes que fallecieron
durante la ventana temporal (3 017), que también se exportan. Población simulada:
Massachusetts, EE. UU.

Archivos utilizados de los 18 que genera Synthea:

| Archivo | Filas | Contenido |
|---|---|---|
| `patients.csv` | 23 018 | Un renglón por paciente: demografía |
| `encounters.csv` | 1 355 775 | Encuentros clínicos |
| `observations.csv` | 17 355 578 | Mediciones: laboratorios y signos vitales |

Los CSV **no se versionan** (ver `.gitignore`): pesan cientos de MB y se regeneran con el
comando de arriba.

## Reproducir el análisis

1. **Requisitos**: Java 11+ (para Synthea) y Python 3.10+.
   Dependencias Python: `pandas numpy pyarrow polars pyspark memory_profiler psutil`
   (la primera celda del notebook las instala).

2. **Generar los datos** con el comando de la sección anterior. Los CSV quedan en
   `output/csv/`.

3. **Ajustar las rutas** en la celda de arranque del notebook. El análisis se desarrolló
   en Google Colab con persistencia en Drive:

   ```python
   BASE = Path('/content/drive/MyDrive/curso-cd-2027/lab02')
   ```

   Para ejecución local, apuntar `BASE` al directorio que contenga `data/` con los CSV.

4. **Ejecutar** `analisis_pacientes.ipynb` con `FORCE_REBUILD = True` y *Restart & Run All*.

### Sobre el sistema de checkpoints

El notebook persiste los DataFrames ya tipados en Parquet bajo `ckpt/`, para sobrevivir a
las desconexiones de Colab sin rehacer el pipeline completo. Parquet conserva el esquema
—`category`, `datetime64[ns, UTC]`, `float32`—, cosa que un CSV no puede hacer.

`FORCE_REBUILD = True` ignora el caché y fuerza la ejecución completa desde los CSV. **Es
el modo en que debe correrse para verificar reproducibilidad**, dado que el caché podría
enmascarar un pipeline roto.

## Resultados principales

- **Reducción de memoria en `observations`: 94.4%** (objetivo del laboratorio: ≥70%),
  mediante `category` para UUID repetidos y códigos clínicos, `datetime64` para fechas y
  partición de la columna mixta `VALUE` en `VALUE_num` (`float32`) y `VALUE_cat`
  (`category`), usando `TYPE` como fuente de verdad.
- **Auditoría**: 0 identificadores de paciente duplicados, 0 encuentros previos al
  nacimiento. Los 3 289 encuentros posteriores a la defunción resultaron ser 526
  artefactos de granularidad temporal y 2 763 certificaciones de defunción legítimas
  (`Death Certification`, entre 1 y 14 días tras el fallecimiento).
- **Merges validados** con `validate='m:1'` e `indicator=True`: 17 355 578 filas antes y
  después de ambos joins, sin multiplicación. El 3.6% de `left_only` corresponde a las
  observaciones con `ENCOUNTER` nulo detectadas en la auditoría.
- **Procesamiento por lotes**: `observations.csv` completo procesado con un pico de
  **106.3 MiB**, dentro del presupuesto autoimpuesto de 200 MiB.

## Comparativa de herramientas (Actividad 8)

Mismo pipeline (preguntas clínicas de la Actividad 5), leyendo desde los mismos CSV.
Memoria medida como RSS incremental del proceso.

| Herramienta | Líneas de código | Tiempo (s) | Memoria pico (MiB) | Qué costó más |
|---|---|---|---|---|
| pandas  | 18 | 64.8 | 1 093.2 | Cargar los CSV completos en RAM en un solo hilo: la lectura domina el tiempo |
| Polars  | 14 | 28.0 | 3 163.1 | La memoria: lectura paralela con varios buffers y dos pasadas sobre `observations.csv` |
| PySpark | 16 | 156.1 | 0.0 * | Overhead de coordinación: 15.5 s de arranque de JVM más planificación por tarea |

\* La medición de PySpark **está subestimada**: en modo local el trabajo ocurre en una JVM
que corre como proceso separado, y el RSS del proceso Python (el driver) no la incluye.
Los 15.5 s de arranque de la `SparkSession` se midieron por separado y no se incluyen en
la columna de tiempo.

Los tres motores producen resultados idénticos hasta el sexto decimal en las cuatro
métricas comparadas.

**Recomendación**: para este volumen (~1.2 GB, 17.4 M filas) y este tipo de análisis
—agregaciones y joins en trabajo exploratorio— **Polars**. El detalle del argumento y los
umbrales a partir de los cuales cambiaría la decisión están en la Actividad 9 del notebook.

## Estructura

```
lab02/
├── README.md                  # este archivo
└── analisis_pacientes.ipynb   # análisis completo, actividades 1-9
```
