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

**Como manter isto atualizado:** cada agente, ao final de uma execução,
acrescenta uma entrada nova (data + achado em 1-2 linhas + link pro arquivo
detalhado) nesta seção, sem apagar entradas anteriores. Se um achado tiver
"Ação sugerida" concreta, também vira uma linha em `implementacao.md`.
