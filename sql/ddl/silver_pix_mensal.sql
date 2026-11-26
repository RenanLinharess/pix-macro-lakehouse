-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.pix_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  natureza STRING COMMENT 'Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc.',
  pagador_tipo STRING COMMENT 'Tipo do pagador: PF ou PJ',
  recebedor_tipo STRING COMMENT 'Tipo do recebedor: PF ou PJ',
  regiao_pagador STRING COMMENT 'Regiao geografica do pagador',
  quantidade BIGINT COMMENT 'Quantidade de transacoes liquidadas',
  valor DECIMAL(20,2) COMMENT 'Valor total liquidado em reais',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
CLUSTER BY (ano_mes)
COMMENT 'Transacoes Pix por mes e natureza, agregadas a partir do bronze. Exclui o mes corrente (incompleto). Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.pix_mensal IS 'Transacoes Pix por mes e natureza, agregadas a partir do bronze. Exclui o mes corrente (incompleto). Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN natureza COMMENT 'Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc.';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN pagador_tipo COMMENT 'Tipo do pagador: PF ou PJ';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN recebedor_tipo COMMENT 'Tipo do recebedor: PF ou PJ';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN regiao_pagador COMMENT 'Regiao geografica do pagador';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN quantidade COMMENT 'Quantidade de transacoes liquidadas';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN valor COMMENT 'Valor total liquidado em reais';
ALTER TABLE workspace.pix_macro_silver.pix_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
