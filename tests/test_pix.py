import pytest

from src.transformacoes.pix import (
    CAPITAIS_IBGE,
    UF_POR_CODIGO_IBGE,
    classificar_capital_interior,
    crescimento_mensal,
    variacao_percentual,
)


def test_porto_alegre_e_capital_e_caxias_e_interior():
    assert classificar_capital_interior(4314902) == "capital"
    assert classificar_capital_interior(4305108) == "interior"  # Caxias do Sul


def test_tabelas_de_apoio_cobrem_27_unidades():
    assert len(CAPITAIS_IBGE) == 27
    assert len(UF_POR_CODIGO_IBGE) == 27
    assert UF_POR_CODIGO_IBGE[43] == "RS"


def test_variacao_percentual():
    assert variacao_percentual(110, 100) == pytest.approx(10.0)
    assert variacao_percentual(90, 100) == pytest.approx(-10.0)
    assert variacao_percentual(10, 0) is None
    assert variacao_percentual(None, 100) is None


def test_crescimento_mensal_e_12_meses():
    serie = [{"ano_mes": 202300 + m, "qtd": 100 + m} for m in range(1, 13)]
    serie.append({"ano_mes": 202401, "qtd": 202})  # dobro de jan/2023 (101)
    resultado = crescimento_mensal(serie, "qtd")
    assert resultado[0]["qtd_var_mensal"] is None
    assert resultado[1]["qtd_var_mensal"] == pytest.approx((102 / 101 - 1) * 100, abs=1e-4)
    assert resultado[-1]["qtd_var_12m"] == pytest.approx(100.0)
    assert resultado[-2]["qtd_var_12m"] is None


def test_crescimento_mensal_ordena_a_entrada():
    serie = [{"ano_mes": 202402, "qtd": 200}, {"ano_mes": 202401, "qtd": 100}]
    resultado = crescimento_mensal(serie, "qtd")
    assert [r["ano_mes"] for r in resultado] == [202401, 202402]
    assert resultado[1]["qtd_var_mensal"] == pytest.approx(100.0)
