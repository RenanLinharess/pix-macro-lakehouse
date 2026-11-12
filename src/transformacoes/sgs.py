"""
Transformacoes das series do SGS (Selic meta e IPCA).

Entrada: registros como vieram da API, {"data": "01/01/2024", "valor": "11.75"}.
Saida: estruturas tipadas e agregadas, prontas para virar tabela silver/gold.

Tudo aqui e Python puro e deterministico: a mesma funcao que o notebook executa
no Databricks e a que o pytest executa localmente.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from src.transformacoes.calendario import data_para_ano_mes, somar_meses


def converter_registro_sgs(registro: dict) -> dict:
    """
    {"data": "01/01/2024", "valor": "11.75"} -> {"data": date(2024, 1, 1), "valor": 11.75}
    Valores vazios ou invalidos viram None (a camada de qualidade decide o que fazer).
    """
    data_convertida = datetime.strptime(registro["data"], "%d/%m/%Y").date()
    try:
        valor = float(registro["valor"])
    except (TypeError, ValueError):
        valor = None
    return {"data": data_convertida, "valor": valor}


def selic_media_mensal(registros_diarios: list[dict]) -> list[dict]:
    """
    Media simples da meta Selic por mes, a partir da serie diaria ja convertida.

    Por que media e nao ultimo valor do mes? O Copom muda a meta no meio do mes;
    a media reflete a taxa que vigorou de fato ao longo do mes.
    Saida ordenada por ano_mes: [{"ano_mes": 202401, "selic_media": 11.75, "dias_observados": 31}, ...]
    """
    soma: dict[int, float] = defaultdict(float)
    dias: dict[int, int] = defaultdict(int)
    for registro in registros_diarios:
        if registro["valor"] is None:
            continue
        ano_mes = data_para_ano_mes(registro["data"])
        soma[ano_mes] += registro["valor"]
        dias[ano_mes] += 1
    return [
        {"ano_mes": ano_mes, "selic_media": round(soma[ano_mes] / dias[ano_mes], 4), "dias_observados": dias[ano_mes]}
        for ano_mes in sorted(soma)
    ]


def ipca_acumulado_12m(registros_mensais: list[dict]) -> list[dict]:
    """
    IPCA acumulado em 12 meses, pela composicao das taxas mensais:
        acumulado = (prod(1 + taxa_i/100) - 1) * 100, para os ultimos 12 meses.

    Nunca se soma inflacao mensal: 1% ao mes por 12 meses nao da 12%, da 12,68%,
    porque cada mes incide sobre o preco ja reajustado (juros compostos).
    Meses sem 12 observacoes anteriores completas recebem None.
    Entrada: [{"data": date(2024, 1, 1), "valor": 0.42}, ...] (um registro por mes).
    Saida: [{"ano_mes": 202401, "ipca_mensal": 0.42, "ipca_12m": 4.51}, ...]
    """
    por_mes = {data_para_ano_mes(r["data"]): r["valor"] for r in registros_mensais if r["valor"] is not None}
    saida = []
    for ano_mes in sorted(por_mes):
        janela = [somar_meses(ano_mes, -i) for i in range(12)]
        if all(m in por_mes for m in janela):
            fator = 1.0
            for m in janela:
                fator *= 1 + por_mes[m] / 100
            acumulado = round((fator - 1) * 100, 4)
        else:
            acumulado = None
        saida.append({"ano_mes": ano_mes, "ipca_mensal": por_mes[ano_mes], "ipca_12m": acumulado})
    return saida


def primeiro_dia(ano_mes: int) -> date:
    """Atalho para montar a coluna de data da base mensal."""
    return date(ano_mes // 100, ano_mes % 100, 1)
