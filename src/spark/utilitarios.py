"""
Utilitarios PySpark usados pelos notebooks. Este e o unico modulo de src/ que importa
pyspark, por isso os testes locais (sem Spark) nunca o importam.
"""
from __future__ import annotations

from pyspark.sql import DataFrame, functions as F

from config.configuracoes import nome_tabela
from src.catalogo.tabelas import colunas


def alinhar_ao_esquema(df: DataFrame, camada: str, chave: str) -> DataFrame:
    """
    Seleciona e converte as colunas do DataFrame para exatamente o esquema da tabela
    (mesma ordem, mesmos tipos). Evita erro de "schema mismatch" do Delta e garante
    que a tabela gravada e identica a especificacao do catalogo.
    """
    return df.select([F.col(nome).cast(tipo).alias(nome) for nome, tipo, _ in colunas(camada, chave)])


def gravar_tabela(df: DataFrame, camada: str, chave: str, modo: str = "overwrite", substituir_onde: str | None = None) -> int:
    """
    Grava o DataFrame na tabela Delta da camada e devolve a quantidade de linhas.

    - modo="overwrite" sem substituir_onde: troca todo o conteudo (gold e silver pequenas);
    - modo="overwrite" com substituir_onde="AnoMes = 202401": troca so as linhas do predicado
      (bronze por mes), o que torna a carga idempotente: rodar duas vezes nao duplica;
    - modo="append": acrescenta (tabela de auditoria, que e historico).
    """
    alinhado = alinhar_ao_esquema(df, camada, chave)
    escrita = alinhado.write.format("delta").mode(modo)
    if substituir_onde:
        escrita = escrita.option("replaceWhere", substituir_onde)
    escrita.saveAsTable(nome_tabela(camada, chave))
    return alinhado.count()


def coluna_data_referencia(coluna_ano_mes: str = "ano_mes"):
    """Expressao que transforma 202011 em DATE 2020-11-01."""
    return F.to_date(F.col(coluna_ano_mes).cast("string"), "yyyyMM")
