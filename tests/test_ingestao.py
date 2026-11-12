"""Testes da ingestao sem internet: so a montagem de URL e do envelope."""
from src.ingestao.cliente_http import montar_envelope, montar_url_odata


def test_url_odata_preserva_arroba_cifrao_e_aspas():
    url = montar_url_odata(
        "https://olinda/odata/EstatisticasTransacoesPix(Database=@Database)",
        {"@Database": "'202401'", "$filter": "AnoMes eq 202401", "$format": "json"},
    )
    assert url == (
        "https://olinda/odata/EstatisticasTransacoesPix(Database=@Database)"
        "?@Database='202401'&$filter=AnoMes%20eq%20202401&$format=json"
    )


def test_envelope_tem_metadados_de_ingestao():
    envelope = montar_envelope("ipca", "https://api", {"formato": "json", "x": 1}, [{"a": 1}, {"a": 2}])
    metadados = envelope["metadados"]
    assert metadados["fonte"] == "ipca"
    assert metadados["quantidade_registros"] == 2
    assert metadados["parametros"] == {"formato": "json", "x": "1"}
    assert metadados["baixado_em"].endswith("+00:00")
    assert envelope["dados"] == [{"a": 1}, {"a": 2}]
