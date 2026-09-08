"""Funciones puras del EDA del laboratorio 03.

Se extraen del notebook para poder testearlas con pytest sin depender de
Drive ni de los CSV de Synthea. Todas son deterministas y sin efectos
secundarios.
"""

from __future__ import annotations

import pandas as pd

DIAS_POR_ANIO = 365.25


def a_dia_naive(s: pd.Series) -> pd.Series:
    """Normaliza cualquier columna de fecha a datetime naive truncado al día.

    El lab02 dejó dos convenciones distintas conviviendo: ``p8.BIRTHDATE``
    es naive y ``obs.DATE`` es ``datetime64[ns, UTC]``. Restarlas levanta
    ``TypeError``. Se unifica asumiendo UTC (que es la zona en que Synthea
    exporta) y se descarta la zona explícitamente.
    """
    fechas = pd.to_datetime(s, errors="coerce", utc=True)
    return fechas.dt.tz_localize(None).dt.normalize()


def a_dia_naive_escalar(ts) -> pd.Timestamp:
    """Versión escalar de :func:`a_dia_naive`."""
    t = pd.Timestamp(ts)
    if t.tzinfo is not None:
        t = t.tz_convert("UTC").tz_localize(None)
    return t.normalize()


def edad_en_fecha(nacimiento: pd.Series, referencia: pd.Series) -> pd.Series:
    """Edad en años en una fecha de referencia (no la edad actual).

    En un estudio observacional la edad se calcula en la *fecha índice*,
    no en la fecha en que se corre el análisis. Usar la edad actual
    introduce una covariable que depende de cuándo se ejecutó el código.
    """
    return (referencia - nacimiento).dt.days / DIAS_POR_ANIO


def marcar_implausibles(s: pd.Series, lo: float, hi: float) -> pd.Series:
    """Booleano: valor presente y fuera del rango de plausibilidad.

    Los nulos devuelven ``False``: la ausencia de dato es un problema de
    completitud, no de plausibilidad, y mezclarlos infla el conteo.
    """
    return s.notna() & ((s < lo) | (s > hi))


def valor_basal(
    largo: pd.DataFrame,
    lookback: int = -365,
    lookahead: int = 30,
) -> pd.DataFrame:
    """Último valor por paciente y analito dentro de la ventana basal.

    Espera formato largo con las columnas ``PATIENT``, ``analito``,
    ``dias_desde_indice`` y ``VALUE_num``. Devuelve formato ancho con una
    columna por analito.

    La ventana se declara explícitamente porque define qué significa
    "basal": ``lookahead`` positivo admite mediciones hechas en el mismo
    encuentro diagnóstico, que es lo habitual en la práctica clínica.
    """
    ventana = largo[
        largo["dias_desde_indice"].between(lookback, lookahead)
        & largo["VALUE_num"].notna()
    ]
    return (
        ventana.sort_values("dias_desde_indice")
        .groupby(["PATIENT", "analito"], observed=True)["VALUE_num"]
        .last()
        .unstack("analito")
    )


def tabla_atricion(pasos: list[tuple[str, int]]) -> pd.DataFrame:
    """Tabla de atrición a partir de pares (descripción del paso, n)."""
    t = pd.DataFrame(pasos, columns=["paso", "n"])
    t["excluidos"] = t["n"].shift(1).sub(t["n"]).fillna(0).astype(int)
    t["pct_del_inicial"] = (100 * t["n"] / t["n"].iloc[0]).round(1)
    return t
