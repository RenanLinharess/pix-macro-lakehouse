"""
Conversao do envelope de ingestao em linhas prontas para o bronze.

O envelope e o mesmo nos dois modos de origem (api ou volume), entao esta funcao
e o unico caminho de entrada do bronze. Ela nao muda nomes de coluna (bronze e
"como veio"); so garante o tipo primitivo de cada campo conforme a especificacao
e anexa os metadados de ingestao.
"""
from __future__ import annotations

from datetime import datetime

from src.catalogo.tabelas import ESPECIFICACAO


def converter_valor(valor, tipo: str):
    """Converte um valor vindo do JSON para o tipo Python que o Spark espera."""
    if valor is None:
        return None
    tipo = tipo.upper()
    if tipo in ("INT", "BIGINT"):
        return int(float(valor)) if isinstance(valor, str) else int(valor)
    if tipo == "DOUBLE":
        return float(valor)
    if tipo == "STRING":
        return str(valor)
    if tipo == "TIMESTAMP":
        return datetime.fromisoformat(valor) if isinstance(valor, str) else valor
    return valor


def envelope_para_linhas(fonte: str, envelope: dict, arquivo_origem: str, carregado_em: datetime) -> list[dict]:
    """
    Transforma {"metadados": {...}, "dados": [...]} em uma lista de dicionarios com as
    colunas da tabela bronze da fonte, mais os metadados de ingestao.
    Campos que a API enviar e nao estiverem na especificacao sao ignorados;
    campos esperados e ausentes viram None.
    """
    colunas_api = ESPECIFICACAO[("bronze", fonte)]["colunas"]
    metadados = envelope["metadados"]
    base_metadados = {
        "fonte": fonte,
        "url_origem": metadados["url"],
        "parametros_requisicao": dict(metadados.get("parametros", {})),
        "baixado_em": converter_valor(metadados["baixado_em"], "TIMESTAMP"),
        "arquivo_origem": arquivo_origem,
        "carregado_em": carregado_em,
    }
    linhas = []
    for registro in envelope["dados"]:
        linha = {nome: converter_valor(registro.get(nome), tipo) for nome, tipo, _ in colunas_api}
        linha.update(base_metadados)
        linhas.append(linha)
    return linhas
