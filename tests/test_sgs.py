from datetime import date

import pytest

from src.transformacoes.sgs import converter_registro_sgs, ipca_acumulado_12m, selic_media_mensal


def test_converter_registro_sgs():
    assert converter_registro_sgs({"data": "01/01/2024", "valor": "11.75"}) == {"data": date(2024, 1, 1), "valor": 11.75}


def test_converter_registro_sgs_valor_invalido_vira_none():
    assert converter_registro_sgs({"data": "01/01/2024", "valor": ""})["valor"] is None


def test_selic_media_mensal_com_mudanca_no_meio_do_mes():
    # 10 dias a 11.75 e 20 dias a 11.25 -> media ponderada pelos dias
    registros = [{"data": date(2024, 2, d), "valor": 11.75} for d in range(1, 11)]
    registros += [{"data": date(2024, 2, d), "valor": 11.25} for d in range(11, 30)]
    resultado = selic_media_mensal(registros)
    assert len(resultado) == 1
    assert resultado[0]["ano_mes"] == 202402
    assert resultado[0]["dias_observados"] == 29
    assert resultado[0]["selic_media"] == pytest.approx((10 * 11.75 + 19 * 11.25) / 29, abs=1e-4)


def test_selic_media_ignora_nulos_e_ordena():
    registros = [
        {"data": date(2024, 3, 1), "valor": 10.0},
        {"data": date(2024, 1, 1), "valor": None},
        {"data": date(2024, 1, 2), "valor": 12.0},
    ]
    resultado = selic_media_mensal(registros)
    assert [r["ano_mes"] for r in resultado] == [202401, 202403]
    assert resultado[0]["selic_media"] == 12.0


def test_ipca_12m_e_produto_nao_soma():
    # 12 meses de 1% ao mes: somar daria 12%, compor da 12,68%
    registros = [{"data": date(2023, m, 1), "valor": 1.0} for m in range(1, 13)]
    resultado = ipca_acumulado_12m(registros)
    assert resultado[-1]["ano_mes"] == 202312
    assert resultado[-1]["ipca_12m"] == pytest.approx(12.6825, abs=1e-3)
    # os 11 primeiros meses nao tem janela completa
    assert all(r["ipca_12m"] is None for r in resultado[:11])


def test_ipca_12m_com_valores_reais_de_2024():
    # Valores oficiais do IPCA 2024 (SGS 433). Acumulado do ano divulgado: 4,83%.
    mensais = [0.42, 0.83, 0.16, 0.38, 0.46, 0.21, 0.38, -0.02, 0.44, 0.56, 0.39, 0.52]
    registros = [{"data": date(2024, m + 1, 1), "valor": v} for m, v in enumerate(mensais)]
    resultado = ipca_acumulado_12m(registros)
    assert resultado[-1]["ipca_12m"] == pytest.approx(4.83, abs=0.01)


def test_ipca_12m_com_buraco_na_serie_devolve_none():
    registros = [{"data": date(2023, m, 1), "valor": 0.5} for m in range(1, 13) if m != 6]
    registros.append({"data": date(2024, 1, 1), "valor": 0.5})
    resultado = ipca_acumulado_12m(registros)
    assert resultado[-1]["ano_mes"] == 202401
    assert resultado[-1]["ipca_12m"] is None
