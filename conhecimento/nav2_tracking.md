# Conhecimento acumulado: Issues e tuning do Nav2/MPPI

## TL;DR

Este arquivo é mantido pelo agente `experiment-nav2-tracking`
(`.claude/agents/experiment-nav2-tracking.md`) — cada execução lê isto
primeiro, pesquisa o que falta, e acrescenta achados novos abaixo, sem
apagar o que já existe.

Resumo em linguagem simples (2026-10-02):

- Das 3 issues que motivaram usar o pacote mínimo (`nav2_minimal_tb4_sim`)
  em vez do bringup padrão do fabricante: uma (#81) foi corrigida de
  verdade pela iRobot/Clearpath; uma (#563) foi fechada só por falta de
  resposta, não por conserto confirmado; e a mais nova e mais parecida
  com o nosso caso (#94, Gazebo Sim + Jazzy) continua aberta e sem
  solução há mais de um ano. Ou seja: a decisão de usar o pacote mínimo
  continua justificada, não ficou obsoleta.
- Achado mais importante e **em tensão com o que já aceitávamos**: o
  Nav2 oficial recomenda `regenerate_noises: false` como padrão (menos
  "tremedeira" de CPU, funciona bem). O arquivo de configuração do
  próprio fabricante TurtleBot4 troca isso pra `true` — ou seja, parte
  da aleatoriedade do MPPI que a gente vinha tratando como "preço a
  pagar, não dá pra mudar" na verdade É uma escolha do TB4 que pode ser
  testada (voltar pro `false` padrão do Nav2) sem trocar de
  controlador. Não decidi mudar nada — é um experimento candidato pra
  quem conduz o experimento de repetibilidade avaliar.
- O time do Nav2 já tentou (e abandonou, com benchmarks que mostraram
  piora, não melhora) uma forma mais sofisticada de reduzir a
  aleatoriedade do MPPI ("ruído colorido"/filtro passa-baixa baseado em
  paper da ICRA 2026). Não existe hoje uma alternativa madura e testada
  upstream pra isso — reforça que o nosso caminho prático é o
  `regenerate_noises` acima, não esperar uma funcionalidade nova.
- Há trabalho recente (meados de setembro de 2026) do Nav2 pra juntar
  vários "lifecycle managers" em um só, reduzindo CPU gasto com
  heartbeats — parecido em espírito com o que a gente já fez (reduzir de
  10 pra 7 nós no `nav2_minimal.launch.py`), mas isso só está no branch
  `main` (futuro), ainda não chegou no Jazzy que usamos.

## Achados

### 2026-10-02 — Issue #81 (turtlebot4_simulator): corrigida upstream, mas é sobre o bringup do fabricante, não o nosso pacote mínimo

- **Fonte:** https://github.com/turtlebot/turtlebot4_simulator/issues/81
  (estado: `closed`, fechada em 2025-03-06)
- Título: "Failed to activate controller - joint_state_broadcaster and
  diffdrive_controller" (`ros2 launch turtlebot4_ignition_bringup
  turtlebot4_ignition.launch.py`).
- Causa raiz identificada nos comentários (civerachb-cpr, Clearpath,
  2024-10-29/2024-11-12): uma mudança no `ros_control` passou a impor
  timeout fixo de 5s pra ativar um controller. Se o Gazebo
  (Ignition/Fortress, na época da issue) inicia **pausado**, os
  controllers tentam ativar antes da simulação rodar de fato e dão
  timeout.
- Fix: adicionar a flag `-r` (roda a simulação já iniciada) no
  `ign_args` do launch file do fabricante. Aplicado também ao branch
  Jazzy do `turtlebot4_simulator` (comentário de civerachb-cpr) e
  liberado nos pacotes Debian do Humble em março/2025
  (https://github.com/turtlebot/turtlebot4_simulator/pull/83).

**Ação sugerida:** essa issue é sobre `turtlebot4_ignition_bringup` (o
bringup padrão do fabricante), não sobre o `nav2_minimal_tb4_sim` que
este projeto usa — corrigir essa issue não torna nossa escolha de pacote
mínimo obsoleta por si só, porque a #94 (abaixo) continua aberta. Não
mudar nada agora; só registrar que pelo menos essa classe específica de
falha (controller ativando antes do sim rodar) tem conserto conhecido,
caso o time reavalie voltar ao bringup padrão no futuro.

### 2026-10-02 — Issue #94 (turtlebot4_simulator): ainda aberta, é a mais parecida com nosso caso (Jazzy + Gazebo Sim)

- **Fonte:** https://github.com/turtlebot/turtlebot4_simulator/issues/94
  (estado: `open`, criada 2025-06-16, última atividade 2025-06-23 — mais
  de um ano sem resposta da iRobot/Clearpath até a data desta pesquisa)
- Título: "DiffDriveController ignoring messages with timeout". Sintoma:
  no Gazebo Sim (não Ignition/Fortress) com ROS 2 Jazzy, mensagens
  `Twist` chegam no `diffdrive_controller` com timestamp considerado
  "velho demais" (mais de 0.5s de diferença do tempo atual), e são
  descartadas — robô não anda, ou anda alguns centímetros e trava.
  Relator já suspeita de problema de clock no Gazebo.

**Ação sugerida:** continua sendo a justificativa mais forte e atual
pra manter o bridge próprio do `nav2_minimal_tb4_sim` (usa `Twist` sem
stamp) e o override `enable_stamped_cmd_vel: false` já aplicado em
`fleet_ws/src/fleet_orchestrator/config/nav2_minimal_override.yaml` —
não reverter essa escolha. Nenhuma ação de código sugerida (eu não
alterei nada fora de `conhecimento/nav2_tracking.md`).

### 2026-10-02 — Issue #563 (turtlebot/turtlebot4, repo diferente de turtlebot4_simulator): fechada por inatividade, não por conserto confirmado

- **Fonte:** https://github.com/turtlebot/turtlebot4/issues/563 (estado:
  `closed`, fechada em 2025-04-14 — mas pelo mantenedor citando
  "closing due to inactivity", sem confirmação do relator de que o
  problema foi resolvido)
- Título: "Failed to activate Controller : diffdrive_controller". Mesmo
  tipo de sintoma do #81 (`Switch controller timed out after 5.000000
  seconds!`), em Humble, via `turtlebot4_ignition_bringup`.
- Nota de precisão: o comentário em
  `fleet_ws/src/fleet_orchestrator/launch/turtlebot4_sim.launch.py`
  cita "#81, #94, #563" como se fossem do mesmo repositório; na
  verdade #81 e #94 são de `turtlebot/turtlebot4_simulator`, e #563 é de
  `turtlebot/turtlebot4` (repo separado, mesma organização GitHub).

**Ação sugerida:** não tratar como "resolvida" — é um fechamento
administrativo por falta de resposta, não um fix verificado nesta
issue especificamente (a causa raiz provável é a mesma do #81, essa sim
corrigida — ver achado acima). Nenhuma mudança de código feita.

### 2026-10-02 — TENSÃO com decisão aceita: `regenerate_noises: true` não é o default do Nav2, é override do TurtleBot4

- **Fontes:**
  - Documentação oficial, branch Jazzy:
    https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/mppi_controller/configuring_mppic/
  - Arquivo local confirmado neste sistema:
    `/opt/ros/jazzy/share/turtlebot4_navigation/config/nav2.yaml`, linha
    64 (lido e usado por
    `fleet_ws/src/fleet_orchestrator/launch/turtlebot4_sim.launch.py`,
    função `_make_nav2_params`).
- A documentação oficial do Nav2 (Jazzy) diz: `regenerate_noises`
  (bool) tem **default `false`**, e descreve: "Practically, this is
  found to work fine since the trajectories are being sampled
  stochastically from a normal distribution and reduces compute
  jittering at run-time due to thread wake-ups to resample normal
  distribution." Ou seja: o próprio Nav2 recomenda NÃO regenerar o
  ruído a cada ciclo.
  - Em linguagem simples: por padrão, o Nav2 sorteia o "ruído" do MPPI
    uma vez só (na inicialização) e reaproveita, porque isso funciona
    bem e evita picos de uso de CPU. Regenerar o ruído a cada ciclo
    (20Hz) é a opção NÃO recomendada por padrão.
  - O `nav2.yaml` do pacote `turtlebot4_navigation` (o que este projeto
    lê como base) define explicitamente `regenerate_noises: true`
    (linha 64) — ou seja, troca o padrão recomendado do Nav2 pelo modo
    que regenera ruído todo ciclo. Essa é a fonte da estocasticidade
    por ciclo que o agente deste projeto já documentava como "por
    design, aceita, não é bug" — mas na verdade é uma escolha do
    **fabricante TurtleBot4**, não do Nav2 em si, e vai contra o
    default/recomendação oficial.
- Isso responde diretamente a uma das perguntas que motivou este
  agente ("existe tuning documentado de MPPI pra reduzir a
  estocasticidade sem trocar de controlador, tipo `regenerate_noises:
  false`, com trade-off conhecido?"): **sim, existe, é literalmente o
  default oficial do Nav2**, e o trade-off documentado é só menos
  "jitter" de CPU (não há menção de perda de qualidade de navegação).

**Isto está em tensão com a decisão já documentada do projeto de tratar
a estocasticidade do MPPI como "fonte de variância aceita, não um
bug/trade-off ajustável". Não decidi sozinho mudar nada.**

**Ação sugerida (experimento, não mudança de código por este agente):**
quem conduz o experimento de repetibilidade pode rodar um teste
controlado (mesmo N de execuções já usado) comparando
`regenerate_noises: true` (atual, herdado do TB4) vs. `false` (default
do Nav2) via override em
`fleet_ws/src/fleet_orchestrator/config/nav2_minimal_override.yaml`
(mesmo mecanismo já usado lá pra `enable_stamped_cmd_vel`), medindo se a
variância de repetibilidade cai. Resultado desconhecido — não assumir
que vai ajudar, só que é uma hipótese testável e barata.

### 2026-10-02 — Nav2 já tentou reduzir a estocasticidade do MPPI de forma mais sofisticada e abandonou (benchmarks mostraram piora)

- **Fonte principal:** https://github.com/ros-navigation/navigation2/pull/6151
  (estado: `closed`, não mergeada, fechada em 2026-07-02) e a cadeia
  anterior de tentativas: https://github.com/ros-navigation/navigation2/pull/5997
  e https://github.com/ros-navigation/navigation2/pull/6149 (ambas
  também fechadas sem merge).
- As três PRs implementam variações de "ruído colorido"/filtro
  passa-baixa nas amostras de ruído do MPPI, baseado no paper "LP-MPPI:
  Low-Pass Filtering for Efficient Model Predictive Path Integral
  Control" (ICRA 2026), numa tentativa de reduzir a aleatoriedade
  ciclo-a-ciclo do MPPI sem trocar de controlador — exatamente o tipo
  de tuning que este agente foi instruído a procurar.
- Resultado: nos comentários da PR #6151 (2026-06-30 a 2026-07-02), o
  próprio contribuidor (mohamedsamirx) e o mantenedor principal do Nav2
  (Steve Macenski) concordam, após benchmarks extensos, que a melhor
  configuração testada teve desempenho **pior** (até uma ordem de
  magnitude em algumas métricas) do que o default sem o filtro. Citação
  do mantenedor: "I had really hoped this would improve things... this
  unfortunately shows no improvement". PR fechada sem merge por essa
  razão, não por falta de interesse.

**Ação sugerida:** não existe hoje upstream uma alternativa madura e
recomendada pra reduzir a estocasticidade do MPPI via ruído estruturado
— não vale esperar por uma feature nova do Nav2 pra isso. O caminho
prático mais promissor continua sendo testar `regenerate_noises: false`
(achado acima), que é o comportamento padrão já existente, não uma
feature experimental.

### 2026-10-02 — Trabalho recente em lifecycle managers (consolidação), ainda não disponível no Jazzy

- **Fonte:** https://github.com/ros-navigation/navigation2/pull/6410
  ("Combine Lifecycle Managers", mergeada em 2026-09-15 no branch
  `main`) e a investigação que a motivou,
  https://github.com/ros-navigation/navigation2/issues/6061 (overhead
  de bond heartbeat). Uma PR concorrente,
  https://github.com/ros-navigation/navigation2/pull/6309 (particionar
  o tópico de bond por servidor), foi fechada em favor desta
  abordagem.
- A PR consolida vários lifecycle managers (localization, navigation,
  slam, keepout, speed-zone, loopback) em um único
  `lifecycle_manager_nav2`, com child launch files ainda podendo ter
  lifecycle manager próprio via parâmetro `use_lifecycle_manager`
  (default `true`). Resultado auto-reportado na PR: reduz CPU do Nav2
  em ~24% (sem IPC) a ~30% (com IPC) ao consolidar 4 managers em 1 —
  número vindo da própria PR, não auditado por mim.
- Isso é sobre overhead de **CPU de heartbeat contínuo** (bond), não
  exatamente sobre a rajada de descoberta DDS na ativação de robô que
  este projeto já mitigou reduzindo de 10 pra 7 nós em
  `fleet_ws/src/fleet_orchestrator/launch/nav2_minimal.launch.py` — mas
  é tangencialmente relevante: menos lifecycle managers tende a
  significar menos nós/bonds no total, o que pode ajudar também com
  tráfego DDS geral em cenário multi-robô.
- **Status de disponibilidade:** só está no branch `main` (pós-Kilted,
  futuro) até a data desta pesquisa — **não confirmei backport pro
  branch `jazzy`**, que é o que este projeto usa. Não dá pra usar sem
  compilar da fonte hoje.

**Ação sugerida:** nenhuma ação possível agora (não disponível no
Jazzy). Vale uma pesquisa futura deste mesmo agente pra checar se houve
backport pro Jazzy.

### 2026-10-02 — Releases recentes do Nav2 (branch Jazzy, série 1.3.x): sem mudança isolável relevante nos corpos de release

- **Fonte:** https://github.com/ros-navigation/navigation2/releases
  (tags `1.3.10` a `1.3.13`, publicadas entre 2025-10-23 e 2026-08-21).
- Os corpos das releases da série 1.3.x (Jazzy) são genéricos ("Jazzy
  sync", "Jazzy release"), exceto a 1.3.10 (2025-10-23), que menciona
  explicitamente corrigir "a regression due to dynamic parameters and
  missing route server from navigation2's metapackage package.xml
  file".
- Não encontrei, nos corpos dessas releases, nenhuma mudança
  especificamente sobre timing de lifecycle/bringup, comportamento do
  MPPI, ou compatibilidade com Gazebo Harmonic — mas os corpos de
  release do Nav2 são resumos curtos, não changelogs completos; não
  confirmado que não haja mudanças relevantes, só que não aparecem
  nesses textos curtos.

**Ação sugerida:** se for importante garantir que nada mudou pra pior
entre versões 1.3.x usadas, o caminho mais confiável é comparar o
`CHANGELOG.rst` de cada pacote (`nav2_mppi_controller`,
`nav2_bringup`) via diff de commits entre tags, não os corpos de
release do GitHub — não fiz isso nesta execução (ficaria caro em tempo
de pesquisa pra esta rodada).

### 2026-10-02 — Pista de baixa confiança, não aprofundada: issue #4552 sobre segundo TurtleBot4 e lifecycle timeout

- **Fonte:** https://github.com/ros-navigation/navigation2/issues/4552
  (estado: `closed`, fechada em 2025-02-02). Título: "Nav2 Fails on
  Second TurtleBot 4".
- Relato (Humble, Nav2 1.1.15, DDS Fast-RTPS, Clearpath Discovery
  Server): ao subir um segundo TurtleBot4, lifecycle manager dá timeout
  em `async_send_request` durante configuração — primeiro robô funciona,
  segundo falha. Workaround relatado no relato original: usar Domain ID
  separado por robô, em vez de só isolar via Discovery Server.
- **Não confirmado** se esse workaround foi validado por outros
  usuários ou pelos mantenedores — a API do GitHub ficou com rate-limit
  esgotado durante esta pesquisa antes de eu conseguir ler todos os
  comentários da issue a fundo. Também é de Humble/Nav2 1.1.15, mais
  antigo; não confirmei se o mecanismo de descoberta DDS usado hoje
  neste projeto (ver `conhecimento/dds_tuning.md`) é comparável.

**Ação sugerida:** nenhuma — registrado só como pista pra uma próxima
execução deste agente (ou do agente de DDS) investigar mais a fundo,
com rate-limit do GitHub disponível.

### 2026-10-02 — Ação aplicada (parcial): toggle de `regenerate_noises` no código

O achado acima sobre `regenerate_noises: true` (TB4) vs. `false` (default
Nav2) ganhou um mecanismo de teste no código, não só a sinalização:
`turtlebot4_sim.launch.py` e `turtlebot4_multi_sim.launch.py` agora leem a
env var `NAV2_MPPI_REGENERATE_NOISES` (mesmo padrão de `FLEET_ROBOTS`) e
sobrescrevem `controller_server.ros__parameters.FollowPath.regenerate_noises`
antes de gravar o YAML temporário usado pelo Nav2. Default sem a variável
definida é `true` — preserva exatamente o comportamento de toda campanha
já reportada na dissertação, ninguém precisa mudar nada pra continuar
igual. Testado isoladamente (chamando `_make_nav2_params()` com
`NAV2_MPPI_REGENERATE_NOISES=true/false`/variável ausente e inspecionando
o YAML gerado) nos dois launch files — o mecanismo funciona.

**O que ainda falta (não é "Feito"):** rodar de fato a campanha com
`NAV2_MPPI_REGENERATE_NOISES=false` num Gazebo/Nav2 reais e comparar a
variância do RMSE entre réplicas contra a baseline (`regenerate_noises:
true`, resultados já reportados) — isso ainda não foi executado. Ver
`implementacao.md`, seção "Em andamento".
