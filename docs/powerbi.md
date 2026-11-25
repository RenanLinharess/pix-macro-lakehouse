# Power BI: como abrir, conectar e montar os visuais

A pasta `powerbi/` contem um **projeto Power BI (PBIP)**: em vez de um `.pbix` binario, o
modelo semantico fica em texto (TMDL) e o relatorio em JSON (PBIR). Isso permite versionar no
Git, revisar diferencas e documentar cada medida DAX com comentario.

```
powerbi/
├── pix_macro.pbip                         # atalho que abre o relatorio
├── pix_macro.Report/
│   ├── definition.pbir                    # aponta para o modelo (byPath)
│   └── definition/                        # paginas e visuais (PBIR)
└── pix_macro.SemanticModel/
    ├── definition.pbism
    └── definition/
        ├── model.tmdl                     # cultura pt-BR, lista de tabelas
        ├── expressions.tmdl               # parametros: servidor, HTTP path, catalogo, schema
        ├── relationships.tmdl             # UF e capital/interior -> indicadores (por mes)
        └── tables/*.tmdl                  # colunas, medidas DAX e consulta M de cada tabela
```

O modelo le as tres tabelas gold do Databricks pelo conector **Databricks** (ADBC,
`Implementation="2.0"`) em modo **Import**: os dados sao copiados para o arquivo e atualizados
com o botao Atualizar. Para este volume (poucos milhares de linhas) Import e mais rapido e
funciona offline; DirectQuery seria a escolha se a tabela fosse grande ou mudasse a toda hora.

> Licao aprendida ao abrir o projeto pela primeira vez: em TMDL, um comentario `///` vira a
> propriedade `description` do objeto seguinte. Tabela, coluna, medida, modelo e expressao
> aceitam; **relacionamento nao**, e o Power BI recusa o projeto inteiro com "A propriedade
> 'description' e desconhecida". Por isso `relationships.tmdl` nao tem comentarios.

## Abrir e atualizar pela primeira vez

1. Abra o Power BI Desktop e use **Arquivo > Abrir relatorio > Procurar relatorios**, escolhendo
   `powerbi/pix_macro.pbip`. (Dar duplo clique no arquivo tambem funciona.)
2. O relatorio abre com o modelo definido, mas **sem dados** (o cache nao e versionado). Clique em
   **Atualizar** na faixa Pagina Inicial.
3. Na primeira atualizacao o Power BI pede credenciais do Databricks. Escolha **OAuth** e entre
   com a mesma conta do workspace. O token fica guardado no Power BI, nunca no repositorio.
4. Se o workspace for outro, ajuste os parametros em **Transformar dados > Editar parametros**
   (`ServidorDatabricks`, `CaminhoHttp`, `Catalogo`, `SchemaGold`). O Server hostname e o HTTP
   path aparecem no Databricks em SQL Warehouses > Connection details.

## Medidas DAX incluidas (e o que ensinam)

| Medida | Tabela | Conceito |
|---|---|---|
| `Valor Pix`, `Transacoes Pix` | indicadores_mensais | agregacao basica `SUM` |
| `Ticket Medio` | indicadores_mensais | `DIVIDE` evita divisao por zero |
| `IPCA 12 Meses` | indicadores_mensais | `CALCULATE` + `LASTDATE`: valor do ultimo mes do contexto |
| `Valor Pix 12 Meses Atras` | indicadores_mensais | `VAR`, `EDATE(-12)`, `REMOVEFILTERS`: comparar com outro periodo |
| `Crescimento Valor 12m` | indicadores_mensais | medida que usa outras medidas |
| `Participacao Nacional` | pix_uf_mensal | `REMOVEFILTERS(coluna)`: total sem o filtro de UF, mantendo o de mes |
| `Transacoes por Pessoa PF` | pix_uf_mensal | razao de somas, nao media de razoes |
| `Participacao na UF` | pix_capital_interior_mensal | mesmo padrao, agora sem o filtro de localidade |

## Exercicio: montar a pagina "Visao geral"

A pagina vem em branco de proposito: montar os visuais e parte do aprendizado. Sugestao de
layout, equivalente ao dashboard AI/BI:

1. **Quatro cartoes** no topo: `Valor Pix`, `Transacoes Pix`, `Crescimento Valor 12m`,
   `IPCA 12 Meses`. Filtre a pagina para o ultimo mes com uma segmentacao de `data_referencia`
   (ou use um filtro de pagina "Top N = 1 por data").
2. **Grafico de colunas e linhas** (combo): eixo = `data_referencia`; colunas = `Valor Pix`;
   linha = `Selic Media` no **eixo Y secundario** (sem ele a Selic some ao lado de trilhoes de
   reais). Titulo descritivo: "Valor do Pix e meta Selic por mes".
3. **Linha**: `Ticket Medio` por `data_referencia`. Titulo: "Ticket medio por transacao".
4. **Barras horizontais**: `Transacoes por Pessoa PF` por `uf`, cor por `regiao`, filtradas no
   ultimo mes e excluindo `ND` (municipio nao informado).
5. **Colunas 100% empilhadas**: `Valor Pix Localidade` por `data_referencia`, legenda
   `tipo_localidade`, com uma segmentacao de `uf` (comece por RS).

Depois de montar, salve (Ctrl+S): o Power BI grava os visuais em
`pix_macro.Report/definition/pages/visao_geral/visuals/`, e eles passam a ser versionados.

## Perguntas de entrevista sobre esta parte

**"Por que Import e nao DirectQuery?"** Volume pequeno, atualizado uma vez por mes; Import e
mais rapido para o usuario e nao gasta o warehouse a cada clique. DirectQuery faria sentido com
tabelas grandes ou necessidade de dado em tempo real.

**"Qual a diferenca entre coluna calculada e medida?"** Coluna calculada e computada linha a
linha na atualizacao e ocupa memoria; medida e calculada na hora, no contexto do visual. Aqui
quase tudo e medida; as razoes por pessoa existem como coluna na gold por conveniencia para
o dashboard AI/BI, mas no Power BI a medida `Transacoes por Pessoa PF` e a forma correta,
porque soma numerador e denominador antes de dividir.

**"O que e contexto de filtro?"** O conjunto de filtros ativos quando a medida e avaliada
(segmentacoes, eixos, legendas). `CALCULATE` modifica esse contexto; `REMOVEFILTERS` tira uma
parte dele, e e assim que se calcula participacao no total.
