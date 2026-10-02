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
- [ ] **Escrever README de replicação separado do README de
  desenvolvimento** (origem: `artifact_publishing`, 2026-10-02),
  estruturado nos 4 eixos de Lier et al. (2017): artefatos técnicos,
  design de experimento, execução, avaliação dos dados.

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

## Como manter isto atualizado

- Um agente de pesquisa pode **adicionar** itens a "Pendente" (nunca
  decidir por conta própria mudar o código).
- Só o autor (ou uma tarefa de implementação explicitamente aberta por
  ele) move um item de "Pendente" → "Em andamento" → "Feito".
- Ao mover pra "Feito", registrar: data, o que mudou de fato (arquivo/
  commit), e o resultado observado (não só "implementado" — o efeito
  medido, se houver).
