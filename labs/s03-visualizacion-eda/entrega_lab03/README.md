# Lab 03 — EDA de una cohorte de diabetes tipo 2 (Synthea)

Análisis exploratorio sobre una cohorte clínica derivada del dataset sintético
del laboratorio 02 (23 018 pacientes, 17.4 M de observaciones).

## Cohorte

Adultos con diabetes mellitus tipo 2 incidente, definida por el código
SNOMED CT `44054006`. La fecha índice es el primer diagnóstico registrado.
Cuatro criterios de inclusión: edad ≥ 18 años al índice, ≥ 365 días de
seguimiento posterior, y fecha índice dentro del período con datos exportados
con ≥ 365 días de historia previa. **n final = 395**, de 1751 diagnosticados.

## Contenido

| Archivo | Qué es |
|---|---|
| `eda_cohorte.ipynb` | Notebook completo: cohorte, checklist de EDA, figuras y Tabla 1 |
| `eda_utils.py` | Funciones puras: fechas, edad al índice, ventana basal, atrición |
| `test_eda_utils.py` | Suite de pytest, 10 tests |
| `tabla1_cohorte_t2d.csv` / `.html` | Tabla de características basales por sexo, con SMD |
| `figuras/figura_principal.pdf` | Figura 2×2, vectorial, fuentes TrueType |
| `figuras/figura_principal.png` | La misma figura a 300 dpi |

## Reproducir

Requiere los CSV de Synthea y los checkpoints del lab 02, que **no se
versionan**: son datos regenerables, no código. El comando de generación está
documentado en el notebook del lab 02. Ajustar `BASE02` y `BASE03` al inicio
del notebook y correr *Restart session and run all*.

    pip install tableone lifelines
    ruff check eda_utils.py test_eda_utils.py
    pytest test_eda_utils.py -q

## Hallazgo principal

Las mediciones no se distribuyen a lo largo del seguimiento: se concentran en
el día del diagnóstico y en sus aniversarios anuales, y los catorce analitos se
registran siempre en el mismo contacto. Esto limita el análisis a resolución
anual e impide estudiar la ausencia informativa.
