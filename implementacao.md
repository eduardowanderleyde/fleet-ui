# Log de implementação — ações a partir dos achados dos agentes de pesquisa

Diferente de `conhecimento/*.md` (pesquisa detalhada por tema) e
`memory.md` (índice resumido entre os 7 agentes), este arquivo rastreia só
o que tem **ação concreta recomendada pro código/experimento**: o que já
foi decidido, o que está pendente de decisão, e o que foi de fato
implementado (com data e resultado observado).

Os agentes de pesquisa (`.claude/agents/experiment-*.md`) **nunca
implementam nada sozinhos** — eles só adicionam itens à seção "Pendente"
abaixo quando um achado tem "Ação sugerida". Mover um item pra "Feito"
exige uma decisão explícita do autor e o teste real (não só a mudança de
código) confirmando o efeito.

## Pendente (aguardando decisão do autor)

- [ ] **Avaliar composição de nós (`ComposableNodeContainer`) pra Nav2 e
  SLAM Toolbox** (origem: `dds_tuning`, 2026-10-02). Hipótese pro problema
  real dos 70% de sucesso na ativação sequencial multi-robô. Risco: médio
  (mudança de arquitetura de launch, não só parâmetro). **Atualização
  2026-10-03**: dado o prazo curto até a defesa, recomendado como
  trabalho futuro documentado, NÃO tentar antes da defesa — ver item
  abaixo (RMW swap) pra alternativa de menor risco/esforço a testar
  primeiro. Risco reforçado por precedente real: os mesmos launch files
  já causaram 1 regressão real nesta sessão (corte do `waypoint_follower`
  por engano, commit `db5ce66`).
- [ ] **Testar `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` em A/B contra o
  default (Fast DDS) na ativação sequencial multi-robô** (origem:
  `dds_tuning`, 2026-10-03, respondendo diretamente à pergunta "o que
  tentar antes da defesa"). Candidata de menor esforço/risco das 3
  hipóteses levantadas: zero mudança de código (confirmado lendo
  `backend/ros_bridge.py` e `run_ground_truth_campaign.py` — ambos
  herdam o ambiente do processo pai sem filtrar nada), 100% reversível
  (desfazer a variável), testável com a infraestrutura de retry que já
  existe (`run_ground_truth_campaign.py`). Pré-requisito: `apt-get
  install ros-jazzy-rmw-cyclonedds-cpp` (não está no `Dockerfile` hoje —
  só `ros-jazzy-desktop`, que não inclui esse pacote). Sugestão de
  teste: N réplicas (≥10) da ativação sequencial com e sem a variável,
  comparando quantos retries cada config precisou, antes de decidir se
  muda o número de 70% já citado na dissertação. Risco: baixo. Chance de
  funcionar: reforçada em 2026-10-05 por corroboração independente real —
  usuários no fórum oficial ROS/Gazebo relatam a mesma classe de sintoma
  (tf falhando ~75% das vezes, timeout de serviço) sob Fast DDS numa
  única máquina, resolvido trocando pra Cyclone DDS, em outro projeto.
  **Atualização importante**: Cyclone DDS tem seu próprio bug conhecido
  sob bringup concorrente (`ros2/rmw_cyclonedds#458`, "Failed to find a
  free participant index") — incluir
  `CYCLONEDDS_URI` com `MaxAutoParticipantIndex` elevado (ex. 100) junto
  da troca de RMW desde a primeira tentativa, não só se aparecer erro
  novo depois. Ver `conhecimento/dds_tuning.md` (achados 2026-10-03 e
  2026-10-05) pro detalhe completo e as fontes.
- [ ] **Avaliar adicionar o plugin `WheelSlip` ao modelo do Gazebo**
  (origem: `gazebo_tracking`, 2026-10-02; reavaliado em 2026-10-03). Hoje
  a dissertação registra "DiffDrive não modela slip" como limitação;
  existe plugin oficial que mitigaria isso. **Reavaliação 2026-10-03**:
  dado que a dissertação nesta versão é só-simulação (sem comparação com
  robô real), a recomendação do agente mudou de "decidir" para "não vale
  o esforço agora" — sem dado real de slip pra calibrar
  `slip_compliance_lateral/longitudinal`, o plugin só troca uma limitação
  honesta ("não modela slip") por uma limitação arbitrária ("modela slip
  com valor inventado"), sem ganho real de fidelidade. Ficaria valioso só
  se o projeto algum dia ganhar uma etapa de comparação com hardware real.
  Decisão final de reformular ou não o texto da dissertação continua
  sendo do autor — ver `conhecimento/gazebo_tracking.md`, achado
  2026-10-03, pergunta 2.
- [ ] **Arquivar uma Release do GitHub no Zenodo pra gerar DOI** (origem:
  `artifact_publishing`, 2026-10-02; roteiro detalhado em 2026-10-03).
  Baixo esforço, baixo risco, não exige mudar código — só criar a Release e
  conectar o Zenodo (exige login do autor no Zenodo, não pode ser feito
  por um agente). `CITATION.cff` já existe (ver "Feito"). Confirmado em
  2026-10-03: ainda não existe nenhuma Release no GitHub do fleet-ui.
  **Roteiro exato** (detalhe completo e justificativa em
  `conhecimento/artifact_publishing.md`, achado "O que deveria entrar no
  pacote de replicação mínimo..."):
  1. (Opcional mas recomendado — ver item separado abaixo sobre as rotas
     YAML) resolver a lacuna das rotas não versionadas ANTES de criar a
     Release, senão o artefato arquivado fica sem as entradas exatas do
     experimento.
  2. Confirmar o commit/branch desejado (ex. depois do merge de
     `mission-coordinate-large-scale` pra `main`).
  3. No GitHub: "Releases" → "Draft a new release" → criar uma tag nova
     (ex. `v1.0.0` ou `dissertacao-cap08-cap09`) → preencher título/notas
     descrevendo o que a versão representa → publicar.
  4. Login em Zenodo com "Log in with GitHub", autorizar o app, ir à
     página de configurações do GitHub dentro do Zenodo, ligar o toggle
     do repo `fleet-ui` — precisa estar ligado ANTES de publicar a
     Release (ou publicar de novo depois de ligar) pro arquivamento
     automático funcionar.
  5. Depois de publicado: Zenodo gera um DOI de versão + um DOI
     "guarda-chuva" (concept DOI, sempre aponta pra versão mais recente) —
     citar o guarda-chuva na dissertação é mais seguro.
  6. Opcional: incluir os bags MCAP brutos relevantes (não a íntegra de
     `collections/`) via "New version" na UI do Zenodo (upload manual,
     sem precisar de outra Release do GitHub) — mecanismo não confirmado
     em fonte primária Zenodo nesta rodada, confirmar na UI antes de
     depender disso. Não é necessário pro pacote mínimo (36MB está muito
     abaixo do limite de 50GB/registro do Zenodo, confirmado em fonte
     primária em 2026-10-03).
  7. Adicionar o DOI resultante ao `CITATION.cff` e citar na dissertação.
- [ ] **Decidir se a dissertação (Cap. 09, Limitações) deve mencionar
  explicitamente que os dados brutos da campanha oficial não foram
  preservados** (origem: achado real desta sessão, 2026-10-02 — não é
  "Ação sugerida" de pesquisa, é fato confirmado no disco/git; ver
  `conhecimento/artifact_publishing.md`). A dissertação hoje não afirma
  que os dados estão disponíveis, então não há afirmação falsa a corrigir
  — é só uma omissão a considerar.
## Em andamento

- [~] **Testar `regenerate_noises: false` no MPPI do Nav2** (origem:
  `nav2_tracking`, 2026-10-02; código em 2026-10-02).
  `_make_nav2_params()` em `turtlebot4_sim.launch.py` e
  `turtlebot4_multi_sim.launch.py` agora lê
  `NAV2_MPPI_REGENERATE_NOISES` (env var, mesmo padrão já usado por
  `FLEET_ROBOTS`) e sobrescreve `controller_server.FollowPath.regenerate_noises`.
  Default sem a variável definida = `true` (preserva o comportamento de
  toda campanha já reportada — ninguém precisa mudar nada pra continuar
  igual). Testado isoladamente (chamando `_make_nav2_params` com
  `true`/`false`/sem variável e inspecionando o YAML gerado) — o
  mecanismo funciona nos dois launch files. **Falta**: rodar de fato a
  campanha com `NAV2_MPPI_REGENERATE_NOISES=false` e comparar a variância
  do RMSE contra a baseline — isso exige Gazebo/Nav2 reais de pé, não foi
  executado ainda. Uso: `NAV2_MPPI_REGENERATE_NOISES=false ros2 launch
  fleet_orchestrator turtlebot4_sim.launch.py ...`.
  **Recomendação (2026-10-03, `nav2_tracking`)**: não rodar essa
  campanha agora, antes da defesa — risco de tempo real (ativação
  sequencial tem ~70% de sucesso histórico, ver `dds_tuning.md`, pode
  exigir vários retries) contra um ganho incerto (a doc oficial do Nav2
  descreve `regenerate_noises: false` como otimização de jitter de CPU,
  não garantia de reduzir variância entre execuções diferentes — não há
  evidência registrada de que isso reduza o RMSE pairwise). Deixar como
  trabalho futuro já com a infraestrutura pronta é a recomendação; ver
  `conhecimento/nav2_tracking.md` pro raciocínio completo. Decisão final
  continua do autor.
- [~] **Pilotar se a camada de agentes de IA degrada a repetibilidade
  pairwise** (origem: item de trabalho futuro criado nesta sessão na
  dissertação, Cap. 09; piloto em 2026-10-02). Primeira execução real da
  camada `backend/agents/` (Planner/Executor) nesta sessão — exigiu criar
  `backend/venv/` (não existia) e corrigir um bug real de incompatibilidade
  entre `anthropic` SDK e o pacote `brotli` do sistema, mascarado como
  "erro de conexão" (ver `conhecimento/mcp_orchestration.md` pro
  diagnóstico completo). Rodado via `/api/agent/run`, N=5, rota nova
  `llm_pilot01` (não mexeu em `dissertation_clean01`): o agente recusou
  corretamente inventar parâmetros ambíguos duas vezes antes de executar;
  rodou 1 baseline + 5 réplicas sem falhas operacionais. RMSE pairwise
  entre réplicas (metodologia correta, mesmo mecanismo de navegação): 4
  de 5 ficaram entre 0,014–0,068m; a réplica 1 destoou das outras 4 em
  0,42–0,45m (outlier não investigado). **Decisão do autor (2026-10-02)**:
  por ora fica só como registro de conhecimento, não entra na dissertação
  — N=5 com 1 outlier não explicado é insuficiente pra conclusão. Falta:
  rodar `diagnose_experiment` no run_id `llm_pilot01_4979c065` pra
  investigar a réplica 1, e repetir com N maior antes de reconsiderar.
## Feito

- [x] **Suavizar "estatisticamente equivalente" na Seção 8.6** (origem:
  `stats_methodology`; feito 2026-10-03, commit `c3ede78`). Trocado por
  "sem diferença perceptível" nos dois lugares (Cap. 08 e Cap. 09) —
  nenhum número mudou.

- [x] **Mencionar a defasagem de timestamp do ground truth** (origem:
  `gazebo_tracking`; feito 2026-10-03, commit `a729674`). Uma frase na
  Seção 8.6: timestamp é hora de recepção pelo filtro, não da física
  (<17ms).

- [x] **Registrar a ressalva de escala do SLAM Toolbox** (origem:
  `slam_toolbox_tracking`; feito 2026-10-03, commit `a729674`). Uma frase
  na Seção 8.6: conclusão testada só até 11,3m.

- [x] **Citar CLiMRS como referência de coordenação multi-robô** (origem:
  `mcp_orchestration`; feito 2026-10-03, commit `59d0b38`). Bib + 1 frase
  no Cap. 09, trabalho futuro. Data de submissão (2025) confirmada em
  fonte primária, inconsistência com o ID do arXiv documentada no .bib.

- [x] **Citar Borenstein & Feng (1996) fundamentando a deriva de odometria**
  (origem: `nav2_tracking`, proposto como "Ação sugerida" sem checkbox
  próprio; feito 2026-10-03, commit `d67cf65`). Bib + 1 frase na Seção
  8.6. DOI/páginas não confirmados em fonte primária, omitidos.

- [x] **Versionar os arquivos de rota (`fleet_ws/routes/*.yaml`) que
  correspondem às campanhas já commitadas** (origem: achado real,
  `artifact_publishing`, 2026-10-03; feito em 2026-10-03). `routes/`
  continua ignorado por padrão em `fleet_ws/.gitignore` (pra rotas de
  teste/scratch futuras), mas os 8 arquivos usados pelos resultados já
  commitados (`dissertation_clean01.yaml`, `rota_longa_curva.yaml`,
  `loop_fechado.yaml`, `llm_pilot01.yaml`, `fleet_pilot_tb1_v2.yaml`,
  `fleet_pilot_tb1_v3.yaml`, `fleet_pilot_tb2_v2.yaml`,
  `fleet_pilot_tb2_v3.yaml`) foram adicionados via `git add -f` (opção
  (a) das duas levantadas pelo agente). Como consequência, a afirmação em
  `fleet_ws/docs/REPLICATION.md` de que a rota "existe no repositório"
  voltou a ser verdadeira sem precisar reescrever o texto.

- [x] **Pilotar `run_fleet` multi-robô (path 3 do trabalho futuro, 2
  robôs, agentes independentes)** (origem: extensão do item acima pro
  Cap. 09 da dissertação, commit `e43ff2e`; feito em 2026-10-03, na 3ª
  tentativa — 2 reinícios inesperados da máquina interromperam as 2
  primeiras). **Achado bloqueante no caminho, já corrigido**:
  `play_route`/replay falhava nos dois robôs com "Nav2 follow_waypoints
  not available" — causa raiz confirmada (não DDS, nó
  `waypoint_follower` literalmente ausente do launch de ativação
  sequencial, cortado por engano de escopo em 2026-09-30). Corrigido e
  verificado (`db5ce66`). Com o fix, `run_fleet` completou de verdade
  (1 baseline + 3 réplicas por robô, sem falha operacional):
  - **tb1**: RMSE vs. baseline 0,26–0,27m; RMSE **entre réplicas**
    (comparação correta) também alto, 0,18–0,34m — nem as réplicas
    concordam entre si.
  - **tb2**: RMSE vs. baseline 0,15–0,18m; RMSE **entre réplicas** baixo
    e consistente, 0,038–0,048m — réplicas concordam bem, só o baseline
    ficou desalinhado (poucas amostras de `/pose`, 3 msgs em 1s).
  **Achado metodológico real, não específico de LLM**: `run_campaign`
  (a ferramenta que os agentes usam) não relança a simulação nem
  reseta a pose do robô entre réplicas dentro da mesma campanha —
  diferente de `run_ground_truth_campaign.py` (criado nesta sessão),
  que faz isso de propósito. O RMSE alto aqui provavelmente reflete essa
  limitação de `run_campaign`, não o agente de IA. Detalhe completo em
  `conhecimento/mcp_orchestration.md`. **Não deve ser citado como "LLM
  multi-robô piora repetibilidade"** sem antes isolar essa variável.
  Processos encerrados e confirmados mortos ao final.

- [x] **Rodar a campanha completa /odom vs /pose vs ground truth (30
  réplicas: 10 × 3 rotas) e analisar o resultado** (origem: todo o plano
  em `orquestracion.md`, "Plano: campanha..."; feito em 2026-10-02). As
  30 réplicas correram: 30/30 ok, 0 retries na curta e no loop, 2 retries
  numa réplica da longa (problema de ativação já conhecido, corrigido
  pelo próprio script). **Resultado real da pergunta de pesquisa** (N=10
  por rota, IC95% t de Student):
  | Rota | RMSE odom vs. GT | RMSE pose vs. GT |
  |---|---|---|
  | Curta (~0,9m) | 0,01cm | 3,28cm |
  | Longa (~7,7m, 1 curva) | 5,18cm | 2,25cm |
  | Loop (~11,3m, 4 curvas) | 14,27cm | 2,45cm |
  Erro de `/odom` cresce com a complexidade da rota; erro de `/pose`
  (SLAM) fica baixo e praticamente constante — o SLAM efetivamente limita
  o erro de localização, a odometria crua não. Detalhe completo em
  `conhecimento/stats_methodology.md`.
  **Bug sério achado e corrigido antes de confiar nesses números**: a
  primeira rodada da análise deu RMSE de `/pose` vs. ground truth de
  ~50-66cm (constante entre rotas — sinal de artefato, não erro real).
  Causa: `_read_traj_xy` (`analyze_runs.py`) rebaseava o tempo de cada
  tópico pro seu próprio t=0, o que é errado ao comparar tópicos
  diferentes no mesmo bag quando eles não começam a publicar junto
  (`/pose` começa ~8-10s depois do ground truth — SLAM Toolbox tem
  `TimerAction` de 8s no launch + tempo até o robô andar os 10cm mínimos
  de `minimum_travel_distance`). Corrigido com um parâmetro novo
  `rebase=False` (tempo absoluto) usado pelas comparações cross-tópico;
  `analyze_runs.py` original (baseline-vs-replay) não foi afetado
  (continua `rebase=True` por padrão). Novo script
  `fleet_ws/scripts/analyze_ground_truth_campaign.py` faz a agregação
  com IC95%.
  **Decisão pendente pro autor**: se esse resultado deve entrar na
  dissertação (Cap. 08) e se a decisão metodológica já tomada (RMSE
  pairwise citando maset2022) deveria ser revisitada à luz dele.
- [x] **Testar `run_ground_truth_campaign.py` nas 2 rotas novas
  (`rota_longa_curva`, `loop_fechado`)** (origem: achado real do autor,
  2026-10-02, ao criar as rotas; feito em 2026-10-02). Mini-campanhas de
  2 réplicas em cada rota, 4/4 ok no total. **Achado valioso no
  caminho**: a réplica 1 da rota longa precisou de 2 retries — as duas
  tentativas falharam exatamente como o problema já documentado
  (`route_server`/`controller_server` dando timeout em `change_state`,
  o mesmo padrão de ~70% de sucesso), e o mecanismo de retry do script
  detectou e corrigiu sozinho, terminando ok na 3ª tentativa. Essa é a
  primeira confirmação real (não hipotética) de que o retry funciona
  numa falha de verdade, não só no caminho feliz. Ground truth
  acompanhou `/odom` corretamente nas 4 réplicas (sem congelamento).
  **Bug real achado e corrigido no caminho**: os nomes de log
  (`sim_attempt{N}.log`) não incluíam o número da réplica — a réplica 2
  sobrescrevia o log da réplica 1 (mesmo "attempt0"), perdendo o
  diagnóstico de qual réplica específica teve problema. Corrigido
  (`r{replicate_id:02d}_sim_attempt{N}.log`).
- [x] **Criar as rotas longa (com curva 90°) e loop fechado** (origem:
  plano em `orquestracion.md`, "Plano: campanha /odom vs. /pose vs.
  ground truth", passo 3; feito em 2026-10-02). Mapeei os obstáculos
  reais do mundo usado pela simulação (não o mapa de referência de
  outro pacote — são mundos diferentes, apesar do mesmo nome
  "warehouse": `nav2_minimal_tb4_sim/worlds/warehouse.sdf`, lido direto
  como XML, 24 modelos com pose exata) pra confirmar que a região
  x:[0,4], y:[0,4] está livre de qualquer estante/obstáculo antes de
  desenhar as rotas — não validei visualmente com GUI (não consigo ver
  uma janela do Gazebo), validei analiticamente a geometria do mundo e
  empiricamente (gravei de verdade, `experiment_repeatability.py
  record`, sem nenhum aviso de colisão/recovery/oscillation nos logs).
  - `rota_longa_curva` (reta + curva de 90°): pontos
    `(2,0,0);(4,0,0);(4,2,1.571);(4,4,1.571)`, 7,66m percorridos
    (teórico 8m), 75 poses salvas, sem falhas.
  - `loop_fechado` (quadrado, retorna ao início): pontos
    `(3,0,0);(3,3,1.571);(0,3,3.142);(0,0,-1.571)`, 11,33m percorridos
    (teórico 12m), 118 poses salvas, sem falhas. **Erro real cometido e
    corrigido**: gravei essa rota a primeira vez sem reiniciar a
    simulação depois da `rota_longa_curva` — o robô ainda estava em
    (4,4), então a rota salva começava contaminada por esse trecho de
    transição, não do spawn (0,0). Descobri isso checando a primeira
    pose do YAML salvo, reiniciei a simulação do zero e regravei
    corretamente (primeira pose agora ~(0,0,0), última pose a 21cm do
    início — dentro da tolerância normal de chegada do Nav2, consistente
    com "loop fechado").
  Ambos os arquivos ficam em `fleet_ws/routes/default/` — **não vão pro
  git** (`fleet_ws/.gitignore` ignora `routes/` deliberadamente, mesmo
  tratamento de `dissertation_clean01.yaml`). Testado rodando
  `run_ground_truth_campaign.py --route rota_longa_curva` ainda não foi
  feito nesta sessão — próximo passo natural antes da campanha completa.
- [x] **Script de campanha com higiene de processo entre réplicas +
  timeout-e-retry pro bringup** (origem: achado real do autor,
  2026-10-02, testando o congelamento de ground truth; feito em
  2026-10-02). `fleet_ws/scripts/run_ground_truth_campaign.py` (novo) —
  antes de CADA réplica, mata agressivamente por padrão de processo
  (`pkill -9 -f`, mesma lista de padrões do `backend/main.py`, com
  extras achados nesta sessão: rviz2, image_bridge, opennav_docking,
  ground_truth_filter), confirma que nada sobrou, e só então relança a
  stack; se o bringup não sinalizar "Managed nodes are active" dentro de
  `--boot-timeout`, mata tudo e tenta de novo até `--max-retries` vezes,
  registrando quantos retries cada réplica precisou num
  `campaign_manifest.json`. Testado de verdade com uma mini-campanha de
  2 réplicas (`--repeat 2`, rota `dissertation_clean01`): 2/2 ok, 0
  retries necessários, ground truth sem congelamento em nenhuma das 2
  (confirmado com `freeze_check.py` — concordância com `/odom` em
  <1mm). Ainda não testado com N grande (10+) nem com as rotas longa/
  loop (que não existem ainda — ver item pendente "criar as 3
  geometrias de rota" nunca formalizado nesta lista, mas presente no
  plano de `orquestracion.md`, passo 3).
- [x] **Gravar o piloto de verdade /odom vs /pose vs ground truth, rota
  curta (`dissertation_clean01`)** (origem: passo 2 do plano em
  `orquestracion.md`; feito em 2026-10-02). Simulação single-robot
  lançada de verdade (headless), coletor gravando as 3 fontes +
  scan/imu, `fleet_ws/scripts/pilot_ground_truth_check.py` (criado hoje)
  rodado em 2 bags reais. Resultado: alinhamento de frame CONFIRMADO ao
  vivo (odom/ground truth ~(0,0,0) no spawn, TF `map`→`base_link`
  identidade exata). `analyze_runs.py` ganhou suporte a `PoseStamped` e
  um parâmetro `use_header_stamp` (ambos aditivos, não mudam
  comportamento existente) pra viabilizar essa análise. **Correção**: a
  primeira tentativa de encerrar os processos da simulação deixou
  órfãos vivos sem eu perceber na hora (só descobri ~30min depois, ao
  testar o item abaixo) — "nenhum órfão deixado rodando" dito aqui
  originalmente estava errado.
- [x] **Testar mais 2 boots frescos pra confirmar/refutar o congelamento
  de ground truth, e medir taxas reais das 3 fontes** (origem: item
  "BLOQUEANTE" anterior + achado do `stats_methodology`; feito em
  2026-10-02). Resultado: ground truth NÃO congelou em nenhum dos 2
  boots limpos (concordância quase perfeita com `/odom`, diferença
  <0,1mm no total percorrido) — pesa contra a hipótese de bug intrínseco.
  No caminho, descobri órfãos de uma bateria de testes anterior
  contaminando CPU (load 14,16) e, numa 3a tentativa já sem órfãos, uma
  reprodução ao vivo do problema JÁ CONHECIDO de ativação sequencial
  instável (`conhecimento/dds_tuning.md`). Taxas reais medidas: ground
  truth ~55-111Hz (varia entre execuções, possivelmente com a carga da
  máquina), odom ~27,8Hz, pose ~0,2-0,8Hz. Novo item BLOQUEANTE revisado
  em "Pendente" acima (higiene de processo + timeout-e-retry, não mais
  sobre ground truth especificamente). Processos encerrados e
  confirmados mortos (`pgrep` vazio) ao final de cada ciclo desta vez.
- [x] **Gravar `/ground_truth_pose_clean` no `fleet_data_collector`**
  (origem: passo 1 do plano em `orquestracion.md`; feito em 2026-10-02).
  `fleet_ws/src/fleet_data_collector/fleet_data_collector/main.py` —
  `_TYPE_MAP` e `_RELIABLE_TOPICS` atualizados. Testado de verdade no
  piloto acima (mensagens gravadas e lidas com sucesso).
- [x] **Criar `CITATION.cff` na raiz do repo** (origem: `artifact_publishing`,
  2026-10-02; feito em 2026-10-02). Autor confirmou o nome (Eduardo
  Wanderley) antes de criar — arquivo em `CITATION.cff`, licença MIT,
  aponta pro repositório. Sem DOI ainda (depende do item Zenodo acima,
  ainda pendente).
- [x] **Escrever README de replicação separado do README de
  desenvolvimento** (origem: `artifact_publishing`, 2026-10-02; feito em
  2026-10-02). `fleet_ws/docs/REPLICATION.md`, estruturado nos 4 eixos de
  Lier et al. (2017), linkado do `README.md` principal. Inclui, com
  honestidade, o achado de que os dados brutos da campanha original
  (`dissertation_clean01_final_manual`) não existem mais — o documento
  descreve como reproduzir o *protocolo* (nova campanha comparável), não
  como recuperar os números exatos já publicados.
- [x] **Gravar commit git + dirty-flag em todo export de
  `experiment_repeatability.py`** (origem: achado real desta sessão,
  2026-10-02, surgido ao investigar o item anterior; feito em 2026-10-02).
  `_git_provenance()` em `fleet_ws/scripts/experiment_repeatability.py`,
  chamado de `_write_export()` — melhor esforço, nunca derruba o
  experimento se o git não estiver disponível. Testado isoladamente
  (resolveu o HEAD atual e detectou árvore suja corretamente). Mitiga a
  lacuna acima para toda campanha futura.

## Como manter isto atualizado

- Um agente de pesquisa pode **adicionar** itens a "Pendente" (nunca
  decidir por conta própria mudar o código).
- Só o autor (ou uma tarefa de implementação explicitamente aberta por
  ele) move um item de "Pendente" → "Em andamento" → "Feito".
- Ao mover pra "Feito", registrar: data, o que mudou de fato (arquivo/
  commit), e o resultado observado (não só "implementado" — o efeito
  medido, se houver).
