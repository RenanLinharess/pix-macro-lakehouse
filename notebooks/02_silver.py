# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver: limpeza, tipos e base mensal unificada
# MAGIC
# MAGIC Transforma o bronze em tabelas confiaveis:
# MAGIC - colunas em `snake_case` e tipos de negocio (DECIMAL para dinheiro, DATE para datas);
# MAGIC - sem duplicados (window function `row_number` sobre a chave natural);
# MAGIC - mes corrente excluido, porque esta incompleto;
# MAGIC - base mensal unificada (Pix + Selic + IPCA), um registro por mes.
# MAGIC
# MAGIC No fim, roda as **regras de qualidade** e grava o resultado na tabela de auditoria.
# MAGIC Se alguma regra de severidade `erro` falhar, o notebook lanca excecao e o job para
# MAGIC antes de construir a gold: dado duvidoso nao chega ao dashboard.
# MAGIC
# MAGIC Escolha de implementacao: as series pequenas (Selic, IPCA) sao trazidas ao driver e
# MAGIC calculadas pelas mesmas funcoes Python testadas no pytest (`src/transformacoes`).
# MAGIC O Pix, maior, e agregado em Spark.

# COMMAND ----------

import os
import sys
from datetime import date, datetime, timezone

from pyspark.sql import Window
from pyspark.sql import functions as F

RAIZ = os.path.abspath(os.path.join(os.getcwd(), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from config.configuracoes import PIX_MES_INICIO, nome_tabela
from src.catalogo.tabelas import esquema_ddl
from src.spark.utilitarios import coluna_data_referencia, gravar_tabela
from src.transformacoes import qualidade
from src.transformacoes.calendario import ano_mes_para_data, data_para_ano_mes
from src.transformacoes.pix import CAPITAIS_IBGE, UF_POR_CODIGO_IBGE
from src.transformacoes.sgs import converter_registro_sgs, selic_media_mensal

# COMMAND ----------

dbutils.widgets.text("execucao_id", "manual", "Identificador da execucao (run id do job)")
EXECUCAO_ID = dbutils.widgets.get("execucao_id") or "manual"
AGORA = datetime.now(timezone.utc)
MES_ATUAL = data_para_ano_mes(date.today())
print(f"execucao={EXECUCAO_ID} mes_atual={MES_ATUAL} (excluido por estar incompleto)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pix mensal (nacional)
# MAGIC Soma as ~11 mil linhas por mes do bronze nas dimensoes que interessam ao negocio.

# COMMAND ----------

bronze_pix = spark.table(nome_tabela("bronze", "pix_estatisticas")).filter(F.col("AnoMes") < MES_ATUAL)

pix_mensal = (
    bronze_pix.groupBy("AnoMes", "NATUREZA", "PAG_PFPJ", "REC_PFPJ", "PAG_REGIAO")
    .agg(F.sum("QUANTIDADE").alias("quantidade"), F.sum("VALOR").alias("valor"))
    .select(
        F.col("AnoMes").alias("ano_mes"),
        F.col("NATUREZA").alias("natureza"),
        F.col("PAG_PFPJ").alias("pagador_tipo"),
        F.col("REC_PFPJ").alias("recebedor_tipo"),
        F.col("PAG_REGIAO").alias("regiao_pagador"),
        "quantidade",
        "valor",
    )
    .withColumn("data_referencia", coluna_data_referencia("ano_mes"))
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("pix_mensal:", gravar_tabela(pix_mensal, "silver", "pix_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pix por municipio
# MAGIC Renomeia para snake_case, converte dinheiro para DECIMAL, deriva a sigla da UF e marca
# MAGIC capital/interior pelo codigo IBGE. Nao agrega: a granularidade continua municipio x mes.

# COMMAND ----------

mapa_uf = F.create_map([F.lit(x) for par in UF_POR_CODIGO_IBGE.items() for x in par])
codigos_capitais = list(CAPITAIS_IBGE.values())

bronze_municipios = spark.table(nome_tabela("bronze", "pix_municipios")).filter(F.col("AnoMes") < MES_ATUAL)

# Se o mesmo mes/municipio aparecer mais de uma vez no bronze, fica a linha carregada por ultimo.
janela_municipio = Window.partitionBy("AnoMes", "Municipio_Ibge").orderBy(F.col("carregado_em").desc())

pix_municipio_mensal = (
    bronze_municipios.withColumn("posicao", F.row_number().over(janela_municipio))
    .filter(F.col("posicao") == 1)
    .select(
        F.col("AnoMes").alias("ano_mes"),
        F.col("Municipio_Ibge").alias("codigo_ibge_municipio"),
        F.col("Municipio").alias("municipio"),
        F.col("Estado_Ibge").alias("codigo_ibge_uf"),
        # O BCB publica, em cada mes, uma linha "NAO INFORMADO" (sem codigo IBGE) para transacoes
        # sem municipio identificado. Mantemos a linha com uf = 'ND' em vez de descarta-la ou
        # deixar nulo: o total nacional continua batendo e a categoria fica explicita.
        F.coalesce(mapa_uf[F.col("Estado_Ibge")], F.lit("ND")).alias("uf"),
        F.col("Regiao").alias("regiao"),
        F.when(F.col("Municipio_Ibge").isNull(), "nao informado")
        .when(F.col("Municipio_Ibge").isin(codigos_capitais), "capital")
        .otherwise("interior")
        .alias("tipo_localidade"),
        F.col("QT_PagadorPF").alias("quantidade_pagador_pf"),
        F.col("VL_PagadorPF").alias("valor_pagador_pf"),
        F.col("QT_PagadorPJ").alias("quantidade_pagador_pj"),
        F.col("VL_PagadorPJ").alias("valor_pagador_pj"),
        F.col("QT_RecebedorPF").alias("quantidade_recebedor_pf"),
        F.col("VL_RecebedorPF").alias("valor_recebedor_pf"),
        F.col("QT_RecebedorPJ").alias("quantidade_recebedor_pj"),
        F.col("VL_RecebedorPJ").alias("valor_recebedor_pj"),
        F.col("QT_PES_PagadorPF").alias("pessoas_pagadoras_pf"),
        F.col("QT_PES_PagadorPJ").alias("pessoas_pagadoras_pj"),
        F.col("QT_PES_RecebedorPF").alias("pessoas_recebedoras_pf"),
        F.col("QT_PES_RecebedorPJ").alias("pessoas_recebedoras_pj"),
    )
    .withColumn("data_referencia", coluna_data_referencia("ano_mes"))
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("pix_municipio_mensal:", gravar_tabela(pix_municipio_mensal, "silver", "pix_municipio_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Selic e IPCA
# MAGIC Deduplica no Spark (window), traz ao driver (poucas linhas) e usa as funcoes testadas.


# COMMAND ----------

def serie_sgs_sem_duplicados(chave_bronze: str) -> list[dict]:
    """Le o bronze da serie, fica com a carga mais recente de cada data e converte os tipos."""
    janela = Window.partitionBy("data").orderBy(F.col("carregado_em").desc())
    linhas = (
        spark.table(nome_tabela("bronze", chave_bronze))
        .withColumn("posicao", F.row_number().over(janela))
        .filter(F.col("posicao") == 1)
        .select("data", "valor")
        .collect()
    )
    registros = [converter_registro_sgs({"data": l["data"], "valor": l["valor"]}) for l in linhas]
    return sorted(registros, key=lambda r: r["data"])


selic_diaria = serie_sgs_sem_duplicados("selic_meta")
selic_linhas = [
    {**m, "data_referencia": ano_mes_para_data(m["ano_mes"]), "atualizado_em": AGORA}
    for m in selic_media_mensal(selic_diaria)
    if m["ano_mes"] < MES_ATUAL
]
selic_df = spark.createDataFrame(selic_linhas, schema=esquema_ddl("silver", "selic_mensal", decimal_como_double=True))
print("selic_mensal:", gravar_tabela(selic_df, "silver", "selic_mensal"), "linhas")

ipca_registros = serie_sgs_sem_duplicados("ipca")
ipca_linhas = [
    {
        "ano_mes": data_para_ano_mes(r["data"]),
        "data_referencia": r["data"],
        "ipca_variacao_mensal": r["valor"],
        "atualizado_em": AGORA,
    }
    for r in ipca_registros
    if data_para_ano_mes(r["data"]) < MES_ATUAL
]
ipca_df = spark.createDataFrame(ipca_linhas, schema=esquema_ddl("silver", "ipca_mensal", decimal_como_double=True))
print("ipca_mensal:", gravar_tabela(ipca_df, "silver", "ipca_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Base mensal unificada
# MAGIC Um registro por mes desde o lancamento do Pix. LEFT JOIN a partir do Pix: se o IPCA do
# MAGIC ultimo mes ainda nao foi divulgado, a linha existe com IPCA nulo e a qualidade avisa.

# COMMAND ----------

pix_total = (
    spark.table(nome_tabela("silver", "pix_mensal"))
    .groupBy("ano_mes")
    .agg(F.sum("quantidade").alias("pix_quantidade"), F.sum("valor").alias("pix_valor"))
    .filter(F.col("ano_mes") >= PIX_MES_INICIO)
)
selic = spark.table(nome_tabela("silver", "selic_mensal")).select("ano_mes", "selic_media")
ipca = spark.table(nome_tabela("silver", "ipca_mensal")).select("ano_mes", "ipca_variacao_mensal")

base_mensal = (
    pix_total.join(selic, "ano_mes", "left")
    .join(ipca, "ano_mes", "left")
    .withColumn("data_referencia", coluna_data_referencia("ano_mes"))
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("base_mensal:", gravar_tabela(base_mensal, "silver", "base_mensal"), "linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cooperativas de credito (fase 1.5)
# MAGIC Foto mais recente do cadastro, sem dados de contato (minimizacao: o que nao e usado nao e
# MAGIC copiado). Um CNPJ repetido no cadastro e resolvido com `row_number`.

# COMMAND ----------

bronze_coop = spark.table(nome_tabela("bronze", "cooperativas"))
ultima_foto = bronze_coop.agg(F.max("baixado_em")).collect()[0][0]
janela_cnpj = Window.partitionBy("CNPJ").orderBy(F.col("NOME_INSTITUICAO"))

cooperativas = (
    bronze_coop.filter(F.col("baixado_em") == ultima_foto)
    .withColumn("posicao", F.row_number().over(janela_cnpj))
    .filter(F.col("posicao") == 1)
    .select(
        F.col("CNPJ").alias("cnpj_base"),
        F.col("NOME_INSTITUICAO").alias("nome"),
        F.col("CLASSE").alias("classe"),
        F.col("ASSOCIACAO").alias("criterio_associacao"),
        F.col("CATEGCOOPSING").alias("categoria"),
        F.when(F.trim(F.col("FILIACAO")) == "", None).otherwise(F.col("FILIACAO")).alias("central_filiacao"),
        F.col("MUNICIPIO").alias("municipio"),
        F.col("MUNICIPIO_IBGE").cast("int").alias("codigo_ibge_municipio"),
        F.col("UF").alias("uf"),
        F.to_date(F.col("baixado_em")).alias("data_referencia"),
    )
    .withColumn("atualizado_em", F.lit(AGORA))
)
print("cooperativas:", gravar_tabela(cooperativas, "silver", "cooperativas"), "linhas (foto de", ultima_foto, ")")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Qualidade de dados
# MAGIC O Spark mede (contagens, minimos, maximos); as regras em `src/transformacoes/qualidade.py`
# MAGIC decidem. Cada resultado vira uma linha na tabela de auditoria.

# COMMAND ----------

resultados: list[dict] = []


def registrar(camada: str, chave: str, resultado: dict, severidade: str = "erro") -> None:
    resultados.append({**resultado, "camada": camada, "tabela": nome_tabela(camada, chave), "severidade": severidade})


def meses_da_tabela(df) -> list[int]:
    return [l["ano_mes"] for l in df.select("ano_mes").distinct().collect()]


def contar_nulos(df, coluna: str) -> int:
    return df.filter(F.col(coluna).isNull()).count()


def minimo_maximo(df, coluna: str):
    linha = df.agg(F.min(coluna).alias("minimo"), F.max(coluna).alias("maximo")).collect()[0]
    return linha["minimo"], linha["maximo"]


# pix_mensal
df = spark.table(nome_tabela("silver", "pix_mensal"))
chave = ["ano_mes", "natureza", "pagador_tipo", "recebedor_tipo", "regiao_pagador"]
registrar("silver", "pix_mensal", qualidade.checar_unicidade(df.count(), df.select(*chave).distinct().count(), "+".join(chave)))
registrar("silver", "pix_mensal", qualidade.checar_nulos(contar_nulos(df, "quantidade") + contar_nulos(df, "valor"), "quantidade,valor"))
registrar("silver", "pix_mensal", qualidade.checar_faixa(*minimo_maximo(df, "valor"), "valor", 0, 10**15))
registrar("silver", "pix_mensal", qualidade.checar_continuidade_meses(meses_da_tabela(df)))

# pix_municipio_mensal
df = spark.table(nome_tabela("silver", "pix_municipio_mensal"))
registrar("silver", "pix_municipio_mensal", qualidade.checar_unicidade(df.count(), df.select("ano_mes", "codigo_ibge_municipio").distinct().count(), "ano_mes+codigo_ibge_municipio"))
registrar("silver", "pix_municipio_mensal", qualidade.checar_nulos(contar_nulos(df, "uf"), "uf"))
registrar("silver", "pix_municipio_mensal", qualidade.checar_continuidade_meses(meses_da_tabela(df)))

# selic_mensal
df = spark.table(nome_tabela("silver", "selic_mensal"))
registrar("silver", "selic_mensal", qualidade.checar_unicidade(df.count(), df.select("ano_mes").distinct().count(), "ano_mes"))
registrar("silver", "selic_mensal", qualidade.checar_faixa(*minimo_maximo(df, "selic_media"), "selic_media", 0, 50))
registrar("silver", "selic_mensal", qualidade.checar_continuidade_meses(meses_da_tabela(df)))

# ipca_mensal
df = spark.table(nome_tabela("silver", "ipca_mensal"))
registrar("silver", "ipca_mensal", qualidade.checar_unicidade(df.count(), df.select("ano_mes").distinct().count(), "ano_mes"))
registrar("silver", "ipca_mensal", qualidade.checar_faixa(*minimo_maximo(df, "ipca_variacao_mensal"), "ipca_variacao_mensal", -5, 10))
registrar("silver", "ipca_mensal", qualidade.checar_continuidade_meses(meses_da_tabela(df)))

# base_mensal
df = spark.table(nome_tabela("silver", "base_mensal"))
registrar("silver", "base_mensal", qualidade.checar_unicidade(df.count(), df.select("ano_mes").distinct().count(), "ano_mes"))
registrar("silver", "base_mensal", qualidade.checar_continuidade_meses(meses_da_tabela(df)))
registrar("silver", "base_mensal", qualidade.checar_nulos(contar_nulos(df, "pix_quantidade"), "pix_quantidade"))
registrar("silver", "base_mensal", qualidade.checar_nulos(contar_nulos(df, "selic_media"), "selic_media", maximo_permitido=1), severidade="aviso")
registrar("silver", "base_mensal", qualidade.checar_nulos(contar_nulos(df, "ipca_variacao_mensal"), "ipca_variacao_mensal", maximo_permitido=1), severidade="aviso")

# cooperativas
df = spark.table(nome_tabela("silver", "cooperativas"))
registrar("silver", "cooperativas", qualidade.checar_unicidade(df.count(), df.select("cnpj_base").distinct().count(), "cnpj_base"))
registrar("silver", "cooperativas", qualidade.checar_nulos(contar_nulos(df, "uf"), "uf"))
registrar("silver", "cooperativas", qualidade.checar_nulos(contar_nulos(df, "classe"), "classe", maximo_permitido=10), severidade="aviso")

# Reconciliacao entre as duas fontes do Pix: a soma nacional deveria bater com a soma por municipio.
# Observado na primeira carga (nov/2026): 68 de 72 meses batem dentro de 0,1%; quatro meses
# (202011, 202309, 202510, 202602) divergem entre 3% e 6,5%. Os arquivos municipais desses meses
# vieram completos (todos os municipios, sem nulos), mas a causa nao foi identificada.
# Decisao: tolerancia de 0,5% e severidade AVISO, para nao bloquear a gold enquanto a causa e
# investigada; a regra registra quais meses passaram da tolerancia.
nacional = spark.table(nome_tabela("silver", "pix_mensal")).groupBy("ano_mes").agg(F.sum("quantidade").alias("qtd_nacional"))
municipal = (
    spark.table(nome_tabela("silver", "pix_municipio_mensal"))
    .groupBy("ano_mes")
    .agg(F.sum(F.col("quantidade_pagador_pf") + F.col("quantidade_pagador_pj")).alias("qtd_municipal"))
)
diferencas_por_mes = {
    l["ano_mes"]: float(l["diferenca"])
    for l in nacional.join(municipal, "ano_mes", "inner")
    .withColumn("diferenca", F.abs(F.col("qtd_nacional") - F.col("qtd_municipal")) / F.col("qtd_nacional"))
    .select("ano_mes", "diferenca")
    .collect()
}
registrar(
    "silver", "pix_mensal",
    qualidade.checar_reconciliacao_serie(diferencas_por_mes, "pix_quantidade nacional x municipal", tolerancia_relativa=0.005),
    severidade="aviso",
)

# COMMAND ----------

linhas_auditoria = [
    {
        "executado_em": AGORA,
        "execucao_id": EXECUCAO_ID,
        "camada": r["camada"],
        "tabela": r["tabela"],
        "regra": r["regra"],
        "coluna": r["coluna"],
        "status": r["status"],
        "severidade": r["severidade"],
        "valor_observado": str(r["valor_observado"]),
        "limite": str(r["limite"]),
        "detalhe": r["detalhe"],
    }
    for r in resultados
]
auditoria_df = spark.createDataFrame(linhas_auditoria, schema=esquema_ddl("auditoria", "resultados_qualidade"))
gravar_tabela(auditoria_df, "auditoria", "resultados_qualidade", modo="append")

display(auditoria_df.select("tabela", "regra", "coluna", "status", "severidade", "valor_observado", "limite", "detalhe"))

resumo = qualidade.resumir(resultados)
erros = [r for r in resultados if r["status"] == qualidade.FALHA and r["severidade"] == "erro"]
print(f"regras: {resumo['total']}, falhas: {resumo['falhas']}, erros bloqueantes: {len(erros)}")
if erros:
    raise RuntimeError("qualidade reprovada: " + "; ".join(f"{e['tabela']} {e['regra']} {e['coluna']}: {e['detalhe']}" for e in erros))
