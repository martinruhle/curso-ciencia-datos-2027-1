"""Tests de las funciones puras del EDA (laboratorio 03)."""

import pandas as pd
import pytest

from eda_utils import (
    a_dia_naive,
    a_dia_naive_escalar,
    edad_en_fecha,
    marcar_implausibles,
    tabla_atricion,
    valor_basal,
)


def test_a_dia_naive_unifica_aware_y_naive():
    aware = pd.Series(pd.to_datetime(["2015-03-04T18:30:00Z"]))
    naive = pd.Series(pd.to_datetime(["2015-03-04"]))
    assert a_dia_naive(aware).iloc[0] == a_dia_naive(naive).iloc[0]
    assert a_dia_naive(aware).dt.tz is None


def test_a_dia_naive_propaga_nulos():
    s = pd.Series([pd.NaT, "2020-01-01"])
    assert a_dia_naive(s).isna().tolist() == [True, False]


def test_a_dia_naive_escalar_trunca_al_dia():
    t = a_dia_naive_escalar(pd.Timestamp("2020-06-15T23:59:00Z"))
    assert t == pd.Timestamp("2020-06-15")
    assert t.tzinfo is None


def test_edad_en_fecha_usa_la_referencia_no_el_hoy():
    nac = pd.Series(pd.to_datetime(["1980-01-01", "1980-01-01"]))
    ref = pd.Series(pd.to_datetime(["2000-01-01", "2010-01-01"]))
    edades = edad_en_fecha(nac, ref)
    assert edades.iloc[0] == pytest.approx(20.0, abs=0.02)
    assert edades.iloc[1] == pytest.approx(30.0, abs=0.02)


def test_marcar_implausibles_excluye_nulos():
    s = pd.Series([45.0, 120.0, 250.0, None])
    out = marcar_implausibles(s, 50, 200)
    assert out.tolist() == [True, False, True, False]


def test_marcar_implausibles_limites_inclusivos():
    s = pd.Series([50.0, 200.0])
    assert marcar_implausibles(s, 50, 200).sum() == 0


def _largo_de_prueba():
    return pd.DataFrame(
        {
            "PATIENT": ["p1", "p1", "p1", "p2"],
            "analito": ["HbA1c", "HbA1c", "HbA1c", "HbA1c"],
            "dias_desde_indice": [-400, -100, -10, 5],
            "VALUE_num": [9.0, 7.5, 6.8, 8.1],
        }
    )


def test_valor_basal_toma_el_mas_cercano_al_indice():
    out = valor_basal(_largo_de_prueba())
    assert out.loc["p1", "HbA1c"] == 6.8


def test_valor_basal_respeta_el_lookback():
    out = valor_basal(_largo_de_prueba(), lookback=-500)
    assert out.loc["p1", "HbA1c"] == 6.8  # sigue siendo el último, no el primero


def test_valor_basal_ignora_fuera_de_ventana():
    largo = _largo_de_prueba()
    out = valor_basal(largo, lookback=-365, lookahead=0)
    assert "p2" not in out.index  # su única medición cae en +5 días


def test_tabla_atricion_calcula_excluidos():
    t = tabla_atricion([("elegibles", 100), ("adultos", 80), ("con seguimiento", 60)])
    assert t["excluidos"].tolist() == [0, 20, 20]
    assert t["pct_del_inicial"].tolist() == [100.0, 80.0, 60.0]
