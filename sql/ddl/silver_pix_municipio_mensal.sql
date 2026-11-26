-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.pix_municipio_mensal (
  ano_mes INT COMMENT 'Mes de referencia no formato AAAAMM',
  data_referencia DATE COMMENT 'Primeiro dia do mes de referencia',
  codigo_ibge_municipio INT COMMENT 'Codigo IBGE do municipio (7 digitos)',
  municipio STRING COMMENT 'Nome do municipio',
  codigo_ibge_uf INT COMMENT 'Codigo IBGE da unidade da federacao',
  uf STRING COMMENT 'Sigla da unidade da federacao; ND para a linha mensal de municipio nao informado publicada pelo BCB',
  regiao STRING COMMENT 'Nome da regiao geografica',
  tipo_localidade STRING COMMENT 'capital, interior (pelo codigo IBGE da capital da UF) ou nao informado',
  quantidade_pagador_pf BIGINT COMMENT 'Transacoes pagas por pessoas fisicas do municipio',
  valor_pagador_pf DECIMAL(20,2) COMMENT 'Valor pago por pessoas fisicas, em reais',
  quantidade_pagador_pj BIGINT COMMENT 'Transacoes pagas por pessoas juridicas do municipio',
  valor_pagador_pj DECIMAL(20,2) COMMENT 'Valor pago por pessoas juridicas, em reais',
  quantidade_recebedor_pf BIGINT COMMENT 'Transacoes recebidas por pessoas fisicas do municipio',
  valor_recebedor_pf DECIMAL(20,2) COMMENT 'Valor recebido por pessoas fisicas, em reais',
  quantidade_recebedor_pj BIGINT COMMENT 'Transacoes recebidas por pessoas juridicas do municipio',
  valor_recebedor_pj DECIMAL(20,2) COMMENT 'Valor recebido por pessoas juridicas, em reais',
  pessoas_pagadoras_pf BIGINT COMMENT 'Pessoas fisicas distintas que pagaram no mes',
  pessoas_pagadoras_pj BIGINT COMMENT 'Pessoas juridicas distintas que pagaram no mes',
  pessoas_recebedoras_pf BIGINT COMMENT 'Pessoas fisicas distintas que receberam no mes',
  pessoas_recebedoras_pj BIGINT COMMENT 'Pessoas juridicas distintas que receberam no mes',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
CLUSTER BY (ano_mes, uf)
COMMENT 'Transacoes Pix por municipio e mes, com tipos corrigidos, sigla da UF e classificacao capital/interior. Exclui o mes corrente. Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.pix_municipio_mensal IS 'Transacoes Pix por municipio e mes, com tipos corrigidos, sigla da UF e classificacao capital/interior. Exclui o mes corrente. Cobertura: Pix liquidado no SPI; nao inclui Pix liquidado nos livros do participante (fonte: descricao do recurso no portal de dados abertos do BCB).';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN ano_mes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN data_referencia COMMENT 'Primeiro dia do mes de referencia';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN codigo_ibge_municipio COMMENT 'Codigo IBGE do municipio (7 digitos)';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN municipio COMMENT 'Nome do municipio';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN codigo_ibge_uf COMMENT 'Codigo IBGE da unidade da federacao';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN uf COMMENT 'Sigla da unidade da federacao; ND para a linha mensal de municipio nao informado publicada pelo BCB';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN regiao COMMENT 'Nome da regiao geografica';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN tipo_localidade COMMENT 'capital, interior (pelo codigo IBGE da capital da UF) ou nao informado';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN quantidade_pagador_pf COMMENT 'Transacoes pagas por pessoas fisicas do municipio';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN valor_pagador_pf COMMENT 'Valor pago por pessoas fisicas, em reais';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN quantidade_pagador_pj COMMENT 'Transacoes pagas por pessoas juridicas do municipio';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN valor_pagador_pj COMMENT 'Valor pago por pessoas juridicas, em reais';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN quantidade_recebedor_pf COMMENT 'Transacoes recebidas por pessoas fisicas do municipio';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN valor_recebedor_pf COMMENT 'Valor recebido por pessoas fisicas, em reais';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN quantidade_recebedor_pj COMMENT 'Transacoes recebidas por pessoas juridicas do municipio';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN valor_recebedor_pj COMMENT 'Valor recebido por pessoas juridicas, em reais';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN pessoas_pagadoras_pf COMMENT 'Pessoas fisicas distintas que pagaram no mes';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN pessoas_pagadoras_pj COMMENT 'Pessoas juridicas distintas que pagaram no mes';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN pessoas_recebedoras_pf COMMENT 'Pessoas fisicas distintas que receberam no mes';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN pessoas_recebedoras_pj COMMENT 'Pessoas juridicas distintas que receberam no mes';
ALTER TABLE workspace.pix_macro_silver.pix_municipio_mensal ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
