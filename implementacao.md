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

- [ ] **Validar ao vivo o alinhamento de frames (world/odom/map) ANTES do
  piloto /odom vs /pose vs ground truth** (origem: `gazebo_tracking`,
  2026-10-02, rodada 2). Pesquisa de código-fonte do `DiffDrive`/`gz-math`
  e do `slam_toolbox` indica que, pra este projeto (spawn em 0,0,0,
  yaw=0), as três fontes deveriam reportar ~(0,0,0) no instante inicial
  (antes de qualquer movimento) — mas isso é dedução de como cada peça
  inicializa isoladamente, não um teste real deste projeto. Ação
  concreta: depois do robô spawnar e parado, comparar manualmente uma
  amostra de `/ground_truth_pose_clean`, `/odom` e `/pose` (ou TF
  `map`→`base_link`) — se todas ~(0,0,0)/~0 yaw, alinhamento confirmado
  sem precisar de transformação estática; se não, suspeitar primeiro de
  timing (SLAM só processar o 1º scan depois do robô já ter se movido),
  não de convenção de eixo (Gazebo e ROS já concordam em right-handed
  X-frente/Y-esquerda/Z-cima, confirmado via REP-103 e
  `gazebosim.org/api/sim/8/frame_reference.html`). Baixo esforço, decisivo
  antes de gastar as 30 execuções da campanha principal — já está coberto
  pelo passo 2 ("piloto antes da campanha grande") do plano em
  `orquestracion.md`, só precisa incluir essa checagem explícita no
  início do piloto, não só comparar as trajetórias no fim.
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
- [ ] **Medir ao vivo as taxas reais de `/pose`, `/ground_truth_pose` e
  `/ground_truth_pose_clean` no próprio piloto, e decidir o método de
  alinhamento temporal pra reamostragem ANTES de escalar pra 30 réplicas**
  (origem: `stats_methodology`, 2026-10-02, rodada 2). `/odom` confirmado
  a 30Hz exato (`odom_publish_frequency` em `create3.urdf.xacro`); `/pose`
  pode ser só ~2Hz (`minimum_time_interval: 0.5` em `slam.yaml`, mas a
  lógica exata de combinação com os outros 2 limiares não foi confirmada,
  taxa real pode ser menor); ground truth tem números conflitantes no
  próprio `orquestracion.md` (~51-55Hz vs. ~100Hz) nunca resolvidos.
  Reamostrar as 3 fontes pra uma grade comum arbitrária (como
  `analyze_runs.py --resample-mode time` faz hoje) corre risco de
  interpolar o `/pose` esparso de forma que corte curvas da rota — o que
  poderia simular artificialmente "divergência cresce com a complexidade
  da rota" mesmo que não seja um efeito real do SLAM. Recomendação do
  agente (não decisão): considerar um modo de reamostragem que interpole
  só o ground truth (série densa) pros timestamps nativos de cada fonte a
  avaliar, em vez da grade arbitrária comum; e tratar cada réplica como 1
  observação no Bland-Altman do piloto (não pooled de todos os
  pontos-tempo de todas as réplicas — isso infla artificialmente a
  precisão aparente, confirmado via Bland & Altman 2007). Risco: médio
  (pode exigir um modo novo em `analyze_runs.py`, não só decisão de
  parâmetro). Bloqueante: decidir antes do piloto, não depois de já ter
  rodado as 30 réplicas.
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
