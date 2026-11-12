-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.
CREATE TABLE IF NOT EXISTS workspace.pix_macro_bronze.pix_estatisticas (
  AnoMes INT COMMENT 'Mes de referencia no formato AAAAMM',
  PAG_PFPJ STRING COMMENT 'Tipo do pagador: PF ou PJ',
  REC_PFPJ STRING COMMENT 'Tipo do recebedor: PF ou PJ',
  PAG_REGIAO STRING COMMENT 'Regiao geografica do pagador',
  REC_REGIAO STRING COMMENT 'Regiao geografica do recebedor',
  PAG_IDADE STRING COMMENT 'Faixa etaria do pagador (somente PF)',
  REC_IDADE STRING COMMENT 'Faixa etaria do recebedor (somente PF)',
  FORMAINICIACAO STRING COMMENT 'Forma de iniciacao da transacao (QR code, chave, iniciador etc.)',
  NATUREZA STRING COMMENT 'Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc.',
  FINALIDADE STRING COMMENT 'Finalidade: Pix, Pix Saque, Pix Troco etc.',
  VALOR DOUBLE COMMENT 'Valor total liquidado em reais',
  QUANTIDADE BIGINT COMMENT 'Quantidade de transacoes liquidadas',
  fonte STRING COMMENT 'Nome curto da fonte, conforme config/configuracoes.py',
  url_origem STRING COMMENT 'URL da API chamada para obter os registros',
  parametros_requisicao MAP<STRING,STRING> COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)',
  baixado_em TIMESTAMP COMMENT 'Momento (UTC) em que a resposta foi baixada da API',
  arquivo_origem STRING COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API',
  carregado_em TIMESTAMP COMMENT 'Momento (UTC) em que a linha foi gravada no bronze'
)
USING DELTA
CLUSTER BY (AnoMes)
COMMENT 'Transacoes Pix liquidadas por mes, como vieram da API Olinda do BCB (EstatisticasTransacoesPix). Uma linha por combinacao de dimensoes.';

-- Comentarios reaplicados a cada execucao do pipeline:
COMMENT ON TABLE workspace.pix_macro_bronze.pix_estatisticas IS 'Transacoes Pix liquidadas por mes, como vieram da API Olinda do BCB (EstatisticasTransacoesPix). Uma linha por combinacao de dimensoes.';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN AnoMes COMMENT 'Mes de referencia no formato AAAAMM';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN PAG_PFPJ COMMENT 'Tipo do pagador: PF ou PJ';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN REC_PFPJ COMMENT 'Tipo do recebedor: PF ou PJ';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN PAG_REGIAO COMMENT 'Regiao geografica do pagador';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN REC_REGIAO COMMENT 'Regiao geografica do recebedor';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN PAG_IDADE COMMENT 'Faixa etaria do pagador (somente PF)';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN REC_IDADE COMMENT 'Faixa etaria do recebedor (somente PF)';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN FORMAINICIACAO COMMENT 'Forma de iniciacao da transacao (QR code, chave, iniciador etc.)';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN NATUREZA COMMENT 'Natureza da transacao: P2P, P2B, B2B, P2G, G2P etc.';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN FINALIDADE COMMENT 'Finalidade: Pix, Pix Saque, Pix Troco etc.';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN VALOR COMMENT 'Valor total liquidado em reais';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN QUANTIDADE COMMENT 'Quantidade de transacoes liquidadas';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN fonte COMMENT 'Nome curto da fonte, conforme config/configuracoes.py';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN url_origem COMMENT 'URL da API chamada para obter os registros';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN parametros_requisicao COMMENT 'Parametros enviados na requisicao (mes, filtro, formato)';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN baixado_em COMMENT 'Momento (UTC) em que a resposta foi baixada da API';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN arquivo_origem COMMENT 'Nome do arquivo JSON no Volume, ou api quando lido direto da API';
ALTER TABLE workspace.pix_macro_bronze.pix_estatisticas ALTER COLUMN carregado_em COMMENT 'Momento (UTC) em que a linha foi gravada no bronze';
