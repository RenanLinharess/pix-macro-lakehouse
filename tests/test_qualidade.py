from src.transformacoes.qualidade import (
    FALHA,
    OK,
    checar_continuidade_meses,
    checar_faixa,
    checar_nulos,
    checar_reconciliacao,
    checar_reconciliacao_serie,
    checar_unicidade,
    resumir,
)


def test_nulos():
    assert checar_nulos(0, "valor")["status"] == OK
    assert checar_nulos(3, "valor")["status"] == FALHA
    assert checar_nulos(3, "valor", maximo_permitido=5)["status"] == OK


def test_faixa():
    assert checar_faixa(2.0, 15.0, "selic_media", 0, 50)["status"] == OK
    assert checar_faixa(-1.0, 15.0, "selic_media", 0, 50)["status"] == FALHA
    assert checar_faixa(None, None, "selic_media", 0, 50)["status"] == FALHA


def test_unicidade():
    assert checar_unicidade(100, 100, "ano_mes")["status"] == OK
    resultado = checar_unicidade(100, 98, "ano_mes")
    assert resultado["status"] == FALHA
    assert resultado["valor_observado"] == 2


def test_continuidade_meses():
    assert checar_continuidade_meses([202011, 202012, 202101])["status"] == OK
    resultado = checar_continuidade_meses([202011, 202101])
    assert resultado["status"] == FALHA
    assert "202012" in resultado["detalhe"]
    assert checar_continuidade_meses([])["status"] == FALHA


def test_reconciliacao_tolera_diferenca_pequena():
    # diferenca real observada entre as duas fontes do Pix em jan/2024: 4 em 3,85 bilhoes
    assert checar_reconciliacao(3850642790, 3850642786, "pix_qtd")["status"] == OK
    assert checar_reconciliacao(100, 90, "pix_qtd")["status"] == FALHA
    assert checar_reconciliacao(None, 90, "pix_qtd")["status"] == FALHA


def test_reconciliacao_serie_lista_os_periodos_divergentes():
    diferencas = {202011: 0.0647, 202012: 0.0002, 202101: 0.0001, 202309: 0.0335}
    resultado = checar_reconciliacao_serie(diferencas, "pix_quantidade", tolerancia_relativa=0.005)
    assert resultado["status"] == FALHA
    assert resultado["valor_observado"] == 2
    assert "[202011, 202309]" in resultado["detalhe"]
    assert "6.4700%" in resultado["detalhe"]
    assert checar_reconciliacao_serie({202012: 0.0002}, "x")["status"] == OK
    assert checar_reconciliacao_serie({}, "x")["status"] == FALHA


def test_resumir():
    resultados = [checar_nulos(0, "a"), checar_nulos(1, "b")]
    resumo = resumir(resultados)
    assert resumo == {"total": 2, "falhas": 1, "regras_com_falha": ["nulos:b"]}
