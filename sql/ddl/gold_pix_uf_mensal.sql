-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_gold.pix_uf_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  uf STRING COMMENT 'Sigla da unidade da federacao do pagador',
  regiao STRING COMMENT 'Regiao geografica',
  quantidade BIGINT COMMENT 'Transacoes pagas por PF e PJ da UF',
  valor DECIMAL(20,2) COMMENT 'Valor pago por PF e PJ da UF, em reais',
  pessoas_pagadoras BIGINT COMMENT 'Soma das pessoas pagadoras distintas por municipio (PF e PJ)',
  municipios INT COMMENT 'Municipios da UF com transacoes no mes',
  valor_por_pessoa DECIMAL(12,2) COMMENT 'Valor pago dividido pelas pessoas pagadoras, em reais',
  participacao_nacional_valor_pct DECIMAL(8,4) COMMENT 'Participacao da UF no valor pago nacional, em %',
  valor_var_12m_pct DECIMAL(10,4) COMMENT 'Variacao do valor pago em relacao ao mesmo mes do ano anterior, em %',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Pix pago por residentes de cada UF, por mes: volume, pessoas pagadoras, participacao nacional e crescimento em 12 meses.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_gold.pix_uf_mensal IS 'Pix pago por residentes de cada UF, por mes: volume, pessoas pagadoras, participacao nacional e crescimento em 12 meses.';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN uf COMMENT 'Sigla da unidade da federacao do pagador';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN regiao COMMENT 'Regiao geografica';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN quantidade COMMENT 'Transacoes pagas por PF e PJ da UF';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN valor COMMENT 'Valor pago por PF e PJ da UF, em reais';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN pessoas_pagadoras COMMENT 'Soma das pessoas pagadoras distintas por municipio (PF e PJ)';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN municipios COMMENT 'Municipios da UF com transacoes no mes';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN valor_por_pessoa COMMENT 'Valor pago dividido pelas pessoas pagadoras, em reais';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN participacao_nacional_valor_pct COMMENT 'Participacao da UF no valor pago nacional, em %';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN valor_var_12m_pct COMMENT 'Variacao do valor pago em relacao ao mesmo mes do ano anterior, em %';
ALTER TABLE workspace.pix_macro_gold.pix_uf_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
