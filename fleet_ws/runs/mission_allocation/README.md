# Estudo de alocação de missão multi-robô (Fase 1, sem simulador)

Dados brutos dos estudos de 2026-10-13. Cada pasta tem `summary.json`
(agregado + proveniência: commit, argumentos, linha de comando) e
`runs.jsonl` (uma alocação por linha, com plano, custo, problemas, modelo que
respondeu, tokens, latência e a justificativa do LLM).

Pergunta: quando a missão chega em linguagem natural, quem distribui melhor as
zonas entre os robôs MUUT — e quem decide de forma repetível? Alocadores:
`fixed` (zona i → robô i mod N, o despacho do painel Missão Coordenada),
`greedy`, `optimal` (busca exaustiva, referência) e o Claude (`claude-opus-5-5`,
effort `medium`, sem controle de temperatura): `llm` recebe o texto, as zonas,
os robôs e (no cenário difícil) uma descrição do mapa; `llm_dist` recebe também
a tabela de distâncias. Custo da missão = makespan (maior distância de um robô).

| Pasta | Cenário | Commit | Repetições LLM | Chamadas | Custo aprox. |
|---|---|---|---|---|---|
| `01_simples_20261013T130646Z` | `warehouse.yaml` — 2 MUUT + 1 FUUT, 5 missões, distância em linha reta | `1907edf` | 10 | 100 | US$ 3,17 |
| `02_dificil_20261013T134805Z` | `warehouse_dificil.yaml` — 3 MUUT + 1 FUUT, 10 missões, distância pelo caminho no mapa | `344f366` | 5 | 100 | US$ 4,12 |
| `03_dificil_corrigido_20261013T141704Z` | idem, após corrigir a ambiguidade abaixo; só as 4 missões afetadas | `318eb37` | 5 | 40 | US$ 1,67 |

Reproduzir (da raiz do repositório, com `ANTHROPIC_API_KEY` definida e o
commit indicado em checkout):

```bash
python fleet_ws/scripts/mission_allocation_study.py --repeat 10                      # 01
python fleet_ws/scripts/mission_allocation_study.py --repeat 5 \
  --scenario backend/mission/scenarios/warehouse_dificil.yaml                         # 02 / 03
```

## Correção no meio do estudo (registrar no texto)

Na rodada 02, as missões `e2`, `o3`, `l2` e `f1` falavam em "corredores entre
as estantes do sul" e o gabarito incluía o corredor leste. Três estantes formam
só dois corredores *entre* elas; o leste fica *ao lado* da terceira. O LLM
excluiu o corredor leste com justificativa correta, e o erro era do gabarito.
O commit `318eb37` passou a definir nas notas do mapa "os três corredores do
sul" (oeste, central, leste) e reescreveu essas quatro missões; a rodada 03
refaz só elas. A mesma correção alterou as notas do mapa que entram no prompt
das outras seis missões, cujos dados continuam vindo da rodada 02 (prompt com a
redação antiga das notas, sem mudança de zonas, robôs ou distâncias).

## Resultado consolidado

Cenário difícil = rodada 02 para `e1, o1, o2, l1, f2, p1` + rodada 03 para
`e2, o3, l2, f1`.

| | Simples (5 missões) | Difícil (10 missões) |
|---|---|---|
| `fixed` (painel atual): pior caso acima do ótimo | +42,3% | +105,9% |
| `greedy`: pior caso | +28,9% | +56,8% |
| `llm`: alocações válidas | 50/50 | 50/50 |
| `llm`: no ótimo | 50/50 | 35/50 |
| `llm`: pior caso | 0% | +53,7% |
| `llm`: missões com a mesma alocação em todas as repetições | 5/5 | 5/10 |
| `llm_dist`: no ótimo | 50/50 | 50/50 |
| `llm_dist`: missões com a mesma alocação em todas as repetições | 5/5 | 9/10 (a outra varia só entre planos de mesmo custo) |
| Usou robô FUUT ou indisponível | nunca | nunca |

Cenário difícil, por missão (`llm` sem tabela de distâncias):

| Missão | Categoria | No ótimo | Alocações distintas | Pior caso |
|---|---|---|---|---|
| e1 todas as 9 zonas | escala | 3/5 | 3 | +0,7% |
| e2 cinco zonas | escala | 3/5 | 3 | +2,1% |
| o1 doca de carga | obstáculo | 5/5 | 1 | 0% |
| o2 sala noroeste | obstáculo | 3/5 | 2 | +53,7% |
| o3 três corredores do sul | obstáculo | 5/5 | 1 | 0% |
| l1 "tudo ao norte da estante" | linguagem | 0/5 | 1 | +53,7% |
| l2 negação ("exceto o fechado") | linguagem | 5/5 | 1 | 0% |
| f1 tb2 falhou no meio | falha | 2/5 | 2 | +32,5% |
| f2 tb1 travou | falha | 5/5 | 1 | 0% |
| p1 FUUT ao lado das zonas | papel | 4/5 | 2 | +7,3% |

Leitura: o LLM interpretou corretamente todas as missões (zonas pedidas,
negação, falha, papéis), mas, sem as distâncias reais, errou alocações em que
o robô mais perto em linha reta é o mais longe pelo caminho (o2, l1) e deu
respostas diferentes para a mesma missão em 5 de 10 casos. Com a tabela de
distâncias, ficou no ótimo em todas as 50 chamadas.

Limitações: decisão apenas (sem execução no Gazebo); distância pelo grid do
`warehouse.pgm` (não o planejador do Nav2); um ambiente; 5 repetições no
cenário difícil.
