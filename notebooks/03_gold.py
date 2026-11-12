# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold: indicadores para analise e dashboard
# MAGIC
# MAGIC Constroi as tabelas que respondem a pergunta de negocio:
# MAGIC - `indicadores_mensais`: crescimento do Pix (mes a mes e 12 meses), Selic media e IPCA
# MAGIC   acumulado em 12 meses (produto das taxas mensais, nunca soma);
# MAGIC - `pix_uf_mensal`: Pix pago por residentes de cada UF, participacao nacional e crescimento;
# MAGIC - `pix_capital_interior_mensal`: capital versus interior em cada UF (interiorizacao do Pix).
# MAGIC
# MAGIC A gold e pequena (dezenas a poucos milhares de linhas) e e reconstruida inteira a cada
# MAGIC execucao: simples, deterministico e idempotente.
# MAGIC
# MAGIC Os calculos de serie (variacao, acumulado) usam as funcoes de `src/transformacoes`,
# MAGIC as mesmas que o pytest testa. O recorte por UF usa window functions do Spark
# MAGIC (`lag` para 12 meses atras, `sum over` para participacao).

# COMMAND ----------

import os
import sys
from datetime import datetime, timezone

from pyspark.sql import Window
from pyspark.sql import functions as F

RAIZ = os.path.abspath(os.path.join(os.getcwd(), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from config.configuracoes import nome_tabela
from src.catalogo.tabelas import esquema_ddl
from src.spark.utilitarios import coluna_data_referencia, gravar_tabela
from src.transformacoes.pix import crescimento_mensal
from src.transformacoes.sgs import ipca_acumulado_12m

AGORA = datetime.now(timezone.utc)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Indicadores mensais
# MAGIC A base mensal tem ~70 linhas: trazemos ao driver e aplicamos as funcoes testadas.


# COMMAND ----------

def para_float(valor):
    return None if valor is None else float(valor)


base = [
    {
        "ano_mes": l["ano_mes"],
        "data_referencia": l["data_referencia"],
        "pix_quantidade": l["pix_quantidade"],
        "pix_valor": para_float(l["pix_valor"]),
        "selic_media": para_float(l["selic_media"]),
        "ipca_variacao_mensal": para_float(l["ipca_variacao_mensal"]),
    }
    for l in spark.table(nome_tabela("silver", "base_mensal")).orderBy("ano_mes").collect()
]

# O acumulado em 12 meses precisa de historico anterior ao Pix, por isso usa a serie completa do IPCA.
ipca_completo = [
    {"data": l["data_referencia"], "valor": para_float(l["ipca_variacao_mensal"])}
    for l in spark.table(nome_tabela("silver", "ipca_mensal")).orderBy("ano_mes").collect()
]
ipca_12m = {r["ano_mes"]: r["ipca_12m"] for r in ipca_acumulado_12m(ipca_completo)}

serie = crescimento_mensal(crescimento_mensal(base, "pix_quantidade"), "pix_valor")
indicadores = [
    {
        "ano_mes": r["ano_mes"],
        "data_referencia": r["data_referencia"],
        "pix_quantidade": r["pix_quantidade"],
        "pix_valor": r["pix_valor"],
        "pix_ticket_medio": (r["pix_valor"] / r["pix_quantidade"]) if r["pix_quantidade"] else None,
        "pix_quantidade_var_mensal_pct": r["pix_quantidade_var_mensal"],
        "pix_quantidade_var_12m_pct": r["pix_quantidade_var_12m"],
        "pix_valor_var_mensal_pct": r["pix_valor_var_mensal"],
        "pix_valor_var_12m_pct": r["pix_valor_var_12m"],
        "selic_media": r["selic_media"],
        "ipca_variacao_mensal": r["ipca_variacao_mensal"],
        "ipca_acumulado_12m": ipca_12m.get(r["ano_mes"]),
        "atualizado_em": AGORA,
    }
    for r in serie
]
indicadores_df = spark.createDataFrame(indicadores, schema=esquema_ddl("gold", "indicadores_mensais", decimal_como_double=True))
print("indicadores_mensais:", gravar_tabela(indicadores_df, "gold", "indicadores_mensais"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pix por UF
# MAGIC Perspectiva do pagador: transacoes feitas por residentes da UF. `lag(valor, 12)` busca o
# MAGIC mesmo mes do ano anterior dentro de cada UF; `sum(valor) over (partition by ano_mes)` da o
# MAGIC total nacional do mes para calcular a participacao.

# COMMAND ----------

municipios = spark.table(nome_tabela("silver", "pix_municipio_mensal"))

por_uf = municipios.groupBy("ano_mes", "uf", "regiao").agg(
    F.sum(F.col("quantidade_pagador_pf") + F.col("quantidade_pagador_pj")).alias("quantidade"),
    F.sum(F.col("valor_pagador_pf") + F.col("valor_pagador_pj")).alias("valor"),
    F.sum(F.col("pessoas_pagadoras_pf") + F.col("pessoas_pagadoras_pj")).alias("pessoas_pagadoras"),
    F.countDistinct("codigo_ibge_municipio").alias("municipios"),
)

janela_nacional = Window.partitionBy("ano_mes")
janela_uf = Window.partitionBy("uf").orderBy("ano_mes")

pix_uf_mensal = (
    por_uf.withColumn("participacao_nacional_valor_pct", F.col("valor") / F.sum("valor").over(janela_nacional) * 100)
    .withColumn("valor_12m_atras", F.lag("valor", 12).over(janela_uf))
    .withColumn("valor_var_12m_pct", (F.col("valor") / F.col("valor_12m_atras") - 1) * 100)
    .withColumn("valor_por_pessoa", F.col("valor") / F.col("pessoas_pagadoras"))
    .withColumn("data_referencia", coluna_data_referencia("ano_mes"))
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("pix_uf_mensal:", gravar_tabela(pix_uf_mensal, "gold", "pix_uf_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Capital versus interior

# COMMAND ----------

janela_uf_mes = Window.partitionBy("ano_mes", "uf")

pix_capital_interior = (
    municipios.groupBy("ano_mes", "uf", "tipo_localidade")
    .agg(
        F.sum(F.col("quantidade_pagador_pf") + F.col("quantidade_pagador_pj")).alias("quantidade"),
        F.sum(F.col("valor_pagador_pf") + F.col("valor_pagador_pj")).alias("valor"),
        F.sum(F.col("pessoas_pagadoras_pf") + F.col("pessoas_pagadoras_pj")).alias("pessoas_pagadoras"),
        F.countDistinct("codigo_ibge_municipio").alias("municipios"),
    )
    .withColumn("participacao_uf_valor_pct", F.col("valor") / F.sum("valor").over(janela_uf_mes) * 100)
    .withColumn("data_referencia", coluna_data_referencia("ano_mes"))
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("pix_capital_interior_mensal:", gravar_tabela(pix_capital_interior, "gold", "pix_capital_interior_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferencia
# MAGIC Ultimos 12 meses dos indicadores e o ranking de UFs no ultimo mes.

# COMMAND ----------

display(spark.table(nome_tabela("gold", "indicadores_mensais")).orderBy(F.col("ano_mes").desc()).limit(12))

ultimo_mes = spark.table(nome_tabela("gold", "pix_uf_mensal")).agg(F.max("ano_mes")).collect()[0][0]
display(
    spark.table(nome_tabela("gold", "pix_uf_mensal"))
    .filter(F.col("ano_mes") == ultimo_mes)
    .orderBy(F.col("valor").desc())
    .select("uf", "regiao", "quantidade", "valor", "pessoas_pagadoras", "participacao_nacional_valor_pct", "valor_var_12m_pct")
)
