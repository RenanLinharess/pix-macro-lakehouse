"""
Ingestao de series temporais do SGS (Sistema Gerenciador de Series Temporais do BCB).

Fatos verificados: a API aceita no maximo 10 anos por consulta em series diarias
(HTTP 406 acima disso). Por isso o download e feito em janelas (ver calendario.janelas_sgs).
Os valores vem como texto ("11.75"); a conversao para numero e feita na camada silver.
"""
from __future__ import annotations

from datetime import date

from config.configuracoes import FONTES, URL_SGS
from src.ingestao.cliente_http import montar_envelope, obter_json
from src.transformacoes.calendario import formatar_data_sgs


def baixar_janela(fonte: str, data_inicio: date, data_fim: date) -> dict:
    """Baixa uma serie SGS entre duas datas (inclusive)."""
    config = FONTES[fonte]
    if config["tipo"] != "sgs":
        raise ValueError(f"{fonte} nao e uma fonte SGS")
    url = URL_SGS.format(codigo=config["codigo"])
    parametros = {
        "formato": "json",
        "dataInicial": formatar_data_sgs(data_inicio),
        "dataFinal": formatar_data_sgs(data_fim),
    }
    dados = obter_json(url, parametros)
    return montar_envelope(fonte, url, parametros, dados)
