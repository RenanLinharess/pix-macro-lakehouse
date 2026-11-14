-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_gold.pix_capital_interior_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  uf STRING COMMENT 'Sigla da unidade da federacao',
  tipo_localidade STRING COMMENT 'capital ou interior',
  quantidade BIGINT COMMENT 'Transacoes pagas por PF e PJ',
  valor DECIMAL(20,2) COMMENT 'Valor pago por PF e PJ, em reais',
  pessoas_pagadoras BIGINT COMMENT 'Soma das pessoas pagadoras distintas por municipio (PF e PJ)',
  municipios INT COMMENT 'Municipios com transacoes no mes',
  participacao_uf_valor_pct DECIMAL(8,4) COMMENT 'Participacao no valor pago da UF, em %',
  quantidade_pf BIGINT COMMENT 'Transacoes pagas por pessoas fisicas',
  valor_pf DECIMAL(20,2) COMMENT 'Valor pago por pessoas fisicas, em reais',
  pessoas_pagadoras_pf BIGINT COMMENT 'Soma das pessoas fisicas pagadoras distintas por municipio',
  transacoes_por_pessoa_pf DECIMAL(10,2) COMMENT 'Transacoes por pessoa fisica pagadora no mes',
  valor_por_pessoa_pf DECIMAL(12,2) COMMENT 'Valor pago por pessoa fisica pagadora no mes, em reais',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Pix pago por residentes da capital versus do interior, por UF e mes. Mostra a interiorizacao do uso do Pix.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_gold.pix_capital_interior_mensal IS 'Pix pago por residentes da capital versus do interior, por UF e mes. Mostra a interiorizacao do uso do Pix.';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN uf COMMENT 'Sigla da unidade da federacao';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN tipo_localidade COMMENT 'capital ou interior';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN quantidade COMMENT 'Transacoes pagas por PF e PJ';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN valor COMMENT 'Valor pago por PF e PJ, em reais';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN pessoas_pagadoras COMMENT 'Soma das pessoas pagadoras distintas por municipio (PF e PJ)';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN municipios COMMENT 'Municipios com transacoes no mes';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN participacao_uf_valor_pct COMMENT 'Participacao no valor pago da UF, em %';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN quantidade_pf COMMENT 'Transacoes pagas por pessoas fisicas';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN valor_pf COMMENT 'Valor pago por pessoas fisicas, em reais';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN pessoas_pagadoras_pf COMMENT 'Soma das pessoas fisicas pagadoras distintas por municipio';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN transacoes_por_pessoa_pf COMMENT 'Transacoes por pessoa fisica pagadora no mes';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN valor_por_pessoa_pf COMMENT 'Valor pago por pessoa fisica pagadora no mes, em reais';
ALTER TABLE workspace.pix_macro_gold.pix_capital_interior_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
