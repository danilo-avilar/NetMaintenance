# Simulador da Camada NetMaintenance em Redes Mesh

Este projeto implementa, em **Python 3.6+**, uma simulação da **NetMaintenance** baseada nos conceitos do protocolo **HyParView**.
O objetivo é validar a modelagem da manutenção adaptativa da vizinhança (Active View e Passive View) em uma rede mesh, medindo **tempo médio de convergência** (em execuções), **diversidade da lista passiva** e **distribuição final da conectividade** a partir de ** múltiplas execuções experimentais **.

---

## Descrição Geral

O script `sc.py` é reponsável pela execução da simulação de funcionamento da camanda de conectividade. Cada nó da rede (simulado como um objeto `Node`) mantém duas listas dinâmicas:
- **Active View (ativos)** → vizinhos conectados diretamente, com quem o nó troca mensagens de dados.
- **Passive View (passivos)** → lista de backup de nós conhecidos, para substituir ativos que falharem.

A cada **ciclo**:
1. Cada nó envia **pings** apenas aos seus vizinhos da Active View.  
2. Nós que não respondem são removidos da Active View e substituídos por nós sorteados da Passive View.  
3. Cada nó tem uma probabilidade de falha definida a partir de uma distribuição de dados gaussiana, controlada por média e desvio padrão.
4. Uma fração (30%) da Passive View é **trocada com um vizinho ativo** (operação de *shuffle*), promovendo diversidade.  
5. Métricas são registradas e gráficos atualizados ao final de cada ciclo.

---

## Parâmetros importantes

| Parâmetro | Descrição |
|------------|------------|
| `total_nodes` | Número total de nós na rede. |
| `active_size` | Tamanho da Active View. |
| `passive_size` | Tamanho da Passive View. |
| `fail_mean` | Probabilidade média de falha de cada nó, obtida a partir de uma distribuição gaussiana. |
| `fail_std` | Desvio padrão para `fail_mean`. |
| `max_cycles` | Quantidade de ciclos (iterações) de atualização da rede. |
| `debug_nodes` | Lista de nós exibidos em modo detalhado (debug). |
| `csv_filename` | Nome do arquivo CSV gerado com os resultados. |
| `save_graphs` | Indica se os gráficos devem ser salvos automaticamente. |

---

## Modo Debug

O modo de depuração (debug) mostra em detalhes o comportamento de até **três nós** selecionados (`debug_nodes`), evitando sobrecarga visual.  
Em cada ciclo, para esses nós são exibidos:
- **Active View inicial e final**.  
- **Passive View inicial e final**.  
- Resultados dos pings:  
  - `Ping OK [x, x, x, ...]`: nós que responderam ao comando.  
  - `Ping FAIL [y, y, y, ...]`: nós que não responderam ao comando.
    - Para cada nó que falhar, ID do nó passivo que será promovido
- Resumo da rede:  
  - Média de vizinhos ativos.  
  - Diversidade média da Passive View.
  - Mensagens no ciclo
  - Total acumulado de mensagens

---

## Estrutura de Saída

Após execução, são gerados:
**1. Arquivo CSV** (`res.csv`) contendo:
   - `Ciclo`: número do ciclo.
   - `MediaAtivos`: média de vizinhos ativos.
   - `MediaDiversidadePassiva`: média de diversidade da Passive View.
   - `MensagensCiclo`: quantidade total de mensagens trocadas no ciclo em questão.
   - `MensagensAcumuladas`: quantidade de mensagens acumuladas considerando os ciclos anteriores.
   - `NoX_Ativos`: tamanho da Active View de cada nó.
   - `NoX_MensagensCiclo`: quantidade de mensagens trocadas pelo nó no ciclo atual.
   - `NoX_MensagensAcumuladas`: quantidade de mensagens acumuladas pelo nó considerando os ciclos anteriores.

**2. Arquivo CSV** (`res_acc.csv`) contendo:
   - `No`: número do ciclo.
   - `MensagensAcumuladas`: quantidade total de mensagens acumuladas ao final da execução no respectivo ciclo.

**3. Arquivo TXT** (`debug.txt`) contendo:
   - Informações **Modo Debug** dos nós especificados em `debug_nodes`
   
**4. Gráficos**:
   - `grafico_media_ativos.png`: Evolução da média de vizinhos ativos.
   - `grafico_diversidade_passiva.png`: Evolução da diversidade da Passive View.
   - `grafico_distribuicao`: Histograma da conectividade final.
   - `grafico_mensagens_acumuladas_por_no_debug.png`: Evolução das mensagens acumuladas da lista `debug_nodes`.
   - `grafico_mensagens_acumuladas.png`: Histograma das mensagens acumuladas por nó.
   - `grafico_mensagens.png`: Quantidade de mensagens trocadas por ciclo.

---

## Requisitos e Execução

### Requisitos
- Python **3.6.15** ou superior.
- Bibliotecas:
  ```bash
  pip install matplotlib
  ```

### Execução
  ```bash
  python3 sc.py --total_nodes 50 --active_size 4 --passive_size 6 --fail_mean 0.3 --fail_std 0.1 --max_cycles 30 --debug_nodes 0 1 2 --csv_filename res.csv --save_graphs
  ```
ou
  ```bash
  python3 sc.py --help
  ```
para ajuda.

---

## Interpretação dos resultados
**1. Tempo de convergência**
Indica o ciclo em que todos os nós atingiram o número máximo de vizinhos ativos. Impresso no terminal como:
  ```bash
  Tempo de convergência: X ciclos
  ```

**2. Evolução da média de ativos**
Quanto mais rápido atingir a linha vermelha tracejada, melhor a convergência.

**3. Diversidade da Passive View**
Mede quantos vizinhos diferentes já passaram pela Passive View de cada nó. Em cada ciclo, para cada nó, é contabilizado quantos vizinhos únicos ele já teve na Passive View desde o início da simulação. Isso dá uma noção de renovação de contatos ao longo do tempo. Portanto, uma linha crescente indica que a rede está trocando passivos com sucesso, enquanto uma linha estagnada indica que o shuffle não está trazendo novos nós (pode indicar problema de conectividade).

**4. Distribuição final**
Mostra quantos nós terminaram com X vizinhos ativos. Idealmente, todos devem estar no valor alvo (`active_size`).

---
---

# Scripts de Apoio

Criados para automatização dos testes e sintetização dos resultados obtidos.

---

## Teste Automatizado

O script `run.py` realiza uma execução automatizada variando a quantidade de nós da rede e permitindo também variar o valor médio da distribuição de probabilidade de falha. Para isso cada cenário é repetido por **30 vezes** para cálculo de médias e desvios padrão.  

---

## Estrutura de Saída
```
  .
  └── n10
      └── prob0_1
          └── rep1
              ├── debug.txt
              ├── grafico_distribuicao.png
              ├── grafico_diversidade_passiva.png
              ├── grafico_media_ativos.png
              ├── grafico_mensagens_acumuladas.png
              ├── grafico_mensagens_acumuladas_por_no_debug.png
              ├── grafico_mensagens.png
              ├── res_acc.csv
              └── res.csv

```

Após execução, uma estrutura de diretórios é gerada de acordo com o seguinte formato:
   - Diretórios nXX → XX = {10, 20, ..., XX}:  quantidade de nós.
   - Subdiretórios prob0_Y → Y = {1, 2, ..., Y}: correspondem ao valor médio da probabilidade de falha {0.1, 0.2, ..., 0.Y}.
   - Subdiretórios rep_W → W = {1, 2, ..., W}: correspondem a repetição em questão do cenário de teste.
        - Dentro de cada subdiretório rep_W, os resultados obtidos a partir da execução de `sc.py` são salvos.

---

## Execução

  ```bash
  python3 run.py
  ```
---

## Sintetização de Resultados

O script `analysis.py` produz uma visão consolidada dos resultados obtidos a partir do teste automatizado, comparando a quantidade de nós da rede vs probabilidade de falha.

O parâmetro `modo_graficos`, configurado em hardcode, permite determinar se os gráficos serão criados separados por nó (`modo_graficos = "separado"`) ou um único arquivo com todos os nós unificados (`modo_graficos = "junto"`).

---

## Estrutura de Saída

Após execução, são gerados:
**1. Arquivo CSV** (`analise_resultados.csv`) contendo:
   - `Total_Nodes`: quantidade de nós.
   - `Fail_Prob`: probabilidade de falha média.
   - `Convergiu_pct`: média de vezes que a rede convergiu.
   - `Tempo_Convergencia_medio`: em média, qual ciclo ocorre a convergência.
   - `Tempo_Convergencia_std`: desvio padrão para o dado anterior.
   - `Media_Ativos_Ciclo0_medio`: quantidade média de nós ativos.
   - `Media_Ativos_Ciclo0_std`: desvio padrão para o dado anterior.

**2. Gráficos Unificados**:
   - `ativos_ciclo0`: Média de nós ativos no primeiro ciclo.
   - `tempo_convergencia`: Tempo médio de convergência (em ciclos).
---

## Execução

  ```bash
  python3 analysis.py
  ```
---
---

**Autor**
Contato: daniloavilar@gmail.com
Versão: 11.0
Data: 08-10-2025
Licença: MIT
