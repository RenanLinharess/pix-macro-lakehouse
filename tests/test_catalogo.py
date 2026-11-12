from src.catalogo.tabelas import (
    ESPECIFICACAO,
    METADADOS_BRONZE,
    colunas,
    ddl_comentarios,
    ddl_criar_tabela,
    esquema_ddl,
    todas_as_tabelas,
)


def test_toda_tabela_tem_comentario_em_todas_as_colunas():
    for camada, chave in todas_as_tabelas():
        assert ESPECIFICACAO[(camada, chave)]["comentario"], f"{camada}.{chave} sem comentario de tabela"
        for nome, tipo, comentario in colunas(camada, chave):
            assert comentario, f"{camada}.{chave}.{nome} sem comentario"
            assert tipo, f"{camada}.{chave}.{nome} sem tipo"


def test_nomes_de_coluna_sao_unicos():
    for camada, chave in todas_as_tabelas():
        nomes = [nome for nome, _, _ in colunas(camada, chave)]
        assert len(nomes) == len(set(nomes)), f"{camada}.{chave} tem coluna repetida"


def test_bronze_recebe_metadados_e_silver_gold_sao_snake_case():
    for camada, chave in todas_as_tabelas():
        nomes = [nome for nome, _, _ in colunas(camada, chave)]
        if camada == "bronze":
            for nome, _, _ in METADADOS_BRONZE:
                assert nome in nomes
        else:
            for nome in nomes:
                assert nome == nome.lower() and " " not in nome, f"{camada}.{chave}.{nome} nao e snake_case"


def test_ddl_gerado():
    ddl = ddl_criar_tabela("silver", "base_mensal")
    assert ddl.startswith("CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.base_mensal")
    assert "pix_valor DECIMAL(20,2) COMMENT" in ddl
    assert ddl.rstrip().endswith("'")
    assert "CLUSTER BY (AnoMes)" in ddl_criar_tabela("bronze", "pix_estatisticas")


def test_esquema_ddl_e_comentarios():
    assert esquema_ddl("silver", "selic_mensal").startswith("ano_mes INT, data_referencia DATE, selic_media DECIMAL(8,4)")
    comandos = ddl_comentarios("silver", "selic_mensal")
    assert comandos[0].startswith("COMMENT ON TABLE workspace.pix_macro_silver.selic_mensal IS")
    assert len(comandos) == 1 + len(colunas("silver", "selic_mensal"))
