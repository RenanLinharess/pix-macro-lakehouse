-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.base_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  pix_quantidade BIGINT COMMENT 'Total de transacoes Pix liquidadas no mes',
  pix_valor DECIMAL(20,2) COMMENT 'Valor total liquidado via Pix no mes, em reais',
  selic_media DECIMAL(8,4) COMMENT 'Media da meta Selic no mes, em % ao ano',
  ipca_variacao_mensal DECIMAL(8,4) COMMENT 'Variacao do IPCA no mes, em %',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Base mensal unificada desde o lancamento do Pix: volume do Pix, Selic media e IPCA do mes. Um registro por mes, sem buracos.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.base_mensal IS 'Base mensal unificada desde o lancamento do Pix: volume do Pix, Selic media e IPCA do mes. Um registro por mes, sem buracos.';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN pix_quantidade COMMENT 'Total de transacoes Pix liquidadas no mes';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN pix_valor COMMENT 'Valor total liquidado via Pix no mes, em reais';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN selic_media COMMENT 'Media da meta Selic no mes, em % ao ano';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN ipca_variacao_mensal COMMENT 'Variacao do IPCA no mes, em %';
ALTER TABLE workspace.pix_macro_silver.base_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
