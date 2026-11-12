"""
Regras de qualidade de dados.

Cada funcao recebe valores simples (listas, numeros) e devolve um resultado
padronizado, que o notebook grava na tabela de auditoria:

    {"regra": "nulos", "coluna": "valor", "status": "ok" | "falha",
     "valor_observado": 0, "limite": 0, "detalhe": "..."}

A decisao de parar o pipeline ou so registrar fica no notebook (severidade).
Manter as regras puras permite testa-las em milissegundos e explicar cada uma
numa entrevista sem abrir o Spark.
"""
from __future__ import annotations

from src.transformacoes.calendario import meses_entre

OK = "ok"
FALHA = "falha"


def _resultado(regra: str, coluna: str | None, status: str, valor_observado, limite, detalhe: str) -> dict:
    return {
        "regra": regra,
        "coluna": coluna,
        "status": status,
        "valor_observado": valor_observado,
        "limite": limite,
        "detalhe": detalhe,
    }


def checar_nulos(quantidade_nulos: int, coluna: str, maximo_permitido: int = 0) -> dict:
    """Falha se houver mais nulos do que o permitido na coluna."""
    status = OK if quantidade_nulos <= maximo_permitido else FALHA
    return _resultado("nulos", coluna, status, quantidade_nulos, maximo_permitido, f"{quantidade_nulos} nulos em {coluna}")


def checar_faixa(valor_minimo, valor_maximo, coluna: str, limite_inferior, limite_superior) -> dict:
    """Falha se o minimo ou o maximo observados sairem da faixa plausivel."""
    dentro = valor_minimo is not None and valor_maximo is not None and limite_inferior <= valor_minimo and valor_maximo <= limite_superior
    status = OK if dentro else FALHA
    return _resultado(
        "faixa", coluna, status, f"[{valor_minimo}, {valor_maximo}]", f"[{limite_inferior}, {limite_superior}]",
        f"faixa observada de {coluna}",
    )


def checar_unicidade(total_linhas: int, linhas_distintas: int, chave: str) -> dict:
    """Falha se existirem linhas repetidas para a chave (total > distintas)."""
    duplicadas = total_linhas - linhas_distintas
    status = OK if duplicadas == 0 else FALHA
    return _resultado("unicidade", chave, status, duplicadas, 0, f"{duplicadas} linhas duplicadas na chave {chave}")


def checar_continuidade_meses(meses: list[int], coluna: str = "ano_mes") -> dict:
    """
    Falha se faltar algum mes entre o primeiro e o ultimo observados.
    Um buraco na serie quebraria o calculo de variacao mensal e de acumulado 12 meses.
    """
    if not meses:
        return _resultado("continuidade_meses", coluna, FALHA, 0, 0, "serie vazia")
    esperados = meses_entre(min(meses), max(meses))
    faltantes = sorted(set(esperados) - set(meses))
    status = OK if not faltantes else FALHA
    detalhe = "sem buracos" if not faltantes else f"meses faltantes: {faltantes[:12]}"
    return _resultado("continuidade_meses", coluna, status, len(faltantes), 0, detalhe)


def checar_reconciliacao(valor_a: float, valor_b: float, descricao: str, tolerancia_relativa: float = 0.001) -> dict:
    """
    Compara dois totais que deveriam ser iguais (ex.: soma nacional do Pix vs soma
    por municipio). Falha se a diferenca relativa passar da tolerancia.
    """
    if valor_a is None or valor_b is None:
        return _resultado("reconciliacao", descricao, FALHA, None, tolerancia_relativa, "valor ausente")
    base = max(abs(valor_a), abs(valor_b), 1e-9)
    diferenca = abs(valor_a - valor_b) / base
    status = OK if diferenca <= tolerancia_relativa else FALHA
    return _resultado("reconciliacao", descricao, status, round(diferenca, 6), tolerancia_relativa, f"a={valor_a} b={valor_b}")


def resumir(resultados: list[dict]) -> dict:
    """Conta ok e falhas; util para decidir se o job continua."""
    falhas = [r for r in resultados if r["status"] == FALHA]
    return {"total": len(resultados), "falhas": len(falhas), "regras_com_falha": [f"{r['regra']}:{r['coluna']}" for r in falhas]}
