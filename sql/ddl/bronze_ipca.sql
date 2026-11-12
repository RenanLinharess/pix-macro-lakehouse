-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_bronze.ipca_mensal (
  data STRING COMMENT 'Primeiro dia do mes no formato dd/MM/aaaa, como enviado pela API',
  valor STRING COMMENT 'Variacao mensal do IPCA em %, como texto enviado pela API',
  fonte STRING COMMENT 'Nome curto da fonte, conforme config/configuracoes.py',
  url_origem STRING COMMENT 'URL da API chamada para obter os registros',
  parametros_requisicao MAP<STRING,STRING> COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)',
  baixado_em TIMESTAMP COMMENT 'Momento (UTC) em que a resposta foi baixada da API',
  arquivo_origem STRING COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API',
  carregado_em TIMESTAMP COMMENT 'Momento (UTC) em que a linha foi gravada no bronze'
)
USING DELTA
COMMENT 'IPCA variacao mensal (SGS serie 433), como veio da API: data e valor em texto.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_bronze.ipca_mensal IS 'IPCA variacao mensal (SGS serie 433), como veio da API: data e valor em texto.';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN data COMMENT 'Primeiro dia do mes no formato dd/MM/aaaa, como enviado pela API';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN valor COMMENT 'Variacao mensal do IPCA em %, como texto enviado pela API';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN fonte COMMENT 'Nome curto da fonte, conforme config/configuracoes.py';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN url_origem COMMENT 'URL da API chamada para obter os registros';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN parametros_requisicao COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN baixado_em COMMENT 'Momento (UTC) em que a resposta foi baixada da API';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN arquivo_origem COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API';
ALTER TABLE workspace.pix_macro_bronze.ipca_mensal ALTER COLUMN carregado_em COMMENT 'Momento (UTC) em que a linha foi gravada no bronze';
