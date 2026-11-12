-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.ipca_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  ipca_variacao_mensal DECIMAL(8,4) COMMENT 'Variacao do IPCA no mes, em %',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Variacao mensal do IPCA (SGS 433) com tipos corrigidos e sem duplicados.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.ipca_mensal IS 'Variacao mensal do IPCA (SGS 433) com tipos corrigidos e sem duplicados.';
ALTER TABLE workspace.pix_macro_silver.ipca_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_silver.ipca_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_silver.ipca_mensal ALTER COLUMN ipca_variacao_mensal COMMENT 'Variacao do IPCA no mes, em %';
ALTER TABLE workspace.pix_macro_silver.ipca_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
