from datetime import datetime, timezone

from src.transformacoes.bronze import converter_valor, envelope_para_linhas


def test_converter_valor_por_tipo():
    assert converter_valor("77", "BIGINT") == 77
    assert converter_valor(77.0, "BIGINT") == 77
    assert converter_valor("11.75", "DOUBLE") == 11.75
    assert converter_valor(202401, "STRING") == "202401"
    assert converter_valor(None, "INT") is None
    assert converter_valor("2026-11-12T18:41:17+00:00", "TIMESTAMP") == datetime(2026, 11, 12, 18, 41, 17, tzinfo=timezone.utc)


def test_envelope_para_linhas_mantem_nomes_originais_e_anexa_metadados():
    envelope = {
        "metadados": {
            "fonte": "pix_municipios",
            "url": "https://olinda/x",
            "parametros": {"@DataBase": "'202401'", "$filter": "AnoMes eq 202401"},
            "baixado_em": "2026-11-12T18:41:17+00:00",
            "quantidade_registros": 1,
        },
        "dados": [
            {"AnoMes": 202401, "Municipio_Ibge": 4314902, "Municipio": "PORTO ALEGRE", "Estado_Ibge": 43,
             "Estado": "RIO GRANDE DO SUL", "Sigla_Regiao": "SU", "Regiao": "SUL",
             "VL_PagadorPF": 5887712566.44, "QT_PagadorPF": 25359366, "CampoNovoDaApi": "ignorado"}
        ],
    }
    carregado_em = datetime(2026, 11, 12, 19, 0, tzinfo=timezone.utc)
    linhas = envelope_para_linhas("pix_municipios", envelope, "pix_municipios_202401.json", carregado_em)
    assert len(linhas) == 1
    linha = linhas[0]
    assert linha["Municipio"] == "PORTO ALEGRE"
    assert linha["QT_PagadorPF"] == 25359366
    assert linha["VL_PagadorPJ"] is None  # esperado e ausente vira None
    assert "CampoNovoDaApi" not in linha
    assert linha["fonte"] == "pix_municipios"
    assert linha["arquivo_origem"] == "pix_municipios_202401.json"
    assert linha["parametros_requisicao"]["$filter"] == "AnoMes eq 202401"
    assert linha["carregado_em"] == carregado_em
