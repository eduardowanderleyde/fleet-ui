# Conhecimento acumulado: Bugs e configuração do SLAM Toolbox

## TL;DR

Pesquisamos as três perguntas originais (2026-10-02), direto no GitHub
oficial do SLAM Toolbox. Resumo em português simples:

1. **Buffer de TF do consumidor após restart**: o SLAM Toolbox já é um
   lifecycle node nativo (desde 2024) e reseta parte do próprio estado
   interno ao reativar, mas isso é o estado *dele*, não o buffer de TF
   de quem consome (o orquestrador do fleet-ui). Não existe config
   nativa que resolva isso do lado do consumidor — o reset manual do
   buffer que já fazemos (`_reset_robot_pose_tracking`) continua sendo
   o caminho certo, sem alternativa documentada.
2. **Timestamp "velho demais" depois do restart**: existe um parâmetro,
   `restamp_tf`, que parece feito exatamente pra esse tipo de problema
   (troca o timestamp do TF publicado pelo tempo atual em vez do
   timestamp do scan). Mas achamos um issue aberto e não resolvido de
   outro usuário mostrando que `restamp_tf: true` **não** garantiu a
   solução — então isso é uma hipótese a testar, não um substituto
   comprovado do reset manual de buffer que já usamos.
3. **Sinal de "pronto" sem esperar 8s fixos**: não existe um
   serviço/tópico oficial de "mapa->odom já está válido". Mas o nó
   publica `/pose` e eventos (`/slam_toolbox/new_node_event`,
   `/slam_toolbox/loop_closure_event`) que dão um sinal baseado em
   evento (esperar a primeira mensagem) em vez de um atraso fixo —
   ainda não testado nem implementado.
4. **Multi-robô na mesma máquina**: o SLAM Toolbox usa tópicos globais
   (`/scan`, `/map`) **por decisão de design**, não por bug — o
   mantenedor confirmou isso em 2023 e disse que não vai mudar. Pra
   multi-robô é preciso remapear os tópicos manualmente no launch.
   **Não achamos nenhuma issue ou relato confirmando conflito de
   performance/recursos** ao rodar várias instâncias na mesma máquina
   — essa pergunta específica continua sem resposta.
5. Achado lateral interessante: o próprio SLAM Toolbox teve, em agosto
   de 2026, um bug real de estado que não resetava direito numa
   transição de lifecycle (pausa que "trava" silenciosamente depois de
   reativar) — corrigido no código mas ainda não lançado em nenhum
   release. É o mesmo tipo de problema (estado preso após reativação)
   que já documentamos e corrigimos no nosso lado, só que dentro do
   próprio SLAM Toolbox.

Este arquivo é mantido pelo agente `experiment-slam-toolbox-tracking`
(`.claude/agents/experiment-slam-toolbox-tracking.md`) — cada execução lê
isto primeiro, pesquisa o que falta, e acrescenta achados novos abaixo,
sem apagar o que já existe.

## Achados

### 2026-10-02

- **Lifecycle node nativo existe desde 2024, mas não cobre o buffer do
  consumidor.** PR
  [#561 "Convert nodes to lifecycle nodes"](https://github.com/SteveMacenski/slam_toolbox/pull/561)
  (merged 2024-01-04, branch `ros2`) converteu os nós do SLAM Toolbox
  pra `LifecycleNode` de verdade, com reset de threads e do
  `loop_closure_assistant` em `on_activate`/`on_deactivate`. Confirmado
  lendo a mensagem de commit real via API do GitHub. Isso resolve o
  estado *interno* do SLAM Toolbox, não o `tf2_ros.Buffer` de quem
  consome a TF (nosso orquestrador) — não achei nenhum mecanismo nativo
  do lado do SLAM Toolbox que avise o consumidor "limpa seu buffer, eu
  reiniciei". Conclusão: nossa solução atual
  (`_reset_robot_pose_tracking` antes de reativar) não tem substituto
  documentado — é mesmo responsabilidade da aplicação consumidora.

- **Bug real recente e muito parecido com o nosso, mas dentro do SLAM
  Toolbox.** Issue
  [#884](https://github.com/SteveMacenski/slam_toolbox/issues/884)
  ("`PausedState state_` survives lifecycle transitions and desyncs
  from `paused_new_measurements`, leaving the node silently paused"),
  aberta 2026-08-13 e fechada 2026-08-17, reproduzida em ROS 2 Jazzy
  com o binário oficial `ros-jazzy-slam-toolbox` 2.8.5. Rodando como
  lifecycle node sob o `lifecycle_manager` do Nav2, o ciclo
  `deactivate → cleanup → configure → activate` deixava o nó
  "silenciosamente" preso descartando scans, mesmo o parâmetro
  reportando que não estava mais pausado. Corrigido pelas PRs
  [#885 (branch `jazzy`)](https://github.com/SteveMacenski/slam_toolbox/pull/885),
  #886 (branch principal) e #887 (branch `lyrical`), todas merged em
  2026-08-17. **Importante**: o release mais recente pra Jazzy
  (`2.8.5`, publicado 2026-04-29, confirmado via API de releases do
  GitHub) é de ANTES desse fix — ou seja, quem instala via apt ainda
  não tem essa correção. Não é o mesmo bug que documentamos (o nosso é
  no buffer de TF do consumidor, este é no `paused_new_measurements`
  interno do SLAM Toolbox), mas é evidência de que "estado que não
  reseta direito numa transição de lifecycle, travando silenciosamente
  depois de reativar" é um padrão de bug conhecido e recorrente no
  próprio projeto — reforça a plausibilidade da nossa hipótese, sem
  provar que o bug seja o mesmo.

- **Parâmetro `restamp_tf` existe pro problema de timestamp antigo, mas
  tem tensão com um relato de usuário que não conseguiu resolver com
  ele.** Confirmado no README oficial
  (`SteveMacenski/slam_toolbox`, branch `ros2`): `restamp_tf` — "Whether
  to restamp the TF messages with the current time or use the scan's
  message. Default False." Isso é exatamente o tipo de ajuste que
  poderia ajudar no cenário "buffer antigo rejeita dado novo com
  timestamp mais baixo do SLAM recém-reiniciado". **Mas** issue
  [#799](https://github.com/SteveMacenski/slam_toolbox/issues/799)
  ("Unable to map offline, timestamp earlier than all data in
  transform cache", aberta 2025-08-01, sem resolução até hoje) mostra
  um usuário que tentou `restamp_tf: true` e ainda assim bateu no mesmo
  tipo de erro. Issue
  [#717](https://github.com/SteveMacenski/slam_toolbox/issues/717)
  ("TF timestamp problem", também sem resolução) mostra histórico de
  que trocar pra usar `now()` em vez do timestamp do scan já causou
  problemas de localização em outro contexto. **Registro como achado
  em tensão com a decisão já tomada**: `restamp_tf` é candidato a
  testar no nosso setup, mas não é uma solução comprovada — não
  substitui o reset manual de buffer sem validação própria.

- **Não existe sinal oficial de "mapa→odom pronto", mas há tópicos de
  evento que podem substituir o atraso fixo de 8s.** Confirmado no
  README oficial: tópicos publicados incluem `pose`
  (`geometry_msgs/PoseWithCovarianceStamped`),
  `/slam_toolbox/new_node_event` (`slam_toolbox/NewNodeEvent`,
  disparado a cada nó novo no pose-graph) e
  `/slam_toolbox/loop_closure_event`. Não há serviço nem tópico
  documentado que sirva estritamente como "sinal de pronto" pra TF
  map→odom. **Ação sugerida** (não implementada por mim): trocar o
  `TimerAction` fixo de 8s por uma espera orientada a evento — assinar
  `/pose` (ou `/slam_toolbox/new_node_event`) com timeout e seguir no
  primeiro valor recebido, em vez de confiar num atraso fixo.

- **Tópicos globais em multi-robô são decisão de design confirmada pelo
  mantenedor, não bug.** Issue
  [#620 "Poor Topic Namespacing Practices"](https://github.com/SteveMacenski/slam_toolbox/issues/620)
  (aberta 2023-06-29, fechada no mesmo dia). O autor relatou que
  `/scan`, `/map`, `/map_metadata` usam caminho absoluto por padrão, o
  que colide entre robôs num setup multi-robô. Resposta do mantenedor
  (Steve Macenski), citação real confirmada via API: "They can still
  be just as easily remapped, but they're set in the global namespace
  so you can namespace slam toolbox without the main topics
  disconnecting. [...] Given this is how its been for ~5 years, I'm
  hesitant to changing it". Ou seja: **não vai mudar o default**, o
  caminho é remapear explicitamente `scan_topic` e os demais tópicos
  por robô no launch. Confirmado também no README atual: "`scan_topic`
  - scan topic, *absolute* path, i.e. `/scan` not `scan`" — documentado
  como comportamento intencional. Ação sugerida: conferir se o launch
  multi-robô do fleet-ui já remapeia esses tópicos explicitamente por
  namespace (não depender do push-down automático de namespace do
  ROS 2 pra esses tópicos específicos).

- **Não confirmado**: conflito de performance/recursos ao rodar várias
  instâncias de SLAM Toolbox (uma por robô, namespaced) na mesma
  máquina. Pesquisei via WebSearch e via busca de issues no GitHub
  oficial (`SteveMacenski/slam_toolbox`) e não encontrei nenhuma issue,
  PR ou relato que confirme ou documente esse tipo de problema
  especificamente. A issue mais próxima em tema,
  [#645 "Multi robot environment not working"](https://github.com/SteveMacenski/slam_toolbox/issues/645)
  (aberta 2023-11-08), foi fechada pelo mantenedor no mesmo dia só com
  "Please don't cross post with question sites" — sem conteúdo técnico,
  não serve como resposta. Pergunta permanece aberta pra próximas
  execuções.

- **Releases recentes confirmados via API do GitHub** (não inventados):
  `2.8.0` (2024-06-24, "Initial Jazzy release"), `2.8.1` (2024-06-25),
  `2.8.2` (2024-12-13), `2.8.3` (2025-04-15), `2.8.4` (2026-01-24),
  `2.8.5` (2026-04-29, release Jazzy mais recente até hoje), `2.9.0`
  (2025-05-29, primeiro release Kilted), `2.10.0` (2026-07-21, primeiro
  release do novo distro "Lyrical" — confirmei que a branch `lyrical`
  existe de fato no repositório, não é invenção). Não consegui ler o
  changelog detalhado de cada versão (página de release não carregou o
  texto completo na ferramenta de fetch) — fica pendente pra uma
  próxima execução conferir item a item se há algo relevante além do
  que já registrado aqui sobre `paused_new_measurements`.

### Ação sugerida (resumo, não implementada)

1. Não alterar o reset manual de buffer no orquestrador — não há
   alternativa nativa documentada do lado do SLAM Toolbox.
2. Testar `restamp_tf: true` isoladamente como experimento, sabendo que
   não é garantia (achado em tensão, ver acima) — não trocar a
   mitigação atual sem validar.
3. Avaliar substituir o `TimerAction` de 8s por uma espera orientada a
   evento na primeira mensagem de `/pose` (ou
   `/slam_toolbox/new_node_event`), com timeout de segurança.
4. Conferir se o launch multi-robô remapeia `scan_topic` (e `/map`,
   `/map_metadata` se aplicável) explicitamente por namespace — o
   default global é intencional e não vai mudar.
5. Verificar qual versão do SLAM Toolbox está instalada no ambiente do
   projeto; se for `<= 2.8.5` e o orquestrador usar
   `pause_new_measurements`, há um bug conhecido (#884) ainda sem
   release — considerar build from source do branch `jazzy` se isso
   afetar o experimento.
