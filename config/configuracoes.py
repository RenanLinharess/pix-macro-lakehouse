"""
Configuracao central do projeto.

Tudo que e nome de catalogo, schema, tabela, caminho, data de inicio ou parametro
de fonte fica aqui, em um unico lugar. Notebooks, scripts e testes importam deste
modulo. Se algo precisar mudar (por exemplo, o catalogo), muda-se em uma linha.
"""
from __future__ import annotations

from datetime import date

# --- Unity Catalog ----------------------------------------------------------------
CATALOGO = "workspace"  # catalogo padrao do Databricks Free Edition
SCHEMA_BRONZE = "pix_macro_bronze"
SCHEMA_SILVER = "pix_macro_silver"
SCHEMA_GOLD = "pix_macro_gold"
SCHEMA_AUDITORIA = "pix_macro_auditoria"

# Volume do Unity Catalog que recebe os JSONs brutos (zona de pouso).
VOLUME_BRUTO = "dados_brutos"
CAMINHO_VOLUME_BRUTO = f"/Volumes/{CATALOGO}/{SCHEMA_BRONZE}/{VOLUME_BRUTO}"

# Pasta local equivalente ao Volume, usada pelo script de download.
PASTA_DADOS_BRUTOS = "data/raw"

# --- Fontes publicas do Banco Central ---------------------------------------------
URL_OLINDA_PIX = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata"
URL_OLINDA_INSTITUICOES = (
    "https://olinda.bcb.gov.br/olinda/servico/Instituicoes_em_funcionamento/versao/v1/odata"
)
URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# Cada fonte tem um nome curto (chave) usado em pastas, arquivos e tabelas bronze.
FONTES: dict[str, dict] = {
    "pix_estatisticas": {
        "tipo": "olinda_pix",
        "funcao": "EstatisticasTransacoesPix(Database=@Database)",
        "parametro": "@Database",  # mes inicial AAAAMM (a API devolve dali em diante)
        "descricao": "Transacoes Pix liquidadas por mes, com dimensoes de pagador e recebedor.",
    },
    "pix_municipios": {
        "tipo": "olinda_pix",
        "funcao": "TransacoesPixPorMunicipio(DataBase=@DataBase)",
        "parametro": "@DataBase",
        "descricao": "Transacoes Pix por municipio e mes, separadas por PF e PJ.",
    },
    "selic_meta": {
        "tipo": "sgs",
        "codigo": 432,
        "periodicidade": "diaria",
        "descricao": "Meta da taxa Selic definida pelo Copom, % ao ano, serie diaria.",
    },
    "ipca": {
        "tipo": "sgs",
        "codigo": 433,
        "periodicidade": "mensal",
        "descricao": "IPCA, variacao mensal em %.",
    },
    "cooperativas": {
        "tipo": "olinda_instituicoes",
        "recurso": "SedesCooperativas",
        "descricao": "Cadastro das cooperativas de credito em funcionamento no pais.",
    },
}

# --- Janela temporal ---------------------------------------------------------------
PIX_MES_INICIO = 202011  # lancamento do Pix (novembro de 2020)
SGS_DATA_INICIO = date(2018, 1, 1)  # contexto de juros e inflacao antes do Pix
SGS_JANELA_ANOS = 5  # a API SGS recusa janelas acima de 10 anos em series diarias
MESES_RECARGA = 3  # o BCB revisa meses recentes; sempre recarregamos os ultimos N

# --- Tabelas por camada ------------------------------------------------------------
TABELAS: dict[str, dict[str, str]] = {
    "bronze": {
        "pix_estatisticas": "pix_estatisticas",
        "pix_municipios": "pix_municipios",
        "selic_meta": "selic_meta_diaria",
        "ipca": "ipca_mensal",
        "cooperativas": "cooperativas",
    },
    "silver": {
        "pix_mensal": "pix_mensal",
        "pix_municipio_mensal": "pix_municipio_mensal",
        "selic_mensal": "selic_mensal",
        "ipca_mensal": "ipca_mensal",
        "base_mensal": "base_mensal",
        "cooperativas": "cooperativas",
    },
    "gold": {
        "indicadores_mensais": "indicadores_mensais",
        "pix_uf_mensal": "pix_uf_mensal",
        "pix_rs_capital_interior": "pix_rs_capital_interior",
        "cooperativas_uf": "cooperativas_uf",
    },
    "auditoria": {
        "resultados_qualidade": "resultados_qualidade",
    },
}

_SCHEMAS = {
    "bronze": SCHEMA_BRONZE,
    "silver": SCHEMA_SILVER,
    "gold": SCHEMA_GOLD,
    "auditoria": SCHEMA_AUDITORIA,
}


def nome_tabela(camada: str, chave: str) -> str:
    """Devolve o nome completo catalogo.schema.tabela de uma tabela da camada."""
    return f"{CATALOGO}.{_SCHEMAS[camada]}.{TABELAS[camada][chave]}"


def schema_completo(camada: str) -> str:
    """Devolve catalogo.schema da camada."""
    return f"{CATALOGO}.{_SCHEMAS[camada]}"
