"""
Ingestao das estatisticas do Pix (API Olinda do BCB, protocolo OData).

Fatos verificados em respostas reais (nov/2026):
- O parametro Database/DataBase e o MES INICIAL (AAAAMM); a API devolve dali em diante.
- $skip devolve HTTP 500 e $count e ignorado, entao paginamos por mes com $filter.
- Um mes tem ~11 mil linhas (estatisticas) ou ~5,6 mil (municipios). Um arquivo por mes.
"""
from __future__ import annotations

from config.configuracoes import FONTES, URL_OLINDA_PIX
from src.ingestao.cliente_http import montar_envelope, montar_url_odata, obter_json


def baixar_mes(fonte: str, ano_mes: int) -> dict:
    """Baixa todas as linhas de um recurso Pix para um unico mes AAAAMM."""
    config = FONTES[fonte]
    if config["tipo"] != "olinda_pix":
        raise ValueError(f"{fonte} nao e uma fonte Olinda Pix")
    url = f"{URL_OLINDA_PIX}/{config['funcao']}"
    parametros = {
        config["parametro"]: f"'{ano_mes}'",
        "$filter": f"AnoMes eq {ano_mes}",
        "$format": "json",
    }
    resposta = obter_json(montar_url_odata(url, parametros))
    return montar_envelope(fonte, url, parametros, resposta["value"])
