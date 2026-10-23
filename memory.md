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

### 2026-10-22 (noite, cont. 3) — agentes de IA fora da dissertação + re-validação completa

- Pedido: tirar os agentes de IA (saem da dissertação), que agora termina no
  teste com o TurtleBot4 real na UFPE, junto da Fernanda e da Beatriz; atualizar
  a dissertação e re-validar cada número e afirmação técnica.
- Código (`new-way-samsung`): painel de agentes escondido (`b7167eb`,
  `VITE_SHOW_AGENTS=true` religa). Dados da campanha oficial recuperados do
  stash `5b0a82e` (`6e2484d`); os 10 bags MCAP só existem no disco desta
  máquina, **fazer backup**.
- Dissertação (`dissertacao` `f1968c0`): números do Cap. 8 reproduzidos
  exatamente dos bags brutos (só com `--trajectory-topic odom`). Corrigidos:
  desvios-padrão amostrais (1,16 cm / 0,38 s / 2,2% / 0,011 m); mecanismo
  record/replay estava invertido (o replay é que para em cada pose densa + 200 ms);
  filtro de saltos 0,12 m @ 50 Hz que nunca existiu; odom 30 Hz; RPLIDAR genérico
  e OAK-D Pro; 9 campos no RobotRuntime; ros2 service call 1,5–3 s; tf2 limpa
  buffer em qualquer recuo de relógio; "uma réplica com 2 tentativas" (os manifestos
  dizem 0); classificador LLM do piloto FUUT removido. Nova seção de estudo de caso
  CBSoft com a Tabela 3 refeita dos dados brutos (diferenças ≤0,4 dBm, ≤0,006 m/s,
  ≤0,3 m). Ressalva registrada: o robô da UFPE roda Humble, o fleet-ui roda Jazzy.
- Nome certo da autora pelo certificado do CBSoft: **Beatriz Barros** (a nota de
  2026-10-18 dizendo "Oliveira" está errada).
- Hardware: novo MCE às 20:08, ~20 min depois do reboot (matou o orquestrador
  no Docker). Defeito de RAM continua; memtest recomendado.

### 2026-10-22 (noite, cont. 2) — análise do experimento CBSoft incorporada ao fleet-ui

- Pedido: incorporar a análise das meninas (antes só a navegação estava
  integrada). Commit `116d8d0` em `new-way-samsung`, com push.
- `fleet_ws/scripts/cbsoft/bag_to_nav_csv.py`: converte a gravação MCAP do
  replay do fleet-ui no CSV do nav_3points.py (mesmas colunas, 0,2 s).
  Achados no caminho: (1) a /amcl_pose é TRANSIENT_LOCAL e chega na
  gravação com o horário do último publish, ~40 s antes, o que deslocava a
  corrida inteira; agora o início é o 1º /odom. (2) O container usa UTC e
  o log do nRF Connect é local; os comandos make passam o TZ do host.
- `fleet_ws/scripts/cbsoft/analise/`: sync_rssi_nav.py e
  analise_agregados.py delas, com argumentos, PNG sem janela, linhas (0,0)
  descartadas e base do celular = 1ª pose válida.
- `make cbsoft-csv` / `make cbsoft-analise`: rodam como o usuário do host
  (a pasta collections/cbsoft tinha virado do root via nav_3points no
  container).
- **Validação com dados reais de 19/05:** recalculando a Tabela 3 do artigo
  com a sincronização delas, RSSI médio e distância até desconectar batem
  (diferenças de décimos). A corrida com o bug (0,0) (homogênea 1, 15:57)
  deu 68,6 m contra 68,4 m do artigo, então **o artigo NÃO foi afetado**.
  Isso fecha a dúvida aberta nas notas anteriores.
- Dados delas copiados em `fleet_ws/collections/cbsoft/ufpe_2026-05-19/`
  (gitignored, não vai pro repositório), junto do `tabela3.py` de
  validação.
- Ainda não integrado: leitura de BLE no robô real e mapa real do CIn
  (hall_cin_v4).

### 2026-10-22 (noite, cont.) — `new-way-samsung` pronta pra máquina do laboratório (UFPE)

- Pergunta do usuário: "vai funcionar o experimento na UFPE?". Dois
  bloqueios achados e corrigidos (commit `a320f8f`):
  1. O README mandava `git clone -b perfect-bot`, que não tem o percurso
     CBSoft. Agora aponta pra `new-way-samsung`.
  2. ROS_DOMAIN_ID=0 no Docker: na rede da UFPE, a simulação se misturaria
     com TurtleBot4 reais (padrão 0), e o Nav2 simulado poderia comandar
     robô real. `make cbsoft-up` agora usa o domínio 42 (CBSOFT_DOMAIN).
     Testado: funciona no 42 e é invisível pro domínio 0.
- Ainda não validado na máquina de lá (Ubuntu 22.04): instalação do Docker
  Engine + plugin compose, primeiro build (~15–30 min), RViz/X11 sem
  monitor. O experimento com o ROBÔ REAL não passa pelo fleet-ui (conectar
  por SSH não está implementado); o script delas (nav_3points.py) no robô
  real continua como era.
- Erros MCE: o histórico real são 3 dias com erro em ~3 semanas
  (30/09: 1, 18/10: 1, 21/10: 4). O "7 erros em 18/10" das notas
  anteriores estava errado: era 1 erro com 7 linhas de log.

### 2026-10-22 (noite) — branch `new-way-samsung`: revisão de código do diff inteiro da branch

- Pedido: "aprofunde no código". Revisei os 6 commits sobre a
  `perfect-bot` (~400 linhas de lógica) e corrigi o que importava (commit
  `e5dc4b3`, com push):
  1. Frontend: rota de outro mundo (percurso_cbsoft com o armazém aberto)
     podia ser executada e mandava o robô pra fora do mapa. Agora conta os
     pontos fora da área conhecida (mapa ao vivo + planta do mesmo lugar)
     e bloqueia o "Executar replay" com aviso. Testado nos dois mundos.
  2. experiment_repeatability.py: volta ao início que falhava seguia pro
     replay e gravava corrida partindo do lugar errado. Agora aborta antes
     de gravar (error_code RETURN_TO_START_FAILED).
  3. Backend: /amcl_pose sobrescrevia a pose do TF ("pulo pra trás");
     agora só entra se o TF está sem responder há mais de 1 s. Pose vira
     inválida/stale sem TF nem pose_topic há mais de 2 s: testado matando
     o AMCL, fica inválida em ~12 s (10 s de buffer TF + 2 s). Antes,
     ficava válida pra sempre.
  4. /api/status devolve cópias (o JSON sai fora da trava); tf_last_rx sob
     trava. Comentário errado sobre SIGBUS/shm no compose corrigido.
- Não corrigido (menor): a planta do armazém aparece um instante antes do
  mapa ao vivo chegar; no armazém isso é útil.
- Máquina reiniciada em 2026-10-22 19:42: 0 erros MCE desde então (até
  ~21h). Memtest ainda não rodado.
- 110 testes passam no container.

### 2026-10-22 (madrugada) — ⚠️ HARDWARE COM DEFEITO nesta máquina + auditoria completa do frontend/backend

- **Achado mais importante:** a máquina de dev (AMD Ryzen 7 5800XT, 48 GB
  RAM) tem **erros de hardware não corrigíveis (MCE)**, registrados no
  kernel. `journalctl -k -b 0 | grep -E "Hardware Error|MCE: Killing"`
  mostra 4 nesta inicialização, em núcleos diferentes (7, 12, 15), todos
  "Instruction Fetch Unit… Poison". A inicialização `-b -3` (18/10) teve
  `MC15 … UECC … Deferred … Poison … Scrub` no controlador de memória.
  Suspeita principal: **RAM instável** (pente com defeito ou perfil
  XMP/EXPO agressivo). Recomendado ao usuário: memtest86+ (opção no menu
  do GRUB), testar sem XMP/EXPO e testar pente a pente.
- O kernel mata com SIGBUS todo processo que mapeia a página corrompida.
  Quando a página é código do Python, morrem todos os processos Python de
  todos os containers juntos. Isso explicou falhas que pareciam bugs:
  - 22:44: matou o `amcl`. O `map→odom` parou de ser publicado e o
    planner abortou a "volta ao início" com "extrapolation into the past"
    (o "relógio congelado" das notas anteriores).
  - 23:12: matou o Nav2 inteiro na 2ª tentativa de volta ao início.
  - 23:49: matou backend, fleet_orchestrator, sensor_collector e
    ground_truth_filter juntos (exit -7 / 135).
  - Provavelmente também o "Gazebo server morreu e só a GUI ficou" de
    2026-10-21.
  **Antes de culpar o software por um crash aleatório nesta máquina,
  rode o grep acima.** Testes de estabilidade/repetibilidade feitos aqui
  podem ter falhas que não são do código.
- Bugs de software reais achados na auditoria, corrigidos e medidos
  (commits `eb8ef33`, `f81b090` em `new-way-samsung`):
  1. Sincronia: no backend, `nav2_check_cb` (subprocess de ~2 s) estava no
     callback group padrão, que é mutuamente exclusivo. Isso travava todos
     os callbacks e o /tf chegava em rajadas. Com group próprio, a pose
     na tela vs real passou de mediana 1,04 m (máx 4,3) a 0,16 m (máx
     0,52), as atualizações de 0,8/s a 5/s e a latência HTTP máxima de
     1,7 s a 25 ms.
  2. 11 endpoints `async def` com subprocess bloqueante congelavam o
     servidor HTTP (até 40 s no "Procurar"). Viraram `def`.
  3. Agentes IA "Connection error" no Docker: a imagem pegava versões
     soltas do pip, e o python3-brotli 1.1.0 do Ubuntu quebra o httpx2.
     Agora usa requirements.lock.txt + brotli==1.2.0 (setup.sh também usa
     o lock).
  4. Histórico de Execuções sumia: runs_history virou volume montado.
  5. Ground truth mudo no headless (faltava SceneBroadcaster) e com índice
     errado no cbsoft_open (robô = entidade 0, não 2).
  6. Gravação: amcl_pose e ground_truth_pose_clean na interface (com AMCL,
     /pose gravava 0 msgs).
  7. Agentes IA com tb1/tb2/tb3 fixos → robôs que o backend vê.
     "Iniciar simulação" bloqueado com simulação externa rodando.
  8. DDS só por UDP (FASTDDS_BUILTIN_TRANSPORTS=UDPv4) e restart:
     on-failure no backend. Isso foi aplicado achando que o SIGBUS era
     /dev/shm; era hardware, mas a mudança é inofensiva e evita acumular
     segmentos órfãos.
- Revisitar: a "volta ao início" automática foi retirada do frontend por
  um diagnóstico errado (era o hardware matando o AMCL/Nav2). Vale
  re-testar numa máquina estável antes de religar.

### 2026-10-21 (noite, cont.) — branch `new-way-samsung`: replay do percurso CBSoft pelo frontend + prints

- Pedido do usuário: abrir o frontend já em Reproduzir + `percurso_cbsoft`
  e clicar pra executar. Também: tirar os 2 mapas sobrepostos (a planta
  do armazém por cima do mundo aberto) e "usar os plugins de frontend"
  (skill frontend-ui-engineering) pra melhorar a tela.
- Esclarecido pro usuário: "Conectar robô" NÃO procura Bluetooth, só testa
  se o backend responde. BLE no fleet-ui é o nó opcional
  `ble_rssi_publisher` (tópico ble_rssi + MAC). Na simulação ele não
  significa nada (o celular não se mexe) e não está ligado no Docker.
- Frontend: abre em Reproduzir + percurso_cbsoft. Desenha o percurso da
  rota escolhida (novo `GET /api/route_poses`, nome validado contra
  `../`). A planta só aparece se o mapa ao vivo cabe na área dela; senão o
  botão vira "Planta · outro mapa", desativado.
- Bugs achados ao vivo, corrigidos e testados:
  1. `--wait-goal` fixo de 300 s cortava o replay (~390 s): marcava
     FALHOU, desligava a coleta no meio e o "Percurso" saía 75 m. Agora é
     proporcional ao tamanho da rota (694 s pro CBSoft).
  2. "Nav2 OFF/offline" com o robô andando: a checagem só olhava
     simulação subida pelo backend, e `ros2 lifecycle get` leva ~2,0 s
     contra um timeout de 2 s. Agora checa sim externa (Docker/run_all.sh)
     e o timeout é 5 s.
  3. CPU saturada (carga ~20 em 16 núcleos; GUI do Gazebo ~430% + RViz
     ~270%): o controle caía pra 3 Hz e o Nav2 abortava. O modo CBSoft
     agora é HEADLESS + RViz com config vazia a 1 fps + mapa a 0,10 m.
     Carga ficou em ~2,4.
  4. Nav2 abortava rota longa com "Timed out ... acknowledge goal request
     for compute_path_to_pose": `default_server_timeout` do TB4 é de
     20 ms. Com `NAV2_DEFAULT_SERVER_TIMEOUT_MS=1000` e
     `NAV2_NAVFN_USE_ASTAR=true` (opt-in por env, só no `make
     cbsoft-up`), as campanhas do armazém não mudam.
- Validado: replay pelo navegador (Playwright clicando os mesmos botões)
  deu "Sucesso", 96,13 m, 0,247 m/s, Nav2 ON. Prints em
  `docs/images/cbsoft/` e no README.
- NÃO resolvido: volta automática ao início ("Retornar ao início") numa
  rota de ~95 m. Primeiro abortava num goal diagonal único; refazendo o
  percurso ao contrário (já implementado, a partir do ponto mais próximo)
  chegou até ~19 m do início e abortou com "extrapolation into the past"
  (pose com carimbo antigo no replanejamento após recuperação do Nav2).
  O preenchimento automático foi retirado. Pra repetir: `make cbsoft-up`.
  Solução melhor pendente: reposicionar o robô direto no Gazebo
  (set_pose + /initialpose) em vez de dirigir de volta.
- Commits `4750926`, `80ef60c`, `765e608` em `new-way-samsung`, com push.

### 2026-10-21 — branch `new-way-samsung`: percurso BLE do CBSoft'26 rodando no Docker num mundo aberto

- Contexto: artigo da Fernanda Neves e da Beatriz Barros (UFPE, com Adrien
  Durand-Petiteville e Breno Miranda), premiado como Artigo de Destaque no
  CBSoft'26 / SBES IIER. Material recebido em
  `~/Downloads/CBSoft-*/CBSoft/`. O TurtleBot4 leva um celular por um "L"
  (64 m reto + 31 m) até a conexão BLE cair. Tem 6 corridas do robô
  (2026-05-19) e uma pasta `human_test/` com 12 corridas a pé com GPS
  (2026-07-14) que ainda não estão no PDF submetido. Esse é o experimento
  de comparação que o artigo promete, mas não mostra.
- Pedido do usuário: rodar o percurso do script delas (`nav_3points.py`)
  pelo Docker do fleet-ui, num lugar aberto (sem bater em nada), vendo
  pelo frontend.
- Feito: mundo `cbsoft_open` (gerado por
  `fleet_ws/scripts/cbsoft/gen_open_world.py`), com chão aberto, paredes
  na borda e pilares a ≥2,5 m do percurso. Usa mapa pronto + AMCL e o
  frame `map` igual às coordenadas do hall_cin_v4, então o script roda
  com as coordenadas originais. O launch ganhou `localization:=slam|amcl`.
  Atalhos: `make cbsoft-up` / `make cbsoft-run`.
- Bug achado (vale avisar as autoras): o script original assina
  `/amcl_pose` como VOLATILE, mas o AMCL publica TRANSIENT_LOCAL e só
  republica com movimento. Resultado: as primeiras linhas do CSV saem em
  (0,0). Aconteceu em 1 das 6 corridas reais (`2026-05-19_15-57-33`, a da
  Fig. 4 esquerda). Somar o caminho a partir da 1ª linha infla a distância
  em ~17 m. A Tabela 3 parece coerente, provavelmente tratado, mas falta
  confirmar. O backend tinha o mesmo problema em `/map` e `/amcl_pose`.
  Corrigido nos dois.
- Validado: 2 corridas completas, 96,3 vs 96,5 m, 0,254 vs 0,253 m/s
  (artigo: 0,244 a 0,253), 382 vs 383 s.
- Incidente: na 1ª subida do Docker o servidor do Gazebo morreu e só a
  janela (`gz sim -g`) ficou viva, pedindo "list of world names" em loop.
  Não era RAM nem GPU. `docker compose down` + subir de novo resolveu.
- Commit `2006f4a` em `new-way-samsung`, com push.

### 2026-10-18 (noite, cont. 4) — branch `perfect-bot`: README fixa `perfect-bot` nos comandos de clone

- Achado real (apontado pelo usuário): `main`, a branch padrão do
  repositório no GitHub, **não tem** `run_all.sh`/`setup.sh` nem nada
  do que foi construído hoje — um `git clone <repo-url>` sem
  `-b perfect-bot` cairia numa branch onde o README inteiro (Quick
  start incluso) não bate com o que existe no disco. Toda a validação
  de "clone limpo funciona" desta sessão foi feita clonando
  explicitamente `perfect-bot` — sem fixar isso no README, a validação
  não valeria pra quem seguisse o comando literal do documento.
- Corrigido: os 2 `git clone` do README agora especificam
  `-b perfect-bot`, com nota logo no topo do arquivo explicando o
  porquê. Commit `93b7098` em `perfect-bot`, com push.

### 2026-10-18 (noite, cont. 3) — branch `perfect-bot`: Docker validado de ponta a ponta de verdade — é o caminho mais garantido entre máquinas

- Pergunta do usuário: existe opção técnica melhor pra isso funcionar
  100%? Resposta: Docker, porque fixa a versão de SO+ROS2+deps dentro
  da imagem — o caminho nativo (`setup.sh`+`run_all.sh`) continua
  dependendo do ROS2 Jazzy do sistema bater certinho, o que varia
  entre máquinas; essa é a fonte real de "funcionou aqui, não lá".
- Validado de verdade, não só o build (que já tinha sido confirmado
  antes): pausei a stack nativa do usuário (só backend+frontend,
  simulação e dados gravados intactos), subi `docker compose up` de
  verdade — sim+fleet+backend+frontend todos de pé, mapa/LiDAR/pose do
  robô renderizando ao vivo na tela, idêntico ao caminho nativo.
  Confirmado via curl + screenshot Playwright. Depois derrubei o
  Docker (`docker compose down`, zero container sobrando) e subi a
  stack nativa de novo pro usuário continuar usando do jeito que
  estava.
- README atualizado: seção Docker agora abre dizendo explicitamente
  que é o caminho mais garantido entre máquinas diferentes, com a
  ressalva que continua de pé (GUI do Gazebo via X11/GPU é tranquila
  no Linux, mais chata no Docker Desktop macOS/Windows); Quick start
  aponta pra lá logo de cara pra quem for trocar de máquina.
- Commit `a7434d1` em `perfect-bot`, com push.

### 2026-10-18 (noite, cont. 2) — branch `perfect-bot`: setup.sh — validação real de "baixa num PC novo e funciona"

- Pergunta do usuário que motivou tudo isso: será que um clone novo,
  só seguindo o Quick Start, realmente funciona sem mexer em código?
  Testado de verdade (não só raciocinado): `git clone` do repo local
  pra uma pasta nova, sem reaproveitar nada da máquina de dev (sem
  `backend/venv/`, sem `fleet_ws/install/`, sem `frontend/
  node_modules/`), e segui o Quick Start à risca.
- Gap real encontrado: `run_all.sh` só INICIA processos, não instala
  nada. Numa máquina nova ele caía no mesmo erro de `httpx` faltando
  já documentado antes (sem `backend/venv/`, cai pro python do
  sistema, que não tem as deps da camada de agentes de IA). Faltava
  um script que preparasse o ambiente ANTES do `run_all.sh`.
- Criado `setup.sh`: builda os pacotes ROS 2 (`build.sh`), cria e
  popula `backend/venv/`, roda `npm install` — tudo automatizado.
  Único pré-requisito que continua manual de propósito: ROS 2 Jazzy
  já instalado no sistema (não é algo que um script de repo deveria
  instalar sozinho sem o usuário saber). Testado no mesmo clone limpo:
  `./setup.sh` sozinho deixou tudo pronto pro `run_all.sh` funcionar.
- Verificado também o caminho Docker (alternativa que evita precisar
  instalar ROS2 no host): `docker compose build` builda do zero com
  sucesso hoje. Não testado subindo os containers de verdade (portas
  8000/5173 já ocupadas pela stack nativa rodando na mesma máquina
  durante o teste) — não é falha do Docker, só as duas rodando junto.
- **2 incidentes reais durante o teste, ambos corrigidos**:
  1. Rodei um teste de `run_all.sh` no clone de teste com `timeout
     40s` sem perceber que isso deixaria uma SEGUNDA simulação
     (Gazebo+Nav2) rodando ao mesmo tempo da stack original do
     usuário (que ele estava usando de verdade, com dados reais
     gravados) — achado porque o próprio usuário notou ("tem 2 abertos
     né"). `kill -TERM` no grupo de processo certo (confirmado por
     PGID antes de matar) resolveu sem tocar na stack dele. Lição: não
     usar `timeout` externo pra testar `run_all.sh` — o trap de
     cleanup do script nem sempre dispara a tempo com esse mecanismo
     de sinal; usar controle de processo em segundo plano de verdade
     (`run_in_background` + `TaskStop`, que já confirmado funcionar
     limpo) em vez disso.
  2. `docker compose build` falhou na primeira tentativa por disco
     cheio (`/tmp` a 0MB livre, ENOSPC) — a máquina já tinha ~29GB em
     imagens/cache Docker de builds anteriores (91% do disco usado).
     `docker builder prune -af` liberou 15.44GB, build refeito com
     sucesso na segunda tentativa.
- Commit `61eb929` em `perfect-bot`, com push.

### 2026-10-18 (noite, cont.) — branch `perfect-bot`: README reescrito pra quem não é da robótica + validação real ao vivo

- Pedido do usuário: reescrever o README pensando em gente que não usa
  robótica — fácil, quick start. Nova seção "Quick start" logo no
  topo (antes de Architecture/Prerequisites): 3 passos (clonar+buildar
  uma vez, `./run_all.sh`, abrir a página) + passo a passo de botões
  em linguagem simples, com um screenshot real do app rodando
  (`docs/images/screenshot.png`, capturado ao vivo nesta sessão). O
  resto do README (instalação do zero, rodar na mão, CLI, config) virou
  material de referência explícito pra quem for desenvolver no
  projeto, não pra quem só quer usar. "## Running" renomeada pra
  "## Running manually" (o caminho fácil mora no topo agora).
- Achado no caminho: `fleet_ws/runs_history/` (a feature de histórico
  de execuções, criada mais cedo hoje) não estava no `.gitignore`
  igual `routes/`/`collections/` já estavam — corrigido.
- **Sinal forte de que o pedido de hoje deu certo**: enquanto o stack
  ficou de pé pro usuário acessar (`run_all.sh` rodando, link
  `localhost:5173` compartilhado), apareceu uma gravação REAL no
  histórico — `percurso_initial`, 36s, 5.43m, `exit_code=0`,
  `success=true` — ou seja, alguém (provavelmente o próprio usuário)
  clicou em "Executar record" na tela e funcionou de ponta a ponta,
  sem eu ter disparado esse run. Não é um teste meu — é a primeira
  evidência real de uso espontâneo da interface.
- Commit `89129fc` em `perfect-bot`, com push.

### 2026-10-18 (noite) — branch `perfect-bot`: run_all.sh — stack inteiro com 1 comando

- Pedido do usuário: um script documentado no README pra subir tudo
  sem precisar mexer em código além de rodar. Criado `run_all.sh`
  (raiz do repo) — sobe simulação → nós da frota → backend → frontend
  nessa ordem, esperando cada um reportar pronto de verdade (grep no
  log de cada processo) antes do próximo; Ctrl+C derruba tudo limpo
  (cada processo em sessão própria via `setsid`, alcança os
  sub-processos que `gz sim`/`ros2 launch` spawnam — sem isso sobra
  processo órfão, o mesmo problema já visto antes nesta sessão com
  `pkill`).
- 2 achados reais testando ao vivo (não só escrevendo o script às
  cegas):
  1. O README mandava esperar `All BT navigator servers are active`
     no Terminal 1 — essa frase **nunca aparece** de verdade; o sinal
     certo, confirmado em duas execuções reais, é
     `Managed nodes are active` (do `lifecycle_manager_navigation`,
     a mesma string que a lógica de prontidão do Painel de Simulação
     no backend já usava — só o README estava desatualizado).
  2. `python3 main.py` direto pro backend (caminho documentado no
     README/`backend/run.sh`) **quebra hoje**: `backend/agents/
     executor.py` importa `httpx`, que não está nos pacotes apt
     listados — provavelmente porque esse caminho é anterior à
     camada de agentes de IA. `backend/venv/` (usado a sessão toda)
     tem tudo certo; `run_all.sh` usa ele quando existe, com fallback
     pro python do sistema. Ambos os achados corrigidos no README.
- Testado ao vivo, 2x: stack completo sobe em ~25s, mapa SLAM real +
  LiDAR + pose do robô aparecem na tela, `/api/status` confirma pose
  válida. Commit `5aa5b2d` em `perfect-bot`, com push.

### 2026-10-18 (tarde) — branch `dissertacao`: camada de agentes de IA removida a pedido da banca; branch `perfect-bot`: histórico de execuções + comparação

- **Dissertação** (`dissertacao`, commit `1102972`, com push): pedido
  explícito da banca (via Breno Miranda) — manter só a parte web do
  framework, tirar a camada de agentes de IA (Planner/Executor/Analyst,
  MissionRouter) da narrativa. Removida a subseção inteira "A Camada de
  Agentes de IA" do Cap. 4, os 2 itens de trabalhos futuros sobre LLM/
  coordenação multi-agente do Cap. 9, e os pontos menores nos Caps. 1 e
  6. Os argumentos de extensibilidade que usavam a camada de IA como
  evidência foram reescritos usando o **Painel de Simulação** no lugar
  (mesma estrutura: construído sobre a API REST sem alterar o
  orquestrador ROS 2). 4 citações que só apareciam nos trechos cortados
  removidas do `.bib`. Compilação verificada via `latexmk` (117
  páginas, zero referência/citação quebrada). **Importante**: isso é
  só sobre o TEXTO da dissertação — o código/feature de agentes IA
  continua existindo no software (`backend/agents/`), só não é mais
  descrito como contribuição científica.
- Contexto do Breno (relayed pelo usuário, duas vezes): a parte
  consistente/valorizada é a de **automação de teste/cenário**
  (protocolo record-replay + interface web pra montar o cenário
  experimental), com ênfase em mostrar que funciona com robô real, não
  só simulação — não a camada de IA. Isso motivou a feature abaixo.
- **Software** (`perfect-bot`, commit `9bf2947`, com push): fechada a
  lacuna que isso expôs — não existia histórico persistente de
  execuções de `/api/run_config` (resultado vivia só na memória do
  backend, apagado do disco logo após ser lido) nem jeito de comparar
  duas execuções lado a lado. Backend agora persiste cada job em
  `fleet_ws/runs_history/<job_id>.json`; `GET /api/runs` lista; painel
  novo "📊 Execuções" no frontend mostra cards com métricas e permite
  selecionar 2 pra comparar numa tabela. Testado ao vivo com execuções
  reais via Playwright (card com `bag_metrics` reais comparando certo
  contra um sem métricas, mostrando "—" corretamente).
- Pesquisa de referência de UI mal-sucedida, registrada pra não
  repetir: Foxglove Studio (visualizador de `.mcap`) virou produto
  pago/corporativo — o app web (`app.foxglove.dev`, antigo
  `studio.foxglove.dev`) agora exige conta, não dá mais pra abrir um
  `.mcap` local sem login.

### 2026-10-18 — branch `perfect-bot`: código real da Bia/Fernanda (repo mobile-robotics) analisado + 3 gaps fechados no web

- Usuário recebeu o repositório real do experimento da Bia/Fernanda
  (`mobile-robotics-main.zip`, equipe CRIAR-CIn/UFPE: Fernanda Neves,
  **Beatriz Oliveira** — corrige nome registrado antes como "Barros" —,
  Adrien Durand-Petiteville e Breno Miranda, orientadores). Paper-alvo:
  "Wireless Connectivity Testing with Mobile Robots: A Bluetooth Low
  Energy Case Study", CBSoft 2026.
- Lido o código real (`nav_3points.py`, `script_celular.ps1`,
  `docs/setup.md`, `docs/troubleshoot.md`, mapas): ROS 2 **Humble** (não
  Jazzy), rota de só 3 pontos hardcoded (START/MIDPOINT/FINAL_GOAL) no
  mapa real `hall_cin_v4` (corredor do CIn, ~64m, `.pgm`+`.yaml`,
  convenção Nav2 map_server). A coleta BLE **não lê RSSI numérico
  nenhum** — é tap automatizado via ADB na tela do app nRF Connect num
  celular Android, com conectado/desconectado detectado por regex em
  `dumpsys bluetooth_manager`; o número de RSSI nunca é logado em
  nenhum arquivo por esse script. Dor documentada por elas em
  `troubleshoot.md`: tiveram que trocar FastDDS→CycloneDDS por causa do
  link USB-C RPi↔Create3, e montar hierarquia NTP/chrony pra parar de
  corromper a TF por clock skew (achado real, candidato a alimentar
  `conhecimento/dds_tuning.md` se for revisitado).
- 3 gaps reais identificados e fechados no fleet-ui (commit `fce2d93`
  em `perfect-bot`):
  1. **Import de mapa real** (.yaml+.pgm) como fundo selecionável no
     `MapView` — antes só dava pra ter fundo rodando SLAM ao vivo uma
     vez (sem jeito de importar um mapa já pronto). Backend: parser PGM
     (P2/P5) + conversão de ocupação (negate/thresholds, fórmula do
     Nav2 map_server) pra PNG; endpoints `/api/import_map`,
     `/api/list_maps`, `/api/slam_map_meta?name=`. Frontend: seletor de
     mapa + mini-form de import em `MapToolbar`. Validado ponta a ponta
     com o `hall_cin_v4.pgm` real delas (985×1369px) — corredor
     renderiza alinhado com as coordenadas reais do `nav_3points.py`
     delas (START no topo do corredor vertical, MIDPOINT na junção,
     FINAL_GOAL no corredor horizontal à esquerda).
  2. **Campo "Rótulo da execução"** em `ConfigForm` — metadado livre
     (ex.: par de dispositivo BLE testado, homogênea/heterogênea) que
     viaja pro JSON exportado. Resolve a perda de contexto que o fluxo
     delas tem hoje (qual par de celular foi aquele run vira
     conhecimento tácito de quem rodou, não fica em nenhum arquivo).
  3. **Campo "Endereço BLE alvo"** em `ConfigForm`, setado via
     `ros2 param set` antes de cada execução. Isso exigiu consertar
     `ble_rssi_publisher.py`: o nó só lia `target_address` uma vez na
     construção — sem callback de parâmetro, o campo seria cosmético,
     não funcional. Adicionado `add_on_set_parameters_callback` +
     início do scanner sob demanda quando o endereço é setado em
     runtime.
- Achado colateral consertado (bug real, não relacionado aos 3 gaps):
  `useMapCanvas.js` tinha um efeito de carregar o fundo que dependia de
  `draw`, e `draw` muda de identidade a cada poll de pose/status
  (~300ms, não tem nada a ver com qual mapa está selecionado) — isso
  causava reload infinito do fundo (fetch + decode de imagem em loop
  sem nunca estabilizar) toda vez que o mapa mudava. Corrigido trocando
  a dependência do efeito pra só `[mapName]`. Achado ao vivo testando o
  import do `hall_cin_v4` via Playwright — parecia "travado" mas era
  centenas de requisições disparando em loop.
- Nota de ambiente (não é bug do produto): testando via Playwright
  headless neste sandbox, a primeira requisição de uma página recém-
  carregada contra o Vite dev server pode levar ~15-20s pra responder
  (conexão fria do Chromium headless); depois disso tudo fica
  instantâneo. Isso mascarou o diagnóstico do bug acima por um tempo —
  qualquer teste futuro com Playwright nesse ambiente deve esperar esse
  "aquecimento" passar antes de medir timing.

### 2026-10-16 — branch `perfect-bot`: fecha a lacuna "grava BLE RSSI mas não tem como ver depois"

- Revisão do enredo completo do `perfect-bot` (BLE real via `bleak` +
  simulado via Gazebo `RFComms`, ver entradas anteriores) achou um gap:
  dava pra gravar o tópico `ble_rssi` no bag, mas `_bag_compute_metrics()`
  em `fleet_ws/scripts/experiment_repeatability.py` não lia esse tópico —
  o resultado nunca aparecia em lugar nenhum depois da gravação.
- Fechado: `_bag_compute_metrics()` agora deserializa `/ble_rssi` como
  `std_msgs/Int32` e calcula `ble_rssi_mean_dbm`/`min`/`max`/`n`; `App.jsx`
  mostra isso como card de métrica novo, ao lado dos cards de
  odom/scan/imu que já existiam (mesmo padrão visual).
- Checado: `fleet_ws/scripts/analyze_runs.py` **não** tem parser de
  métricas de bag próprio (só `experiment_repeatability.py` tem) — não
  havia segundo lugar pra replicar a mudança. O backend
  (`backend/ros_bridge.py::run_experiment_step`) só faz
  `json.loads(export_path)` genérico, sem whitelist de campos — então o
  novo campo passa automaticamente sem precisar tocar no backend.
- Importante manter em mente (já valia pros dados crus, vale pro
  resumo também): RSSI aqui é presença/ausência de leitura por pacote
  entregue, não uma curva suave de degradação até a queda de sinal —
  então min/max/mean descrevem ruído/sombreamento *dentro* da gravação,
  não "distância até perder o robô".
- Testado: `py_compile` no script, `npm run build` + `vitest run` no
  frontend, suíte Python completa via `backend/venv` (103 testes, sem
  regressão). Commitado em `perfect-bot` (`4cc30ff`).

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

### 2026-10-17 (continuação 2) — RFComms do Gazebo: achado real que corrige minha resposta anterior, piloto simulado construído (não validado ponta a ponta)

- **[correção]** Eu tinha dito antes que "Gazebo não tem simulação de RF/Bluetooth"
  — errado, pelo menos parcialmente. Existe sim um sistema **oficial e
  mantido**: `RFComms` (`gz-sim-rf-comms-system`), portado do projeto SubT
  da OSRF. Confirmado instalado nesta máquina (`libgz-sim8-rf-comms-system.so`,
  Gazebo Sim 8.11.0) e **rodado ao vivo** com o mundo de exemplo oficial
  (`rf_comms.sdf`) — carregou sem erro, tópicos `/addr1/rx` e `/addr2/rx`
  subiram.
- **[achado de código, lido o .cc de verdade]** `RFComms.cc`
  (gazebosim/gz-sim, branch main): perda log-distância
  (`kPL = l0 + 10×fadingExponent×log10(distância)`) + sombreamento gaussiano
  (`sigma`). O RSSI sorteado (`rxPower`) é escrito no cabeçalho da mensagem
  (`rssiPtr->set_key("rssi")`) **só quando o pacote é entregue** — descarte é
  silencioso (sem leitura nenhuma), não existe degradação suave até
  desconectar. **Não faz raycasting nem detecta parede** — é puramente
  distância + ruído estatístico, não geometria. Isso significa: serve pra
  simular "sinal cai com a distância, com ruído realista", mas **não**
  reproduz o efeito específico que o paper da Bia/Fernanda mede (paredes
  atenuando mais que espaço aberto).
- **[achado]** `ros_gz_interfaces/msg/Dataframe` (ROS2, já instalado) tem
  campo `float64 rssi` de primeira classe — diferente do `gz.msgs.Dataframe`
  cru (só tem header/endereços/payload). Confirmado ao vivo: a bridge
  `ros2 run ros_gz_bridge parameter_bridge
  "/addr2/rx@ros_gz_interfaces/msg/Dataframe[gz.msgs.Dataframe"` cria sem
  erro — conversão de fábrica, não precisei escrever bridge de baixo nível.
- **[feito, branch `perfect-bot`]** `ble_rssi_sim_bridge.py`: assina o
  tópico já bridgeado e republica `.rssi` em `std_msgs/Int32` no MESMO
  tópico `ble_rssi` que `ble_rssi_publisher.py` usa com hardware real —
  gravação/análise não precisam saber a diferença.
- **Honestidade**: tentei validar o fluxo **completo** de ponta a ponta
  (publicar uma mensagem de teste via `gz topic pub` no `/broker/msgs` e
  ver ela chegar em `/addr2/rx` com RSSI) — **não funcionou**, sem erro
  visível no log. O exemplo oficial usa um publicador C++ compilado
  (`examples/standalone/comms/publisher.cc`), não CLI; não investiguei a
  fundo o porquê (timing de bind, serialização do payload, ou nome de
  serviço do broker). Registrado como pendência real no commit, não
  escondido atrás de "funciona".

### 2026-10-17 (continuação 3) — ble_rssi_sim_bridge validado ponta a ponta de verdade (a "falha" anterior era erro de teste, não de código)

- **[correção da entrada anterior]** O "não funcionou" registrado há pouco
  não era um bug real — era eu testando o listener (`gz`/`ros2 topic echo`)
  **depois** de publicar a mensagem, e gz-transport não reenvia mensagem
  antiga pra assinante tardio. Corrigido a ordem (listener de pé primeiro,
  publica depois) e funcionou de primeira.
- **[achado de código, foi mais fundo]** Li `Broker.cc` e `MsgManager.cc`
  (gazebosim/gz-sim, `src/comms/`) pra entender o fluxo real de entrega:
  `Broker::OnMsg` recebe a mensagem de saída e enfileira em
  `MsgManager::AddOutbound` (fila `outboundMsgs` do endereço de origem) —
  sem validar nada, nem se o endereço existe. Quem decide entregar ou
  descartar é o **modelo de comunicação** (`RFComms::Step`, chamado pelo
  laço de simulação), que aplica a perda de sinal, sorteia o RSSI, e só se
  o pacote "sobreviver" move ele pra `inboundMsgs` do destino. Só então
  `MsgManager::DeliverMsgs` publica no tópico ROS2 e limpa a fila. Ou seja:
  o Broker é só uma fila intermediária, quem decide fisicamente é o RFComms.
- **[validado ao vivo, cadeia completa]**: `gz sim` (mundo oficial
  `rf_comms.sdf`) + `ros2 run ros_gz_bridge parameter_bridge` + o nó
  `ble_rssi_sim_bridge.py` (branch `perfect-bot`), tudo rodando junto.
  Publiquei 5 mensagens via `gz topic pub -t /broker/msgs`, e o tópico
  final `/ble_rssi` (`std_msgs/Int32`, o mesmo que `fleet_data_collector`
  grava) recebeu **5 valores reais**: -56, -78, -76, -71, -61 dBm — a
  variação batendo com o `sigma=10` (sombreamento gaussiano) configurado
  no mundo de exemplo. Pipeline de simulação do piloto BLE **funciona de
  ponta a ponta**, confirmado, não só em partes isoladas.
- Commit: `d9966ba` em `perfect-bot`.

### 2026-10-17 (continuação 4) — instala de verdade as 3 skills.sh de teste (antes só tinha pesquisado)

- **[feito, branch `perfect-bot`]** Autor perguntou se eu tinha "trazido"
  as habilidades do skills.sh — não tinha, só relatado o que existia.
  Instalado de verdade agora, commit `7d57e0b`:
  - **webapp-testing** (anthropics/skills): toolkit completo, não só o
    SKILL.md — trouxe `scripts/with_server.py` (gerencia ciclo de vida de
    backend+frontend juntos) e os 3 exemplos (`console_logging.py`,
    `element_discovery.py`, `static_html_automation.py`).
  - **verification-before-completion** (obra/superpowers): só o SKILL.md.
  - **playwright-best-practices** (currents-dev): **decisão deliberada de
    escopo** — essa skill tem dezenas de arquivos de referência (GraphQL,
    Electron, pagamentos, i18n) que não se aplicam a este projeto; trouxe
    só o SKILL.md (índice), não a árvore inteira — peso morto seria trazer
    tudo sem uso.
  - Hash de cada `SKILL.md` calculado com `sha256sum` real (não inventado),
    mesmo não tendo o CLI original do skills.sh pra replicar o algoritmo
    exato de hash dos outros registros — é um hash real do arquivo, só não
    necessariamente idêntico byte a byte ao que a ferramenta original geraria.
- **Confirmado**: `frontend/src/components/ConfigForm.jsx` com o tópico
  `ble_rssi` + descrições intuitivas já estava presente em `perfect-bot`
  (herdado de `mission-coordinate-large-scale` na hora do branch) — a parte
  web já estava lá, só não tinha sido mencionada de novo nessa frente.

### 2026-10-17 (continuação 5) — aplica o diagnóstico estético que ficou só registrado antes (skill webapp-testing usada de verdade pela primeira vez)

- **[feito, branch `perfect-bot`, commit `446bf55`]** O diagnóstico de uma
  sessão anterior (skill `frontend-design`) achou 2 clichês reais e autor
  tinha pedido só relatório na hora, sem aplicar. Hoje, autor confirmou
  aplicar:
  - `styles/tokens.js`: `color.brand` novo (`#F2994A`, laranja de
    sinalização) — **deliberadamente separado** de `color.success`. Antes
    as duas coisas eram a mesma cor verde (`#6ee7b7`), cobrindo "isto é o
    Fleet UI" (marca) e "isto deu certo" (status) ao mesmo tempo — essa
    sobreposição era parte do motivo de ler como clichê genérico. Verde
    continua reservado só pra status semântico (NAV2 ON, Gravar ativo,
    checkmarks) — não trocado em lugar nenhum.
  - Título "Fleet UI" + os 2 botões de CTA principal (Executar, Iniciar
    simulação) agora usam a cor de marca nova.
  - 10 ocorrências de `textTransform: 'uppercase'` removidas em 6 arquivos
    (App.jsx, ConnectionPanel, DiscoveryPanel, AgentFleetPanel,
    SimulationPanel, ConfigForm) — confirmei antes que todo texto-fonte já
    estava em case normal (CSS só forçava maiúsculas), então a remoção não
    muda nenhum texto visível, só a apresentação. `fontWeight:600` mantém
    a hierarquia de "isto é rótulo de seção" sem precisar de caixa alta.
- **[primeira vez usando a skill `webapp-testing` de verdade, não só
  instalada]** Segui a árvore de decisão dela (app dinâmico → 
  `scripts/with_server.py --help` primeiro → script Python puro de
  automação). Achei e corrigi 2 problemas reais no processo: faltava o
  pacote Python `playwright` (só tinha instalado a versão Node antes);
  minha primeira asserção usava `text=` (substring) e contava
  "ble_rssi" duas vezes por bater também dentro de "ble_rssi_publisher"
  no texto de ajuda — troquei pra `get_by_text(..., exact=True)`.
  Resultado confirmado com screenshot real, não só "parece ter funcionado".

**Como manter isto atualizado:** cada agente, ao final de uma execução,
acrescenta uma entrada nova (data + achado em 1-2 linhas + link pro arquivo
detalhado) nesta seção, sem apagar entradas anteriores. Se um achado tiver
"Ação sugerida" concreta, também vira uma linha em `implementacao.md`.
