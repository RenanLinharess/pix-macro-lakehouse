-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_gold.indicadores_mensais (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  pix_quantidade BIGINT COMMENT 'Transacoes Pix liquidadas no SPI no mes (nao e o total do Pix)',
  pix_valor DECIMAL(20,2) COMMENT 'Valor do Pix liquidado no SPI no mes, em reais (nao e o total do Pix)',
  pix_ticket_medio DECIMAL(12,2) COMMENT 'Valor medio por transacao (valor / quantidade), em reais',
  pix_quantidade_var_mensal_pct DECIMAL(10,4) COMMENT 'Variacao da quantidade em relacao ao mes anterior, em %',
  pix_quantidade_var_12m_pct DECIMAL(10,4) COMMENT 'Variacao da quantidade em relacao ao mesmo mes do ano anterior, em %',
  pix_valor_var_mensal_pct DECIMAL(10,4) COMMENT 'Variacao do valor em relacao ao mes anterior, em %',
  pix_valor_var_12m_pct DECIMAL(10,4) COMMENT 'Variacao do valor em relacao ao mesmo mes do ano anterior, em %',
  selic_media DECIMAL(8,4) COMMENT 'Media da meta Selic no mes, em % ao ano',
  ipca_variacao_mensal DECIMAL(8,4) COMMENT 'Variacao do IPCA no mes, em %',
  ipca_acumulado_12m DECIMAL(8,4) COMMENT 'IPCA acumulado em 12 meses pela composicao das taxas mensais, em %',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Painel mensal: crescimento do Pix, Selic media e IPCA acumulado em 12 meses. Uma linha por mes desde nov/2020. Alimenta o dashboard. Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_gold.indicadores_mensais IS 'Painel mensal: crescimento do Pix, Selic media e IPCA acumulado em 12 meses. Uma linha por mes desde nov/2020. Alimenta o dashboard. Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_quantidade COMMENT 'Transacoes Pix liquidadas no SPI no mes (nao e o total do Pix)';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_valor COMMENT 'Valor do Pix liquidado no SPI no mes, em reais (nao e o total do Pix)';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_ticket_medio COMMENT 'Valor medio por transacao (valor / quantidade), em reais';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_quantidade_var_mensal_pct COMMENT 'Variacao da quantidade em relacao ao mes anterior, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_quantidade_var_12m_pct COMMENT 'Variacao da quantidade em relacao ao mesmo mes do ano anterior, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_valor_var_mensal_pct COMMENT 'Variacao do valor em relacao ao mes anterior, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN pix_valor_var_12m_pct COMMENT 'Variacao do valor em relacao ao mesmo mes do ano anterior, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN selic_media COMMENT 'Media da meta Selic no mes, em % ao ano';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN ipca_variacao_mensal COMMENT 'Variacao do IPCA no mes, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN ipca_acumulado_12m COMMENT 'IPCA acumulado em 12 meses pela composicao das taxas mensais, em %';
ALTER TABLE workspace.pix_macro_gold.indicadores_mensais ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
