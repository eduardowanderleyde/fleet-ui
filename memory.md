# Memória consolidada dos agentes de pesquisa do experimento

Este arquivo é o **índice cross-agente** dos 7 agentes `experiment-*`
(`.claude/agents/experiment-*.md`). Cada agente mantém o detalhe da sua
pesquisa em `conhecimento/<topico>.md` (fonte, data, link, "Ação
sugerida") — este arquivo aqui é só o resumo rápido pra não precisar abrir
os 7 arquivos pra saber o que já existe. Quem quiser o achado completo
(com fonte/link) vai no arquivo `conhecimento/` indicado.

Ver também `implementacao.md` — lista do que já foi de fato aplicado no
código/experimento a partir desses achados (ou está pendente de decisão).

## Índice por agente

| Agente | Tema | Arquivo detalhado |
|---|---|---|
| `experiment-dds-tuning` | DDS/CPU na ativação sequencial multi-robô | `conhecimento/dds_tuning.md` |
| `experiment-nav2-tracking` | Nav2/MPPI, issues upstream | `conhecimento/nav2_tracking.md` |
| `experiment-stats-methodology` | Metodologia estatística da campanha | `conhecimento/stats_methodology.md` |
| `experiment-gazebo-tracking` | Fidelidade do Gazebo/gz-sim, bridge de ground truth | `conhecimento/gazebo_tracking.md` |
| `experiment-slam-toolbox-tracking` | Bugs/config do SLAM Toolbox | `conhecimento/slam_toolbox_tracking.md` |
| `experiment-artifact-publishing` | Publicação de artefato (FAIR/replicação) | `conhecimento/artifact_publishing.md` |
| `experiment-mcp-orchestration` | MCP e orquestração multi-agente | `conhecimento/mcp_orchestration.md` |

## Linha do tempo (mais recente primeiro)

### 2026-10-02 — rodada 2, `experiment-stats-methodology`: sincronização temporal pro piloto

- **[stats_methodology]** `/odom` confirmado publicando a 30Hz exato (fonte
  própria do projeto: `odom_publish_frequency` no plugin DiffDrive do
  `create3.urdf.xacro`). `/pose` (SLAM, ~2Hz) e ground truth (taxa com
  números conflitantes no próprio `orquestracion.md`, ~51-55Hz vs. ~100Hz,
  não resolvido) têm taxas tão diferentes que reamostrar as 3 pra uma
  grade comum arbitrária (como `--resample-mode time` faz hoje) corre risco
  de cortar curvas da rota ao interpolar o `/pose` esparso — achado em
  tensão direta com o objetivo da campanha (ver se divergência cresce com
  complexidade da rota: o corte de curva por reamostragem poderia simular
  esse efeito artificialmente). Também confirmado (fonte primária, Martin
  Bland): pooled de pontos-tempo não-independentes de uma mesma réplica
  infla artificialmente a precisão de um Bland-Altman — reforça manter 1
  observação por réplica (N=10), como `analyze_runs.py` já faz pro RMSE. →
  `conhecimento/stats_methodology.md`

### 2026-10-02 — rodada 2, `experiment-gazebo-tracking`: alinhamento de frames pro piloto

- **[gazebo_tracking]** Pesquisa de código-fonte (não só doc) confirma:
  `/odom` do `DiffDrive` (gz-sim) sempre zera pra (0,0,0,heading=0) ao
  inicializar, independente da pose real de spawn; `slam_toolbox` (sync)
  inicializa `map`→`odom` como identidade e a calcula no 1º scan a partir
  da pose do `odom` naquele instante — bate com a convenção da REP-105
  ("map e odom tipicamente alinhados com a pose inicial do robô"). Pra
  este projeto (spawn em 0,0,0), as três fontes da campanha /odom vs
  /pose vs ground truth deveriam coincidir no instante inicial, mas isso
  não é garantido por código — depende do robô estar parado entre spawn e
  1º scan. Ação sugerida: validar ao vivo comparando a 1ª amostra de
  cada fonte antes do piloto grande. → `conhecimento/gazebo_tracking.md`

### 2026-10-02 — primeira rodada de todos os 7 agentes

- **[nav2_tracking]** `nav2.yaml` do TurtleBot4 força `regenerate_noises: true`
  no MPPI, contra o próprio default recomendado do Nav2 (`false`). Candidato
  de teste barato pra reduzir estocasticidade do controlador. →
  `conhecimento/nav2_tracking.md`
- **[dds_tuning]** Nav2 e SLAM Toolbox suportam composição de nós
  (`ComposableNodeContainer`); os launch files deste projeto sobem cada
  servidor como processo separado — hipótese mais direta pro problema real
  dos 70% de sucesso na ativação sequencial. → `conhecimento/dds_tuning.md`
- **[stats_methodology]** A campanha /odom vs /pose vs ground truth pode
  estar enquadrada errado: como ground truth é referência, a pergunta real
  se parece mais com concordância entre métodos de medição (estilo
  Bland-Altman) do que um teste simétrico entre 3 grupos (ANOVA/Friedman).
  Decisão de enquadramento necessária antes do piloto. →
  `conhecimento/stats_methodology.md`
- **[gazebo_tracking]** Plugin oficial `WheelSlip` existe e não é usado
  (em tensão com a limitação "DiffDrive não modela slip" já escrita na
  dissertação); ruído gaussiano de LiDAR já é nativo via SDF, não precisava
  de plugin — lacuna de documentação, não do simulador. →
  `conhecimento/gazebo_tracking.md`
- **[slam_toolbox_tracking]** O próprio SLAM Toolbox teve, em agosto/2026,
  um bug do mesmo padrão que já corrigimos no nosso lado (estado preso após
  reativação de lifecycle) — corrigido lá, ainda sem release. Tópicos
  globais (`/scan`, `/map`) são decisão de design confirmada pelo
  mantenedor, não bug. → `conhecimento/slam_toolbox_tracking.md`
- **[artifact_publishing]** Selo ACM formal é desproporcional (ICRA/IROS
  não têm essa trilha); Zenodo DOI + `CITATION.cff` são baixo esforço e
  valem a pena antes da defesa; Lier et al. (2017), 4 eixos, é a estrutura
  mais próxima pra um README de replicação. →
  `conhecimento/artifact_publishing.md`
- **[mcp_orchestration]** Spec do MCP ficou mais complexo desde a decisão
  original (3 revisões maiores), não mais simples; com ~12 tools fixas e 1
  cliente, o argumento a favor de MCP genérico é fraco — reforça manter
  tool-calling direto. → `conhecimento/mcp_orchestration.md`

### 2026-10-02 — ação em andamento: toggle de `regenerate_noises`

- **[nav2_tracking]** Implementado (não testado em campanha real ainda) o
  mecanismo pra testar o achado acima: `NAV2_MPPI_REGENERATE_NOISES=false`
  (env var, mesmo padrão de `FLEET_ROBOTS`) agora sobrescreve
  `controller_server.FollowPath.regenerate_noises` em
  `turtlebot4_sim.launch.py` e `turtlebot4_multi_sim.launch.py`. Default
  sem a variável = `true`, preservando toda campanha já reportada. Ver
  `implementacao.md` ("Em andamento") e `conhecimento/nav2_tracking.md`.

### 2026-10-02 — feito: `CITATION.cff`

- **[artifact_publishing]** `CITATION.cff` criado na raiz do repo
  (autor confirmado: Eduardo Wanderley, MIT). Falta só o DOI via Zenodo
  (exige login do autor, não pode ser feito por agente). Ver
  `implementacao.md` ("Feito") e `conhecimento/artifact_publishing.md`.

### 2026-10-02 — achado real + mitigação: dados da campanha oficial perdidos

- **[artifact_publishing]** Ao escrever o README de replicação, confirmado
  no disco e no git: os dados brutos da campanha oficial do Capítulo 8
  (`dissertation_clean01_final_manual`) não existem em lugar nenhum
  rastreável, e o commit exato nunca foi registrado. Autor confirmou que
  podem ter sido perdidos mesmo. Mitigação: todo export de
  `experiment_repeatability.py` agora grava commit+dirty automaticamente
  (`_git_provenance()`). README de replicação criado em
  `fleet_ws/docs/REPLICATION.md`, honesto sobre a lacuna. Ver
  `implementacao.md` ("Feito") e `conhecimento/artifact_publishing.md`.
  Decisão pendente: mencionar isso no Cap. 09 (Limitações) da dissertação —
  ver `implementacao.md` ("Pendente").

### 2026-10-02 — piloto real rodado: alinhamento OK, mas ground truth congela no cold-start

- **[gazebo_tracking]** Rodei o piloto de verdade (não é achado de agente,
  é o autor rodando a simulação ao vivo): simulação single-robot subida,
  rota `dissertation_clean01` reproduzida 2x, gravando `/odom`, `/pose`,
  `/ground_truth_pose_clean`. Alinhamento de frame CONFIRMADO (odom/ground
  truth ~(0,0,0) no spawn, TF `map`→`base_link` identidade exata) — mas
  achei algo mais grave: `/ground_truth_pose_clean` ficou congelado em
  (0,0,0) por ~10-16s na primeira gravação (logo após o boot da stack),
  e funcionou perfeitamente numa segunda gravação com a stack já
  "aquecida". **Isso é potencialmente bloqueante pra campanha principal**,
  que relança a simulação inteira antes de cada uma das 30 réplicas. Ver
  `conhecimento/gazebo_tracking.md` ("Achado real e grave...") e
  `implementacao.md` ("Pendente", item BLOQUEANTE). Rates reais medidos:
  ground truth ~105-111Hz, odom ~27,8Hz, scan 10,0Hz exato, pose
  ~0,2-0,8Hz (ainda mais esparso que a estimativa anterior do agente de
  estatística, porque `minimum_travel_distance`/`minimum_travel_heading`
  também gateiam, não só `minimum_time_interval`). O RMSE de 43,96cm de
  `/pose` vs. ground truth do piloto original é artefato do congelamento,
  não deve ser citado como resultado real.

### 2026-10-02 — correção: ground truth provavelmente não congela; problema real é outro

- **[gazebo_tracking / dds_tuning]** Testei mais 2 boots frescos pra
  confirmar o congelamento de ground truth achado antes — **não se
  repetiu em nenhum dos dois** (concordância quase perfeita com
  `/odom`). Pesa contra a hipótese de bug intrínseco de ground truth.
  O que encontrei de real: processos órfãos de uma bateria de testes
  anterior sobreviveram e contaminaram CPU de um boot novo (load chegou
  a 14,16); numa 3a tentativa, já sem órfãos, a ativação travou de
  verdade por >2min — reprodução ao vivo do problema JÁ CONHECIDO de
  ativação sequencial instável (~70% de sucesso, já documentado antes).
  Conclusão revisada: o risco real pra campanha principal é higiene de
  processo entre réplicas + falta de timeout-e-retry no bringup, não
  ground truth. Ver `implementacao.md` ("Pendente", item BLOQUEANTE
  revisado) e `conhecimento/gazebo_tracking.md`/`dds_tuning.md`.

### 2026-10-02 — feito: script de campanha com higiene de processo + retry

- **[dds_tuning / gazebo_tracking]** `fleet_ws/scripts/run_ground_truth_campaign.py`
  (novo): mata agressivamente por padrão de processo antes de cada
  réplica e confirma que nada sobrou; se o bringup não ficar pronto a
  tempo, mata tudo e tenta de novo (até N vezes), registrando retries
  num `campaign_manifest.json`. Testado com mini-campanha real (2
  réplicas): 2/2 ok, 0 retries, ground truth sem congelamento nas duas
  (4a e 5a confirmação consecutiva de que o congelamento original não
  era um bug de ground truth). Ainda falta: testar com N grande e com
  as rotas longa/loop (que não existem ainda). Ver `implementacao.md`
  ("Feito" e "Pendente").

### 2026-10-02 — feito: rotas longa e loop fechado criadas

- **[gazebo_tracking]** `rota_longa_curva` (7,7m, reta+curva 90°) e
  `loop_fechado` (11,3m, quadrado, retorna ao início) gravadas de
  verdade, sem falhas — fecham o passo 3 do plano da campanha de ground
  truth. Achado no caminho: o mapa estático de referência do
  `turtlebot4_navigation` NÃO é o mundo real desta simulação (mundos de
  mesmo nome "warehouse", pacotes e geometria diferentes) — usei o SDF
  real (`nav2_minimal_tb4_sim/worlds/warehouse.sdf`) pra confirmar área
  livre. Erro cometido e corrigido no caminho: gravei `loop_fechado` a
  primeira vez sem reiniciar a sim depois da rota anterior, contaminando
  o início com a posição residual do robô — regravado do zero. Rotas
  ficam em `fleet_ws/routes/default/`, não vão pro git (gitignored, como
  `dissertation_clean01`). Falta testar `run_ground_truth_campaign.py`
  com essas 2 rotas antes da campanha completa. Ver `implementacao.md`.

### 2026-10-02 — feito: campanha validada nas 3 rotas, retry provado numa falha real

- **[dds_tuning]** `run_ground_truth_campaign.py` testado nas 3 rotas
  (curta, longa, loop) — 8/8 réplicas ok no total, ground truth sem
  congelamento em nenhuma. Na rota longa, a réplica 1 bateu de verdade
  no problema de ~70% de sucesso (2 timeouts de `change_state` em nós
  diferentes, retry corrigiu sozinho na 3ª tentativa) — primeira prova
  real de que o mecanismo funciona numa falha de verdade, não só no
  caminho feliz. Bug achado e corrigido no caminho: nomes de log sem o
  número da réplica faziam a réplica 2 sobrescrever o log da réplica 1.
  Ver `implementacao.md` ("Feito") e `conhecimento/dds_tuning.md`.

### 2026-10-02 — RESULTADO FINAL da campanha de ground truth (30 réplicas) + bug de alinhamento corrigido

- **[stats_methodology]** Campanha completa rodou (10 réplicas × 3 rotas,
  30/30 ok). Resultado real: RMSE `/odom` vs. ground truth cresce com a
  rota (0,01→5,18→14,27cm); RMSE `/pose` (SLAM) vs. ground truth fica
  baixo e quase constante (3,28→2,25→2,45cm) — SLAM limita o erro de
  localização, odometria crua não. Responde diretamente à pergunta que
  motivou toda essa campanha. No caminho, achei e corrigi um bug sério
  na própria análise: `_read_traj_xy` rebaseava cada tópico pro seu
  próprio t=0, inválido ao comparar `/pose` (começa ~8-10s depois do
  ground truth) contra ground truth — produzia ~60cm de erro artificial
  antes da correção. Ver `conhecimento/stats_methodology.md` e
  `implementacao.md` ("Feito"). Decisão pendente: levar isso pra
  dissertação (Cap. 08).

### 2026-10-02 — piloto: camada de agentes de IA rodada pela primeira vez nesta sessão

- **[mcp_orchestration]** Primeira execução real de `backend/agents/`
  (Planner/Executor) — exigiu criar `backend/venv/` e corrigir um bug real
  (incompatibilidade `anthropic` SDK + `brotli` do sistema, mascarado como
  "erro de conexão"). Piloto N=5 via `/api/agent/run`: agente recusou
  corretamente inventar parâmetros ambíguos 2x, depois rodou 1 baseline +
  5 réplicas sem falhas. RMSE pairwise entre réplicas: 4/5 entre
  0,014–0,068m, 1 outlier (0,42–0,45m, não investigado). Autor decidiu
  manter só como registro, não levar pra dissertação ainda (N pequeno,
  outlier sem explicação). Ver `implementacao.md` ("Em andamento") e
  `conhecimento/mcp_orchestration.md`.

### 2026-10-03 — bug real achado e corrigido pilotando run_fleet multi-robô; sessão interrompida no meio

- **[dds_tuning]** Primeiro teste real de `run_fleet` (2 robôs, agente
  independente por robô). `play_route`/replay falhava nos dois com "Nav2
  follow_waypoints not available" — causa raiz: `waypoint_follower`
  literalmente ausente do launch de ativação sequencial multi-robô
  (cortado por engano em 2026-09-30, nunca testado contra `play_route`
  até agora). Corrigido e verificado (commit `db5ce66`). Depois do fix,
  tb1+tb2 ativaram e `run_fleet` foi disparado de verdade — mas a sessão
  foi interrompida no meio da execução (reinício inesperado), sem RMSE
  coletado. O fix está seguro no git; falta só repetir a campanha do
  zero. Ver `implementacao.md` ("Em andamento") e `conhecimento/dds_tuning.md`.

### 2026-10-03 — piloto run_fleet multi-robô completo (3ª tentativa, 2 reinícios da máquina no meio)

- **[mcp_orchestration]** `run_fleet` com tb1+tb2 (agentes independentes)
  completou de verdade: RMSE entre réplicas baixo pro tb2 (0,038–0,048m),
  alto pro tb1 (0,18–0,34m), mas a causa mais provável não é o LLM — é
  que `run_campaign` não reseta a pose do robô entre réplicas (diferente
  de `run_ground_truth_campaign.py`, que faz isso de propósito). Ver
  `implementacao.md` ("Feito") e `conhecimento/mcp_orchestration.md`.

**Como manter isto atualizado:** cada agente, ao final de uma execução,
acrescenta uma entrada nova (data + achado em 1-2 linhas + link pro arquivo
detalhado) nesta seção, sem apagar entradas anteriores. Se um achado tiver
"Ação sugerida" concreta, também vira uma linha em `implementacao.md`.
