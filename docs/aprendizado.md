# Guia de aprendizado do projeto

Este documento acompanha o pipeline etapa por etapa. Para cada uma: os conceitos usados, o
porque de cada escolha, as perguntas que um entrevistador faria e como eu responderia, e
exercicios para fazer sozinho. A ideia e conseguir explicar qualquer linha do repositorio.

Convencao: os trechos "Como eu responderia" estao em primeira pessoa de proposito, para
servirem de ensaio.

---

## 1. Ingestao: buscar dados em APIs publicas

Arquivos: `src/ingestao/cliente_http.py`, `olinda_pix.py`, `sgs.py`, `cooperativas.py`,
`baixar_dados_brutos.py`, `src/transformacoes/calendario.py`.

### Conceitos

- **API REST e JSON.** As fontes do Banco Central respondem a um GET com um JSON. O SGS devolve
  uma lista `[{"data": "01/01/2024", "valor": "11.75"}, ...]`; o Olinda devolve um objeto
  `{"value": [...]}` no padrao OData.
- **OData.** Protocolo de consulta em cima de HTTP: `$filter`, `$top`, `$skip`, `$select`,
  `$orderby`, `$format`. Parametros de funcao vao na URL como `Funcao(Database=@Database)?@Database='202401'`.
  Descobri na pratica que o Olinda nao aceita `@` codificado como `%40` nem espaco como `+`,
  por isso a URL e montada a mao em `montar_url_odata`.
- **Paginacao.** Nunca se baixa uma serie longa de uma vez. O SGS limita a 10 anos em series
  diarias (HTTP 406); o Olinda devolve HTTP 500 com `$skip`. Solucao: janelas de 5 anos no
  SGS e um arquivo por mes no Pix (`$filter=AnoMes eq 202401`).
- **Retry com backoff exponencial.** Erros 429, 500, 502, 503, 504 e timeouts sao temporarios:
  espera-se 2s, 4s, 8s, 16s e tenta-se de novo. Erros 400, 404 e 406 sao permanentes: repetir
  nao resolve, entao falha-se na hora.
- **Envelope de ingestao.** Cada download vira `{"metadados": {...}, "dados": [...]}`. Os
  metadados (URL, parametros, hora, quantidade) sao a prova de origem de cada linha do bronze.
- **Idempotencia.** Rodar o download duas vezes produz o mesmo resultado: o arquivo do mes e
  sobrescrito, nao duplicado. `--somente-faltantes` pula o que ja existe, mas sempre rebaixa os
  ultimos `MESES_RECARGA` meses porque o BCB revisa dados recentes.

### Por que assim

- Dois modos de origem (script local + Volume, ou API direto do notebook) porque o Databricks
  Free Edition restringe a saida para a internet. O script local e o plano B que sempre funciona.
- Funcoes de calendario separadas (`meses_entre`, `janelas_sgs`) porque sao faceis de errar
  (virada de ano, limites inclusivos) e faceis de testar.

### Perguntas de entrevista

**"Como voce lida com uma API instavel?"**
Como eu responderia: separo erros temporarios de permanentes. Para os temporarios uso retry com
backoff exponencial, com limite de tentativas, e registro cada falha em log. Para os
permanentes falho rapido e deixo a mensagem clara. Tambem baixo em pedacos pequenos (um mes por
arquivo), entao uma falha perde pouco e o reprocessamento e barato.

**"O que e idempotencia e por que importa num pipeline?"**
Como eu responderia: e a garantia de que rodar o mesmo processo duas vezes da o mesmo
resultado. Importa porque pipelines falham no meio e precisam ser reexecutados sem gerar
duplicidade. No projeto, o download sobrescreve o arquivo do mes e o bronze grava com
`replaceWhere` por mes.

**"Por que voce guarda metadados de ingestao?"**
Como eu responderia: para auditoria e depuracao. Se um numero parece errado, consigo saber de
qual URL, com quais parametros e em que hora aquela linha veio. Em instituicao financeira
regulada isso e requisito, nao luxo.

### Exercicios

1. Adicione a serie 4390 do SGS (Selic acumulada no mes) em `FONTES` e baixe-a com o script.
   Compare com a media mensal que calculamos a partir da serie 432.
2. Faca `obter_json` registrar o tempo de cada tentativa e imprima um resumo ao final do
   download: quantas chamadas, quantas repetidas, tempo medio.

---

## 2. Bronze: dado bruto com rastreabilidade

Arquivos: `notebooks/01_bronze.py`, `src/transformacoes/bronze.py`, `src/catalogo/tabelas.py`.

### Conceitos

- **Arquitetura medalhao.** Tres camadas com responsabilidades claras: bronze guarda o dado como
  veio; silver limpa e tipa; gold agrega para o negocio. Cada camada pode ser reconstruida a
  partir da anterior.
- **Delta Lake.** Formato de tabela em cima de arquivos Parquet com log de transacoes. Da ACID,
  historico de versoes (time travel), `MERGE`, e `replaceWhere`.
- **`replaceWhere`.** Sobrescreve so as linhas que atendem a um predicado (`AnoMes = 202401`),
  numa unica transacao. E o que torna a carga do Pix idempotente por mes.
- **Volume do Unity Catalog.** Area de arquivos governada (permissoes, lineage) acessivel como
  caminho `/Volumes/catalogo/schema/volume/...`. E a zona de pouso dos JSONs.
- **Esquema explicito.** `spark.createDataFrame(linhas, schema="AnoMes INT, ...")` em vez de
  inferir. Inferencia e fragil: um mes com valor nulo muda o tipo e quebra a escrita.
- **Liquid clustering (`CLUSTER BY`).** Substituto moderno de particionamento: organiza os
  arquivos pela coluna de filtro mais comum (`AnoMes`) sem criar milhares de pastas pequenas.

### Por que assim

- Colunas com os nomes originais da API (`VL_PagadorPF`) no bronze: e "como veio". A traducao
  para snake_case fica na silver, entao o bronze serve de prova contra a fonte.
- Metadados em colunas (nao em texto JSON) porque facilitam filtro em SQL
  (`WHERE arquivo_origem = ...`).
- Carga incremental: so meses ausentes mais os ultimos tres. A primeira carga e lenta, as
  seguintes levam segundos.

### Perguntas de entrevista

**"Por que nao transformar ja no bronze?"**
Como eu responderia: porque o bronze e a copia fiel da fonte. Se eu errar uma regra na silver,
reconstruo a partir do bronze sem baixar de novo. E se a fonte revisar um numero, consigo
comparar as duas versoes.

**"Qual a diferenca entre `mode('overwrite')` e `replaceWhere`?"**
Como eu responderia: `overwrite` troca a tabela inteira; `replaceWhere` troca so as linhas do
predicado, atomicamente. Uso `overwrite` em tabelas pequenas (Selic, IPCA) e `replaceWhere`
onde a carga e por pedaco (Pix por mes).

**"O que acontece se o mesmo mes for carregado duas vezes?"**
Como eu responderia: nada de ruim. O `replaceWhere` apaga e regrava as linhas daquele mes na
mesma transacao. Nao ha duplicidade e nao ha janela em que a tabela fica vazia.

### Exercicios

1. Use `DESCRIBE HISTORY workspace.pix_macro_bronze.pix_estatisticas` e identifique a operacao e
   o predicado de uma carga com `replaceWhere`.
2. Consulte a versao anterior da tabela com `VERSION AS OF` e compare a contagem de um mes
   antes e depois de uma recarga.

---

## 3. Silver: tipos, deduplicacao e base unificada

Arquivo: `notebooks/02_silver.py`, `src/transformacoes/sgs.py`, `src/transformacoes/pix.py`.

### Conceitos

- **Tipos de negocio.** Dinheiro em `DECIMAL(20,2)`, nunca `DOUBLE`: ponto flutuante acumula
  erro de arredondamento em somas grandes. Datas em `DATE`, nao texto.
- **snake_case.** Padrao de nome legivel e consistente (`valor_pagador_pf`), facil de digitar em
  SQL e de documentar.
- **Window functions.** `row_number() OVER (PARTITION BY chave ORDER BY carregado_em DESC)`
  numera as linhas dentro de cada chave; ficar com `posicao = 1` e a forma classica de
  deduplicar mantendo a mais recente. Em T-SQL e identico.
- **Mes corrente excluido.** O mes em andamento esta incompleto; incluir distorceria qualquer
  variacao mensal.
- **LEFT JOIN na base mensal.** Partimos do Pix e trazemos Selic e IPCA. Se o IPCA do ultimo
  mes ainda nao saiu, a linha existe com nulo e a qualidade avisa, em vez de o mes sumir.
- **Trazer ao driver (`collect`).** Para series pequenas (Selic tem ~3 mil linhas diarias,
  IPCA ~100), e mais simples e testavel calcular em Python puro do que em Spark. Para o Pix
  (800 mil linhas), agregamos em Spark.

### Qualidade de dados

- **Regras padronizadas** (`src/transformacoes/qualidade.py`): nulos, faixa, unicidade,
  continuidade de meses, reconciliacao. Cada regra devolve `{regra, coluna, status,
  valor_observado, limite, detalhe}`.
- **Severidade.** `erro` interrompe o job antes da gold; `aviso` so registra. O IPCA do ultimo
  mes faltando e aviso; linha duplicada na chave e erro.
- **Reconciliacao entre fontes.** A soma nacional do Pix deve bater com a soma por municipio.
  Duas fontes independentes concordando e a melhor evidencia de que o dado esta certo.
- **Tabela de auditoria.** Historico de todas as execucoes, nunca sobrescrito. Permite
  perguntar "quando essa regra falhou pela primeira vez?".

### Perguntas de entrevista

**"Como voce garante a qualidade dos dados?"**
Como eu responderia: regras explicitas, versionadas junto com o codigo, executadas a cada carga
e com resultado gravado em tabela. Separo severidades: o que invalida o dado para o job
(duplicidade, buraco na serie) e o que so merece atencao. E uso reconciliacao entre fontes
independentes quando existe.

**"Por que DECIMAL e nao DOUBLE para dinheiro?"**
Como eu responderia: DOUBLE e binario e nao representa 0,10 exatamente; em somas de bilhoes de
centavos a diferenca aparece. DECIMAL guarda o valor exato com escala fixa. O bronze pode ter
DOUBLE porque e como o JSON veio; a silver converte.

**"Como voce remove duplicados mantendo o registro mais recente?"**
Como eu responderia: `row_number()` particionado pela chave natural, ordenado pela data de carga
decrescente, e filtro `= 1`. Funciona igual em PySpark, Spark SQL e T-SQL.

### Exercicios

1. Escreva em SQL a deduplicacao da serie Selic (bronze) e compare a contagem com a silver.
2. Crie uma regra nova em `qualidade.py` (por exemplo, "o ticket medio do Pix deve ficar entre
   R$ 50 e R$ 1.000") com teste no pytest, e ligue-a no notebook da silver com severidade aviso.

---

## 4. Gold: indicadores que respondem a pergunta

Arquivo: `notebooks/03_gold.py`, `src/transformacoes/sgs.py`, `src/transformacoes/pix.py`.

### Conceitos

- **IPCA acumulado em 12 meses e produto, nunca soma.** `(prod(1 + taxa/100) - 1) * 100`. Um
  por cento ao mes por doze meses da 12,68 por cento, nao 12. Em SQL:
  `EXP(SUM(LN(1 + taxa/100)) OVER (ORDER BY ano_mes ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)) - 1`.
- **Selic media mensal.** Media simples da serie diaria da meta. O Copom muda a meta no meio do
  mes; a media reflete a taxa que vigorou.
- **Variacao mensal e em 12 meses.** `(atual / anterior - 1) * 100`. Em Python puro
  (`crescimento_mensal`) e o equivalente a `LAG(valor, 1)` e `LAG(valor, 12)`.
- **Window functions em Spark.** `lag('valor', 12) OVER (PARTITION BY uf ORDER BY ano_mes)` busca
  o mesmo mes do ano anterior; `sum('valor') OVER (PARTITION BY ano_mes)` da o total nacional
  para calcular participacao.
- **Perspectiva do pagador.** No recorte por UF usamos as transacoes feitas por residentes da UF
  (`*_pagador_*`), porque a pergunta e sobre adocao do Pix pela populacao local.
- **Capital versus interior.** Classificacao pelo codigo IBGE da capital. Mostra interiorizacao
  do uso, tema caro a quem atua fora dos grandes centros.

### Por que assim

- Gold reconstruida inteira a cada execucao: e pequena, o calculo e deterministico e assim
  evita-se estado parcial.
- A mesma funcao testada no pytest e a que roda no job. Nao ha "versao de teste" e "versao de
  producao" da logica.

### Perguntas de entrevista

**"Por que nao somar a inflacao mensal para ter o acumulado do ano?"**
Como eu responderia: porque inflacao e composta. Cada mes incide sobre o preco ja reajustado.
Somar subestima o acumulado. O certo e multiplicar os fatores `(1 + taxa)` e subtrair 1.

**"Explique uma window function que voce usou."**
Como eu responderia: na gold por UF uso `lag(valor, 12)` particionado por UF e ordenado por mes
para pegar o valor de doze meses atras na mesma UF, e com isso calculo a variacao anual. A
window evita um self join e deixa claro o que esta sendo comparado.

**"Como voce evitaria que um buraco na serie quebrasse o LAG?"**
Como eu responderia: a regra `continuidade_meses` na silver falha com severidade erro se faltar
algum mes, entao a gold nunca roda em cima de serie com buraco.

### Exercicios

1. Reescreva `ipca_acumulado_12m` em Spark SQL usando `EXP(SUM(LN(...)))` com window e compare
   com a coluna `ipca_acumulado_12m` da gold.
2. Adicione a gold uma tabela `pix_regiao_mensal` (Norte, Nordeste, ...) reaproveitando
   `pix_uf_mensal`, com participacao nacional por regiao.

---

## 5. Testes: por que Python puro e como testar logica de dados

Arquivos: `tests/`, `pyproject.toml`.

### Conceitos

- **pytest.** Funcoes `test_*` com `assert`. `pytest.approx` para comparar floats.
- **Teste com valor oficial.** O teste do IPCA 2024 usa os doze valores reais e confere o
  acumulado publicado (4,83 por cento). E um teste de regressao contra a realidade.
- **Separar logica de infraestrutura.** O que precisa de Spark (ler tabela, gravar) fica fino
  no notebook; o que e regra de negocio fica em funcao pura. Funcao pura e trivial de testar.
- **Teste de especificacao.** `tests/test_catalogo.py` garante que toda coluna de toda tabela
  tem tipo e comentario. Governanca testada, nao prometida.

### Por que sem Spark local

Nao ha Java na maquina e o Free Edition so roda Spark serverless. Instalar um Spark local so
para testar criaria atrito e divergencia de versao. A troca: nao testo a parte Spark
localmente; ela e validada pelas regras de qualidade no proprio Databricks.

### Perguntas de entrevista

**"Como voce testa um pipeline de dados?"**
Como eu responderia: em tres niveis. Unitario, com pytest sobre funcoes puras de regra de
negocio. Qualidade de dados, com regras executadas a cada carga e gravadas em tabela de
auditoria. E reconciliacao com fontes independentes quando existem. O que nao consigo testar
localmente (escrita Delta) e coberto pelas regras no ambiente real.

### Exercicios

1. Escreva um teste para `janelas_sgs` com `anos=10` e um periodo de exatamente 10 anos.
2. Escreva um teste parametrizado (`@pytest.mark.parametrize`) para `classificar_capital_interior`
   com cinco municipios do RS.

---

## 6. Governanca: Unity Catalog e documentacao viva

Arquivos: `src/catalogo/tabelas.py`, `src/catalogo/gerar_ddl.py`, `sql/ddl/`,
`notebooks/00_preparar_ambiente.py`.

### Conceitos

- **Unity Catalog.** Camada de governanca: catalogo > schema > tabela/volume, com permissoes,
  lineage e comentarios pesquisaveis.
- **Comentario de tabela e coluna.** `COMMENT ON TABLE ...` e `ALTER TABLE ... ALTER COLUMN ...
  COMMENT`. Aparecem no Catalog Explorer e na busca do catalogo.
- **Fonte unica de verdade.** A especificacao em Python gera o DDL, os comentarios e o esquema
  do Spark. Mudou a especificacao, tudo muda junto; nao existe doc desatualizada.
- **DDL gerado e versionado.** `sql/ddl/*.sql` existe para leitura e revisao; o notebook usa a
  especificacao direto.

### Perguntas de entrevista

**"Como voce documenta as tabelas?"**
Como eu responderia: no proprio catalogo, com comentario em toda tabela e toda coluna, gerados
a partir de uma especificacao versionada e reaplicados a cada execucao. Um teste garante que
nenhuma coluna fica sem comentario.

### Exercicios

1. Adicione uma coluna nova a uma tabela silver na especificacao, rode `gerar_ddl`, rode os
   testes e observe o que precisa mudar no notebook.
2. No Catalog Explorer, procure a tabela `base_mensal` e leia a lineage: de quais tabelas ela
   depende?

---

## 7. Deploy: bundle e job serverless

Arquivos: `databricks.yml`, `resources/pipeline_pix_macro.job.yml`.

### Conceitos

- **Declarative Automation Bundle (DAB).** O job e descrito em YAML, versionado e publicado com
  `databricks bundle deploy`. Infraestrutura como codigo.
- **Modo `development`.** O nome do job ganha prefixo `[dev usuario]` e a agenda fica pausada;
  cada pessoa publica a sua copia sem conflito.
- **Serverless.** Sem cluster para configurar: tarefa sem bloco de cluster roda em serverless.
  `performance_target: STANDARD` porque e carga mensal, sem pressa.
- **Parametros do job.** `modo_origem`, `fontes`, `mes_fim` viram widgets nos notebooks.
  `{{job.run_id}}` identifica a execucao na tabela de auditoria.
- **Dependencias entre tarefas.** `depends_on` encadeia preparar -> bronze -> silver -> gold.
  Se a silver falhar na qualidade, a gold nao roda.

### Perguntas de entrevista

**"Como voce colocaria esse pipeline em producao?"**
Como eu responderia: com o bundle. Criaria um target `prod` em modo `production`, com a agenda
ativa e um service principal como dono, e publicaria via CI. O mesmo YAML serve para dev e
prod, mudando so variaveis.

### Exercicios

1. Adicione um target `prod` ao `databricks.yml` com `mode: production` e `pause_status: UNPAUSED`,
   e valide com `databricks bundle validate -t prod`.
2. Rode o job com `--params modo_origem=api` e compare o tempo com o modo `volume`.

---

## 8. Dashboard AI/BI e Power BI

(Esta secao sera completada depois da publicacao do dashboard, com os visuais escolhidos,
o porque de cada um e o passo a passo de conexao do Power BI ao SQL warehouse.)
