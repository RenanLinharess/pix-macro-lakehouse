# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Preparar ambiente
# MAGIC
# MAGIC Cria (se nao existirem) os schemas, o Volume e todas as tabelas das camadas bronze, silver,
# MAGIC gold e auditoria, com comentario de tabela e de coluna no Unity Catalog.
# MAGIC
# MAGIC A especificacao vem de um unico lugar: `src/catalogo/tabelas.py`. Os comentarios sao
# MAGIC reaplicados a cada execucao, entao o catalogo nunca fica diferente do codigo.
# MAGIC Rodar este notebook varias vezes e seguro (idempotente).

# COMMAND ----------

import os
import sys

# O notebook fica em notebooks/; a raiz do projeto (config/, src/) e a pasta acima.
RAIZ = os.path.abspath(os.path.join(os.getcwd(), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from config.configuracoes import CATALOGO, SCHEMA_BRONZE, VOLUME_BRUTO, schema_completo
from src.catalogo.tabelas import ddl_comentarios, ddl_criar_tabela, todas_as_tabelas

# COMMAND ----------

COMENTARIOS_SCHEMAS = {
    "bronze": "Dados brutos do Banco Central, como vieram das APIs, com metadados de ingestao.",
    "silver": "Dados limpos e tipados: snake_case, sem duplicados, base mensal unificada.",
    "gold": "Indicadores prontos para analise e dashboard: crescimento do Pix, Selic, IPCA, recorte por UF.",
    "auditoria": "Resultados das regras de qualidade de cada execucao do pipeline.",
}

for camada, comentario in COMENTARIOS_SCHEMAS.items():
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_completo(camada)} COMMENT '{comentario}'")
    print("schema ok:", schema_completo(camada))

spark.sql(
    f"CREATE VOLUME IF NOT EXISTS {CATALOGO}.{SCHEMA_BRONZE}.{VOLUME_BRUTO} "
    "COMMENT 'Zona de pouso: arquivos JSON brutos baixados das APIs do Banco Central.'"
)
print("volume ok:", f"{CATALOGO}.{SCHEMA_BRONZE}.{VOLUME_BRUTO}")

# COMMAND ----------

for camada, chave in todas_as_tabelas():
    spark.sql(ddl_criar_tabela(camada, chave))
    for comando in ddl_comentarios(camada, chave):
        spark.sql(comando)
    print("tabela ok:", camada, chave)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferencia
# MAGIC Lista as tabelas criadas com seus comentarios, direto do catalogo.

# COMMAND ----------

for camada in COMENTARIOS_SCHEMAS:
    display(spark.sql(f"SHOW TABLES IN {schema_completo(camada)}"))
