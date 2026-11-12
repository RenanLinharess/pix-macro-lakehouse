-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_bronze.cooperativas (
  CNPJ STRING COMMENT 'CNPJ base (8 digitos) da cooperativa',
  NOME_INSTITUICAO STRING COMMENT 'Razao social',
  ENDERECO STRING COMMENT 'Endereco da sede',
  COMPLEMENTO STRING COMMENT 'Complemento do endereco',
  BAIRRO STRING COMMENT 'Bairro da sede',
  CEP STRING COMMENT 'CEP da sede',
  MUNICIPIO STRING COMMENT 'Municipio da sede',
  UF STRING COMMENT 'Unidade da federacao da sede',
  DDD STRING COMMENT 'DDD do telefone institucional',
  TELEFONE STRING COMMENT 'Telefone institucional',
  CLASSE STRING COMMENT 'Classe: Singular, Central ou Confederacao',
  ASSOCIACAO STRING COMMENT 'Criterio de associacao (livre admissao, empregados, produtor rural etc.)',
  CATEGCOOPSING STRING COMMENT 'Categoria da singular: Classica, Plena ou Capital e Emprestimo',
  FILIACAO STRING COMMENT 'Central a qual a cooperativa e filiada',
  E_MAIL STRING COMMENT 'E-mail institucional',
  SITIO_NA_INTERNET STRING COMMENT 'Site institucional',
  MUNICIPIO_IBGE STRING COMMENT 'Codigo IBGE do municipio da sede',
  fonte STRING COMMENT 'Nome curto da fonte, conforme config/configuracoes.py',
  url_origem STRING COMMENT 'URL da API chamada para obter os registros',
  parametros_requisicao MAP<STRING,STRING> COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)',
  baixado_em TIMESTAMP COMMENT 'Momento (UTC) em que a resposta foi baixada da API',
  arquivo_origem STRING COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API',
  carregado_em TIMESTAMP COMMENT 'Momento (UTC) em que a linha foi gravada no bronze'
)
USING DELTA
COMMENT 'Cadastro das cooperativas de credito em funcionamento, como veio da API Olinda do BCB (SedesCooperativas). Uma foto por data de download.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_bronze.cooperativas IS 'Cadastro das cooperativas de credito em funcionamento, como veio da API Olinda do BCB (SedesCooperativas). Uma foto por data de download.';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN CNPJ COMMENT 'CNPJ base (8 digitos) da cooperativa';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN NOME_INSTITUICAO COMMENT 'Razao social';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN ENDERECO COMMENT 'Endereco da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN COMPLEMENTO COMMENT 'Complemento do endereco';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN BAIRRO COMMENT 'Bairro da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN CEP COMMENT 'CEP da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN MUNICIPIO COMMENT 'Municipio da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN UF COMMENT 'Unidade da federacao da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN DDD COMMENT 'DDD do telefone institucional';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN TELEFONE COMMENT 'Telefone institucional';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN CLASSE COMMENT 'Classe: Singular, Central ou Confederacao';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN ASSOCIACAO COMMENT 'Criterio de associacao (livre admissao, empregados, produtor rural etc.)';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN CATEGCOOPSING COMMENT 'Categoria da singular: Classica, Plena ou Capital e Emprestimo';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN FILIACAO COMMENT 'Central a qual a cooperativa e filiada';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN E_MAIL COMMENT 'E-mail institucional';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN SITIO_NA_INTERNET COMMENT 'Site institucional';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN MUNICIPIO_IBGE COMMENT 'Codigo IBGE do municipio da sede';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN fonte COMMENT 'Nome curto da fonte, conforme config/configuracoes.py';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN url_origem COMMENT 'URL da API chamada para obter os registros';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN parametros_requisicao COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN baixado_em COMMENT 'Momento (UTC) em que a resposta foi baixada da API';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN arquivo_origem COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API';
ALTER TABLE workspace.pix_macro_bronze.cooperativas ALTER COLUMN carregado_em COMMENT 'Momento (UTC) em que a linha foi gravada no bronze';
