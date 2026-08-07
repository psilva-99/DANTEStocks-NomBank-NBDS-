# DANTEStocks-NomBank-NBDS-
O DANTEStocks-NounBank (DSNB) é a versão do corpus [DANTEStocks](https://sites.google.com/icmc.usp.br/poetisa/porttinari-3-0) [(Di-Felippo; Roman, 2025)](https://doi.org/10.1590/1984-6398202549802) no formato [CoNLL-U Plus](https://universaldependencies.org/ext-format.html), que define duas colunas adicionais ao formato tradicional (CoNLL-U) destinadas à anotação de papéis semânticos em predicações nominais que ocorrem em tweets do mercado financeiro. Do total de 4.048 tweets do DSNB, 822 deles contém 1.000 predicações nominais que, além da anotação sintática segundo o modelo gramatical [Universal Dependencies](https://universaldependencies.org/) (UD) [(Nivre et al., 2020](https://aclanthology.org/2020.lrec-1.497/), [de Marneffe et al. 2021)](https://doi.org/10.1162/coli_a_00402), possui anotação semântica ao estilo [NomBank](https://nlp.cs.nyu.edu/meyers/nombank/nombank.1.0/) [(Meyers, 2004](http://nlp.cs.nyu.edu/meyers/papers/nombank-pap.pdf), [2007)](http://nlp.cs.nyu.edu/meyers/papers/nombank-ann.pdf). Para viabilizar a unificação das anotações UD e semântica, adotou-se o formato de anotação semântica dependency-based (isto é, as relações semânticas entre um predicador e seus argumentos são estabelecidas por meio de dependências diretas entre palavras). Os papéis semânticos do DSNB são provenientes do repositório lexical NounBank.DS [(Barbosa; Di Felippo, 2025)](https://sol.sbc.org.br/index.php/stil/article/view/37811/37589).

O DANTESTocks-Nounbank é resultado da pesquisa intitulada "Anotação de papéis semânticos em tweets do mercado financeiro: definição de formatos e reutilização de recurso lexical", desenvolvido por Pedro Henrique Silva (UFSCar), no âmbito do projeto do POeTiSA.

### Agradecimentos

Este trabalho foi realizado no Centro de Inteligência Artificial da Universidade de São Paulo (C4AI), com apoio da Fundação de Amparo à Pesquisa do Estado de São Paulo (FAPESP, processo nº 2019/07665-4) e da IBM Corporation. O projeto também contou com o apoio do Ministério da Ciência, Tecnologia e Inovações, com recursos da Lei nº 8.248, de 23 de outubro de 1991, no âmbito do PPI-SOFTEX, coordenado pela Softex e publicado como Residência em TIC 13, DOU 01245.010222/2022-44.
Agradecemos, ainda, à FAPESP pelo auxílio financeiro específico a este trabalho, concedido por meio de bolsa de iniciação científica (processo nº 2025/07948-7).

### Como Citar

SILVA, P. H.; DI-FELIPPO, A. Metodologia de construção do DANTEStocks-NounBank. Relatório Técnico do ICMC XXX. São Carlos: Instituto de Ciências Matemáticas e de Computação, Universidade de São Paulo, 2026. 31p.

### Estrutura dos conteúdos deste repositório:

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

### 📝 Logs
Contém:

- Os registros de execução (arquivos `.txt`) gerados durante o processamento em massa.
- O detalhamento de operações de validação, correções estruturais aplicadas e possíveis erros rastreados pelo validador automático.

- ### Financiamento

- Essa pesquisa (FAPESP	2025/07948-7) foi financiada pela Fundação de Amparo à Pesquisa do Estado de São Paulo (FAPESP).
