"""
Funcoes de calendario usadas pela ingestao e pelas transformacoes.

Sao funcoes puras (recebem valores, devolvem valores, sem efeito colateral),
por isso sao faceis de testar sem Spark e sem internet.
"""
from __future__ import annotations

from datetime import date, timedelta


def ano_mes_para_data(ano_mes: int) -> date:
    """202011 -> date(2020, 11, 1)."""
    return date(ano_mes // 100, ano_mes % 100, 1)


def data_para_ano_mes(d: date) -> int:
    """date(2020, 11, 15) -> 202011."""
    return d.year * 100 + d.month


def somar_meses(ano_mes: int, n: int) -> int:
    """Soma n meses (n pode ser negativo). somar_meses(202011, 3) -> 202102."""
    indice = (ano_mes // 100) * 12 + (ano_mes % 100 - 1) + n
    return (indice // 12) * 100 + indice % 12 + 1


def meses_entre(ano_mes_inicio: int, ano_mes_fim: int) -> list[int]:
    """Lista de meses AAAAMM do inicio ao fim, inclusive: [202011, 202012, 202101, ...]."""
    if ano_mes_fim < ano_mes_inicio:
        return []
    meses = []
    atual = ano_mes_inicio
    while atual <= ano_mes_fim:
        meses.append(atual)
        atual = somar_meses(atual, 1)
    return meses


def janelas_sgs(data_inicio: date, data_fim: date, anos: int) -> list[tuple[date, date]]:
    """
    Quebra o periodo em janelas de no maximo `anos` anos, encostadas uma na outra.
    A API SGS recusa consultas acima de 10 anos em series diarias; usamos janelas
    menores para ficar com folga e para que cada arquivo baixado seja pequeno.
    """
    if data_fim < data_inicio:
        return []
    janelas = []
    inicio = data_inicio
    while inicio <= data_fim:
        fim_janela = date(inicio.year + anos, 1, 1) - timedelta(days=1)
        fim = min(fim_janela, data_fim)
        janelas.append((inicio, fim))
        inicio = fim + timedelta(days=1)
    return janelas


def formatar_data_sgs(d: date) -> str:
    """A API SGS usa dd/MM/aaaa. date(2018, 1, 1) -> '01/01/2018'."""
    return d.strftime("%d/%m/%Y")
