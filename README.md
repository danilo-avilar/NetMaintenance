# Simulador da Camada NetMaintenance em Redes Mesh

---

## Resumo do Artefato

Este repositório disponibiliza o artefato computacional associado ao artigo:

**“Modelagem e Avaliação de uma Camada de Conectividade Adaptativa para Atualizações OTA em Redes Mesh IoT”**

O artefato consiste em um **simulador em Python** da camada **NetMaintenance**, inspirada no protocolo **HyParView**, responsável pela manutenção adaptativa da vizinhança lógica de uma rede mesh de dispositivos embarcados.  
O objetivo principal é **validar experimentalmente** a capacidade da camada em:

- manter conectividade lógica sob falhas,
- promover diversidade estrutural via *shuffle* da lista passiva,
- alcançar rápida convergência da vizinhança ativa,

conforme as **reivindicações apresentadas no artigo**.

---

## Estrutura do README.md

Este README está organizado da seguinte forma:

1. Estrutura do Repositório
2. Selos Considerados
3. Informações Básicas
4. Dependências
5. Preocupações com Segurança
6. Instalação
7. Teste Mínimo
8. Experimentos e Reivindicações
9. Licença

---

## 1. Estrutura do Repositório

```
  .
  ├── Exemplo de resultados/ # Diretórios contendo exemplo de resultados já gerados
  ├── LICENSE # Licença de software
  ├── README.md # Documentação do artefato
  ├── analysis.py # Consolidação e análise estatística dos resultados
  ├── run.py # Execução automatizada de múltiplos cenários experimentais
  └── sc.py # Simulador principal da camada NetMaintenance

```
Durante a execução, são criados diretórios e arquivos de saída contendo resultados experimentais, conforme descrito nas seções posteriores.

---

## 2. Selos Considerados

Os selos considerados para avaliação deste artefato são:

- **Artefatos Disponíveis (SeloD)**
- **Artefatos Funcionais (SeloF)**
- **Artefatos Sustentáveis (SeloS)**
- **Experimentos Reprodutíveis (SeloR)**

---

## 3. Informações Básicas

### Ambiente de Execução

- **Sistema Operacional**: Linux (testado em openSUSE Leap 15.4)
- **Arquitetura**: x86_64
- **Linguagem**: Python 3.6 ou superior
- **Memória RAM recomendada**: ≥ 2 GB
- **Armazenamento**: ≥ 500 MB livres
- **Tempo médio de execução**:
  - Teste mínimo: < 1 minuto
  - Experimentos completos: até alguns minutos, dependendo dos parâmetros avaliados

Obs.: Não é necessário GPU ou acesso à internet após a instalação.

---

## 4. Dependências

As dependências externas são mínimas:

- **Python** ≥ 3.6
- **matplotlib** ≥ 3.3.4

Instalação da dependência principal:

```bash
    pip install matplotlib
```

Obs.: Demais bibliotecas utilizadas (tais como csv, random, math, argparse) fazem parte da biblioteca padrão do Python.

---

## 5. Preocupações com Segurança

Este artefato não apresenta riscos de segurança aos avaliadores. O código não executa comandos privilegiados, não acessa a rede e não manipula dados sensíveis. Todos os experimentos são executados localmente em modo usuário.

---

## 6. Instalação

1. Clone o repositório:
```bash
    git clone https://github.com/danilo-avilar/NetMaintenance.git
    cd <repositorio>
```

2. Instale as dependências:
```bash
    pip install matplotlib
```
Após esses passos, o artefato estará pronto para execução.

---

## 7. Teste Mínimo

Permite verificar rapidamente o funcionamento do simulador.

### Comando

```bash
    python3 sc.py --total_nodes 50 --active_size 4 --passive_size 6 --fail_mean 0.3 --fail_std 0.1 --max_cycles 30 --debug_nodes 0 1 2 --csv_filename res.csv --save_graphs
```
ou
```bash
    python3 sc.py --help
```
para ajuda.

### Resultado Esperado

Execução sem erros, incluindo a impressão no terminal do tempo de convergência e a geração de arquivos `.csv`, gráficos `.png` e arquivo de debug `.txt`. A presença dessas informações confirma que o artefato está funcional.

### Descrição Geral

O script `sc.py` é reponsável pela execução da simulação de funcionamento da camanda de conectividade. Cada nó da rede (simulado como um objeto `Node`) mantém duas listas dinâmicas:
- **Active View (ativos)** → vizinhos conectados diretamente, com quem o nó troca mensagens de dados.
- **Passive View (passivos)** → lista de backup de nós conhecidos, para substituir ativos que falharem.

A cada **ciclo**:
1. Cada nó envia **pings** apenas aos seus vizinhos da Active View.  
2. Nós que não respondem são removidos da Active View e substituídos por nós sorteados da Passive View.  
3. Cada nó tem uma probabilidade de falha definida a partir de uma distribuição de dados gaussiana, controlada por média e desvio padrão.
4. Uma fração (30%) da Passive View é **trocada com um vizinho ativo** (operação de *shuffle*), promovendo diversidade.  
5. Métricas são registradas e gráficos atualizados ao final de cada ciclo.

### Parâmetros importantes

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


### Modo Debug

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

### Estrutura de Saída

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

### Interpretação dos resultados
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

## 8. Experimentos e Reivindicações

Esta seção descreve como reproduzir as principais reivindicações do artigo.

### Reivindicação #1

A camada NetMaintenance mantém alta taxa de convergência sob regimes de falhas baixa a moderada.

#### Procedimento

Execute o script automatizado:
```bash
    python3 run.py
```

O script varia o número de nós da rede e o valor médio da distribuição de probabilidade de falha
$$
    \mu_f = 0.10 + (k \times 0.05),\; k \in \{0,1,\ldots,9\}
$$
e repete cada cenário **30 vezes** para cálculo de médias e desvios padrão.

Após execução, uma estrutura de diretórios é gerada de acordo com o seguinte formato:
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
   - Diretórios nXX → XX = {10, 20, ..., XX}:  quantidade de nós.
   - Subdiretórios prob0_Y → Y = {1, 2, ..., Y}: correspondem ao valor médio da probabilidade de falha {0.1, 0.2, ..., 0.Y}.
   - Subdiretórios rep_W → W = {1, 2, ..., W}: correspondem a repetição em questão do cenário de teste.
        - Dentro de cada subdiretório rep_W, os resultados obtidos a partir da execução de `sc.py` são salvos.

Em seguida, execute o script:
```bash
    python3 analysis.py
```
O script `analysis.py` produz uma visão consolidada dos resultados obtidos a partir do teste automatizado, comparando a quantidade de nós da rede vs probabilidade de falha.

O parâmetro `modo_graficos`, configurado em hardcode, permite determinar se os gráficos serão criados separados por nó (`modo_graficos = "separado"`) ou um único arquivo com todos os nós unificados (`modo_graficos = "junto"`).

#### Resultado Esperado

O arquivo `analise_resultados.csv` apresenta alta taxa de convergência (Convergiu_pct) para valores baixos e moderados da probabilidade média de falha e tempos médios de convergência compatíveis com os apresentados no artigo.

#### Estrutura de Saída

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

### Reivindicação #2

A troca parcial da lista passiva promove diversidade estrutural da vizinhança.

#### Procedimento

Durante a execução de `sc.py`, observe o gráfico `grafico_diversidade_passiva.png`. A cada ciclo, uma fração fixa (30%) da Passive View é trocada com vizinhos ativos (shuffle).

#### Resultado Esperado

Crescimento monotônico da diversidade média da lista passiva e indicação de renovação contínua de contatos, conforme discutido no artigo.

### Reivindicação #3

A recomposição da vizinhança ativa ocorre rapidamente após falhas.

#### Procedimento

Analise os aquivos `grafico_media_ativos.png` e `histograma grafico_distribuicao.png`.

#### Resultado Esperado

Recuperação rápida da média de vizinhos ativos até o valor alvo (`active_size`) e distribuição final concentrada no grau desejado.

---

## 9. Licença

Este projeto é distribuído sob a licença MIT.

---
---

Contato: danilo.avilar@ifce.edu.br
Versão: 11.0
Data: 08-01-2026
Licença: MIT