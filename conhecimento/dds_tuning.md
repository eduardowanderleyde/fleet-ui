# Conhecimento acumulado: Tuning de DDS/ROS 2 para multi-robô

## TL;DR

(atualizado 2026-10-03) **Pergunta direta respondida nesta rodada:** dado
o prazo curto até a defesa, das 3 hipóteses levantadas, a de melhor
relação esforço/risco/chance é **trocar `RMW_IMPLEMENTATION` pra
`rmw_cyclonedds_cpp` e testar em A/B contra o padrão atual** — é literalmente
1 variável de ambiente (confirmado no código: tanto o backend quanto o
script de campanha herdam o ambiente do processo pai sem filtrar nada,
então nem precisa mudar 1 linha de código), 100% reversível (só
desfazer a variável), e testável com as ferramentas que já existem
(`run_ground_truth_campaign.py` já conta retries). O `ComposableNodeContainer`
continua sendo a hipótese com maior potencial teórico de resolver a
causa raiz de verdade (reduz ~9 participantes DDS por robô pra 1-2), mas
é mudança de arquitetura de launch files — fica recomendado como
**trabalho futuro documentado**, não pra tentar antes da defesa (o
projeto já se queimou uma vez cortando nó demais num launch "enxuto"
sem testar todos os usos, ver achado de 2026-10-03 abaixo sobre
`waypoint_follower` — editar esses mesmos arquivos de novo sob prazo
curto é risco real). `ROS_DISCOVERY_SERVER` fica em último lugar: além
do esforço (processo novo pra manter vivo e saudável durante 30 réplicas
de campanha), a pesquisa não achou nenhuma fonte confirmando ganho real
em localhost/shared-memory (o benefício de até 93% medido é pra tráfego
de rede real, não pra 1 máquina só). Achado novo relevante no caminho:
o próprio TurtleBot4 real tem suporte oficial, documentado no manual do
usuário, pra alternar entre Fast DDS (padrão) e Cyclone DDS via
ferramenta de setup — ou seja, essa troca é um caminho conhecido e
testado pelo próprio fabricante da plataforma, não uma combinação
exótica.

(atualizado 2026-10-02) O ROS 2 Jazzy usa Fast DDS por padrão — mas
não há confirmação ao vivo de qual RMW este projeto usa de fato (não
está fixado em nenhum script/Dockerfile do repo); é só inferência pelo
default. O sintoma "jump back in time" é compatível tanto com
sobrecarga de descoberta DDS quanto com contenção de CPU, e a pesquisa
não achou uma forma pronta e validada de separar as duas causas sem
medir ao vivo (a sugestão mais concreta: capturar tráfego de descoberta
com `tcpdump`/Wireshark e CPU com `pidstat` no mesmo intervalo de uma
ativação). **O achado de maior confiança até agora:** Nav2 e SLAM
Toolbox já têm suporte oficial a "composição" (juntar vários nós num
processo só = um participante DDS só), mas os launch files deste
projeto (`nav2_minimal.launch.py`, `activate_robot_nav.launch.py`)
sobem cada servidor como processo separado — isso é provavelmente a
alavanca mais direta pra atacar a rajada de ~15-18 nós/participantes
por robô, mais direta que trocar de RMW ou configurar um Discovery
Server. `ROS_DOMAIN_ID` diferente por robô isolaria a descoberta de
verdade, mas exigiria um bridge (`domain_bridge`, pacote oficial) pro
backend continuar enxergando os dois robôs — é mudança de arquitetura,
não só configuração. `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` não
ajuda aqui: o ambiente real do projeto já usa a variável antiga
equivalente (`ROS_LOCALHOST_ONLY=1`, confirmado por um log de teste
real capturado no próprio repo) e os robôs já estão todos na mesma
máquina mesmo assim, então não há isolamento a ganhar por aí.

## Achados

### 2026-10-02 — RMW padrão do ROS 2 Jazzy é Fast DDS, mas não confirmado ao vivo neste projeto

Fonte: [docs.ros.org/en/jazzy/Installation/RMW-Implementations.html](https://docs.ros.org/en/jazzy/Installation/RMW-Implementations.html)
— o vendor default do RMW em Jazzy é `rmw_fastrtps_cpp` (eProsima Fast
DDS), a menos que `RMW_IMPLEMENTATION` seja setada pra outra coisa (ex.
`rmw_cyclonedds_cpp`).

Nesta sessão de pesquisa, `echo $RMW_IMPLEMENTATION` no shell do agente
voltou vazio, e um `grep -rn "RMW_IMPLEMENTATION"` em todo o repo (`.py`,
`.sh`, `.yaml`, `Dockerfile*`, `.md`) não achou nenhuma definição
explícita em código do projeto. Isso é consistente com "está usando o
default (Fast DDS)", mas **não é uma confirmação ao vivo** rodando
dentro do ambiente de execução real (que pode ter a variável setada via
`.bashrc`/perfil de shell fora do repo, ou dentro de um container).

**Ação sugerida:** antes de qualquer decisão de trocar de RMW, confirmar
com `printenv RMW_IMPLEMENTATION` ou `ros2 doctor --report | grep -i rmw`
rodando dentro do ambiente real (não só grep no código).

### 2026-10-02 — Achado de arqueologia de código (não é pesquisa externa): `ROS_LOCALHOST_ONLY=1` já está ativo no ambiente real

Evidência: `tests/test_ros_bridge.py` (em torno da linha 105-108) contém
um trecho de `stderr` **real**, capturado ao vivo de um
`ros2 service call list_robots fleet_msgs/srv/ListRobots '{}'` contra
uma frota `tb1`+`tb2` rodando de verdade (comentário no teste diz
exatamente isso):

```
[WARN] [rcl]: ROS_LOCALHOST_ONLY is deprecated but still honored if it is enabled. Use ROS_AUTOMATIC_DISCOVERY_RANGE and ROS_STATIC_PEERS instead.
[WARN] [rcl]: 'localhost_only' is enabled, 'automatic_discovery_range' and 'static_peers' will be ignored.
```

Isso confirma que o ambiente real do projeto já restringe a descoberta
a localhost — só que pela variável antiga/depreciada, não pela nova.
`backend/ros_bridge.py:24` também confirma que o backend já lê
`ROS_DOMAIN_ID` do ambiente (com default `"0"` se não setada), ou seja,
hoje todos os robôs compartilham o mesmo domain ID 0.

**Implicação:** a variável nova `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`
(achado abaixo) não teria efeito nenhum enquanto `ROS_LOCALHOST_ONLY=1`
continuar definida no ambiente — o próprio aviso do ROS 2 diz que a
variável nova é ignorada nesse caso.

### 2026-10-02 — `ROS_AUTOMATIC_DISCOVERY_RANGE` / `ROS_STATIC_PEERS`: não atacam o problema deste projeto

Fonte primária: [raw.githubusercontent.com/ros2/ros2_documentation (branch jazzy) — Improved-Dynamic-Discovery.rst](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Tutorials/Advanced/Improved-Dynamic-Discovery.rst)
(mesmo conteúdo da página oficial `docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html`,
que bloqueou fetch automatizado via proteção anti-bot "Anubis" — confirmado lendo o `.rst` fonte direto do GitHub).

Valores de `ROS_AUTOMATIC_DISCOVERY_RANGE`: `SUBNET` (default, multicast),
`LOCALHOST` (só a mesma máquina), `OFF` (nenhuma descoberta), `SYSTEM_DEFAULT`
(não muda nada). `ROS_STATIC_PEERS` é uma lista de endereços pra descoberta
unicast dirigida. Funcionam em middleware baseado em DDS (Fast DDS, Cyclone
DDS) — a doc afirma explicitamente que **não são suportadas por `rmw_zenoh`**.

**Por que não ajuda aqui:** como `tb1` e `tb2` já rodam na MESMA máquina,
`LOCALHOST` não isola um robô do outro — os dois já "são" localhost. Essa
variável resolveria overhead de tentar descoberta multicast fora da
máquina (que nem estava acontecendo, já que o achado acima mostra que
`ROS_LOCALHOST_ONLY=1` já bloqueia isso). **Achado em tensão/sem efeito
prático** com o problema real: quem isolaria descoberta entre tb1 e tb2
de verdade é `ROS_DOMAIN_ID` diferente por robô (achado seguinte), não
o `ROS_AUTOMATIC_DISCOVERY_RANGE`.

### 2026-10-02 — `ROS_DOMAIN_ID` por robô isola descoberta DDS de verdade, mas exige um bridge pro backend ver os dois robôs

Mecanismo confirmado (documentação geral de design DDS/ROS 2 citada em
múltiplas fontes consistentes entre si): nodes com `ROS_DOMAIN_ID`
diferentes não se descobrem de forma alguma — é isolamento total de
descoberta (cada domain ID é uma rede lógica separada), não um throttle.
Isso atacaria direto a hipótese de "rajada de nós do robô 2 competindo
com a rajada/descoberta residual do robô 1" levantada no
`experiment-dds-tuning.md`.

**Custo:** `backend/ros_bridge.py:24` mostra que o backend de hoje
assume um único `ROS_DOMAIN_ID` pra toda a frota. Se cada robô ganhasse
um domain ID próprio, o backend (e qualquer ferramenta de
debug/monitoramento) deixaria de ver automaticamente os tópicos de
AMBOS os robôs — precisaria de um processo ponte explícito.

**Ação sugerida:** o pacote oficial `domain_bridge` existe exatamente
pra esse cenário — confirmado real, documentado em
[docs.ros.org/en/jazzy/p/domain_bridge/](https://docs.ros.org/en/jazzy/p/domain_bridge/),
instalável via `apt install ros-jazzy-domain-bridge`, roda cliente e
servidor na MESMA máquina em domain IDs diferentes e expõe via YAML
quais tópicos atravessam a ponte. Seria um experimento válido (ex.:
`tb1` no domain 1, `tb2` no domain 2, `domain_bridge` expondo só os
tópicos que o backend/painel precisam de volta pro domain 0) — mas é
mudança de arquitetura não-trivial (contradiz a simplicidade da solução
atual de "15s de pausa", ver `orquestracion.md`), não decidir sozinho,
só registrar como caminho viável e sinalizar a tensão.

### 2026-10-02 — Fast DDS Discovery Server reduz tráfego de descoberta em até 93% (fase PDP/EDP) vs SDP padrão — utilidade numa única máquina não confirmada

Fonte primária confirmada (post oficial da eProsima por Katrin_Kellner,
com esclarecimento adicional do engenheiro EduPonz da própria eProsima):
[discourse.openrobotics.org/t/new-discovery-server/17383](https://discourse.openrobotics.org/t/new-discovery-server/17383).
Citação: "This strategy has reduced the network traffic by up to 93%
when compared to the standard SDP, and by up to 83% when compared to
the previous implementation of the Discovery Server." EduPonz esclarece
que o 93% é especificamente da fase PDP/EDP (descoberta inicial de
participantes/endpoints), e que o ganho em steady-state com muitos
"late joiners" é ainda maior, mas sem número fechado citado.

Discovery Server foi desenhado pra evitar multicast (útil em redes
corporativas/sem multicast) e pra deployments grandes com muitos
participantes numa rede real. **Não encontrei nenhuma fonte que meça
esse ganho especificamente em localhost/shared-memory** (caso deste
projeto, 1 máquina só) — registrar como **não confirmado para este
caso específico**, não decidir sozinho.

Setup: 1 processo servidor (`fastdds discovery -i 0 -l 127.0.0.1 -p
11811`) + variável `ROS_DISCOVERY_SERVER` nos clientes — custo de setup
baixo, então pode valer testar mesmo sem certeza do ganho real em
localhost.

### 2026-10-02 — Mapeamento 1:1 nó→participante DDS gera overhead de CPU mensurável; composição (`ComposableNode`) é a correção oficial — Nav2 e SLAM Toolbox já suportam, o projeto não usa

Fonte da métrica: [discourse.openrobotics.org/t/reconsidering-1-to-1-mapping-of-ros-nodes-to-dds-participants](https://discourse.openrobotics.org/t/reconsidering-1-to-1-mapping-of-ros-nodes-to-dds-participants)
— números concretos citados por um usuário num teste próprio: 10 nós
com 20 publishers/subscribers e 200 subscribers = **255,1% CPU**; o
mesmo volume de pub/sub rodando num único nó = **139,1% CPU**; DDS puro
sem ROS por cima = **51,3% CPU**. Ou seja, os participantes DDS
(múltiplos nós = múltiplos participantes) respondem por boa parte do
overhead de CPU, o resto vem do executor.

**Confirmado por leitura direta do código-fonte oficial (não
extrapolação):**
- `nav2_bringup/launch/bringup_launch.py` (branch jazzy,
  [api.nav2.org/nav2-jazzy](https://api.nav2.org/nav2-jazzy/html/bringup__launch_8py_source.html))
  declara `use_composition` com **default `'True'`** — o Nav2 upstream
  já roda todos os servidores (controller_server, planner_server,
  smoother_server, behavior_server, bt_navigator etc.) dentro de UM
  `ComposableNodeContainer` (1 processo = 1 participante DDS) por
  padrão, quando se usa o launch oficial do vendor.
- `slam_toolbox` também é composable: confirmado lendo o `CMakeLists.txt`
  real do repo
  ([github.com/SteveMacenski/slam_toolbox, branch jazzy](https://github.com/SteveMacenski/slam_toolbox/blob/jazzy/CMakeLists.txt))
  — `rclcpp_components_register_nodes` registra
  `slam_toolbox::SynchronousSlamToolbox` e
  `slam_toolbox::AsynchronousSlamToolbox` como componentes carregáveis
  num container.

**Mas o projeto não usa nenhum dos dois.** Lido diretamente:
`fleet_ws/src/fleet_orchestrator/launch/nav2_minimal.launch.py` sobe
`controller_server`, `smoother_server`, `planner_server`,
`behavior_server`, `bt_navigator`, `velocity_smoother`,
`collision_monitor` e `lifecycle_manager` cada um via `Node(...)`
individual (processo próprio = participante DDS próprio) — sem
`ComposableNodeContainer`, sem `use_composition`. E
`activate_robot_nav.launch.py` inclui o `slam.launch.py` padrão do
`turtlebot4_navigation` por cima disso, também como processo separado.

**Ação sugerida (destaque):** o projeto já atacou a rajada de nós
cortando ~30% deles (`nav2_minimal.launch.py` remove `route_server`,
`waypoint_follower`, `docking_server` — ver docstring do próprio
arquivo, achado de 2026-09-30 em `orquestracion.md`), mas não aplicou a
ferramenta oficial que ataca o MESMO sintoma de forma mais direta:
carregar os servidores restantes (e o nó do SLAM Toolbox) como
`ComposableNode` dentro de um único `ComposableNodeContainer` por robô
reduziria de ~9 processos/participantes DDS pra 1-2, cortando a rajada
de descoberta na raiz em vez de só reduzir a contagem de nós. Essa é a
recomendação mais concreta e de maior confiança encontrada nesta rodada
pro problema dos 70%/"jump back in time" — mas é mudança de código real
(fora do escopo deste agente alterar). Valeria como experimento
controlado: testar `activate_robot_nav` com um container composto pra 1
robô, comparar contagem de avisos "jump back in time" e tempo até
"ready" contra a baseline já documentada em `orquestracion.md`
("tb2 com 15s de pausa: 9 avisos, pronto em ~6s").

### 2026-10-02 — "jump back in time" é sintoma de descontinuidade do `/clock`, não prova de causa (CPU vs DDS); nenhuma receita publicada pronta pra diferenciar

Fonte: código-fonte do `tf2_ros.Buffer`
([docs.ros.org/en/jazzy/.../tf2_ros_py/_modules/tf2_ros/buffer.html](https://docs.ros.org/en/jazzy/p/tf2_ros_py/_modules/tf2_ros/buffer.html))
confirma que o "jump callback" dispara e limpa o buffer de TF sempre
que detecta um salto pra trás no relógio usado (aqui, `/clock`
simulado) — é um mecanismo de segurança genérico do tf2, não uma
métrica de causa raiz. Não encontrei (e não inventei) uma receita
publicada específica de "meça X, se bater Y é CPU, se bater Z é DDS"
pra esse sintoma exato.

Achado tangencial que corrobora que isso é uma classe de problema
conhecida em middlewares diferentes, não um bug isolado deste projeto:
uma discussão real e **não resolvida** no GitHub do roadmap do Zenoh —
[github.com/eclipse-zenoh/roadmap/discussions/227](https://github.com/eclipse-zenoh/roadmap/discussions/227)
— descreve exatamente "rota de `/tf` cai quando 13+ participantes DDS
entram simultaneamente" no `zenoh-bridge-ros2dds` com ROS 2 Jazzy, sem
fix confirmado até a data da consulta. **Não é diretamente aplicável**
(este projeto não usa `rmw_zenoh`/bridge Zenoh), mas é evidência
independente de que "muitos participantes entrando ao mesmo tempo
quebra rotas de TF" é um padrão recorrente através de camadas de
middleware diferentes — reforça (sem provar) que a causa raiz aqui
também é mais estrutural (contagem de participantes) do que específica
de uma implementação de RMW.

**Ação sugerida (ferramenta de diagnóstico, não testada ao vivo nesta
sessão):** pra separar CPU de DDS antes de tunar a coisa errada,
capturar `tcpdump -i lo -w discovery.pcap udp port 7400` (porta padrão
de descoberta RTPS) durante uma ativação, abrir no Wireshark com o
dissector RTPS e ver se há explosão de pacotes SPDP/SEDP correlacionada
no tempo exato dos avisos "jump back in time" (indicaria DDS/descoberta)
— em paralelo, rodar `pidstat`/`mpstat` no mesmo intervalo pra ver se
algum núcleo satura a 100% ANTES da explosão de pacotes (indicaria
CPU/scheduling como causa primária, com DDS como efeito colateral, não
causa). Isso é recomendação de ferramenta, não um resultado medido.

### 2026-10-02 — Reprodução ao vivo do problema, achada por acaso rodando o piloto de ground truth

Não é pesquisa nova — é confirmação ao vivo, ao rodar 3 boots frescos
seguidos da simulação pra testar outra coisa (congelamento de ground
truth, ver `conhecimento/gazebo_tracking.md`). Dois achados relevantes
pra este tema:

1. **Confirmei um caso real de órfãos de processo contaminando um boot
   novo:** depois de uma bateria de testes, `parameter_bridge`/
   `image_bridge` de PIDs antigos (~30min de vida) sobreviveram ao
   `kill` que eu pensava ter encerrado tudo, e ficaram competindo por
   CPU com uma simulação nova que eu tinha acabado de subir —
   `uptime` chegou a load average 14,16 (baseline da máquina é ~0,2).
   Só caiu pra próximo do normal depois de eu matar os PIDs órfãos
   manualmente. Isso é evidência direta e concreta (não só suspeita) de
   que processos não encerrados de uma réplica anterior podem contaminar
   a réplica seguinte — relevante pra campanha principal, que depende de
   encerrar e relançar a stack inteira 30 vezes.
2. **Numa 3a tentativa de boot fresco (já sem órfãos, load baixo), a
   ativação travou de verdade** — parou de progredir por mais de 2
   minutos em `docking_server.rclcpp: failed to send response to
   /docking_server/change_state (timeout)`, nunca chegou a "Managed
   nodes are active". Reproduz o problema que já motivou este agente
   (ativação sequencial com ~70% de taxa de sucesso) — não achei causa
   nova, só confirmo que ainda acontece espontaneamente, mesmo com a
   máquina relativamente descansada no momento exato do boot.

**Ação sugerida:** pra campanha principal (30 réplicas, cada uma
relançando a stack inteira), não basta um `kill` simples entre réplicas
— o script de campanha precisa (a) confirmar ativamente que não sobrou
processo da réplica anterior antes de subir a próxima (`pgrep` + kill
forçado se necessário, não só esperar um tempo fixo), e (b) ter um
timeout-e-retry pro próprio bringup (se não chegar em "Managed nodes are
active" em N segundos, matar tudo e tentar de novo, contando quantas
réplicas precisaram de retry — é um dado relevante pra reportar a taxa
real de sucesso). Nenhuma dessas duas coisas existe hoje no script de
campanha, até onde verificado nesta sessão.

### 2026-10-02 — O retry foi implementado e já se provou necessário na prática

`fleet_ws/scripts/run_ground_truth_campaign.py` (ver `implementacao.md`)
implementa exatamente a ação sugerida acima. Testando-o nas rotas
longa/loop recém-criadas, a réplica 1 da rota longa bateu o problema de
verdade: 2 tentativas de boot seguidas falharam por timeout em
`change_state` (`route_server` na 1ª, `controller_server` na 2ª — nó
diferente a cada vez, reforçando que não é um nó específico com bug, é
contenção de recursos durante a rajada de ativação, consistente com o
que já se sabia). O script matou tudo e tentou de novo automaticamente,
terminando ok na 3ª tentativa, sem intervenção manual. Essa é a primeira
confirmação real (não só hipotética) de que o mecanismo de retry
funciona numa falha de verdade — antes disso, só tínhamos a suspeita
(~70% de sucesso) e o código do retry, nunca os dois juntos numa falha
ao vivo.

### 2026-10-03 — Bug real achado pilotando run_fleet multi-robô: waypoint_follower faltando, não DDS

Não é pesquisa — é achado ao vivo, primeira vez que `run_fleet` (2 robôs,
agente de IA independente por robô) foi testado de verdade. Os dois
agentes gravaram baseline com sucesso (`go_to_point`), mas o replay
falhou nos dois com "Nav2 follow_waypoints not available". Diagnóstico
com `ros2 action info` mostrou a action listada mas com **0 servidores**
respondendo, e `ros2 lifecycle get .../waypoint_follower` devolveu "Node
not found" — o nó simplesmente não existia, não era timing de descoberta
DDS. Causa: `nav2_minimal.launch.py` (usado só por
`activate_robot_nav.launch.py`, o caminho de ativação sequencial
multi-robô) tinha sido enxugado em 2026-09-30 pra reduzir a rajada de nós
na ativação (o próprio achado de contenção DDS/CPU documentado acima), e
`waypoint_follower` foi cortado junto por engano de escopo — na época só
se pensava em `go_to_point`, sem considerar que `play_route`/replay
(usado o tempo todo no resto do projeto, inclusive pelas campanhas de
ground truth desta sessão) depende dele. Corrigido reintroduzindo o nó
(commit `db5ce66`). Depois do fix, tb1 e tb2 ativaram com sucesso sem
retry, `ros2 action info` confirmou 1 servidor real pros dois.

Também confirmado DE NOVO, separadamente, o problema de contenção
DDS/CPU já conhecido: numa tentativa de ativação (ANTES do fix acima ser
testado), tb1 ficou preso num loop de "jump back in time" sem nunca ficar
pronto — matei tudo, esperei a carga normalizar, e a segunda tentativa
funcionou de primeira. Mesmo padrão já documentado, não é achado novo em
si, só mais uma ocorrência real registrada.

**Ação sugerida:** nenhuma pendente — o fix já foi aplicado e verificado.
Só sinalizando que esse tipo de corte "enxuto só pro caso de uso X"
(já usado 2x neste projeto: `nav2_minimal.launch.py` original, cortando
`route_server`/`docking_server`/`waypoint_follower`) corre risco real de
quebrar um caso de uso diferente (replay) que ninguém testou contra esse
caminho de ativação até agora — vale revisar se há outros cortes
semelhantes no projeto que nunca foram testados contra todos os usos
reais (`go_to_point` E `play_route`).

### 2026-10-03 — Pergunta direta: qual hipótese tentar ANTES da defesa (prazo curto)? RMW swap vence por esforço/risco/reversibilidade

Contexto da pergunta: o número de 70% (7/10) deixou de ser observação
informal e passou a estar citado como resultado quantitativo no Cap. 09
(Limitações) da dissertação (branch `dissertacao`, não acessível direto
deste checkout na branch de código — não pude ler o `.tex` nesta sessão,
mas a informação foi dada no pedido da rodada e é consistente com o que
já se sabia). Isso eleva a prioridade de qualquer mitigação barata.

**Comparação das 3 hipóteses, com achados novos confirmados nesta rodada:**

1. **`RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` (troca de RMW via variável
   de ambiente) — recomendação: tentar antes da defesa.**
   - **Confirmado por leitura direta do código (não suposição) que o
     teste exige ZERO mudança de código:** `backend/ros_bridge.py:21-25`
     (`ros_env()`) monta o ambiente dos subprocessos com `**os.environ`
     (herda tudo do processo pai) só sobrescrevendo `ROS_DOMAIN_ID`;
     `fleet_ws/scripts/run_ground_truth_campaign.py:102-109`
     (`launch_bash`) chama `subprocess.Popen(["bash", "-c", full], ...)`
     **sem passar `env=` nenhum**, o que em Python significa herdar o
     ambiente do processo pai automaticamente. Ou seja: exportar
     `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` no shell antes de rodar o
     backend OU o script de campanha já propaga pra toda a árvore de
     processos `ros2 launch`, sem tocar em nenhum `.py`.
   - **Pré-requisito real, confirmado pelo `Dockerfile` (raiz do repo,
     linha 38): só `ros-${ROS_DISTRO}-desktop` é instalado — isso NÃO
     inclui `ros-jazzy-rmw-cyclonedds-cpp`** (é um pacote apt separado
     do metapacote desktop). Testar exige primeiro
     `apt-get install ros-jazzy-rmw-cyclonedds-cpp` (1 linha, baixo
     risco, pacote oficial do mesmo repositório apt já configurado no
     Dockerfile) — sem isso, setar a variável só faz o `ros2 launch`
     falhar ao carregar o RMW.
   - **Achado novo, bem confirmado (fonte primária oficial — corrige uma
     suposição que eu quase assumi errada):** o manual oficial do
     usuário do TurtleBot4
     ([turtlebot.github.io/turtlebot4-user-manual/software/turtlebot4_setup.html](https://turtlebot.github.io/turtlebot4-user-manual/software/turtlebot4_setup.html))
     confirma que a ferramenta de setup do robô real tem uma opção
     explícita `RMW_IMPLEMENTATION` com 2 valores (`rmw_fastrtps_cpp` —
     **default** —, `rmw_cyclonedds_cpp`), com a única ressalva de que
     o RMW escolhido precisa bater com o que o firmware do Create 3
     suporta. **Correção de uma busca anterior nesta mesma rodada:** um
     resumo de busca inicial sugeriu que "o TurtleBot4 usa Cyclone DDS
     por padrão" — isso é falso, fui conferir na fonte primária (o
     manual oficial) antes de registrar, e o default real é Fast DDS,
     igual ao ROS 2 Jazzy puro. O que FICA confirmado e é útil mesmo
     assim: alternar pra Cyclone DDS no TurtleBot4 é um caminho
     oficialmente suportado e documentado pelo próprio fabricante da
     plataforma (não uma combinação exótica/não testada), o que reduz o
     risco de incompatibilidade.
   - **Achado correlato, registrado como NÃO CONFIRMADO (não achei fonte
     primária que bata o número exato):** uma thread no fórum do ROS
     ([discourse.openrobotics.org/t/how-many-dds-participants-are-currently-used-allowed-by-rmw/49976](https://discourse.openrobotics.org/t/how-many-dds-participants-are-currently-used-allowed-by-rmw/49976))
     discute um limite de participantes (um usuário cita "32" associado
     a `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`/`maxInitialPeersRange`
     do Fast DDS) e afirma que Fast DDS falha silenciosamente ao bater
     esse limite (nós somem de `ros2 node list` sem aviso) enquanto
     Cyclone DDS emite aviso no console. Tentei confirmar o número "32"
     direto na documentação oficial do Fast DDS e no `.rst` oficial do
     ROS 2 sobre `ROS_AUTOMATIC_DISCOVERY_RANGE` — **nenhum dos dois
     menciona esse número**; a doc oficial do ROS 2 não cita limite
     numérico nenhum. Registro isso como pista NÃO CONFIRMADA, não como
     fato: *se* for real, seria um mecanismo plausível pra explicar por
     que as falhas não têm padrão limpo (ora o 1º robô, ora o 2º —
     consistente com "cruzar um limiar de contagem de participantes de
     forma não-determinística conforme o timing de cleanup de DDS dos
     processos anteriores", não um bug fixo em um nó específico). Mas
     isso é hipótese, não achado verificado — não deve ser citado na
     dissertação como fato.

2. **`ComposableNodeContainer` — recomendação: manter como trabalho
   futuro documentado, não tentar antes da defesa.**
   É a hipótese com o mecanismo mais diretamente confirmado (achado
   de 2026-10-02: Nav2 upstream já usa por padrão, SLAM Toolbox suporta,
   números reais de CPU no fórum mostram overhead por participante), mas
   exige reescrever `nav2_minimal.launch.py`/`activate_robot_nav.launch.py`
   de verdade — os mesmos arquivos que, há 3 dias, já causaram uma
   regressão real neste projeto (corte do `waypoint_follower` por engano
   de escopo, só descoberto ao vivo rodando `run_fleet`, ver achado de
   2026-10-03 acima). Editar esses arquivos de novo, sob prazo curto, sem
   tempo de testar AMBOS os casos de uso (`go_to_point` e `play_route`)
   de novo, é o tipo exato de risco que já se materializou uma vez aqui.
   Esforço alto + risco real de regressão nova perto da defesa > ganho
   potencial não comprovado em cenário localhost especificamente.

3. **`ROS_DISCOVERY_SERVER` — recomendação: manter como trabalho futuro
   documentado, prioridade mais baixa que as outras duas.**
   Sem mudança no achado de 2026-10-02 (ganho de até 93% medido é pra
   tráfego de rede real/SDP, nenhuma fonte encontrada confirma ganho em
   localhost/shared-memory). Esforço aqui é maior que a troca de RMW
   (precisa de um processo servidor novo, vivo e saudável durante toda
   uma campanha de 30 réplicas, com seu próprio risco de ponto único de
   falha) sem evidência de que o ganho se aplica ao cenário real deste
   projeto (1 máquina só).

**Ação sugerida (resumo pra decisão do autor):** rodar um A/B antes da
defesa — N réplicas (sugestão: igual ou maior que as 10 já usadas na
campanha de ground truth) da ativação sequencial multi-robô com o
default atual vs. com `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` exportada
antes de subir o backend/script, usando a infraestrutura de retry que
já existe (`run_ground_truth_campaign.py` ou o piloto de ativação
sequencial) pra contar quantas tentativas cada réplica precisou — isso
dá um número real pra comparar contra os 7/10 já citados na dissertação,
não só "testamos e parece melhor". Pré-requisito: instalar
`ros-jazzy-rmw-cyclonedds-cpp` (não está no `Dockerfile` hoje). Se não
houver tempo nem pra esse teste simples antes da defesa, a alternativa
mais honesta é documentar os 70% como limitação conhecida (já é o caso)
e citar `ComposableNodeContainer`/`ROS_DISCOVERY_SERVER`/troca de RMW
como trabalho futuro no texto já existente — não inventar um resultado
de mitigação que não foi medido.

### 2026-10-05 — detalhe concreto sobre ComposableNodeContainer (achado via skill ros2 instalada, não pesquisa nova)

- **[sessão, não agente]** Ao explorar a skill `ros2` recém-instalada
  (`.claude/skills/ros2`), confirmei direto no arquivo real que este
  projeto usa (`/opt/ros/jazzy/share/turtlebot4_navigation/launch/nav2.launch.py`,
  linha 73): ele inclui `nav2_bringup/launch/navigation_launch.py` com
  `('use_composition', 'False')` **hardcoded inline**, não exposto como
  `DeclareLaunchArgument` próprio (só `use_sim_time`, `params_file`,
  `namespace` são declarados). `navigation_launch.py` em si **já suporta
  composição nativamente** (6 ocorrências reais de `use_composition`, não
  comentário solto) — não seria preciso escrever componente C++ do zero,
  só ativar o que já existe. Mas como `nav2.launch.py` do TurtleBot4 não
  expõe essa opção pra quem chama de fora, a única forma de usar é (a)
  fazer um fork pequeno desse arquivo específico (mesmo padrão já usado
  pro xacro do DiffDrive) trocando a string `'False'` por
  `LaunchConfiguration('use_composition')`, ou (b) escrever um launch
  próprio que inclua `navigation_launch.py` direto, pulando o wrapper do
  TurtleBot4. Não muda a recomendação de ontem (RMW primeiro, composição
  depois da defesa) — só deixa mais preciso o "porquê" técnico de ser
  mexer em launch file, não parâmetro simples.

### 2026-10-05 — pesquisa mais a fundo: confirma RMW atual (Fast DDS), achado de corroboração forte, e um risco novo a conhecer antes de trocar

- **[sessão, não agente]** Confirmado direto nesta máquina (`RMW_IMPLEMENTATION`
  vazio, só `ros-jazzy-rmw-fastrtps-cpp` instalado via `dpkg -l`, nenhum
  pacote `rmw-cyclonedds` presente): o bug reproduzido ao vivo hoje
  (tentativa de demo com 2 robôs, "jump back in time" repetido, Nav2 nunca
  ficou pronto em 300s) aconteceu sob **Fast DDS**, o default do Jazzy —
  não Cyclone DDS.
- **Corroboração forte e independente da recomendação de ontem** (trocar
  pra Cyclone DDS): no fórum oficial ROS/Gazebo (ROS Discourse,
  `discourse.openrobotics.org/t/fastdds-without-discovery-server/26117`),
  múltiplos usuários independentes relatam exatamente essa classe de
  sintoma — um especificamente diz que reiniciar launch files individuais
  faz tópicos (particularmente `tf`) falharem ao conectar **~75% das
  vezes** sob Fast DDS numa única máquina, `ros2 node list` não lista
  todos os nós, chamadas de serviço dão timeout — e que "todos os
  problemas desapareceram magicamente" ao trocar pra Cyclone DDS. Isso é
  da mesma ordem de grandeza do nosso próprio achado (70% de sucesso =
  ~30% de falha), em outro projeto, outro autor, mesma dupla de sintomas
  (TF + serviço). Fortalece bastante a prioridade de testar RMW antes da
  defesa.
- **Risco novo a conhecer, não descoberto antes**: Cyclone DDS tem seu
  próprio bug real e documentado sob bringup concorrente — issue oficial
  `github.com/ros2/rmw_cyclonedds/issues/458`, erro "Failed to find a
  free participant index for domain 0" quando vários processos sobem ao
  mesmo tempo (exatamente o padrão do Nav2 bringup). Fix conhecido: variável
  de ambiente antes do launch —
  `CYCLONEDDS_URI='<CycloneDDS><Discovery><ParticipantIndex>auto</ParticipantIndex><MaxAutoParticipantIndex>100</MaxAutoParticipantIndex></Discovery></CycloneDDS>'`
  (default do índice de participante é baixo o bastante — a faixa 32-99
  aparece em fontes diferentes, não cravei o número exato — pra esgotar
  sob bringup de frota). **Ação sugerida**: se/quando o teste de RMW
  acontecer, aplicar essa env var junto da troca pra Cyclone DDS desde o
  início, não só depois de ver falha nova — senão corre o risco de trocar
  um bug conhecido por outro bug conhecido e achar que "não funcionou".
