# Agente aspirador de pó do AIMA: testes e análise PEAS

Autor: André Goveia. Data: 09/09/2026.

Código analisado: implementação oficial do AIMA, repositório
[aimacode/aima-python](https://github.com/aimacode/aima-python), usada sem modificação.

---

## 1. Especificação PEAS

O AIMA traz dois ambientes de aspirador: o mundo de dois quadrados do capítulo 2 e uma grade 10×10. Os
testes usam os dois, porque a comparação entre eles é justamente o que mostra o valor da especificação
PEAS.

| PEAS | Mundo de dois quadrados | Grade 10×10 |
|---|---|---|
| Performance | +10 por sujeira aspirada, −1 por movimento, sem custo para aspirar ou ficar parado | +100 por sujeira, −1 por qualquer ação exceto ficar parado |
| Environment | dois quadrados, A e B, cada um limpo ou sujo. A sujeira não reaparece. Um agente, com posição inicial sorteada | grade 10×10 com paredes no perímetro, sujeira espalhada pelas células. Um agente |
| Actuators | Left, Right, Suck, NoOp | Suck, Forward, TurnLeft, TurnRight |
| Sensors | o par (localização, status), ou seja, o agente sabe onde está e se o quadrado está sujo | o par (status, bump), ou seja, sabe se está sujo e se bateu na parede, mas não sabe onde está |

Propriedades dos dois ambientes: parcialmente observáveis (só o quadrado atual é percebido),
determinísticos, sequenciais (a medida de desempenho acumula ao longo do tempo), estáticos, discretos e
de agente único. O caráter sequencial é o que penaliza agentes sem memória.

### Agentes testados, os quatro que o AIMA implementa para esse mundo

| Agente | Tipo (AIMA cap. 2) | Comportamento |
|---|---|---|
| Reflexo simples | reflexo simples (Fig. 2.8) | aspira se o quadrado está sujo, senão vai para o outro |
| Tabela | dirigido por tabela (Fig. 2.3) | consulta uma tabela com 10 sequências de percepções |
| Baseado em modelo | reflexo com estado interno | lembra o que já viu em A e em B, e fica parado quando os dois estão limpos |
| Aleatório | linha de base | sorteia entre Left, Right, Suck e NoOp |

## 2. Metodologia

Gerador aleatório com semente fixa e horizonte padrão de 1000 passos. O agente aleatório é a média de 30
execuções. Cada corrida registra o desempenho, o instante em que o mundo ficou limpo, o número de
movimentos, as aspiradas úteis e inúteis, e as ações gastas depois da limpeza. Os experimentos foram:

1. os 8 estados iniciais possíveis (4 configurações de sujeira × 2 posições iniciais)
2. sensibilidade ao horizonte de tempo (t = 5 até 1000)
3. comparação dos quatro agentes em 50 ambientes sorteados, com a rotina de comparação do próprio AIMA
4. traço das primeiras ações, para inspeção qualitativa
5. o mesmo agente no outro PEAS, a grade 10×10 com 10 sujeiras, em 20 repetições

## 3. Resultados

### 3.1 Desempenho nos 8 estados iniciais (1000 passos)

| Estado inicial | Reflexo | Tabela | Modelo | Aleatório | Ótimo onisciente |
|---|---:|---:|---:|---:|---:|
| A=sujo, B=sujo, início A | −978 | 19 | 19 | −478,1 | 19 |
| A=sujo, B=sujo, início B | −978 | 19 | 19 | −478,1 | 19 |
| A=sujo, B=limpo, início A | −989 | 9 | 9 | −488,1 | 10 |
| A=sujo, B=limpo, início B | −989 | 9 | 9 | −488,1 | 9 |
| A=limpo, B=sujo, início A | −989 | 9 | 9 | −488,1 | 9 |
| A=limpo, B=sujo, início B | −989 | 9 | 9 | −488,1 | 10 |
| A=limpo, B=limpo, início A | −1000 | −1 | −1 | −498,1 | 0 |
| A=limpo, B=limpo, início B | −1000 | −1 | −1 | −498,1 | 0 |
| Média | −989,00 | 9,00 | 9,00 | −488,10 | 9,50 |

A coluna "ótimo onisciente" é o que faria um agente que já conhecesse o estado dos dois quadrados.

### 3.2 Desempenho médio por horizonte de tempo

| Agente | t=5 | t=10 | t=50 | t=100 | t=500 | t=1000 |
|---|---:|---:|---:|---:|---:|---:|
| Reflexo simples | 6,0 | 1,0 | −39,0 | −89,0 | −489,0 | −989,0 |
| Tabela | 9,0 | 9,0 | 9,0 | 9,0 | 9,0 | 9,0 |
| Baseado em modelo | 9,0 | 9,0 | 9,0 | 9,0 | 9,0 | 9,0 |
| Aleatório | 2,9 | 2,0 | −15,6 | −40,4 | −238,5 | −488,1 |

### 3.3 Traço das primeiras ações, com A e B sujos e início em A

Ação escolhida em cada passo, precedida do quadrado em que o agente estava.

| Agente | 1 | 2 | 3 | 4 | 5 | 6 | Depois disso |
|---|---|---|---|---|---|---|---|
| Reflexo | A Suck | A Right | B Suck | B Left | A Right | B Left | segue oscilando entre A e B |
| Tabela | A Suck | A Right | B Suck | B nada | B nada | B nada | fica inerte, a tabela acabou |
| Modelo | A Suck | A Right | B Suck | B NoOp | B NoOp | B NoOp | fica em NoOp por decisão |
| Aleatório | A Suck | A Left | A Left | A Left | A Right | B Right | continua sorteando ações |

Os três primeiros agentes deixam o mundo limpo no passo 3. O aleatório aspira A no passo 1 e só volta a
aspirar B no passo 31, nessa semente. "nada" significa que o agente não escolheu ação alguma, que é o
que acontece quando a consulta à tabela falha.

### 3.4 Trocando o PEAS: o mesmo agente na grade 10×10

| Agente | Desempenho | Sujeiras limpas |
|---|---:|---:|
| Reflexo simples do AIMA, feito para o mundo de dois quadrados | −1000,0 | 0,00 de 10 |
| Agente reflexo reescrito para a percepção (status, bump) | −445,0 | 5,55 de 10 |

O segundo agente não vem do AIMA, foi escrito para este trabalho com a mesma ideia reflexa, só que
adaptada à nova percepção.

## 4. Análise

### 4.1 A medida de desempenho define a racionalidade (P)

O agente reflexo limpa o mundo tão rápido quanto o melhor agente possível (o instante em que o mundo
fica limpo é idêntico ao do agente com modelo nos 8 casos), mas continua oscilando entre A e B para
sempre: de 998 a 1000 movimentos, dos quais cerca de 99% acontecem depois que tudo já está limpo. Como a
medida de desempenho cobra −1 por movimento, ele perde 1 ponto por passo, o que explica a queda linear
da tabela 3.2 e a média de −989. Ele não é burro, é ótimo para outra medida de desempenho: se o placar
contasse apenas a sujeira removida, ou se houvesse desligamento automático, o mesmo comportamento seria
racional. Vale notar que em t=5 ele é o melhor de todos (6,0 pontos), ou seja, a racionalidade também
depende do horizonte de tempo contratado.

### 4.2 Sensores limitados custam pontos: racionalidade não é onisciência (S)

O agente com modelo obtém 9,00 contra 9,50 do ótimo onisciente. A diferença de 0,5 ponto aparece só nos
casos em que o outro quadrado já estava limpo (linhas 3, 6, 7 e 8 da tabela 3.1): como o sensor enxerga
apenas o quadrado atual, o agente precisa gastar um movimento para descobrir que não há nada a fazer.
Esse é o preço da observabilidade parcial, não um defeito do agente. Dada a percepção disponível, o
comportamento dele é o melhor possível.

### 4.3 Memória torna tratável um ambiente sequencial

A única diferença entre o agente reflexo e o baseado em modelo é lembrar o que foi visto em cada um dos
dois quadrados e poder ficar parado, e isso vale 998 pontos de desempenho (de −989 para +9). Em ambiente
sequencial e parcialmente observável, estado interno não é luxo.

### 4.4 O agente da tabela empata, mas por acidente

A tabela do AIMA cobre apenas sequências de até 3 percepções. Da quarta em diante a consulta falha, o
agente não escolhe ação alguma e fica inerte, como se vê no traço da seção 3.3. Como nesse ambiente uma
ação desconhecida não tem efeito nem custo, ficar inerte imita o NoOp e o placar coincide com o do
agente baseado em modelo. Bastaria cobrar por ação inválida, ou deixar a sujeira reaparecer, para o
empate desaparecer. A abordagem também não escala: com 4 percepções distintas, uma tabela completa para
T passos exigiria a soma de 4^t entradas, cerca de 1,4 milhão para T=10, enquanto a do AIMA tem 10.

### 4.5 Trocar o ambiente invalida o agente (A e E)

Na grade 10×10 a percepção passa a ser o par (status, bump), sem localização. O agente reflexo do AIMA,
que espera receber (localização, status), lê o valor de sujeira como se fosse a localização, não casa
com nenhuma das suas regras e não escolhe ação alguma a cada passo. Como aqui a medida de desempenho
cobra por toda ação diferente de ficar parado, ele termina com −1000 pontos e zero sujeira removida.
Reescrito para a nova percepção (aspirar se sujo, girar se bateu, senão andar), o mesmo esquema reflexo
limpa 5,55 das 10 sujeiras, mas ainda com desempenho negativo (−445), porque sem mapa nem memória a
busca aleatória paga 1000 ações por 555 pontos de limpeza. No ambiente maior, a falta de estado interno
volta a ser o gargalo.

A comparação em 50 ambientes sorteados confirma o mesmo ranking do mundo de dois quadrados: −990,32 para
o reflexo, 7,80 para a tabela, 7,80 para o baseado em modelo e −488,04 para o aleatório.

## 5. Conclusão

Os testes reproduzem quantitativamente três teses do capítulo 2 do AIMA. Primeiro, PEAS não é
formalidade: o mesmo agente vale 6 ou −989 pontos conforme a medida de desempenho e o horizonte, e vale
−1000 se o par sensores e atuadores mudar. Segundo, estado interno paga: são 998 pontos de diferença
entre lembrar e não lembrar o que já foi visto. Terceiro, racionalidade não é onisciência: o agente
racional perde 0,5 ponto por ser obrigado a explorar e ainda assim é o melhor possível para os sensores
que tem. O agente baseado em modelo é o único que atinge o ótimo alcançável nos 8 estados iniciais e o
único cujo desempenho não se degrada com o tempo, sendo a escolha correta para o PEAS especificado.
