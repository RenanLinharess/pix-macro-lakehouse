-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_gold.cooperativas_uf (
  uf STRING COMMENT 'Sigla da unidade da federacao',
  data_referencia DATE COMMENT 'Data da foto do cadastro',
  total INT COMMENT 'Total de cooperativas com sede na UF',
  singulares INT COMMENT 'Cooperativas singulares',
  centrais INT COMMENT 'Cooperativas centrais',
  confederacoes INT COMMENT 'Confederacoes',
  livre_admissao INT COMMENT 'Singulares de livre admissao de associados',
  centrais_distintas INT COMMENT 'Quantidade de centrais diferentes as quais as singulares da UF sao filiadas',
  participacao_nacional_pct DECIMAL(8,4) COMMENT 'Participacao da UF no total nacional de cooperativas, em %',
  atualizado_em TIMESTAMP COMMENT 'Momento (UTC) da ultima execucao que gravou a linha'
)
USING DELTA
COMMENT 'Cooperativas de credito em funcionamento por UF e classe, com participacao no total nacional.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_gold.cooperativas_uf IS 'Cooperativas de credito em funcionamento por UF e classe, com participacao no total nacional.';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN uf COMMENT 'Sigla da unidade da federacao';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN data_referencia COMMENT 'Data da foto do cadastro';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN total COMMENT 'Total de cooperativas com sede na UF';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN singulares COMMENT 'Cooperativas singulares';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN centrais COMMENT 'Cooperativas centrais';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN confederacoes COMMENT 'Confederacoes';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN livre_admissao COMMENT 'Singulares de livre admissao de associados';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN centrais_distintas COMMENT 'Quantidade de centrais diferentes as quais as singulares da UF sao filiadas';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN participacao_nacional_pct COMMENT 'Participacao da UF no total nacional de cooperativas, em %';
ALTER TABLE workspace.pix_macro_gold.cooperativas_uf ALTER COLUMN atualizado_em COMMENT 'Momento (UTC) da ultima execucao que gravou a linha';
