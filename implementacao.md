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

- [ ] **Testar `run_ground_truth_campaign.py` nas 2 rotas novas
  (`rota_longa_curva`, `loop_fechado`), não só na curta** (origem: achado
  real do autor, 2026-10-02, ao criar as rotas — ver "Feito" abaixo). O
  script só foi validado com `dissertation_clean01` (mini-campanha de 2
  réplicas). Rotas mais longas (7,7m e 11,3m vs. ~0,9m da curta) podem
  expor timeouts diferentes — `--boot-timeout` é só sobre o bringup da
  simulação, não sobre a duração do replay em si, então não deveria
  precisar de ajuste, mas isso não foi confirmado na prática. Fazer antes
  da campanha completa de 30 réplicas.

- [ ] **Avaliar composição de nós (`ComposableNodeContainer`) pra Nav2 e
  SLAM Toolbox** (origem: `dds_tuning`, 2026-10-02). Hipótese pro problema
  real dos 70% de sucesso na ativação sequencial multi-robô. Risco: médio
  (mudança de arquitetura de launch, não só parâmetro).
- [ ] **Decidir o enquadramento estatístico da campanha /odom vs /pose vs
  ground truth ANTES do piloto** (origem: `stats_methodology`,
  2026-10-02). Escolher entre: (a) concordância de método estilo
  Bland-Altman (cada fonte vs. ground truth, separadamente) ou (b) teste
  simétrico entre 3 grupos (ANOVA de medidas repetidas/Friedman) — ou
  ambos, respondendo perguntas diferentes. Bloqueante: mudar depois do
  piloto é retrabalho.
- [ ] **Avaliar adicionar o plugin `WheelSlip` ao modelo do Gazebo**
  (origem: `gazebo_tracking`, 2026-10-02). Hoje a dissertação registra
  "DiffDrive não modela slip" como limitação; existe plugin oficial que
  mitigaria isso. Decisão: vale o esforço pra este experimento, ou fica
  como limitação documentada mesmo?
- [ ] **Arquivar uma Release do GitHub no Zenodo pra gerar DOI** (origem:
  `artifact_publishing`, 2026-10-02). Baixo esforço, baixo risco, não
  exige mudar código — só criar a Release e conectar o Zenodo (exige
  login do autor no Zenodo, não pode ser feito por um agente). `CITATION.cff`
  já existe (ver "Feito") — falta só criar a Release no GitHub e ligar a
  conta do Zenodo a ela. Fazer antes da defesa pra poder citar o
  repositório com DOI na dissertação.
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

## Feito

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
