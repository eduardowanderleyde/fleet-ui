# Design

## Context

`backend/main.py` (`_read_robot_roles`, linha 638) já lê `roles.yaml` e
documenta em comentário que só MUUT deveria aceitar comandos de movimento,
mas nenhum endpoint aplica isso. `roles.yaml` hoje declara tb1/tb2/tb3
todos como MUUT, com o papel original (tb2=FUUT, tb3=SU) só em comentário.
A infraestrutura de ativação sequencial (`activate_robot_nav.launch.py`,
`_deactivate_robot_nav`) já permite ligar Nav2 de um robô por vez — basta
não chamar ativação pro robô que deve ficar FUUT.

`backend/agents/fuut_verify.py` (construído nesta sessão) já recebe uma
`FuutObservation` pré-processada (distância/direção/instante de um
obstáculo transitório) e julga corroboração contra uma `MuutClaim` via
TypeSafe. Deliberadamente **não** faz detecção de robô em LiDAR bruto —
isso ainda não existe em lugar nenhum do projeto.

## Goals / Non-Goals

**Goals:**
- Papel FUUT/SU passa a restringir comandos de movimento de fato.
- Uma campanha piloto pequena (N=3-5) produz observação real do FUUT,
  cruzada com a pose reivindicada pelo MUUT, via `FuutVerifier`.

**Non-Goals:**
- Detecção robusta de robôs em LiDAR bruto (classificação, tracking
  multi-objeto). Este piloto usa subtração de referência estática
  (explicado em Decisões) — suficiente pra um obstáculo transiente único
  num cenário estático, não um detector geral.
- Validar estatisticamente a precisão do FuutVerifier — é piloto, não
  campanha com poder amostral.
- Hardware real — continua em simulação Gazebo, como o resto da avaliação
  empírica desta dissertação.

## Decisions

**1. Onde aplicar o enforcement de papel.**
Um único helper (`_require_muut(robot_id)`) chamado no topo de cada
endpoint que hoje despacha movimento (`/api/agent/run`,
`/api/agent/run_fleet`, serviços de record/replay), levantando HTTP 403
com o papel declarado no corpo do erro. Alternativa descartada: checar
papel dentro de cada serviço ROS 2 individualmente — mais espalhado, mais
difícil de testar de forma unificada.

**2. Fonte da pose reivindicada pelo MUUT (`MuutClaim`).**
Usar `/pose` (corrigida por SLAM), não `/odom` nem o *ground truth* do
Gazebo. `/odom` tem erro maior em rotas longas (até 14,27cm medido na
Seção de Fonte de Trajetória) e não é o que o MUUT usaria num cenário sem
simulador. *Ground truth* foi descartado porque usá-lo como a própria
reivindicação do MUUT tornaria a verificação circular — o valor do FUUT é
ser uma fonte **independente** do que o MUUT já sabe de si mesmo via SLAM,
não uma segunda comparação contra o mesmo *ground truth* já medido na
Seção~\ref{sec:res_fonte_trajetoria}.

**3. Fonte da observação do FUUT (`FuutObservation`).**
Subtração de referência: antes do MUUT entrar em cena, o FUUT (parado)
grava um scan de referência do ambiente vazio. Durante cada réplica,
pontos do scan vivo que divergem do scan de referência por mais que o
raio do TurtleBot4 (~0,17m) são agrupados; o centróide do maior cluster
nessa janela de tempo se torna `distance_m`/`bearing_deg`. Alternativa
descartada: detecção/classificação geral de objetos — overscoped pra um
piloto, e já descartada deliberadamente no próprio `fuut_verify.py`.

**4. Alinhamento temporal.**
Casar o scan do FUUT com a pose do MUUT por vizinho mais próximo dentro de
200ms. Réplica sem observação do FUUT dentro dessa janela é reportada como
"sem correspondência" (já coberto pela spec), não descartada em silêncio.

**5. Tamanho do piloto.**
N=3-5 réplicas. Não é a campanha quantitativa formal — é o primeiro dado
empírico que a dissertação pode citar como "evidência preliminar" em vez
de "zero evidência".

## Risks / Trade-offs

- [Risco] Subtração de referência pode confundir ruído de sensor com o
  obstáculo real → Mitigação: cenário estático (mesma suposição que o
  protocolo já assume em toda a dissertação), limiar de distância
  calibrado manualmente na primeira réplica, documentado como calibração
  informal, não um detector validado.
- [Risco] Enforcement de papel pode quebrar fluxos que hoje mandam tb2/tb3
  navegar como MUUT (demos, testes) → Mitigação: `roles.yaml` só muda
  (tb2=FUUT) durante a execução do script do piloto; reverte depois.
- [Risco] `FuutVerifier` depende de `TYPESAFE_API_KEY` (API externa paga),
  que precisa ser reexportada em todo novo shell desta sessão → Mitigação:
  documentar como pré-requisito explícito em tasks.md.
- [Risco] Geometria assume a pose do próprio FUUT conhecida com precisão
  → Mitigação: ler a pose de spawn do FUUT do launch/world do Gazebo, não
  estimar.

## Migration Plan

Não há migração de usuários — é um script de experimento novo. Rollback é
trivial: reverter `roles.yaml` pro estado atual (todos MUUT) e remover o
helper de enforcement se ele causar atrito inesperado em algum fluxo
existente (improvável, já que só restringe, nunca muda o comportamento de
um robô MUUT).
