-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_auditoria.resultados_qualidade (
  executado_em TIMESTAMP COMMENT 'Momento (UTC) da execucao',
  execucao_id STRING COMMENT 'Identificador da execucao do job (run id) ou manual',
  camada STRING COMMENT 'Camada verificada: bronze, silver ou gold',
  tabela STRING COMMENT 'Nome completo da tabela verificada',
  regra STRING COMMENT 'Nome da regra: nulos, faixa, unicidade, continuidade_meses, reconciliacao',
  coluna STRING COMMENT 'Coluna ou chave verificada',
  status STRING COMMENT 'ok ou falha',
  severidade STRING COMMENT 'erro interrompe o pipeline; aviso apenas registra',
  valor_observado STRING COMMENT 'Valor medido na verificacao',
  limite STRING COMMENT 'Limite aceito pela regra',
  detalhe STRING COMMENT 'Descricao legivel do resultado'
)
USING DELTA
CLUSTER BY (executado_em)
COMMENT 'Resultado de cada regra de qualidade executada pelo pipeline. Uma linha por regra, por execucao. Historico completo, nunca sobrescrito.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_auditoria.resultados_qualidade IS 'Resultado de cada regra de qualidade executada pelo pipeline. Uma linha por regra, por execucao. Historico completo, nunca sobrescrito.';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN executado_em COMMENT 'Momento (UTC) da execucao';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN execucao_id COMMENT 'Identificador da execucao do job (run id) ou manual';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN camada COMMENT 'Camada verificada: bronze, silver ou gold';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN tabela COMMENT 'Nome completo da tabela verificada';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN regra COMMENT 'Nome da regra: nulos, faixa, unicidade, continuidade_meses, reconciliacao';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN coluna COMMENT 'Coluna ou chave verificada';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN status COMMENT 'ok ou falha';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN severidade COMMENT 'erro interrompe o pipeline; aviso apenas registra';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN valor_observado COMMENT 'Valor medido na verificacao';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN limite COMMENT 'Limite aceito pela regra';
ALTER TABLE workspace.pix_macro_auditoria.resultados_qualidade ALTER COLUMN detalhe COMMENT 'Descricao legivel do resultado';
