# DANTEStocks-NomBank-NBDS-
O objetivo deste repositório é abrigar os resultados da pesquisa "Anotação de papéis semânticos em tweets do mercado financeiro: definição de formatos e reutilização de recurso lexical", desenvolvido por Pedro Henrique Silva (UFSCar), no âmbito do projeto do POeTiSA.

O DANTEStocks é um corpus de material textual compilado a partir do Twitter (atualmente X). As postagens foram coletadas automaticamente em 2014 com base nos tickers (códigos das ações) negociadas pelo índice IBOVESPA naquele ano. Este é o primeiro corpus em português de conteúdo gerado por usuários (user-generated content – UGC) com anotação seguindo o modelo Universal Dependencies (UD).

### 📂 Data
Contém:
- Os arquivos de entrada e as bases de conhecimento utilizados no projeto.
- A pasta `input_conllu` com os arquivos originais em formato CoNLL-U.
- A pasta `jsons` contendo os dicionários que mapeiam os papéis predicadores (Rolesets).
- O arquivo `argm.xlsx` com a listagem e taxonomia dos argumentos modificadores (ArgM).

### ⚙️ Scripts
Contém:
- Os códigos em Python desenvolvidos para o processamento, conversão e auditoria dos dados.
- O arquivo `conversor.py`, responsável pela conversão em larga escala da camada anotação semântica em formato standoff para inline.
- O arquivo `auditor.py`, utilizado para auditar e diagnosticar erros na estrutura colunar dos arquivos.

### 🚀 Output
Contém:
- A versão final dos arquivos convertidos e processados pelo sistema.
- Os corpora divididos em treino, desenvolvimento e teste (arquivos `.conllup` do DANTEStocks).
- A **última versão do corpus anotada** (a anotação semântica está codificada nas duas últimas colunas do formato CoNLL-U Plus: `NBDS:ROLESET` e `NBDS:ARGN`).
- Arquivos secundários de análise (`analyze.py`, `count_stats.py`) e a pasta de backup das versões finais.

### 📝 Logs
Contém:
- Os registros de execução (arquivos `.txt`) gerados durante o processamento em massa.
- O detalhamento de operações de validação, correções estruturais aplicadas e possíveis erros rastreados pelo validador automático.
