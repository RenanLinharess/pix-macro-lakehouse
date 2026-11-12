# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze: ingestao bruta
# MAGIC
# MAGIC Carrega as fontes do Banco Central nas tabelas bronze, **sem alterar nomes nem valores**,
# MAGIC acrescentando apenas metadados de ingestao (fonte, URL, parametros, quando foi baixado,
# MAGIC arquivo de origem, quando foi gravado).
# MAGIC
# MAGIC Dois modos de origem, escolhidos pelo parametro `modo_origem`:
# MAGIC - `volume`: le os JSONs que o script local `src/ingestao/baixar_dados_brutos.py` baixou e
# MAGIC   `src/ingestao/subir_volume.py` copiou para o Volume. Funciona mesmo sem saida para a internet.
# MAGIC - `api`: chama as APIs direto do notebook (exige saida para a internet liberada no workspace).
# MAGIC
# MAGIC Nos dois modos o caminho de entrada e o mesmo envelope `{"metadados": ..., "dados": [...]}`.
# MAGIC
# MAGIC Idempotencia: o Pix e gravado mes a mes com `replaceWhere` (substitui so aquele mes);
# MAGIC as series do SGS sao pequenas e sobrescritas inteiras; o cadastro de cooperativas e
# MAGIC substituido por arquivo de origem. Rodar duas vezes nao duplica nada.

# COMMAND ----------

import json
import os
import sys
from datetime import date, datetime, timezone

RAIZ = os.path.abspath(os.path.join(os.getcwd(), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from config.configuracoes import (
    CAMINHO_VOLUME_BRUTO,
    FONTES,
    MESES_RECARGA,
    PIX_MES_INICIO,
    SGS_DATA_INICIO,
    SGS_JANELA_ANOS,
    nome_tabela,
)
from src.catalogo.tabelas import esquema_ddl
from src.ingestao import cooperativas, olinda_pix, sgs
from src.spark.utilitarios import gravar_tabela
from src.transformacoes.bronze import envelope_para_linhas
from src.transformacoes.calendario import data_para_ano_mes, janelas_sgs, meses_entre, somar_meses

# COMMAND ----------

dbutils.widgets.text("modo_origem", "volume", "Origem: volume ou api")
dbutils.widgets.text("fontes", "", "Fontes separadas por virgula (vazio = todas)")
dbutils.widgets.text("mes_fim", "", "Ultimo mes AAAAMM (vazio = mes atual)")

MODO = dbutils.widgets.get("modo_origem").strip().lower()
FONTES_ESCOLHIDAS = [f.strip() for f in dbutils.widgets.get("fontes").split(",") if f.strip()] or sorted(FONTES)
HOJE = date.today()
MES_FIM = int(dbutils.widgets.get("mes_fim") or data_para_ano_mes(HOJE))
AGORA = datetime.now(timezone.utc)

if MODO not in ("volume", "api"):
    raise ValueError(f"modo_origem invalido: {MODO}")
print(f"modo={MODO} fontes={FONTES_ESCOLHIDAS} mes_fim={MES_FIM}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Funcoes de apoio
# MAGIC `gravar_envelope` e o unico ponto que escreve no bronze: converte o envelope em linhas
# MAGIC (tipos conforme a especificacao), cria o DataFrame com o esquema da tabela e grava.


# COMMAND ----------

def ler_envelope_do_volume(fonte: str, nome_arquivo: str) -> dict:
    caminho = f"{CAMINHO_VOLUME_BRUTO}/{fonte}/{nome_arquivo}"
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def listar_arquivos_do_volume(fonte: str) -> list[str]:
    pasta = f"{CAMINHO_VOLUME_BRUTO}/{fonte}"
    return sorted(os.listdir(pasta)) if os.path.isdir(pasta) else []


def gravar_envelope(fonte: str, envelope: dict, arquivo_origem: str, substituir_onde: str | None = None) -> int:
    linhas = envelope_para_linhas(fonte, envelope, arquivo_origem, AGORA)
    if not linhas:
        print(f"  {fonte} {arquivo_origem}: vazio, nada gravado")
        return 0
    df = spark.createDataFrame(linhas, schema=esquema_ddl("bronze", fonte))
    gravadas = gravar_tabela(df, "bronze", fonte, modo="overwrite", substituir_onde=substituir_onde)
    print(f"  {fonte} {arquivo_origem}: {gravadas} linhas")
    return gravadas


def meses_ja_carregados(fonte: str) -> set[int]:
    linhas = spark.table(nome_tabela("bronze", fonte)).select("AnoMes").distinct().collect()
    return {linha["AnoMes"] for linha in linhas}


# COMMAND ----------

# MAGIC %md
# MAGIC ## Pix (um arquivo por mes)
# MAGIC Carrega os meses que ainda nao estao no bronze e sempre recarrega os ultimos `MESES_RECARGA`,
# MAGIC porque o Banco Central revisa dados recentes.


# COMMAND ----------

def carregar_fonte_pix(fonte: str) -> None:
    existentes = meses_ja_carregados(fonte)
    recarga = set(meses_entre(somar_meses(MES_FIM, -(MESES_RECARGA - 1)), MES_FIM))
    alvo = [m for m in meses_entre(PIX_MES_INICIO, MES_FIM) if m not in existentes or m in recarga]
    print(f"{fonte}: {len(existentes)} meses no bronze, {len(alvo)} a carregar")
    for ano_mes in alvo:
        nome_arquivo = f"{fonte}_{ano_mes}.json"
        if MODO == "api":
            envelope = olinda_pix.baixar_mes(fonte, ano_mes)
            origem = "api"
        else:
            if nome_arquivo not in listar_arquivos_do_volume(fonte):
                print(f"  {nome_arquivo} nao esta no Volume; pulando")
                continue
            envelope = ler_envelope_do_volume(fonte, nome_arquivo)
            origem = nome_arquivo
        gravar_envelope(fonte, envelope, origem, substituir_onde=f"AnoMes = {ano_mes}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## SGS (Selic e IPCA)
# MAGIC Series pequenas (alguns milhares de linhas): juntamos todas as janelas e sobrescrevemos a tabela.


# COMMAND ----------

def carregar_fonte_sgs(fonte: str) -> None:
    envelopes: list[tuple[dict, str]] = []
    if MODO == "api":
        for inicio, fim in janelas_sgs(SGS_DATA_INICIO, HOJE, SGS_JANELA_ANOS):
            envelopes.append((sgs.baixar_janela(fonte, inicio, fim), "api"))
    else:
        for nome_arquivo in listar_arquivos_do_volume(fonte):
            envelopes.append((ler_envelope_do_volume(fonte, nome_arquivo), nome_arquivo))
    linhas = []
    for envelope, origem in envelopes:
        linhas.extend(envelope_para_linhas(fonte, envelope, origem, AGORA))
    if not linhas:
        raise RuntimeError(f"{fonte}: nenhuma linha encontrada (modo {MODO})")
    df = spark.createDataFrame(linhas, schema=esquema_ddl("bronze", fonte))
    print(f"{fonte}: {gravar_tabela(df, 'bronze', fonte, modo='overwrite')} linhas (tabela sobrescrita)")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Cooperativas (uma foto por data)


# COMMAND ----------

def carregar_fonte_cooperativas(fonte: str) -> None:
    if MODO == "api":
        origem = f"api_{HOJE.isoformat()}"
        gravar_envelope(fonte, cooperativas.baixar_cooperativas(), origem, substituir_onde=f"arquivo_origem = '{origem}'")
        return
    for nome_arquivo in listar_arquivos_do_volume(fonte):
        envelope = ler_envelope_do_volume(fonte, nome_arquivo)
        gravar_envelope(fonte, envelope, nome_arquivo, substituir_onde=f"arquivo_origem = '{nome_arquivo}'")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Execucao

# COMMAND ----------

CARREGADORES = {
    "olinda_pix": carregar_fonte_pix,
    "sgs": carregar_fonte_sgs,
    "olinda_instituicoes": carregar_fonte_cooperativas,
}

for fonte in FONTES_ESCOLHIDAS:
    print(f"== {fonte} ==")
    CARREGADORES[FONTES[fonte]["tipo"]](fonte)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferencia rapida

# COMMAND ----------

for fonte in FONTES_ESCOLHIDAS:
    tabela = nome_tabela("bronze", fonte)
    total = spark.table(tabela).count()
    print(f"{tabela}: {total} linhas")
