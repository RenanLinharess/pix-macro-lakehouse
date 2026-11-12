from datetime import date

from src.transformacoes.calendario import (
    ano_mes_para_data,
    data_para_ano_mes,
    formatar_data_sgs,
    janelas_sgs,
    meses_entre,
    somar_meses,
)


def test_somar_meses_vira_o_ano():
    assert somar_meses(202011, 3) == 202102
    assert somar_meses(202101, -1) == 202012
    assert somar_meses(202012, 12) == 202112


def test_meses_entre_inclui_extremos():
    assert meses_entre(202011, 202102) == [202011, 202012, 202101, 202102]
    assert meses_entre(202102, 202011) == []


def test_conversao_ano_mes_data():
    assert ano_mes_para_data(202011) == date(2020, 11, 1)
    assert data_para_ano_mes(date(2020, 11, 15)) == 202011


def test_janelas_sgs_respeitam_o_limite_e_se_encostam():
    janelas = janelas_sgs(date(2018, 1, 1), date(2026, 11, 12), anos=5)
    assert janelas == [
        (date(2018, 1, 1), date(2022, 12, 31)),
        (date(2023, 1, 1), date(2026, 11, 12)),
    ]
    # nenhuma janela passa de 5 anos
    for inicio, fim in janelas:
        assert (fim - inicio).days < 5 * 366


def test_janelas_sgs_periodo_invertido():
    assert janelas_sgs(date(2024, 1, 1), date(2023, 1, 1), anos=5) == []


def test_formato_de_data_do_sgs():
    assert formatar_data_sgs(date(2018, 1, 1)) == "01/01/2018"
