# Conhecimento acumulado: Tuning de DDS/ROS 2 para multi-robô

## TL;DR

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
