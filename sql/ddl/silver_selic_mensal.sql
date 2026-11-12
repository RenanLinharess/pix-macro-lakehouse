-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.selic_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  selic_media DECIMAL(8,4) COMMENT 'Media simples da meta Selic no mes, em % ao ano',
  dias_observados INT COMMENT 'Quantidade de dias com observacao no mes',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Media mensal da meta Selic, calculada a partir da serie diaria (SGS 432).';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.selic_mensal IS 'Media mensal da meta Selic, calculada a partir da serie diaria (SGS 432).';
ALTER TABLE workspace.pix_macro_silver.selic_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_silver.selic_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_silver.selic_mensal ALTER COLUMN selic_media COMMENT 'Media simples da meta Selic no mes, em % ao ano';
ALTER TABLE workspace.pix_macro_silver.selic_mensal ALTER COLUMN dias_observados COMMENT 'Quantidade de dias com observacao no mes';
ALTER TABLE workspace.pix_macro_silver.selic_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
