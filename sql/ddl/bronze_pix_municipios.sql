-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_bronze.pix_municipios (
  AnoMes INT COMMENT 'Mes de referencia no formato AAAAMM',
  Municipio_Ibge INT COMMENT 'Codigo IBGE do municipio (7 digitos)',
  Municipio STRING COMMENT 'Nome do municipio',
  Estado_Ibge INT COMMENT 'Codigo IBGE da unidade da federacao (2 digitos)',
  Estado STRING COMMENT 'Nome da unidade da federacao',
  Sigla_Regiao STRING COMMENT 'Sigla da regiao geografica',
  Regiao STRING COMMENT 'Nome da regiao geografica',
  VL_PagadorPF DOUBLE COMMENT 'Valor pago por pessoas fisicas do municipio, em reais',
  QT_PagadorPF BIGINT COMMENT 'Quantidade de transacoes pagas por pessoas fisicas',
  VL_PagadorPJ DOUBLE COMMENT 'Valor pago por pessoas juridicas do municipio, em reais',
  QT_PagadorPJ BIGINT COMMENT 'Quantidade de transacoes pagas por pessoas juridicas',
  VL_RecebedorPF DOUBLE COMMENT 'Valor recebido por pessoas fisicas do municipio, em reais',
  QT_RecebedorPF BIGINT COMMENT 'Quantidade de transacoes recebidas por pessoas fisicas',
  VL_RecebedorPJ DOUBLE COMMENT 'Valor recebido por pessoas juridicas do municipio, em reais',
  QT_RecebedorPJ BIGINT COMMENT 'Quantidade de transacoes recebidas por pessoas juridicas',
  QT_PES_PagadorPF BIGINT COMMENT 'Quantidade de pessoas fisicas distintas que pagaram no mes',
  QT_PES_PagadorPJ BIGINT COMMENT 'Quantidade de pessoas juridicas distintas que pagaram no mes',
  QT_PES_RecebedorPF BIGINT COMMENT 'Quantidade de pessoas fisicas distintas que receberam no mes',
  QT_PES_RecebedorPJ BIGINT COMMENT 'Quantidade de pessoas juridicas distintas que receberam no mes',
  fonte STRING COMMENT 'Nome curto da fonte, conforme config/configuracoes.py',
  url_origem STRING COMMENT 'URL da API chamada para obter os registros',
  parametros_requisicao MAP<STRING,STRING> COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)',
  baixado_em TIMESTAMP COMMENT 'Momento (UTC) em que a resposta foi baixada da API',
  arquivo_origem STRING COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API',
  carregado_em TIMESTAMP COMMENT 'Momento (UTC) em que a linha foi gravada no bronze'
)
USING DELTA
CLUSTER BY (AnoMes)
COMMENT 'Transacoes Pix por municipio e mes, como vieram da API Olinda do BCB (TransacoesPixPorMunicipio).';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_bronze.pix_municipios IS 'Transacoes Pix por municipio e mes, como vieram da API Olinda do BCB (TransacoesPixPorMunicipio).';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN AnoMes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Municipio_Ibge COMMENT 'Codigo IBGE do municipio (7 digitos)';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Municipio COMMENT 'Nome do municipio';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Estado_Ibge COMMENT 'Codigo IBGE da unidade da federacao (2 digitos)';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Estado COMMENT 'Nome da unidade da federacao';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Sigla_Regiao COMMENT 'Sigla da regiao geografica';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN Regiao COMMENT 'Nome da regiao geografica';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN VL_PagadorPF COMMENT 'Valor pago por pessoas fisicas do municipio, em reais';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PagadorPF COMMENT 'Quantidade de transacoes pagas por pessoas fisicas';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN VL_PagadorPJ COMMENT 'Valor pago por pessoas juridicas do municipio, em reais';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PagadorPJ COMMENT 'Quantidade de transacoes pagas por pessoas juridicas';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN VL_RecebedorPF COMMENT 'Valor recebido por pessoas fisicas do municipio, em reais';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_RecebedorPF COMMENT 'Quantidade de transacoes recebidas por pessoas fisicas';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN VL_RecebedorPJ COMMENT 'Valor recebido por pessoas juridicas do municipio, em reais';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_RecebedorPJ COMMENT 'Quantidade de transacoes recebidas por pessoas juridicas';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PES_PagadorPF COMMENT 'Quantidade de pessoas fisicas distintas que pagaram no mes';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PES_PagadorPJ COMMENT 'Quantidade de pessoas juridicas distintas que pagaram no mes';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PES_RecebedorPF COMMENT 'Quantidade de pessoas fisicas distintas que receberam no mes';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN QT_PES_RecebedorPJ COMMENT 'Quantidade de pessoas juridicas distintas que receberam no mes';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN fonte COMMENT 'Nome curto da fonte, conforme config/configuracoes.py';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN url_origem COMMENT 'URL da API chamada para obter os registros';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN parametros_requisicao COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN baixado_em COMMENT 'Momento (UTC) em que a resposta foi baixada da API';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN arquivo_origem COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API';
ALTER TABLE workspace.pix_macro_bronze.pix_municipios ALTER COLUMN carregado_em COMMENT 'Momento (UTC) em que a linha foi gravada no bronze';
