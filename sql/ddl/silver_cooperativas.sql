-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_silver.cooperativas (
  cnpj_base STRING COMMENT 'CNPJ base (8 digitos)',
  nome STRING COMMENT 'Razao social',
  classe STRING COMMENT 'Singular, Central ou Confederacao',
  criterio_associacao STRING COMMENT 'Criterio de associacao dos associados',
  categoria STRING COMMENT 'Categoria da singular: Classica, Plena ou Capital e Emprestimo',
  central_filiacao STRING COMMENT 'Central a qual e filiada (vazio quando independente)',
  municipio STRING COMMENT 'Municipio da sede',
  codigo_ibge_municipio INT COMMENT 'Codigo IBGE do municipio da sede',
  uf STRING COMMENT 'Sigla da unidade da federacao da sede',
  data_referencia DATE COMMENT 'Data da foto do cadastro',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Cooperativas de credito em funcionamento (foto mais recente do cadastro), sem dados de contato.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_silver.cooperativas IS 'Cooperativas de credito em funcionamento (foto mais recente do cadastro), sem dados de contato.';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN cnpj_base COMMENT 'CNPJ base (8 digitos)';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN nome COMMENT 'Razao social';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN classe COMMENT 'Singular, Central ou Confederacao';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN criterio_associacao COMMENT 'Criterio de associacao dos associados';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN categoria COMMENT 'Categoria da singular: Classica, Plena ou Capital e Emprestimo';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN central_filiacao COMMENT 'Central a qual e filiada (vazio quando independente)';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN municipio COMMENT 'Municipio da sede';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN codigo_ibge_municipio COMMENT 'Codigo IBGE do municipio da sede';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN uf COMMENT 'Sigla da unidade da federacao da sede';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN data_referencia COMMENT 'Data da foto do cadastro';
ALTER TABLE workspace.pix_macro_silver.cooperativas ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
