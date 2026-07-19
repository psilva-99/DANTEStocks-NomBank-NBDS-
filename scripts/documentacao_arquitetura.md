# Documentação Oficial da Arquitetura (V19 e V10)

Esta documentação detalha o fluxo de execução, a engenharia de dados e as inteligências sintáticas implementadas nas versões definitivas dos scripts de conversão e validação.

## 1. O Conversor em Massa (v19)

O conversor atua como o motor de fusão de dados. Ele pega os dados brutos de entrada (anotações linguísticas, papéis semânticos e Excel de modificadores) e os costura no formato padronizado *CoNLL-U Plus*.

### A. Desacoplamento e CLI (Linha de Comando)
O script foi equipado com o módulo `argparse`. Ele não depende mais de caminhos de disco amarrados ao computador do programador.
Ao ser executado, o script calcula dinamicamente a sua própria localização no disco e mapeia as pastas de trabalho (`data`, `output`, `logs`) com base nessa posição relativa. Ele também expõe parâmetros (`--json-dir`, `--output-dir`, etc.) para que o pesquisador possa customizar as pastas direto pelo terminal, caso queira.

### B. Varredura Universal (`glob`)
Em vez de depender de uma lista fixa de arquivos (`dev`, `test`, `train`), o script faz uma varredura cega (`glob.glob`) na pasta de entrada buscando tudo que termine em `.conllu`. Isso significa que se o seu corpus crescer de 3 para 500 arquivos, o script processará todos eles automaticamente sem nenhuma alteração no código.

### C. Espelhamento Estrito e Proteção contra Hallucination (Refatoração V18)
O motor de processamento agora é um "espelho absoluto" dos seus arquivos JSON. No passado, o script possuía um *fallback* que injetava papéis semânticos sintéticos (sem argumentos) caso encontrasse um verbo no texto que tivesse apenas um sentido no dicionário, mesmo que o anotador humano não o tivesse marcado.
Nesta versão, esse comportamento foi banido. O script injeta **apenas e estritamente** o que consta nos 1000 registros mapeados nos JSONs limpos.

### D. Suporte a Predicadores Repetidos (Refatoração V17)
Caso a mesma palavra atue como predicador duas ou mais vezes na mesma sentença (Ex: duas vezes a palavra "hora" recebendo *rolesets* diferentes na mesma frase), o conversor não funde mais as anotações em uma massa só. Ele usa uma inteligência de consumo de IDs (`used_pred_ids = set()`). 
Quando ele injeta a anotação na primeira palavra, ele "grava" o ID daquele token. Ao processar a segunda anotação, ele desvia da primeira e procura a próxima aparição da palavra na frase, isolando os papéis semânticos adequadamente.

### E. Padronização Universal Dependencies
O conversor exporta os dados gerados com a extensão acadêmica oficial `.conllup`, facilitando a integração do seu dataset com outras ferramentas linguísticas globais.

---

## 2. O Validador de Massa (v10)

O validador é a sua suite de testes automatizada. Ele faz a engenharia reversa do arquivo `.conllup` gerado pelo conversor e o compara com os JSONs (fonte da verdade) em busca de inconsistências sintáticas.

### A. Integração com a Nova Estrutura CLI
Assim como o conversor, o validador rastreia as pastas `data` e `output` dinamicamente pelo terminal, gerando logs sequenciais organizados na pasta `logs`.

### B. Compreensão de Predicadores Duplos (Refatoração V9)
Para testar os predicadores repetidos que o conversor aprendeu a gerar na v17, o validador precisou ficar mais inteligente. Quando ele lê a coluna de *rolesets* no CoNLL-U Plus e encontra múltiplos predicadores na mesma linha delimitados por *pipe* (`|`), ele divide esses elementos em uma lista (Array) de papéis semânticos esperados e avalia independentemente se todos os argumentos casam com a fonte original, resolvendo as "Falsas Falhas" de validação antigas.

### C. Relatório de Discrepância Silenciosa
O validador agora audita unicamente os dados presentes no JSON. Se uma palavra existir no CoNLL-U mas não no JSON, ele a ignora pacificamente, garantindo uma taxa de acerto pautada na anotação puramente humana, culminando na validação livre de erros atual.
