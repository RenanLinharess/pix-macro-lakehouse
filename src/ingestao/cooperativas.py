"""
Ingestao do cadastro de cooperativas de credito em funcionamento (API Olinda do BCB).

E um cadastro pequeno (~740 linhas) que vem inteiro em uma chamada. Guardamos uma
foto por data de download, porque o cadastro muda ao longo do tempo.
"""
from __future__ import annotations

from config.configuracoes import FONTES, URL_OLINDA_INSTITUICOES
from src.ingestao.cliente_http import montar_envelope, montar_url_odata, obter_json


def baixar_cooperativas() -> dict:
    """Baixa o cadastro completo das cooperativas de credito."""
    config = FONTES["cooperativas"]
    url = f"{URL_OLINDA_INSTITUICOES}/{config['recurso']}"
    parametros = {"$top": 100000, "$format": "json"}
    resposta = obter_json(montar_url_odata(url, parametros))
    return montar_envelope("cooperativas", url, parametros, resposta["value"])
