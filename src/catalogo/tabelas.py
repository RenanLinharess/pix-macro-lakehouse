"""
Especificacao de todas as tabelas do projeto: colunas, tipos e comentarios.

Este modulo e a fonte unica de verdade para o esquema. A partir dele geramos:
- o DDL CREATE TABLE com COMMENT em tabela e coluna (governanca no Unity Catalog);
- os comandos ALTER ... COMMENT que mantem os comentarios sincronizados a cada execucao;
- a string de esquema usada pelo Spark ao criar DataFrames (createDataFrame(..., schema=...)).

Convencoes:
- bronze: nomes de coluna EXATAMENTE como a API devolve (AnoMes, VL_PagadorPF), mais metadados;
- silver e gold: snake_case em portugues, tipos de negocio (DECIMAL para dinheiro, DATE para datas).
"""
from __future__ import annotations

from config.configuracoes import TABELAS, nome_tabela

# Colunas de metadados que toda tabela bronze recebe, alem das colunas da API.
METADADOS_BRONZE: list[tuple[str, str, str]] = [
    ("fonte", "STRING", "Nome curto da fonte, conforme config/configuracoes.py"),
    ("url_origem", "STRING", "URL da API chamada para obter os registros"),
    ("parametros_requisicao", "MAP<STRING,STRING>", "Parametros enviados na requisicao (mes, filtro, formato)"),
    ("baixado_em", "TIMESTAMP", "Momento (UTC) em que a resposta foi baixada da API"),
    ("arquivo_origem", "STRING", "Nome do arquivo JSON no Volume, ou api quando lido direto da API"),
    ("carregado_em", "TIMESTAMP", "Momento (UTC) em que a linha foi gravada no bronze"),
]

_ATUALIZADO_EM = ("atualizado_em", "TIMESTAMP", "Momento (UTC) da ultima execucao que gravou a linha")

# Cobertura das series abertas do Pix, conforme a descricao do recurso no portal de dados abertos
# do BCB. Comparando com os totais anuais do BC, cobre ~89% das transacoes (2024 e 2025).
_COBERTURA_SPI = "Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB)."

# Cada entrada: (camada, chave) ->{"comentario", "colunas": [(nome, tipo, comentario)], "cluster_by": [...]}
ESPECIFICACAO: dict[tuple[str, str], dict] = {
    # ------------------------------------------------------------------ BRONZE
    ("bronze", "pix_estatisticas"): {
        "comentario": "Transacoes Pix liquidadas no SPI por mes, como vieram da API Olinda do BCB (EstatisticasTransacoesPix). Uma linha por combinacao de dimensoes. " + _COBERTURA_SPI,
        "cluster_by": ["AnoMes"],
        "colunas": [
            ("AnoMes", "INT", "Mes de referencia no formato AAAAMM"),
            ("PAG_PFPJ", "STRING", "Tipo do pagador: PF ou PJ"),
            ("REC_PFPJ", "STRING", "Tipo do recebedor: PF ou PJ"),
            ("PAG_REGIAO", "STRING", "Regiao geografica do pagador"),
            ("REC_REGIAO", "STRING", "Regiao geografica do recebedor"),
            ("PAG_IDADE", "STRING", "Faixa etaria do pagador (somente PF)"),
            ("REC_IDADE", "STRING", "Faixa etaria do recebedor (somente PF)"),
            ("FORMAINICIACAO", "STRING", "Forma de iniciacao da transacao (QR code, chave, iniciador etc.)"),
            ("NATUREZA", "STRING", "Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc."),
            ("FINALIDADE", "STRING", "Finalidade: Pix, Pix Saque, Pix Troco etc."),
            ("VALOR", "DOUBLE", "Valor total liquidado em reais"),
            ("QUANTIDADE", "BIGINT", "Quantidade de transacoes liquidadas"),
        ],
    },
    ("bronze", "pix_municipios"): {
        "comentario": "Transacoes Pix por municipio e mes, como vieram da API Olinda do BCB (TransacoesPixPorMunicipio). Mesma cobertura da serie nacional (a soma bate, regra de reconciliacao). " + _COBERTURA_SPI,
        "cluster_by": ["AnoMes"],
        "colunas": [
            ("AnoMes", "INT", "Mes de referencia no formato AAAAMM"),
            ("Municipio_Ibge", "INT", "Codigo IBGE do municipio (7 digitos)"),
            ("Municipio", "STRING", "Nome do municipio"),
            ("Estado_Ibge", "INT", "Codigo IBGE da unidade da federacao (2 digitos)"),
            ("Estado", "STRING", "Nome da unidade da federacao"),
            ("Sigla_Regiao", "STRING", "Sigla da regiao geografica"),
            ("Regiao", "STRING", "Nome da regiao geografica"),
            ("VL_PagadorPF", "DOUBLE", "Valor pago por pessoas fisicas do municipio, em reais"),
            ("QT_PagadorPF", "BIGINT", "Quantidade de transacoes pagas por pessoas fisicas"),
            ("VL_PagadorPJ", "DOUBLE", "Valor pago por pessoas juridicas do municipio, em reais"),
            ("QT_PagadorPJ", "BIGINT", "Quantidade de transacoes pagas por pessoas juridicas"),
            ("VL_RecebedorPF", "DOUBLE", "Valor recebido por pessoas fisicas do municipio, em reais"),
            ("QT_RecebedorPF", "BIGINT", "Quantidade de transacoes recebidas por pessoas fisicas"),
            ("VL_RecebedorPJ", "DOUBLE", "Valor recebido por pessoas juridicas do municipio, em reais"),
            ("QT_RecebedorPJ", "BIGINT", "Quantidade de transacoes recebidas por pessoas juridicas"),
            ("QT_PES_PagadorPF", "BIGINT", "Quantidade de pessoas fisicas distintas que pagaram no mes"),
            ("QT_PES_PagadorPJ", "BIGINT", "Quantidade de pessoas juridicas distintas que pagaram no mes"),
            ("QT_PES_RecebedorPF", "BIGINT", "Quantidade de pessoas fisicas distintas que receberam no mes"),
            ("QT_PES_RecebedorPJ", "BIGINT", "Quantidade de pessoas juridicas distintas que receberam no mes"),
        ],
    },
    ("bronze", "selic_meta"): {
        "comentario": "Meta da taxa Selic (SGS serie 432), serie diaria, como veio da API: data e valor em texto.",
        "cluster_by": [],
        "colunas": [
            ("data", "STRING", "Data no formato dd/MM/aaaa, como enviada pela API"),
            ("valor", "STRING", "Meta Selic em % ao ano, como texto enviado pela API"),
        ],
    },
    ("bronze", "ipca"): {
        "comentario": "IPCA variacao mensal (SGS serie 433), como veio da API: data e valor em texto.",
        "cluster_by": [],
        "colunas": [
            ("data", "STRING", "Primeiro dia do mes no formato dd/MM/aaaa, como enviado pela API"),
            ("valor", "STRING", "Variacao mensal do IPCA em %, como texto enviado pela API"),
        ],
    },
    ("bronze", "cooperativas"): {
        "comentario": "Cadastro das cooperativas de credito em funcionamento, como veio da API Olinda do BCB (SedesCooperativas). Uma foto por data de download.",
        "cluster_by": [],
        "colunas": [
            ("CNPJ", "STRING", "CNPJ base (8 digitos) da cooperativa"),
            ("NOME_INSTITUICAO", "STRING", "Razao social"),
            ("ENDERECO", "STRING", "Endereco da sede"),
            ("COMPLEMENTO", "STRING", "Complemento do endereco"),
            ("BAIRRO", "STRING", "Bairro da sede"),
            ("CEP", "STRING", "CEP da sede"),
            ("MUNICIPIO", "STRING", "Municipio da sede"),
            ("UF", "STRING", "Unidade da federacao da sede"),
            ("DDD", "STRING", "DDD do telefone institucional"),
            ("TELEFONE", "STRING", "Telefone institucional"),
            ("CLASSE", "STRING", "Classe: Singular, Central ou Confederacao"),
            ("ASSOCIACAO", "STRING", "Criterio de associacao (livre admissao, empregados, produtor rural etc.)"),
            ("CATEGCOOPSING", "STRING", "Categoria da singular: Classica, Plena ou Capital e Emprestimo"),
            ("FILIACAO", "STRING", "Central a qual a cooperativa e filiada"),
            ("E_MAIL", "STRING", "E-mail institucional"),
            ("SITIO_NA_INTERNET", "STRING", "Site institucional"),
            ("MUNICIPIO_IBGE", "STRING", "Codigo IBGE do municipio da sede"),
        ],
    },
    # ------------------------------------------------------------------ SILVER
    ("silver", "pix_mensal"): {
        "comentario": "Transacoes Pix por mes e natureza, agregadas a partir do bronze. Exclui o mes corrente (incompleto). " + _COBERTURA_SPI,
        "cluster_by": ["ano_mes"],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("natureza", "STRING", "Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc."),
            ("pagador_tipo", "STRING", "Tipo do pagador: PF ou PJ"),
            ("recebedor_tipo", "STRING", "Tipo do recebedor: PF ou PJ"),
            ("regiao_pagador", "STRING", "Regiao geografica do pagador"),
            ("quantidade", "BIGINT", "Quantidade de transacoes liquidadas"),
            ("valor", "DECIMAL(20,2)", "Valor total liquidado em reais"),
            _ATUALIZADO_EM,
        ],
    },
    ("silver", "pix_municipio_mensal"): {
        "comentario": "Transacoes Pix por municipio e mes, com tipos corrigidos, sigla da UF e classificacao capital/interior. Exclui o mes corrente. " + _COBERTURA_SPI,
        "cluster_by": ["ano_mes", "uf"],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("codigo_ibge_municipio", "INT", "Codigo IBGE do municipio (7 digitos)"),
            ("municipio", "STRING", "Nome do municipio"),
            ("codigo_ibge_uf", "INT", "Codigo IBGE da unidade da federacao"),
            ("uf", "STRING", "Sigla da unidade da federacao; ND para a linha mensal de municipio nao informado publicada pelo BCB"),
            ("regiao", "STRING", "Nome da regiao geografica"),
            ("tipo_localidade", "STRING", "capital, interior (pelo codigo IBGE da capital da UF) ou nao informado"),
            ("quantidade_pagador_pf", "BIGINT", "Transacoes pagas por pessoas fisicas do municipio"),
            ("valor_pagador_pf", "DECIMAL(20,2)", "Valor pago por pessoas fisicas, em reais"),
            ("quantidade_pagador_pj", "BIGINT", "Transacoes pagas por pessoas juridicas do municipio"),
            ("valor_pagador_pj", "DECIMAL(20,2)", "Valor pago por pessoas juridicas, em reais"),
            ("quantidade_recebedor_pf", "BIGINT", "Transacoes recebidas por pessoas fisicas do municipio"),
            ("valor_recebedor_pf", "DECIMAL(20,2)", "Valor recebido por pessoas fisicas, em reais"),
            ("quantidade_recebedor_pj", "BIGINT", "Transacoes recebidas por pessoas juridicas do municipio"),
            ("valor_recebedor_pj", "DECIMAL(20,2)", "Valor recebido por pessoas juridicas, em reais"),
            ("pessoas_pagadoras_pf", "BIGINT", "Pessoas fisicas distintas que pagaram no mes"),
            ("pessoas_pagadoras_pj", "BIGINT", "Pessoas juridicas distintas que pagaram no mes"),
            ("pessoas_recebedoras_pf", "BIGINT", "Pessoas fisicas distintas que receberam no mes"),
            ("pessoas_recebedoras_pj", "BIGINT", "Pessoas juridicas distintas que receberam no mes"),
            _ATUALIZADO_EM,
        ],
    },
    ("silver", "selic_mensal"): {
        "comentario": "Media mensal da meta Selic, calculada a partir da serie diaria (SGS 432).",
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("selic_media", "DECIMAL(8,4)", "Media simples da meta Selic no mes, em % ao ano"),
            ("dias_observados", "INT", "Quantidade de dias com observacao no mes"),
            _ATUALIZADO_EM,
        ],
    },
    ("silver", "ipca_mensal"): {
        "comentario": "Variacao mensal do IPCA (SGS 433) com tipos corrigidos e sem duplicados.",
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("ipca_variacao_mensal", "DECIMAL(8,4)", "Variacao do IPCA no mes, em %"),
            _ATUALIZADO_EM,
        ],
    },
    ("silver", "base_mensal"): {
        "comentario": "Base mensal unificada desde o lancamento do Pix: volume do Pix, Selic media e IPCA do mes. Um registro por mes, sem buracos.",
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("pix_quantidade", "BIGINT", "Transacoes Pix liquidadas no SPI no mes (nao e o total do Pix)"),
            ("pix_valor", "DECIMAL(20,2)", "Valor do Pix liquidado no SPI no mes, em reais (nao e o total do Pix)"),
            ("selic_media", "DECIMAL(8,4)", "Media da meta Selic no mes, em % ao ano"),
            ("ipca_variacao_mensal", "DECIMAL(8,4)", "Variacao do IPCA no mes, em %"),
            _ATUALIZADO_EM,
        ],
    },
    ("silver", "cooperativas"): {
        "comentario": "Cooperativas de credito em funcionamento (foto mais recente do cadastro), sem dados de contato.",
        "cluster_by": [],
        "colunas": [
            ("cnpj_base", "STRING", "CNPJ base (8 digitos)"),
            ("nome", "STRING", "Razao social"),
            ("classe", "STRING", "Singular, Central ou Confederacao"),
            ("criterio_associacao", "STRING", "Criterio de associacao dos associados"),
            ("categoria", "STRING", "Categoria da singular: Classica, Plena ou Capital e Emprestimo"),
            ("central_filiacao", "STRING", "Central a qual e filiada (vazio quando independente)"),
            ("municipio", "STRING", "Municipio da sede"),
            ("codigo_ibge_municipio", "INT", "Codigo IBGE do municipio da sede"),
            ("uf", "STRING", "Sigla da unidade da federacao da sede"),
            ("data_referencia", "DATE", "Data da foto do cadastro"),
            _ATUALIZADO_EM,
        ],
    },
    # ------------------------------------------------------------------ GOLD
    ("gold", "indicadores_mensais"): {
        "comentario": "Painel mensal: crescimento do Pix, Selic media e IPCA acumulado em 12 meses. Uma linha por mes desde nov/2020. Alimenta o dashboard. " + _COBERTURA_SPI,
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("pix_quantidade", "BIGINT", "Transacoes Pix liquidadas no SPI no mes (nao e o total do Pix)"),
            ("pix_valor", "DECIMAL(20,2)", "Valor do Pix liquidado no SPI no mes, em reais (nao e o total do Pix)"),
            ("pix_ticket_medio", "DECIMAL(12,2)", "Valor medio por transacao (valor / quantidade), em reais"),
            ("pix_quantidade_var_mensal_pct", "DECIMAL(10,4)", "Variacao da quantidade em relacao ao mes anterior, em %"),
            ("pix_quantidade_var_12m_pct", "DECIMAL(10,4)", "Variacao da quantidade em relacao ao mesmo mes do ano anterior, em %"),
            ("pix_valor_var_mensal_pct", "DECIMAL(10,4)", "Variacao do valor em relacao ao mes anterior, em %"),
            ("pix_valor_var_12m_pct", "DECIMAL(10,4)", "Variacao do valor em relacao ao mesmo mes do ano anterior, em %"),
            ("selic_media", "DECIMAL(8,4)", "Media da meta Selic no mes, em % ao ano"),
            ("ipca_variacao_mensal", "DECIMAL(8,4)", "Variacao do IPCA no mes, em %"),
            ("ipca_acumulado_12m", "DECIMAL(8,4)", "IPCA acumulado em 12 meses pela composicao das taxas mensais, em %"),
            _ATUALIZADO_EM,
        ],
    },
    ("gold", "pix_uf_mensal"): {
        "comentario": "Pix pago por residentes de cada UF, por mes: volume, pessoas pagadoras, participacao nacional e crescimento em 12 meses. " + _COBERTURA_SPI,
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("uf", "STRING", "Sigla da unidade da federacao do pagador"),
            ("regiao", "STRING", "Regiao geografica"),
            ("quantidade", "BIGINT", "Transacoes pagas por PF e PJ da UF"),
            ("valor", "DECIMAL(20,2)", "Valor pago por PF e PJ da UF, em reais"),
            ("pessoas_pagadoras", "BIGINT", "Soma das pessoas pagadoras distintas por municipio (PF e PJ)"),
            ("municipios", "INT", "Municipios da UF com transacoes no mes"),
            ("valor_por_pessoa", "DECIMAL(12,2)", "Valor pago dividido pelas pessoas pagadoras, em reais"),
            ("participacao_nacional_valor_pct", "DECIMAL(8,4)", "Participacao da UF no valor pago nacional, em %"),
            ("valor_var_12m_pct", "DECIMAL(10,4)", "Variacao do valor pago em relacao ao mesmo mes do ano anterior, em %"),
            ("quantidade_pf", "BIGINT", "Transacoes pagas por pessoas fisicas da UF"),
            ("valor_pf", "DECIMAL(20,2)", "Valor pago por pessoas fisicas da UF, em reais"),
            ("pessoas_pagadoras_pf", "BIGINT", "Soma das pessoas fisicas pagadoras distintas por municipio"),
            ("transacoes_por_pessoa_pf", "DECIMAL(10,2)", "Transacoes por pessoa fisica pagadora no mes: intensidade de uso no dia a dia"),
            ("valor_por_pessoa_pf", "DECIMAL(12,2)", "Valor pago por pessoa fisica pagadora no mes, em reais"),
            _ATUALIZADO_EM,
        ],
    },
    ("gold", "pix_capital_interior_mensal"): {
        "comentario": "Pix pago por residentes da capital versus do interior, por UF e mes. " + _COBERTURA_SPI,
        "cluster_by": [],
        "colunas": [
            ("ano_mes", "INT", "Mes de referencia no formato AAAAMM"),
            ("data_referencia", "DATE", "Primeiro dia do mes de referencia"),
            ("uf", "STRING", "Sigla da unidade da federacao"),
            ("tipo_localidade", "STRING", "capital ou interior"),
            ("quantidade", "BIGINT", "Transacoes pagas por PF e PJ"),
            ("valor", "DECIMAL(20,2)", "Valor pago por PF e PJ, em reais"),
            ("pessoas_pagadoras", "BIGINT", "Soma das pessoas pagadoras distintas por municipio (PF e PJ)"),
            ("municipios", "INT", "Municipios com transacoes no mes"),
            ("participacao_uf_valor_pct", "DECIMAL(8,4)", "Participacao no valor pago da UF, em %"),
            ("quantidade_pf", "BIGINT", "Transacoes pagas por pessoas fisicas"),
            ("valor_pf", "DECIMAL(20,2)", "Valor pago por pessoas fisicas, em reais"),
            ("pessoas_pagadoras_pf", "BIGINT", "Soma das pessoas fisicas pagadoras distintas por municipio"),
            ("transacoes_por_pessoa_pf", "DECIMAL(10,2)", "Transacoes por pessoa fisica pagadora no mes"),
            ("valor_por_pessoa_pf", "DECIMAL(12,2)", "Valor pago por pessoa fisica pagadora no mes, em reais"),
            _ATUALIZADO_EM,
        ],
    },
    ("gold", "cooperativas_uf"): {
        "comentario": "Cooperativas de credito em funcionamento por UF e classe, com participacao no total nacional.",
        "cluster_by": [],
        "colunas": [
            ("uf", "STRING", "Sigla da unidade da federacao"),
            ("data_referencia", "DATE", "Data da foto do cadastro"),
            ("total", "INT", "Total de cooperativas com sede na UF"),
            ("singulares", "INT", "Cooperativas singulares"),
            ("centrais", "INT", "Cooperativas centrais"),
            ("confederacoes", "INT", "Confederacoes"),
            ("livre_admissao", "INT", "Singulares de livre admissao de associados"),
            ("centrais_distintas", "INT", "Quantidade de centrais diferentes as quais as singulares da UF sao filiadas"),
            ("participacao_nacional_pct", "DECIMAL(8,4)", "Participacao da UF no total nacional de cooperativas, em %"),
            _ATUALIZADO_EM,
        ],
    },
    # ------------------------------------------------------------------ AUDITORIA
    ("auditoria", "resultados_qualidade"): {
        "comentario": "Resultado de cada regra de qualidade executada pelo pipeline. Uma linha por regra, por execucao. Historico completo, nunca sobrescrito.",
        "cluster_by": ["executado_em"],
        "colunas": [
            ("executado_em", "TIMESTAMP", "Momento (UTC) da execucao"),
            ("execucao_id", "STRING", "Identificador da execucao do job (run id) ou manual"),
            ("camada", "STRING", "Camada verificada: bronze, silver ou gold"),
            ("tabela", "STRING", "Nome completo da tabela verificada"),
            ("regra", "STRING", "Nome da regra: nulos, faixa, unicidade, continuidade_meses, reconciliacao"),
            ("coluna", "STRING", "Coluna ou chave verificada"),
            ("status", "STRING", "ok ou falha"),
            ("severidade", "STRING", "erro interrompe o pipeline; aviso apenas registra"),
            ("valor_observado", "STRING", "Valor medido na verificacao"),
            ("limite", "STRING", "Limite aceito pela regra"),
            ("detalhe", "STRING", "Descricao legivel do resultado"),
        ],
    },
}


def colunas(camada: str, chave: str) -> list[tuple[str, str, str]]:
    """Lista completa de colunas (nome, tipo, comentario). Bronze inclui os metadados."""
    espec = ESPECIFICACAO[(camada, chave)]["colunas"]
    return list(espec) + (METADADOS_BRONZE if camada == "bronze" else [])


def esquema_ddl(camada: str, chave: str, decimal_como_double: bool = False) -> str:
    """
    Esquema no formato aceito por spark.createDataFrame: 'AnoMes INT, VALOR DOUBLE, ...'.

    decimal_como_double=True troca DECIMAL(p,s) por DOUBLE. Usamos isso ao criar um
    DataFrame a partir de valores float do Python (o Spark nao aceita float em coluna
    DECIMAL); a conversao final para DECIMAL acontece na gravacao (alinhar_ao_esquema).
    """
    partes = []
    for nome, tipo, _ in colunas(camada, chave):
        if decimal_como_double and tipo.upper().startswith("DECIMAL"):
            tipo = "DOUBLE"
        partes.append(f"{nome} {tipo}")
    return ", ".join(partes)


def ddl_criar_tabela(camada: str, chave: str) -> str:
    """CREATE TABLE IF NOT EXISTS com COMMENT em cada coluna e na tabela."""
    espec = ESPECIFICACAO[(camada, chave)]
    linhas_colunas = ",\n".join(
        f"  {nome} {tipo} COMMENT '{_escapar(comentario)}'" for nome, tipo, comentario in colunas(camada, chave)
    )
    cluster = f"\nCLUSTER BY ({', '.join(espec['cluster_by'])})" if espec["cluster_by"] else ""
    return (
        f"CREATE TABLE IF NOT EXISTS {nome_tabela(camada, chave)} (\n{linhas_colunas}\n)\n"
        f"USING DELTA{cluster}\nCOMMENT '{_escapar(espec['comentario'])}'"
    )


def ddl_comentarios(camada: str, chave: str) -> list[str]:
    """
    Comandos que reaplicam os comentarios. CREATE TABLE IF NOT EXISTS nao atualiza uma
    tabela existente, entao rodamos estes a cada execucao para o catalogo nunca ficar
    desatualizado em relacao a este arquivo.
    """
    nome = nome_tabela(camada, chave)
    comandos = [f"COMMENT ON TABLE {nome} IS '{_escapar(ESPECIFICACAO[(camada, chave)]['comentario'])}'"]
    for nome_coluna, _, comentario in colunas(camada, chave):
        comandos.append(f"ALTER TABLE {nome} ALTER COLUMN {nome_coluna} COMMENT '{_escapar(comentario)}'")
    return comandos


def ddl_adicionar_colunas(camada: str, chave: str, colunas_existentes: list[str]) -> str | None:
    """
    ALTER TABLE ... ADD COLUMNS para as colunas da especificacao que ainda nao existem na
    tabela. E a evolucao de esquema controlada: nova coluna entra na especificacao, o
    pipeline a cria na proxima execucao, sem recriar a tabela nem perder dados.
    Devolve None quando nao ha nada a adicionar. Colunas removidas da especificacao NAO
    sao apagadas (decisao conservadora: apagar coluna e acao manual).
    """
    existentes = {c.lower() for c in colunas_existentes}
    novas = [(n, t, c) for n, t, c in colunas(camada, chave) if n.lower() not in existentes]
    if not novas:
        return None
    partes = ", ".join(f"{n} {t} COMMENT '{_escapar(c)}'" for n, t, c in novas)
    return f"ALTER TABLE {nome_tabela(camada, chave)} ADD COLUMNS ({partes})"


def todas_as_tabelas() -> list[tuple[str, str]]:
    """[(camada, chave), ...] na ordem de criacao."""
    return list(ESPECIFICACAO)


def _escapar(texto: str) -> str:
    return texto.replace("'", "''")


def _conferir_consistencia() -> None:
    """Garante que toda tabela da configuracao tem especificacao, e vice-versa."""
    esperadas = {(camada, chave) for camada, tabelas in TABELAS.items() for chave in tabelas}
    faltando = esperadas - set(ESPECIFICACAO)
    sobrando = set(ESPECIFICACAO) - esperadas
    if faltando or sobrando:
        raise RuntimeError(f"especificacao fora de sincronia: faltando={faltando} sobrando={sobrando}")


_conferir_consistencia()
