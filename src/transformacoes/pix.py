"""
Transformacoes das estatisticas do Pix.

As agregacoes pesadas (somar 11 mil linhas por mes) rodam em Spark na silver.
Aqui ficam os calculos sobre series ja agregadas (poucas centenas de linhas):
crescimento mes a mes, variacao em 12 meses e classificacao capital/interior.
"""
from __future__ import annotations

# Codigos IBGE das capitais, usados para separar capital e interior por UF.
CAPITAIS_IBGE: dict[str, int] = {
    "AC": 1200401, "AL": 2704302, "AP": 1600303, "AM": 1302603, "BA": 2927408,
    "CE": 2304400, "DF": 5300108, "ES": 3205309, "GO": 5208707, "MA": 2111300,
    "MT": 5103403, "MS": 5002704, "MG": 3106200, "PA": 1501402, "PB": 2507507,
    "PR": 4106902, "PE": 2611606, "PI": 2211001, "RJ": 3304557, "RN": 2408102,
    "RS": 4314902, "RO": 1100205, "RR": 1400100, "SC": 4205407, "SP": 3550308,
    "SE": 2800308, "TO": 1721000,
}

# Codigo IBGE do estado -> sigla. O Olinda traz Estado_Ibge (numero) e Estado (nome por extenso).
UF_POR_CODIGO_IBGE: dict[int, str] = {
    12: "AC", 27: "AL", 16: "AP", 13: "AM", 29: "BA", 23: "CE", 53: "DF", 32: "ES", 52: "GO",
    21: "MA", 51: "MT", 50: "MS", 31: "MG", 15: "PA", 25: "PB", 41: "PR", 26: "PE", 22: "PI",
    33: "RJ", 24: "RN", 43: "RS", 11: "RO", 14: "RR", 42: "SC", 35: "SP", 28: "SE", 17: "TO",
}


def classificar_capital_interior(municipio_ibge: int) -> str:
    """'capital' se o codigo IBGE for de uma capital, senao 'interior'."""
    return "capital" if municipio_ibge in CAPITAIS_IBGE.values() else "interior"


def variacao_percentual(atual: float | None, anterior: float | None) -> float | None:
    """(atual / anterior - 1) * 100, ou None se faltar dado ou o anterior for zero."""
    if atual is None or anterior is None or anterior == 0:
        return None
    return round((atual / anterior - 1) * 100, 4)


def crescimento_mensal(serie: list[dict], coluna: str) -> list[dict]:
    """
    Acrescenta a cada ponto a variacao percentual em relacao ao mes anterior
    (<coluna>_var_mensal) e ao mesmo mes do ano anterior (<coluna>_var_12m).

    A serie deve estar ordenada por ano_mes e sem buracos (a camada de qualidade
    garante a continuidade antes). Quando nao ha mes anterior, o valor e None.
    Isto e o equivalente em Python puro de LAG(coluna, 1) e LAG(coluna, 12) em SQL.
    """
    ordenada = sorted(serie, key=lambda r: r["ano_mes"])
    por_mes = {r["ano_mes"]: r.get(coluna) for r in ordenada}
    saida = []
    for registro in ordenada:
        ano_mes = registro["ano_mes"]
        novo = dict(registro)
        novo[f"{coluna}_var_mensal"] = variacao_percentual(por_mes[ano_mes], por_mes.get(_mes_anterior(ano_mes, 1)))
        novo[f"{coluna}_var_12m"] = variacao_percentual(por_mes[ano_mes], por_mes.get(_mes_anterior(ano_mes, 12)))
        saida.append(novo)
    return saida


def _mes_anterior(ano_mes: int, n: int) -> int:
    from src.transformacoes.calendario import somar_meses

    return somar_meses(ano_mes, -n)
