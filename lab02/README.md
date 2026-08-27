# Laboratorio 02 — Análisis de pacientes con presupuesto de memoria

## Datos
Generados con Synthea (`master-branch-latest`):

    java -jar synthea-with-dependencies.jar -p 20001 \
        --exporter.csv.export true --exporter.fhir.export false

`-p 20001` fija la población **viva**; Synthea simula además a los fallecidos
durante la ventana temporal, por lo que `patients.csv` contiene **23 018**
pacientes (20 001 vivos + 3 017 fallecidos). Población: Massachusetts.

Los CSV no se versionan (ver `.gitignore`): pesan cientos de MB y se
regeneran con el comando de arriba.
