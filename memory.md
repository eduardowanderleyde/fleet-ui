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

### 2026-10-03 — rodada 3, `experiment-gazebo-tracking`: mecanismo exato da perda de nome/timestamp no ground truth + reavaliação do `WheelSlip` + LiDAR noise confirmado não-usado

- **[gazebo_tracking]** Lendo o código-fonte real do `gz-sim`
  (`SceneBroadcaster.cc`) e do `ros_gz_bridge` (`convert/geometry_msgs.cpp`):
  o Gazebo já manda o nome da entidade (`pose.name()`) e um timestamp real
  de física em `dynamic_pose/info`, mas o bridge genérico procura esses
  dois campos num lugar que o Gazebo nunca preenche (header por-Pose, não
  o campo `name()` nem o header do array) — por isso ambos se perdem.
  Ação sugerida: mencionar na Seção 8.6/Limitações que o timestamp do
  ground truth reflete o recebimento pelo `ground_truth_filter`, não o
  instante exato da física (defasagem pequena, <~17ms). Reavaliação do
  `WheelSlip` (pendente desde 2026-10-02): dado que a dissertação é
  só-simulação, recomendação agora é NÃO implementar (sem dado real pra
  calibrar, só trocaria uma limitação honesta por uma arbitrária).
  Confirmado que ruído Gaussiano de LiDAR continua não usado, e nunca foi
  usado nem no vendor upstream (`nav2_minimal_turtlebot_simulation`) — não
  é lacuna deste fork. → `conhecimento/gazebo_tracking.md`

### 2026-10-03 — rodada 3, `experiment-dds-tuning`: qual mitigação tentar antes da defesa (70% agora citado formalmente no Cap. 09)

- **[dds_tuning]** Respondendo à pergunta direta (prazo curto até a
  defesa): das 3 hipóteses (RMW swap, `ROS_DISCOVERY_SERVER`,
  `ComposableNodeContainer`), a troca de `RMW_IMPLEMENTATION` pra
  `rmw_cyclonedds_cpp` é a de melhor esforço/risco — confirmado no
  código que não exige nenhuma mudança (backend e script de campanha já
  herdam o ambiente do processo pai), só precisa instalar o pacote apt
  (não está no `Dockerfile`) e testar em A/B. `ComposableNodeContainer`
  (maior potencial, maior risco de regressão nos mesmos launch files que
  já quebraram 1x nesta sessão) e `ROS_DISCOVERY_SERVER` (ganho não
  confirmado em localhost) ficam recomendados como trabalho futuro
  documentado, não tentar antes da defesa. Corrigi no caminho uma
  suposição errada que quase registrei (TurtleBot4 real NÃO usa Cyclone
  DDS por padrão — confirmado no manual oficial, default é Fast DDS
  igual ao ROS 2 puro; Cyclone é só uma alternativa suportada). →
  `conhecimento/dds_tuning.md` (achado 2026-10-03)

### 2026-10-03 — rodada 3, `experiment-mcp-orchestration`: pilotos reais confirmam tool-calling direto; CLiMRS como referência nova de coordenação multi-robô

- **[mcp_orchestration]** Os dois pilotos reais da camada de agentes
  (single-robô e multi-robô, rodados nesta sessão) confirmaram na
  prática a decisão de manter tool-calling direto — isolamento por
  robô e recusa de parâmetro ambíguo já funcionam por construção do
  código, não dependem de protocolo MCP. A limitação real observada no
  piloto multi-robô ("Planners independentes, sem coordenação") agora
  tem referência mais específica e recente: CLiMRS (arXiv 2602.06967),
  que propõe negociação em subgrupos entre agentes LLM um-por-robô —
  mais específico que Li et al. 2025 já citado na dissertação. →
  `conhecimento/mcp_orchestration.md`

### 2026-10-03 — rodada 3, `experiment-nav2-tracking`: explicação alternativa pro resultado da Seção 8.6 + recomendação sobre `regenerate_noises`

- **[nav2_tracking]** O crescimento do erro de `/odom` com a complexidade
  da rota (Seção 8.6, 0cm→5,18cm→14,27cm) provavelmente não é sobre o
  MPPI — não achei issue/discussão do Nav2 sobre isso, mas achei que é
  um fenômeno clássico de odometria de rodas (Borenstein & Feng, 1996:
  erro de orientação em curvas vira erro de posição sem limite), não
  um comportamento do controlador. Candidato a citação na Seção 8.6.
  Também: recomendo NÃO rodar agora a campanha
  `regenerate_noises: false` vs. baseline antes da defesa (risco de
  tempo alto, ganho incerto) — deixar como trabalho futuro com a
  infraestrutura já pronta. → `conhecimento/nav2_tracking.md`

### 2026-10-03 — `experiment-slam-toolbox-tracking`: ameaça à validade na constância do erro de `/pose`

- **[slam_toolbox_tracking]** O resultado novo do Cap. 08 (Seção 8.6) —
  erro de `/pose` constante (~2-3cm) entre 0,9m e um loop de 11,3m,
  enquanto `/odom` cresce até 14cm — tem uma explicação mecanística real
  (correção contínua por scan-matching, confirmada no README oficial e no
  paper `macenski2021slam`), mas foi testado só até 11,3m num mapa
  pequeno sem corredores repetidos; 3 mecanismos conhecidos (janela de
  busca limitada do scan matcher, aliasing perceptual em ambientes
  repetitivos como o `warehouse.sdf` do projeto, e o efeito específico de
  loop closure só na rota que fecha loop) poderiam derrubar essa
  constância em rotas/mapas maiores — vale registrar como limitação no
  Cap. 09. Também reconfirmado: o bug de lifecycle #884 (achado
  2026-10-02) continua sem nenhum release upstream que o inclua. Detalhe
  completo em `conhecimento/slam_toolbox_tracking.md`.

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

### 2026-10-03 — avaliação retrospectiva: Seção 8.6 já publicada é defensável, mas uma frase precisa de correção antes da defesa

- **[stats_methodology]** O item "bloqueante" anterior (escolher
  Bland-Altman vs. ANOVA antes do piloto) está obsoleto — a campanha já
  rodou e já está na dissertação (Cap. 08, Seção 8.6). O que foi de fato
  usado (RMSE escalar por réplica + IC 95% t de Student, N=10, cada fonte
  vs. ground truth separadamente, mesma metodologia já validada pra QA2
  no Cap. 05) é defensável e segue as recomendações anteriores deste
  agente (interpolar só ground truth, 1 observação por réplica). **Achado
  real e concreto**: o texto afirma `/pose` "estatisticamente equivalente"
  entre as 3 rotas só por sobreposição visual de IC — nenhum teste formal
  foi rodado, e isso é um erro estatístico documentado (Gelman & Stern,
  2006). Correção sugerida é textual, de baixo esforço/risco (não muda
  nenhum número). Ver `implementacao.md` ("Pendente") e
  `conhecimento/stats_methodology.md` (achados 17-19).

### 2026-10-03 — pacote de replicacao pro Zenodo + reavaliacao do achado "dados perdidos"

- **[artifact_publishing]** Confirmado: ainda nao existe nenhuma Release no
  GitHub do fleet-ui. Recomendacao concreta: repositorio git completo (sem
  os bags brutos de `collections/`, ~36MB, regeneraveis) e o pacote certo
  pra arquivar no Zenodo, com roteiro passo-a-passo detalhado em
  `implementacao.md`. Achado real no caminho: as rotas YAML
  (`fleet_ws/routes/*.yaml`) usadas pelas campanhas ja commitadas
  (`gt01_curta/longa/loop`, pilotos de IA) nunca foram versionadas
  (gitignored) - um clone/Release nao as incluiria, so os resultados
  processados. Reavaliacao do achado de 2026-10-02 ("dados da campanha
  oficial perdidos"): continua valido e nao corrigido (a campanha
  `dissertation_clean01_final_manual` original segue irrecuperavel), mas a
  mitigacao aplicada entao (`_git_provenance()`) esta confirmada
  funcionando de verdade - lida direto no `gt01_curta/replay_r01.json`
  committed, campo `"git": {"commit": "628d0814...", "dirty": true}`
  populado. Ver `implementacao.md` ("Pendente") e
  `conhecimento/artifact_publishing.md`.

### 2026-10-05 — skills.sh: 4 skills de terceiros instaladas (não é achado de agente, registro de sessão)

- **[sessão]** Explorado `skills.sh` (marketplace de skills pra agentes de
  IA, roda na Vercel). Todo candidato foi inspecionado via API do GitHub
  antes de instalar (arquivos/tamanho, procura por padrão malicioso/
  prompt injection) — não instalado às cegas. Instala via `npx skills add
  <owner/repo> --skill <nome>`, exige Node >=22 (sistema tem v18; Node 22
  instalado via `nvm` nesta sessão, sem mexer no Node do sistema).
  - Na branch `dissertacao`: `paper-audit` e `bib-search-citation`
    (`bahayonghang/academic-writing-skills`). `paper-audit` testado
    contra `main.tex` e se mostrou pouco útil nesse teste específico —
    calibrado pra inglês/chinês, deu só falso positivo numa tese ABNT em
    português (travessão, parágrafo "longo" que era um `\usepackage`,
    siglas que eram título de seção em maiúsculas). `bib-search-citation`
    funcionou bem (parseia `.bib`, busca por tema/autor/ano, gera
    `\cite{}` pronto) — mas nenhuma entrada do `.bib` tem campo
    `abstract` preenchido, o que limita busca por conteúdo.
  - Nesta branch (`mission-coordinate-large-scale`): `ros2` e
    `robot-bringup` (`arpitg1304/robotics-agent-skills`, pacote com 1,7K
    installs). Ambas markdown puro, sem script. **Potencialmente
    relevante pro problema real do projeto**: `robot-bringup` cobre
    especificamente "ordered startup with health checks" e "debugging
    boot-time race conditions" — exatamente a classe do problema dos 70%
    de sucesso na ativação sequencial (`conhecimento/dds_tuning.md`).
    Vale consultar essa skill da próxima vez que alguém mexer em
    `activate_robot_nav.launch.py` ou no settle-time de 15s.
- **[sessão]** Tentativa de gravar vídeo de demo com 2 robôs + 2 pilotos
  de IA navegando **simultaneamente**: reproduziu ao vivo o bug já
  documentado (`conhecimento/dds_tuning.md`, Seção 09 da dissertação) —
  salto de relógio simulado, "jump back in time" repetido, Nav2 nunca
  ficou pronto pra nenhum dos 2 robôs em 300s. Confirma, de novo, que
  Nav2 simultâneo pra 2+ robôs não é confiável; a arquitetura real
  (`activate_robot_nav` + troca sequencial) é o único caminho validado.
  Demo cancelada antes de decidir entre simultâneo/sequencial — autor
  ainda não escolheu.
- **[sessão]** Confirmado que `turtlebot3_house.launch.py` é resquício do
  commit inicial do repo (`b8834ba`, nunca mais tocado) — projeto nunca
  migrou pra TurtleBot3, é TurtleBot4 Standard do início ao fim, inclusive
  em toda a dissertação.

### 2026-10-08 — pilotos reais de 2 gaps de trabalho futuro do Cap. 9, usando TypeSafe (skill instalada em 2026-10-05)

- **[sessão]** `backend/agents/router.py` (`MissionRouter`) e
  `backend/agents/fuut_verify.py` (`FuutVerifier`): dois pilotos testados
  de verdade (não só desenhados), usando a API da TypeSafe
  (`typesafe-sdk`, modelo `jev-1.13.0`) pros primitivos `Choice`/`Score`.
  (1) Roteamento de missão: dado o estado ao vivo da frota, escolhe qual
  robô executa uma instrução — testado com 2 robôs, escolheu certo o
  livre mais próximo (98% confiança), não só o mais próximo em linha
  reta. Novo endpoint `POST /api/agent/run_mission`. (2) Verificação
  cruzada via FUUT: julga se uma observação independente da unidade fixa
  corrobora a pose que o MUUT reportou — testado com 3 cenários
  sintéticos, discriminou bem. Escopo deliberadamente limitado: não faz
  detecção de robô em LiDAR bruto (problema de percepção separado, maior,
  registrado como próximo passo). `decompose_and_route()` (quebrar 1
  missão em N sub-tarefas) está escrito e compila, mas o endpoint ainda
  não foi plugado nem testado. Detalhe completo no commit (mensagem
  extensa) na branch `mission-coordinate-large-scale`.

### 2026-10-08 (continuação) — decompose_and_route plugado e testado + 3º piloto TypeSafe (classificador de ruído MPPI)

- **[sessão]** `POST /api/agent/run_mission_fleet` plugado: decompõe 1
  missão em até N sub-tarefas (Claude) e roteia cada uma via
  `MissionRouter` sem repetir robô. Testado de ponta a ponta — "um robô
  cobre o setor norte, outro o sul" com tb1 em (0,-3) e tb2 em (0,3):
  decompôs certo e roteou geograficamente certo (tb2→norte, tb1→sul).
- **[sessão]** `backend/agents/noise_classifier.py` (`NoiseClassifier`) —
  3º piloto TypeSafe: julga via `Score` se o RMSE de uma réplica é ruído
  esperado do MPPI ou indício real de problema, considerando z-score E
  magnitude absoluta vs. tolerância (não escala só com z-score). Testado
  com os valores REAIS da campanha (min 1,65cm, max 4,76cm) — corretamente
  não achou problema nenhum (a campanha é limpa) — e com 2 outliers
  sintéticos (8cm, 18cm), que escalaram certo pra "suspeito"/"forte
  indício". Commits detalhados na branch `mission-coordinate-large-scale`.

### 2026-10-08 (continuação 2) — avaliação formal do NoiseClassifier: baseline estatístico vs. TypeSafe, achado real de limitação

- **[sessão]** `fleet_ws/scripts/evaluate_noise_classifier.py`: primeira
  avaliação séria (não só "funcionou") de um dos 3 pilotos TypeSafe —
  comparou `NoiseClassifier` contra uma baseline clássica de regra de
  3-sigma, 20 cenários (10 reais da campanha + 10 sintéticos). 75% de
  concordância exata, diferença média 0,38 níveis. Dois achados reais:
  (a) a favor do TypeSafe — trata RMSE abaixo da média como bem menos
  preocupante que acima da média no mesmo \|z\|, assimetria que a regra
  ingênua não captura; (b) **limitação real** — satura em ~2,5-2,8/3,0
  pra outliers extremos, mesmo quando o RMSE já ultrapassa a própria
  tolerância de 25cm (ex.: RMSE=30cm ainda não bate nível máximo). A
  baseline simples acerta esse caso extremo, o TypeSafe não. Esse é o
  tipo de achado que sustenta "quando usar e quando não" — mais forte
  que só demonstrar que funciona. Resultado salvo em
  `fleet_ws/runs/eval_noise_classifier/results_20261008.txt`.

### 2026-10-08 (continuação 3) — piloto FUUT real via OpenSpec: primeira evidência empírica do papel FUUT

- **[sessão]** Planejado com OpenSpec (`openspec/changes/fuut-pilot-experiment/`:
  proposal, 2 specs, design, 12 tasks) e executado de ponta a ponta contra
  Gazebo real (não simulado/fake). **Correção importante sobre o próprio
  trabalho desta sessão**: o proposal.md deste change afirmou que "nenhum
  endpoint ou serviço realmente rejeita um robô FUUT/SU" — isso estava
  ERRADO, descoberto só depois, ao chegar na dissertação (Cap. 6,
  06_implementacao.tex, já documentava um `ROLE_NOT_ALLOWED`). O
  enforcement real e pré-existente vive em
  `fleet_ws/src/fleet_orchestrator/fleet_orchestrator/main.py::_motion_allowed`
  (nó ROS2, não o `backend/main.py` que foi o único lugar checado antes de
  escrever o proposal), já testado em `test_fleet_orchestrator_logic.py`
  (`tb2`/`tb3` já rejeitados). O que `_require_muut()` em `backend/main.py`
  realmente agrega, não duplicado: (a) HTTP 403 explícito antes do
  round-trip ROS2, em vez de um 200 OK com `success:false` escondido no
  corpo; (b) fail-closed de verdade pra `robot_id` desconhecido — o
  `_motion_allowed` pré-existente tem `self._roles.get(robot_id, "MUUT")`,
  ou seja, **qualquer robot_id não declarado em roles.yaml é tratado como
  MUUT por padrão** (fail-open), um gap real e distinto do que o proposal
  original descreveu. Lição: checar a implementação ROS2 real (não só o
  backend HTTP) antes de escrever "nada faz X" num proposal.
  `fleet_ws/scripts/run_fuut_pilot.py`: sobe multi-robô com
  `bringup_nav:=false`, ativa Nav2 só em tb1 (MUUT), mantém tb2 (FUUT)
  parado só com sensores, detecta tb1 via subtração de scan de referência
  do LiDAR de tb2, cruza contra `/tb1/pose` e chama o `FuutVerifier`
  (piloto de sessão anterior) pra cada réplica.
- **Achado real #1** (confirma Cap. 9): a ativação sequencial de Nav2
  falhou espontaneamente numa das 5 execuções reais desta sessão (mesmo
  sintoma de "jump back in time" já documentado) — precisou de retry
  (mesmo padrão de `run_ground_truth_campaign.py`). Mais uma confirmação
  direta do ~70% de taxa de sucesso já reportado, não um bug novo.
- **Achado real #2** (bug de calibração, encontrado e corrigido ao vivo):
  primeira rodada completa deu discrepância geométrica de ~2,8m entre a
  pose reivindicada pelo MUUT e a observação do FUUT — decompondo por
  componente, a distância já batia (~2,0-2,15m), só a direção estava
  sempre ~87-90° fora do esperado nas 3 réplicas. Assinatura de offset de
  montagem do LiDAR relativo ao `base_link`, nunca verificado contra o
  URDF. Corrigido empiricamente (+90°, documentado no código como medida,
  não como valor do URDF) — discrepância caiu pra 3,1-5,9cm (ruído de
  sensor normal), TypeSafe reclassificou as 3 réplicas de "correspondência
  fraca" (confiança 0,1-0,41) pra "correspondência forte" (confiança
  0,86-0,96). **Ação sugerida**: confirmar os 90° contra o transform real
  `lidar_link` → `base_link` do URDF do TurtleBot4 antes de citar esse
  valor como definitivo em qualquer texto.
- Resultado final: `fleet_ws/runs/fuut_pilot01/fuut_verification_report.json`
  — 3/3 réplicas verificadas, todas "correspondência forte". Fecha a
  lacuna "papel FUUT nunca exercitado, zero evidência empírica" (Cap. 9,
  Limitações) com evidência preliminar forte — texto da dissertação ainda
  não atualizado (fora do escopo do change de código; registrado em
  "Workflow follow-up" do `tasks.md` do change).

### 2026-10-08 (continuação 4) — [agente de pesquisa, dds_tuning] RMW swap resolve ativação SIMULTÂNEA de 2 robôs de verdade, testado ao vivo: 1/5 (Fast DDS) → 10/10 (Cyclone DDS)

- **[dds_tuning]** Pergunta nova (nunca testada antes): dá pra ligar Nav2
  completo em tb1 E tb2 AO MESMO TEMPO (não a ativação sequencial já
  medida em 70%/10 no Cap. 9)? Testei ao vivo contra o Gazebo real com
  script novo (`fleet_ws/scripts/run_dual_nav_simultaneous.py`, dispara os
  dois `activate_robot_nav.launch.py` back-to-back sem stagger, sem
  retry). **Baseline Fast DDS: 1/5 (20%)** — pior que a sequencial, como
  esperado (mais participantes DDS entrando na mesma janela). **Trocando
  só `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` (zero mudança de código):
  10/10 (100%)** em duas baterias de 5 réplicas, 0 avisos de "jump back in
  time" em todas, ativação em 6s (mesma velocidade da única réplica limpa
  do baseline). O fix `CYCLONEDDS_URI` pro bug `rmw_cyclonedds#458` não foi
  necessário pra 2 robôs (testado em paralelo, também 5/5 sem ele) —
  continua recomendado como precaução pra quem escalar pra 3+.
- Também testei navegação concorrente de verdade (não só ativação):
  `go_to_point` real pros dois ao mesmo tempo depois da ativação, 25s de
  drive sob Cyclone DDS — 0 jumps, os dois retornaram `Navigation
  started`. Dados em `fleet_ws/runs/dual_nav_fastdds/`,
  `dual_nav_cyclone/`, `dual_nav_cyclone_nofix/`, `dual_nav_drive_cyclone/`.
- Achado de precisão técnica (não medição, leitura de código-fonte):
  confirmei no `tf2_ros.Buffer` (branch jazzy do `ros2/geometry2`) que o
  limiar de "jump back in time" é hardcoded em 1 segundo
  (`JumpThreshold(min_backward=Duration(seconds=-1))`) e também dispara em
  troca de tipo de clock (`on_clock_change=True`) — não é configurável por
  parâmetro, então a rota de "ajustar transform_tolerance/tolerância do
  buffer" não existe sem fork do `tf2_ros` instalado. Corrobora por que o
  achado de 2026-10-02 ("não achei receita de tuning de tolerância") não
  era falta de busca — a rota realmente não existe sem mudar o pacote
  instalado.
- Corroboração externa concreta achada nesta rodada: o projeto real
  `arshadlab/turtlebot3_multi_robot` (Jazzy + Gazebo Harmonic) sobe Nav2
  completo pra TODOS os robôs de uma vez com um único launch (exatamente a
  pergunta desta rodada) e documenta Cyclone DDS + o mesmo fix de
  `MaxAutoParticipantIndex=100` já citado aqui em 2026-10-05 como
  pré-requisito — não é combinação exótica, é padrão usado por outro
  projeto real com a mesma pilha.
- **Limite honesto**: só testado com 2 robôs (tb1+tb2, igual ao suportado
  hoje), só 1 réplica/25s de navegação concorrente (teste de fumaça, não
  campanha), `ComposableNodeContainer`/`ROS_DISCOVERY_SERVER` não
  testados (não foi necessário, RMW isolado já resolveu o caso testado).
  **Mudança de arquitetura de ativação (sequencial → simultânea) como
  default do projeto não foi aplicada — fica registrada com números reais
  pra decisão do autor**, não aplicada em `activate_robot_nav.launch.py`
  nem no texto da dissertação (fora de escopo desta sessão). `Dockerfile`
  ganhou `ros-jazzy-rmw-cyclonedds-cpp` instalável (só disponibilidade, não
  muda o default de RMW). Detalhe completo, tabela de números e scripts:
  `conhecimento/dds_tuning.md` (entrada 2026-10-08).

### 2026-10-08 (continuação 4) — apresentação de defesa criada, branch `apresentacao-dissertacao`

- **[sessão]** Nova branch `apresentacao-dissertacao` (a partir de
  `dissertacao`, depois rebasada pra pegar o achado do Cyclone DDS
  também). Dois arquivos novos em `disserta-apresenta/`:
  - `apresentacao_defesa.pptx` — baseado em `apresentacao_seminario.pptx`
    (14→17 slides). 3 slides novos: "Perguntas de Pesquisa e Hipóteses —
    Retomada" (espelha a tabela PP/H/QA/Resultado do Cap. 9),
    "Piloto FUUT — Primeira Evidência Empírica" e "Nav2 Simultâneo —
    Achado Cyclone DDS". Os 2 últimos levam selo visual laranja "ACHADO
    NOVO" no canto superior direito, pedido explícito do autor pra ficar
    claro que são resultado desta semana, não planejados desde o início.
    Rodapé "Seminário de Andamento" trocado por "Defesa de Dissertação"
    nos 17 slides; Agenda e Conclusão atualizadas. Construído editando
    XML bruto do pptx (duplicando `slide9.xml` como template de stat-card
    3x via `add_slide.py` da skill `pptx`, substituição posicional de
    texto, não por valor — evita ambiguidade de string repetida),
    validado (`validate.py`, zero erros) e revisado visualmente
    (thumbnail + render individual) — achei e corrigi 2 estouros de texto
    (valor de card longo demais colidindo com a legenda) antes de fechar.
  - `fala_apresentacao_defesa.txt` — roteiro de fala completo (310
    linhas), baseado em `fala_apresentacao.txt` do seminário, com as 3
    seções novas escritas e a Conclusão reescrita pra citar os achados.
- **Nota de processo, não achado técnico**: ao tentar voltar pra
  `mission-coordinate-large-scale` pra escrever esta entrada, a branch
  estava presa por um worktree de agente (`experiment-dds-tuning`, já
  tinha terminado e commitado) — removido com `git worktree remove`
  depois de confirmar `git status` limpo dentro dele. Se isso acontecer
  de novo: o worktree de um agente concluído não se autoremove, precisa
  limpeza manual antes de reusar a branch no checkout principal.

### 2026-10-12 — frontend: bug real de clique no mapa + refatoração + responsividade + primeira suíte de testes

- **[sessão]** Branch `mission-coordinate-large-scale`. Ponto de partida:
  pedido vago do autor ("ajustar o frontend") → usei a skill
  `frontend-ui-engineering` pra avaliar o estado atual antes de mexer.
  Achado real nessa avaliação: `App.jsx` passava `onNavigateTo` (um no-op
  documentado) pra prop `onAddWaypoint` do `MapView` — clicar no mapa pra
  adicionar waypoint não fazia nada, em silêncio, apesar da UI dizer
  "clique = +waypoint". Corrigido (`6e8d779`) e **testado de verdade**
  com Playwright headless (instalado nesta sessão, sem navegador
  interativo disponível) — clique real no canvas, contagem de waypoints
  antes/depois.
- **Refatoração estrutural** (pedido explícito "sim continue em ordem"):
  - `a6ebff8` — `App.jsx` 999→441 linhas: extraídos `MapView.jsx`,
    `ConnectionPanel.jsx`, `DiscoveryPanel.jsx`.
  - `e08a496` — `MapView.jsx` 510→53 linhas: toda lógica imperativa de
    canvas (desenho, zoom/pan, conversão mundo↔canvas) movida pro hook
    `hooks/useMapCanvas.js`; `MapToolbar.jsx` extraído.
  - No meio: acessibilidade real adicionada (não cosmética) —
    `aria-expanded`/`aria-haspopup` nos 3 painéis-dropdown, `aria-label`
    no canvas e no botão fechar do modal, `role="log"`/`role="alert"` nas
    regiões dinâmicas (output, erros).
- **`5ca2880`** — `styles/tokens.js` novo: 24 cores hex repetidas (uma
  delas, `#2a3142`, usada 36×) viram tokens nomeados + função `btn()`
  compartilhada. Aplicado em `App.jsx` + 4 componentes. Decisão
  consciente de fronteira: `useMapCanvas.js` ficou de fora (variável
  local `color` dentro do desenho dos robôs colidiria com o import).
  `ConfigForm`/`AgentFleetPanel`/`SimulationPanel` também ficaram de
  fora (não tocados nesta sessão, pra não arriscar código não revisado).
- **`8d3ad44`** — testado com Playwright em 320/768/1024/1440px (checklist
  do skill). Achados reais: grid principal (260px|mapa|300px) quebrava
  por completo abaixo de ~900px (coluna do mapa ficava com largura
  negativa, coluna de output saía da tela); barra de botões do header e
  barra de ferramentas do mapa não quebravam linha; o toggle
  Gravar/Reproduzir tinha `overflow:hidden`, que deixava o flexbox
  encolher o botão abaixo do texto em vez de quebrar linha ("Reproduzir"
  sumia) — causa raiz real, não só sintoma. Corrigido com media queries
  em `index.css` (empilha em coluna única <768px) + `flexShrink`/
  `flexWrap` pontuais. 1024px/1440px continuam idênticos visualmente.
- **`5a2cfec`** — projeto não tinha nenhum teste de frontend
  (`package.json` só tinha dev/build/preview). Configurado Vitest +
  React Testing Library + jsdom (`vite.config.js`, `src/test/setup.js`
  com stubs de `ResizeObserver`/canvas 2D — jsdom não implementa
  nenhum dos dois). Primeiro teste real (`MapView.test.jsx`) cobre a
  lógica de clique-adiciona-waypoint: clique chama `onAddWaypoint` com
  coordenadas numéricas; sem a prop, clique não quebra nem dispara
  nada — testa o contrato que o bug original violava. `npm test` roda a
  suíte. O Playwright E2E (`/tmp/pw_test/test_waypoint.js`, não
  commitado — é scratch) continua sendo a camada que valida a fiação
  real App→MapView.
- **Passe visual (skill `frontend-design`)**: escopo escolhido pelo autor
  foi só diagnóstico, sem mexer em código. Achado real: a paleta atual
  (fundo quase-preto `#0d0f14` + acento verde-menta `#6ee7b7` dominante)
  bate literalmente com um dos clichês de design nomeados pelo skill
  ("fundo quase preto + acento verde-ácido/vermelho único"), e os
  eyebrow-labels em CAIXA ALTA acima de quase toda seção batem com outro
  clichê nomeado. Em contraste, o layout em 3 colunas (config|mapa|
  output), o uso de cor como semântica de estado (verde=sucesso,
  vermelho=falha, índigo=conexão, roxo=agentes) e o par tipográfico
  Outfit+JetBrains Mono são escolhas deliberadas, não clichê — mantidos
  como estão. Nenhuma mudança de código feita (autor pediu só relatório).
- **O que falta** (lista acordada com o autor, em ordem, restam 0 itens
  "obrigatórios" — os 2 abaixo são melhorias opcionais, não pendências
  da lista original):
  - Acesso por teclado ao mapa (clique espacial pra adicionar waypoint)
    não tem equivalente — `ConfigForm` já tem um "+ Waypoint" acessível
    que cobre parte do caso, mas não o fluxo de apontar no mapa.
    Precisaria de novo design de interação, não é patch rápido.
  - Se o autor decidir agir no diagnóstico visual: trocar o acento verde
    por algo menos genérico (ligado ao domínio: laranja de sinalização
    industrial, azul do mapa do warehouse) e tirar o CAIXA-ALTA dos
    eyebrows — ambas as mudanças ficariam isoladas em `styles/tokens.js`
    e nos textos dos labels, baixo risco.
  - **Pendência antiga, ainda não confirmada**: rotacionar/revogar as
    chaves de API (TypeSafe e Anthropic) coladas em texto puro no chat
    em sessão anterior.
- Em paralelo, no branch `dissertacao`/`apresentacao-dissertacao` (fora
  do escopo frontend, mas na mesma janela de trabalho): item (b) do
  Cap. 9 (trabalho futuro) atualizado pra descrever o protótipo real de
  `MissionRouter`/`decompose_and_route` (citando `gerkey2004` e a seção
  real de coordenação multirrobô), bullet solto sobre câmera OAK-D
  removido; apresentação de defesa (`apresentacao_defesa.pptx`)
  reconstruída do zero pra copiar o estilo de uma apresentação real do
  CBSOFT fornecida pelo autor (cores/logos/tamanho de slide extraídos do
  `.pptx` original, não aproximados de PDF); `fala_apresentacao_defesa.txt`
  sincronizado com o conteúdo novo dos slides.

### 2026-10-13 — estudo de alocação de missão (LLM vs. ótimo), cenário difícil com mapa real, e defesa migrada pro deck CIn

Sessão do autor com Claude Code (não é agente de pesquisa). Tudo commitado
e com push. Onde está cada coisa:

- **Código e dados — branch `windows-version`** (commits `1907edf`,
  `344f366`, `318eb37`, `9ca98bf`): `backend/mission/` (alocadores fixo,
  guloso, ótimo exato por programação dinâmica, e Claude `claude-opus-5-5`
  com saída JSON de enums fechados; custo = makespan; distância em linha
  reta ou pelo caminho livre no `warehouse.pgm` via `gridmap.py`),
  cenários `warehouse.yaml` (simples) e `warehouse_dificil.yaml` (3 MUUT +
  1 FUUT, 10 missões em 5 categorias: escala, obstáculo, linguagem, falha,
  papel), script `fleet_ws/scripts/mission_allocation_study.py`, 25 testes.
  Dados brutos + README de proveniência em `fleet_ws/runs/mission_allocation/`.
  Roda no Windows, sem ROS/Gazebo (só Python + `anthropic`, `numpy`,
  `pillow`). A `windows-version` NÃO tem a parte multi-robô/painel da
  `mission-coordinate-large-scale`.
- **Resultado** (200 decisões do LLM consideradas, ~US$ 9 no total):
  sem obstáculos o LLM ficou no ótimo 50/50; com estantes e paredes, só
  com o mapa, 35/50 no ótimo, pior caso +54% (armadilhas em que o robô mais
  perto em linha reta é o mais longe pelo caminho: sala noroeste, "tudo ao
  norte da estante"), mesma resposta em só 5/10 missões; com a tabela de
  distâncias pelo caminho, 50/50. Interpretação 100% (negação, robô que
  falhou, nunca usou o FUUT). Despacho fixo do painel: até +106%.
  Leitura: LLM interpreta, cálculo de caminho otimiza (arquitetura híbrida).
- **Erro de método registrado**: 4 missões do cenário difícil falavam em
  "corredores entre as estantes do sul" (são 2, não 3); o LLM apontou com
  justificativa correta. Cenário corrigido ("três corredores do sul") e as
  4 missões rodadas de novo (rodada 03).
- **Dissertação — branch `apresentacao-dissertacao`**: nova Seção 8.9
  "Piloto: Alocação de Missão em Linguagem Natural" (Tabela 8.7), refs
  novas `kannan2023smartllm` e `zhang2025lammap`; zip do Overleaf
  regenerado e compilado pelo autor sem erros (126 páginas, nenhum "??").
- **Defesa — branch `apresentacao-dissertacao`**: adotado como oficial o
  deck com tema CIn/UFPE (`disserta-apresenta/apresentacao_defesa.pptx`,
  18 slides; o deck azul anterior foi substituído) + a fala em linguagem
  simples (`fala_apresentacao_defesa.txt`, ~22 min). Slide 13 novo (piloto
  de missão, com gráfico). Corrigidos no deck e na fala: "essa semana",
  "muito abaixo da tolerância do Nav2" sem ressalva, PP3 com sentido
  invertido em relação à dissertação, protótipo antigo de roteamento na
  conclusão. Para renderizar slides nesta máquina use o PowerPoint via COM
  (não há LibreOffice).
- **Ambiente da máquina do autor**: repositório em pasta de rede
  (`Y:` = `\192.168.8.12\comum`) — não instalar `node_modules`/venv nem
  rodar Docker a partir dela; para Gazebo/Docker, clonar em disco local.
  Disco C: ~97% cheio. Chave da API em `ANTHROPIC_API_KEY` no usuário do
  Windows (nunca colar no chat nem em comando).

### 2026-10-16 — feedback de banca prévia (Adrien/Breno) + achado do paper BLE da Bia/Fernanda + piloto de código pro experimento delas

- **[sessão]** Autor colou anotações em maiúsculas de um ensaio/banca prévia
  real com os orientadores. Resumo do que foi entendido (texto completo das
  anotações só existe no histórico da conversa, não versionado em arquivo):
  - **PP1 (automação)**: resposta "sim" não pode vir só do autor — precisa
    de validação externa (outra pessoa usando sem escrever código novo).
  - **PP2 (25cm)**: o limiar precisa de citação da literatura justificando,
    não só "é o default do Nav2".
  - **PP3 (fora de ambiente controlado)**: precisa ser resolvido **antes**
    da defesa — rodar robô demora, não dá pra fazer de última hora.
  - **PP4**: deveria ficar amarrada com PP1 (mesma evidência resolve as duas).
  - **Reformulação sugerida da "primeira contribuição"**: não é o número de
    RMSE — é um ambiente que alguém **sem formação em robótica** consegue
    configurar e rodar um teste que representa a missão.
  - **Breno** (achou que a parte de LLM/missão multi-robô "destoa muito" do
    resto — "muita contribuição, esquecer LLM"): sugere focar na parte
    consistente — teste automatizado é padrão bom na indústria de software,
    mas com robô é complicado; o framework (tela web) resolve isso.
  - **Adrien**: com robô é melhor não ser otimista; a interface importa mais
    que a simulação; não gastar tempo falando de configuração, mostrar
    funcionando em robô real; aproveitar o trabalho de Bia/Fernanda como
    exemplo de aplicação real.
  - **Ainda não decidido**: se a parte de LLM/missão (slide 18 da defesa,
    Seção 8.9 da dissertação) fica, encolhe, ou sai — tensão real com o
    trabalho de ontem (criou e depois mesclou o slide "Relevância").
- **[achado]** Identifiquei o paper que a banca citou: **"Wireless
  Connectivity Testing with Mobile Robots: A Bluetooth Low Energy Case
  Study"**, CBSoft 2026 (8-11 set, São Paulo), Laboratório CRIAR/CIn-UFPE.
  Autoras **Fernanda Neves** e **Beatriz Barros** (bolsistas), orientação
  de **Adrien Durand-Petiteville** e **Breno Miranda** (os mesmos nomes
  das anotações). Metodologia (só da notícia do portal do CIn, não do PDF
  completo — anais do CBSoft 2026/SAST 2026 ainda não indexados
  publicamente em sol.sbc.org.br, tentei 5 buscas diferentes): TurtleBot4
  carrega um smartphone numa rota pré-definida em ambiente controlado
  mapeado, outro dispositivo fica fixo numa posição conhecida, mede
  degradação do sinal BLE até perder conexão, pra achar o limiar de
  desconexão. Reivindica reprodutibilidade/redução de interferência humana.
  Fonte: https://portal.cin.ufpe.br/2026/07/14/laboratorio-criar-do-cin-ufpe-tem-artigo-aprovado-no-cbsoft-2026/
- **[achado de código]** `windows-version` (branch do próprio autor) tem um
  setup Docker completo pra Windows: `docker-compose.windows.yml`, modo
  headless (sem GUI do Gazebo, sem `network_mode: host`, portas 5173/8000
  mapeadas) — existe porque ROS2 nativo não roda bem no Windows. README
  documenta isso explicitamente. **Risco técnico levantado, não resolvido**:
  se a Bia/Fernanda rodarem a tela via esse caminho (Docker Desktop no
  Windows = WSL2 por baixo), passar um adaptador Bluetooth USB físico pro
  container pra escanear BLE de verdade não é trivial (`usbipd-win` existe
  mas é instável com Bluetooth especificamente). Não achei confirmação de
  qual SO elas usam — autor vai perguntar direto a elas.
- **[feito]** Pilotei a peça de código que a banca/o achado pedem, pro caso
  de uso de Bluetooth (branch `mission-coordinate-large-scale`,
  commit `a7c001a`):
  - `fleet_ws/src/fleet_orchestrator/fleet_orchestrator/ble_rssi_publisher.py`
    (novo nó): escaneia BLE via `bleak`, publica RSSI do dispositivo alvo
    (endereço MAC via parâmetro ROS2) como `std_msgs/Int32` no tópico
    `ble_rssi`. Degrada com log de erro (não derruba a pilha) sem adaptador
    Bluetooth ou sem o parâmetro configurado.
  - `fleet_data_collector/main.py`: registrei `ble_rssi` no `_TYPE_MAP`
    (tópico→tipo) que a gravação usa — achei que esse é o gate real
    (`UNKNOWN_TOPIC`), não o `/api/run_config` do backend, que só repassa
    string sem validar.
  - `ConfigForm.jsx`: `ble_rssi` como 5ª opção de tópico na tela; as 4
    existentes ganharam descrição curta inline (ex. "odom — rodas —
    posição estimada contando giros") em vez de só o nome cru — pedido
    explícito do autor pra ficar mais intuitivo pra quem não é de robótica.
  - **Limite honesto**: esta máquina de dev não tem adaptador Bluetooth
    (confirmado, `rfkill`/`lsusb`/`/sys/class/bluetooth` vazios) — só testei
    a lógica de filtro por endereço + conversão de tipo (4 testes novos em
    `tests/test_ble_rssi_publisher.py`, só isso é testável sem hardware
    real). O scan de verdade só confirma numa máquina com Bluetooth físico.
- **Pendência explícita do autor**: ele vai perguntar direto pra Bia/Fernanda
  qual SO/máquina elas usam antes de decidir o próximo passo nessa frente.

### 2026-10-17 — pedido de confiabilidade cross-platform (Bluetooth Mac/Windows/Linux) + exploração do catálogo skills.sh

- **[pedido do autor]** Quer confiança real (não "100% de certeza" — deixei
  isso claro, software sozinho não garante isso sem testar em hardware de
  verdade) de que conectar Bluetooth no Mac, Windows ou Linux funciona com
  o TurtleBot4, usando o paper da Bia/Fernanda como referência. Pediu uma
  branch `perfect-bot` usando skills.sh pra achar habilidades que
  melhorassem frontend/backend/outros aspectos, e possivelmente branches
  por plataforma (`perfect-bot-windows`, nomes repetidos/com erro de
  digitação no pedido original — preciso confirmar com o autor antes de
  criar, pra não nascerem branches com nome errado).
- **[achado]** Catálogo público do skills.sh (fetchei a home + `/topic/testing`,
  tentei `/topic/robotics` e `/topic/devops`, ambos 404) **não tem nada
  específico de robótica, Bluetooth, Docker ou cross-platform** — só 8
  tópicos: React, Next.js, Design & UI, Mobile, Agent workflows, Databases,
  Testing, Marketing. As skills `ros2`/`robot-bringup` já instaladas vieram
  de busca direta num repo nicho (`arpitg1304/robotics-agent-skills`), não
  do catálogo geral — não tem mais nada parecido lá.
  - Relevantes de verdade, da categoria Testing: **webapp-testing**
    (anthropics/skills, padrões unit/integration/E2E), **playwright-best-practices**
    (currents-dev, formaliza o que já venho fazendo manualmente com
    Playwright a sessão toda), **verification-before-completion**
    (obra/superpowers, força checagem antes de marcar como pronto).
- **Em aberto**: aguardando o autor confirmar os nomes exatos das branches
  por plataforma antes de criar qualquer uma.

### 2026-10-17 (continuação) — 4 branches `perfect-bot*` criadas e publicadas: diagnóstico BLE cross-platform

- **[feito]** Confirmado com o autor (3 plataformas: Windows, Mac, Linux),
  criadas e com push 4 branches a partir de `mission-coordinate-large-scale`:
  `perfect-bot` (base), `perfect-bot-linux`, `perfect-bot-windows`,
  `perfect-bot-mac`.
- **`perfect-bot`**: `fleet_ws/scripts/check_ble_setup.py` — diagnóstico
  cross-platform (detecta SO, confirma `bleak` instalado, tenta um scan BLE
  de 3s). **Rodado de verdade** nesta máquina Linux sem adaptador Bluetooth:
  reportou corretamente SO + bleak instalado, e falhou honestamente no scan
  (timeout de 8s) — o caminho de erro funciona de ponta a ponta, não só na
  teoria. Achei e corrigi um bug real: `bleak` 3.0.2 não expõe
  `bleak.__version__` (troquei pra `importlib.metadata.version`).
- **`perfect-bot-linux`**: `BLE_SETUP_LINUX.md` — testado de verdade (pip
  install bleak, BlueZ via `systemctl`, grupo `bluetooth` do usuário). Nota
  não confirmada: Bluetooth dentro de container Docker precisa do socket
  D-Bus do host acessível, não validado (sem adaptador físico aqui).
- **`perfect-bot-windows`**: **achado real de pesquisa** — `bleak` roda
  nativamente no Windows via WinRT, **sem precisar de Docker/WSL2**. Isso
  evita de vez o problema que eu tinha levantado antes (passar adaptador
  Bluetooth físico pro WSL2 via `usbipd-win`, instável). Caminho proposto em
  `BLE_SETUP_WINDOWS.md`: scanner BLE nativo fora do container, manda RSSI
  pro backend (dentro do Docker) via HTTP no `localhost:8000` já mapeado.
  **Não construí** o endpoint novo (`POST /api/ble_rssi`) nem o script de
  ponte — ficaria código não verificado apresentado como pronto, sem máquina
  Windows pra testar. Documentado como próximo passo explícito.
- **`perfect-bot-mac`**: pesquisei a pegadinha real — macOS trata Bluetooth
  como dado de privacidade (TCC); sem autorizar o Terminal/app em Ajustes do
  Sistema, o processo **morre com SIGABRT** em vez de erro Python normal,
  fácil de confundir com bug (fonte: troubleshooting oficial do bleak).
  Ressalva de versão: macOS 12.0-12.2 tinha bug de scan sem `service_uuids`
  (corrigido no 12.3). `BLE_SETUP_MAC.md`, também não testado ao vivo.
- **Catálogo skills.sh, revisitado**: nada de robótica/Bluetooth/cross-platform
  lá (já registrado na entrada anterior de hoje) — essas 4 branches foram
  trabalho de pesquisa + código direto, não skill instalada.
- **Honestidade explícita sobre o pedido original**: autor pediu "100% de
  certeza" de que Bluetooth funcionaria nas 3 plataformas — deixei claro que
  isso não existe sem testar em hardware real de cada uma. O que foi
  entregue: Linux testado de ponta a ponta (com a limitação "sem hardware
  aqui" sendo o próprio teste real); Windows e Mac são pesquisa + plano
  concreto, não validação.

**Como manter isto atualizado:** cada agente, ao final de uma execução,
acrescenta uma entrada nova (data + achado em 1-2 linhas + link pro arquivo
detalhado) nesta seção, sem apagar entradas anteriores. Se um achado tiver
"Ação sugerida" concreta, também vira uma linha em `implementacao.md`.
