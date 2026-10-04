# Conhecimento acumulado: Fidelidade de simulação — Gazebo Harmonic / gz-sim

## TL;DR

A perda do nome da entidade no bridge `Pose_V` → `TFMessage` (que motivou o
nó `ground_truth_filter` por índice fixo) continua sem correção oficial:
revisei todo o changelog do `ros_gz_bridge` até a versão mais recente
(4.0.1, 2026-08-31) e não há nenhuma entrada que preserve nome/`child_frame_id`
por entidade nesse bridge específico — então a solução atual (filtro frágil
por índice) ainda é a única disponível, não é um workaround temporário que
ficou obsoleto. Em compensação, apareceram duas peças novas relevantes pra
fidelidade: (1) existe um plugin oficial `WheelSlip` no gz-sim (separado do
`DiffDrive`) que modela slip lateral/longitudinal de forma configurável —
hoje a dissertação registra "DiffDrive não modela slip" como limitação, mas
isso poderia ser mitigado adicionando esse plugin, não é um limite
intrínseco do simulador; (2) ruído gaussiano em sensores LiDAR já é nativo
do formato SDF (`<sensor><noise type="gaussian">`), não precisa de plugin
de terceiros — só não documentamos isso antes. Bindings Python de
gz-transport via apt continuam inexistentes para Jazzy/Harmonic (reconfirmado).

**Atualização 2026-10-03 (ground truth agora é resultado publicado, não só
infraestrutura — 3 perguntas novas):** (1) achei a causa raiz EXATA (lendo o
código-fonte do `gz-sim` e do `ros_gz_bridge` linha a linha) de por que o
nome da entidade se perde no bridge: o Gazebo (`SceneBroadcaster`) **já
coloca o nome de cada entidade** (`pose.name()`) em todo item de
`dynamic_pose/info`, só que o `ros_gz_bridge` procura o `child_frame_id` num
lugar diferente (dentro de `header().data()` de cada Pose individual, que o
Gazebo nunca preenche) — é um descompasso de dois códigos que nunca olham
pro mesmo campo, não falta de dado na fonte. Isso é novo em relação ao
achado de 2026-10-02 (que só confirmou "não tem correção no changelog", sem
saber o mecanismo exato). Também achei que `dynamic_pose/info` é limitado a
60Hz por padrão (configurável, `dynamic_pose_hertz` no SDF do mundo deste
projeto não foi localizado/confirmado) e que o timestamp real da física
(`simTime`) existe no nível do `Pose_V` mas se perde na conversão por causa
do mesmo descompasso — o `ground_truth_filter` deste projeto já contorna
isso usando o clock da simulação no momento do recebimento, o que é
correto, mas não é exatamente o instante em que a física calculou aquela
pose (ver achado detalhado, inclui "Ação sugerida" sobre mencionar isso como
ameaça à validade). (2) **Reavaliação do `WheelSlip`: dado que a dissertação
é só-simulação (sem comparação com robô real nesta versão), a recomendação
mudou de "avaliar se vale implementar" para "não vale o esforço agora,
melhor deixar só como limitação documentada"** — sem dado real de slip pra
calibrar `slip_compliance_lateral/longitudinal`, adicionar o plugin só troca
um parâmetro não-modelado por um parâmetro modelado-mas-arbitrário, não
aumenta fidelidade de verdade. `implementacao.md` atualizado. (3) Ruído
Gaussiano de LiDAR via SDF: confirmado que **continua não usado** — e o
motivo é que nunca foi usado nem no pacote vendor de onde este projeto faz
fork (`nav2_minimal_tb4_description`, upstream oficial do Nav2/TurtleBot4);
não é uma lacuna introduzida por este projeto. Achado lateral: o IMU deste
mesmo robô **tem** blocos `<noise type="gaussian">` (também herdados do
vendor), mas com `stddev="0.0"` em todos os eixos — presentes na estrutura,
mas sem efeito nenhum (equivalente a não ter ruído).

**Atualização 2026-10-02 (pergunta de alinhamento de frames pro piloto):**
pesquisei de verdade (código-fonte do `gz-math`/`gz-sim`, código-fonte do
`slam_toolbox`, REP-103, REP-105) a dúvida registrada em `orquestracion.md`
sobre se `/ground_truth_pose_clean` (frame world), `/odom` (frame odom) e
`/pose`/TF `map` (SLAM) começam na mesma origem. Resultado direto do
código, não de convenção informal: o plugin `DiffDrive` do Gazebo **sempre
zera `/odom` pra (0,0,0,heading=0) no instante em que o plugin inicializa**,
independente da pose real de spawn do robô no mundo SDF — não é uma
convenção, é hard-coded. O `slam_toolbox` (modo sync) inicializa a TF
`map`→`odom` como identidade e, no primeiro scan processado, calcula essa
TF a partir da pose do `odom` naquele instante (sem correção ainda) — ou
seja, `map` também nasce alinhado com onde o `odom` estava no primeiro
scan. Pra este projeto específico (spawn em x=0,y=0,yaw=0, sem nenhum
offset explícito), as três fontes **deveriam** reportar ~(0,0,0) no
instante inicial, mas isso depende de o robô estar parado entre o spawn e
o primeiro scan do SLAM — não é garantido por nenhuma das bibliotecas,
é consequência do setup. Ver achados detalhados abaixo. Ação sugerida:
validação prática ao vivo antes do piloto grande (não dá pra confirmar
100% só por literatura, convenções variam por simulador/config).

Este arquivo é mantido pelo agente `experiment-gazebo-tracking`
(`.claude/agents/experiment-gazebo-tracking.md`) — cada execução lê isto
primeiro, pesquisa o que falta, e acrescenta achados novos abaixo, sem
apagar o que já existe.

## Achados

### 2026-10-02

- **Perda de nome de entidade no bridge Pose_V→TFMessage: ainda não corrigida.**
  Revisei o `CHANGELOG.rst` completo do `ros_gz_bridge` (repo
  `gazebosim/ros_gz`, branch `ros2`) até a versão 4.0.1 (2026-08-31). A
  conversão `TFMessage`/`Pose_V` existe desde a PR #117 (bem antiga). As
  únicas mudanças relacionadas a frame_id/Pose_V nas versões recentes são:
  "Add support for configurable frame_id in Gazebo subscriber" (#825) e
  "Add override_frame_id parameter" (#826), ambas na versão 3.0.6
  (2026-02-04), e "Fix missing timestamp in Pose_V -> PoseArray bridge"
  (#812). Nenhuma delas resolve o problema de perda de nome por entidade —
  `override_frame_id` sobrescreve o `header.frame_id` com **uma única
  string fixa** pra todo o bridge (pensado pra câmeras/frames ópticos), não
  ajuda a distinguir entidades dentro do array `Pose_V`. Conclusão: o nó
  `ground_truth_filter` por índice fixo continua sendo a única solução
  disponível, não ficou obsoleto. Fonte primária:
  `https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_bridge/CHANGELOG.rst`
  (lido diretamente via `curl`, conteúdo real, não resumo de busca).

- **Versão do `ros_gz_bridge` instalada localmente está defasada.** O pacote
  `ros-jazzy-ros-gz-bridge` instalado nesta máquina é 1.0.22
  (`1.0.22-1noble.20260412.043437`); há candidato 1.0.24 disponível no apt
  (`apt-cache policy`). Nota: o esquema de versão do pacote apt (1.0.x) não
  parece corresponder diretamente às tags do repo upstream (3.0.x/4.0.x do
  CHANGELOG.rst) — pode ser um pacote de release separado por distro ROS
  (Jazzy) vs. versionamento do repo em si. Não investigado a fundo; vale
  reconferir se for tentar reproduzir `override_frame_id` localmente.

- **Existe plugin oficial `WheelSlip` no gz-sim, separado do `DiffDrive`,
  que modela slip de roda de forma configurável.** Confirmado via
  documentação oficial `https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1WheelSlip.html`
  (sim8 = API da linha Harmonic, confirmado em
  `https://gazebosim.org/docs/harmonic/install_ubuntu`, que lista
  "sim" apontando pra `/api/sim/8`). Parâmetros: `slip_compliance_lateral`
  e `slip_compliance_longitudinal` (adimensionais — razão entre força
  tangencial e normal; zero = sem slip), mais `wheel_normal_force` e
  `wheel_radius` por roda. **Tensão com decisão já tomada**: a dissertação
  registra "o plugin DiffDrive do Gazebo não modela slip de roda" como
  limitação de validade externa — isso está correto para o `DiffDrive`
  isoladamente, mas existe um plugin oficial adicional (`WheelSlip`, atua
  nos contatos roda-solo, usado junto com `DiffDrive`) que poderia mitigar
  essa limitação. Não decidi se vale adotar — registro aqui pra quem revisar
  a seção de limitações decidir se reformula o texto (de "o simulador não
  modela slip" pra "o setup atual não ativa o modelo de slip disponível").

- **Ruído gaussiano em LiDAR é nativo do SDF, não precisa de plugin de
  terceiros.** Confirmado via busca nos resultados oficiais de
  `gazebosim.org/api/sdformat` (classe `Lidar`, elemento `<noise
  type="gaussian">` com `mean`/`stddev`, função `ApplyNoise()` no
  `gz-sensors`). Isso já é suportado nativamente há várias versões — não é
  um achado "novo" do Gazebo, é uma lacuna de documentação nossa: ainda não
  tínhamos registrado que dá pra configurar ruído de LiDAR sem plugin
  externo, só editando o SDF do sensor. Ação sugerida abaixo.

- **DiffDrive (sim8/Harmonic) confirmado sem parâmetros de ruído/slip
  nativos.** Revisei a doc oficial completa do plugin
  (`gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1DiffDrive.html`):
  parâmetros são `left_joint`, `right_joint`, `wheel_separation`,
  `wheel_radius`, `odom_publish_frequency`, `topic`, `enable_topic`,
  `odom_topic`, `tf_topic`, `frame_id`, `child_frame_id`, e limites de
  velocidade/aceleração/jerk. Nenhum parâmetro de ruído ou slip. Confirma
  que a limitação registrada na dissertação está correta pro `DiffDrive`
  isolado (ver achado do `WheelSlip` acima pra nuance).

- **Bindings Python de gz-transport via apt: reconfirmado que não existem
  para Jazzy/Harmonic.** `apt-cache search python3-gz` e
  `apt-cache show python3-gz-transport13`/`14` nesta máquina (Ubuntu
  Noble) só retornam `python3-gz-math6` e `python3-gz-sim6`, que são
  pacotes de transição (`Section: oldlibs`) apontando pra
  `python3-ignition-gazebo6`/`ignition-math6` 6.x — binários antigos da
  era Ignition/Jammy (Fortress), não relacionados a Jazzy/Harmonic. Não
  existe `python3-gz-transport13` nem `14` no apt. O pacote
  `ros-jazzy-gz-transport-vendor` instalado (vendoring de gz-transport13
  13.6.0 pro ROS) é C++, sem bindings Python expostos via apt. Sem mudança
  em relação ao que já tinha sido observado antes.

### 2026-10-02 (rodada 2) — alinhamento de frames world/odom/map antes do piloto /odom vs /pose vs ground truth

Pergunta concreta (vem de `orquestracion.md`, seção "Plano: campanha
/odom vs. /pose vs. ground truth"): `/ground_truth_pose_clean` (frame
`world` do Gazebo), `/odom` (`DiffDrive`) e `/pose`/TF `map` (SLAM
Toolbox) começam todos na mesma origem/orientação, ou existe um offset
padrão entre eles que precisaria de transformação antes de calcular
RMSE? Pesquisei direto no código-fonte (não documentação de alto nível),
porque a pergunta é sobre comportamento exato de inicialização.

- **`/odom` (plugin `DiffDrive`, gz-sim) sempre começa em (0,0,0,heading=0)
  por construção, independente da pose real do robô no mundo SDF.**
  Confirmado lendo o código-fonte real de
  `gz::math::DiffDriveOdometry::Init()`
  (`https://raw.githubusercontent.com/gazebosim/gz-math/gz-math7/src/DiffDriveOdometry.cc`,
  lido via curl, conteúdo primário, não resumo): `Init()` zera
  explicitamente `x = 0.0; y = 0.0; heading = 0.0;` toda vez que a
  odometria é inicializada (chamado de `DiffDrivePrivate::UpdateOdometry`
  em `DiffDrive.cc` do `gz-sim`, repo
  `https://raw.githubusercontent.com/gazebosim/gz-sim/gz-sim8/src/systems/diff_drive/DiffDrive.cc`,
  também lido via curl — `if (!this->odom.Initialized()) { this->odom.Init(...); }`).
  Ou seja: **não é uma convenção documentada em prosa, é comportamento de
  código** — a odometria é puramente integração das juntas das rodas a
  partir de zero, sem nenhuma leitura da pose absoluta do modelo no mundo
  SDF. Implicação importante pra generalizar: se o robô fosse spawnado
  com `yaw` ≠ 0 (não é o caso deste projeto, que usa default `"0.0"`), o
  heading=0 do `/odom` NÃO coincidiria com o heading=0 do frame `world` —
  o eixo "x" do `/odom` seria a direção que o robô apontava no instante em
  que o plugin inicializou, não o eixo x do mundo SDF. Pra este projeto
  (yaw de spawn = 0 por default), isso não é um problema, mas é um
  detalhe que quebraria se alguém mudasse o `yaw` de spawn sem lembrar
  disso.

- **`slam_toolbox` (modo sync) inicializa a TF `map`→`odom` como
  identidade e a computa pela primeira vez a partir da pose do `odom` no
  primeiro scan processado (sem correção de scan-matching ainda).**
  Confirmado lendo `slam_toolbox_common.cpp` (repo
  `https://raw.githubusercontent.com/SteveMacenski/slam_toolbox/ros2/src/slam_toolbox_common.cpp`,
  via curl): `map_to_odom_.setIdentity();` no construtor/configure (linha
  ~343); `shouldProcessScan()` dá passe livre pro primeiro scan
  (`first_measurement_`, linha ~829) sem exigir deslocamento mínimo;
  `setTransformFromPoses()` (linha ~732) calcula `map_to_odom_` a partir
  de `corrected_pose` vs. `odom_pose` — e pra esse primeiro scan a pose
  "corrigida" pelo mapeador (Karto) ainda não teve nenhuma correção real
  aplicada (não há mapa anterior pra comparar), então na prática
  `corrected_pose ≈ odom_pose` nesse instante, e a TF `map`→`odom`
  resultante fica ≈ identidade. **Isso bate exatamente com o texto da
  REP-105** (fonte oficial ROS,
  `https://docs.ros.org/en/independent/api/rep/html/rep-0105.html`,
  confirmada via busca — tentativa de `WebFetch` direto em
  `reps.openrobotics.org/rep-0105.html` deu 404, então uso a cópia em
  `docs.ros.org` como referência, não verifiquei o conteúdo completo
  dessa URL específica diretamente nesta sessão, só via resultado de
  busca — marcar como **não 100% confirmado por leitura direta da
  página**, mas o texto citado é consistente e amplamente reproduzido):
  "The map and odom frames are world-fixed frames whose origins are
  typically aligned with the robot's start position." Ou seja: o
  comportamento do `slam_toolbox` implementa exatamente essa convenção
  documentada — não é coincidência.

- **Convenção de eixos: Gazebo (gz-sim/SDF) e ROS usam a mesma convenção
  de mão (right-handed, X-frente/Y-esquerda/Z-cima) — não é esperado um
  rotação sistemática entre o frame `world` bruto e os frames ROS por
  esse motivo.** Confirmado via `gazebosim.org/api/sim/8/frame_reference.html`
  (conteúdo lido via `WebFetch`): a página afirma explicitamente "Gazebo
  follows REP 103" e descreve a mesma convenção X-frente/Y-esquerda/Z-cima
  que a REP-103 (fonte ROS) documenta pra frames robóticos
  (`answers.ros.org`/busca confirmou o texto da REP-103, não li o HTML
  oficial da REP-103 diretamente nesta sessão — mesma ressalva de "não
  100% confirmado por leitura direta da página primária", mas o conteúdo
  é consistente entre múltiplas fontes). A mesma página do gz-sim também
  menciona que o Gazebo suporta coordenadas geográficas reais (WGS84) com
  um plano tangente local em convenção ENU **por padrão apenas quando o
  mundo usa coordenadas geográficas** — não é o caso deste projeto
  (mundo `warehouse`, sem referência geográfica), então essa ressalva de
  ENU-vs-outra-convenção não se aplica aqui. **Conclusão da pergunta 3
  do pedido**: não encontrei nenhuma convenção documentada que preveja um
  offset/rotação sistemático entre `world` (Gazebo), `odom` (`DiffDrive`)
  e `map` (SLAM Toolbox) quando o robô é spawnado na origem com yaw=0 —
  pelo contrário, o código de ambos os sistemas (`DiffDrive` zera pra
  (0,0,0); `slam_toolbox` inicializa `map`→`odom` como identidade a
  partir da pose do `odom` no primeiro scan) aponta pra alinhamento
  exato nesse caso específico. Mas isso é dedução a partir de como cada
  peça é inicializada isoladamente, não um teste end-to-end real deste
  projeto — pesquisa de literatura não é garantia equivalente a medir.

### Ação sugerida (prioridade alta — fazer antes do piloto)

**Validar ao vivo, não só por dedução de código.** A pergunta 4 do pedido
é a ação mais decisiva e barata disponível: depois do robô spawnar e
ANTES de qualquer comando de movimento (robô parado), gravar/ler uma
amostra de cada uma das três fontes (`/ground_truth_pose_clean`, `/odom`,
`/pose` ou a TF `map`→`base_link`) e comparar manualmente. Se as três
reportarem ~(0,0,0) de posição e ~0 de yaw nesse instante (tolerância de
alguns mm/graus, não exata), o alinhamento está confirmado empiricamente
pra esta configuração específica, sem precisar de nenhuma transformação
estática adicional — e o passo 2 do plano da campanha ("piloto antes da
campanha grande") já cobre isso, só precisa ser feito com essa checagem
explícita no início, não só no fim (comparar as trajetórias sobrepostas
já é bom, mas comparar o PRIMEIRO ponto de cada fonte, isolado, é um
teste mais direto e mais fácil de diagnosticar se falhar). Se não
coincidirem, a causa mais provável — dado o que o código mostra — não é
convenção de eixo (gz-sim e ROS já concordam nisso), e sim: (a) o SLAM
Toolbox só processar o primeiro scan DEPOIS do robô já ter se movido um
pouco (ex.: delay de bringup), ou (b) algum offset manual/parâmetro de
`initial_pose` configurado em algum lugar do bringup do Nav2/SLAM deste
projeto que eu não localizei nesta pesquisa (não procurei exaustivamente
por `initial_pose` nos arquivos de launch/params do projeto — isso é
verificação de código do próprio projeto, não pesquisa de literatura,
fora do escopo desta execução, mas vale conferir antes de rodar o
piloto). Conferi rapidamente (grep por `initial_pose`/`map_frame`/
`odom_frame` em `fleet_ws/src/**/*.yaml`/`*.py`) e não encontrei nenhum
`initial_pose` explícito no código próprio do projeto — só
`use_shared_map_frame`, que é parâmetro próprio do `fleet_orchestrator`,
não do SLAM Toolbox/Nav2. Reforça que (b) é pouco provável, mas não é
auditoria exaustiva dos `.yaml` de bringup do TB4/Nav2 vendor (fora deste
repo). Não alterei nenhum código do projeto nesta execução.

- Considerar adicionar `<noise type="gaussian">` ao sensor LiDAR usado no
  experimento (editar o SDF/URDF do TurtleBot4, ou o xacro, se o projeto
  usa um) pra ter ruído realista configurável sem precisar de plugin
  externo. Não fiz essa edição — só código, e a regra desta execução é não
  alterar nada fora deste arquivo.
- Avaliar se vale adicionar o plugin `WheelSlip` ao modelo do robô (junto
  com `DiffDrive`) nos links de roda, como experimento complementar de
  fidelidade, ou pelo menos reformular o texto da limitação na dissertação
  de "o simulador não modela slip" pra algo mais preciso tecnicamente. Essa
  é uma decisão de conteúdo da dissertação, não tome sozinho — só sinalizo.
- Se algum dia for necessário reescrever `ground_truth_filter` de forma
  menos frágil (não mais por índice fixo), a conclusão desta execução é que
  não vai vir de uma correção upstream do `ros_gz_bridge` — vai ter que ser
  lógica própria (ex.: casar poses por nome via outro tópico, tipo
  `/world/<world>/pose/info` com `gz.msgs.Pose_V` que porventura preserve
  nome, a confirmar em execução futura — não testado nesta sessão).

### 2026-10-02 — Achado real e grave: ground truth congela por ~10-16s logo após o boot da simulação

Não é pesquisa de literatura — é achado ao vivo do autor rodando o piloto
da campanha /odom vs /pose vs ground truth (ver `orquestracion.md`, plano
dessa campanha, e `fleet_ws/scripts/pilot_ground_truth_check.py`, criado
nesta sessão).

**O que aconteceu:** logo depois de subir a stack do zero
(`turtlebot4_sim.launch.py` + `fleet.launch.py`), gravei um replay da rota
`dissertation_clean01` com `/odom`, `/pose`, `/ground_truth_pose_clean`.
`/odom` e `/pose` mostraram o robô se movendo normalmente (até ~0,93m),
mas `/ground_truth_pose_clean` ficou **congelado em (0,0,0) por quase toda
a gravação de 18s**, só "pulando" pro valor correto na ÚLTIMA mensagem do
bag. Isso inflou artificialmente o RMSE de `/pose` vs. ground truth
(43,96cm) pra um valor PIOR que `/odom` vs. ground truth (15,49cm) — o que
seria um resultado contraintuitivo e preocupante (SLAM corrigindo pra
pior) se fosse real.

**Diagnóstico (eliminei 2 hipóteses antes de achar a causa real):**
1. Não é desalinhamento de timestamp (bag-write-time vs. header.stamp) —
   testei as duas formas em `analyze_runs.py::_read_traj_xy` (parâmetro
   novo `use_header_stamp`), resultado idêntico.
2. Não é o índice fixo (`ROBOT_INDEX=2`) errado — confirmei com
   `gz topic -e -t /world/warehouse/dynamic_pose/info -n 1` (nomes reais,
   bypassando o bridge) que o índice 2 É `turtlebot4` e reporta a posição
   correta e em movimento quando testado isoladamente nessa checagem
   pontual.
3. **Causa real: artefato de cold-start.** Regravei o MESMO replay, na
   MESMA stack (sem reiniciar nada), depois que o robô já tinha se movido
   uma vez antes (stack "aquecida") — `/ground_truth_pose_clean` acompanhou
   `/odom` corretamente o tempo todo, numa gravação de 67s com ida e volta
   completa pela rota (path=2,17m), sem nenhum congelamento. A diferença
   entre as duas gravações foi só "é a primeira vez que o robô se move
   depois do boot da stack" vs. "não é".

**Rates reais medidos ao vivo (resolve a inconsistência que o agente
`experiment-stats-methodology` já tinha sinalizado em `stats_methodology.md`
sobre números conflitantes pro ground truth):**
- `/ground_truth_pose_clean`: ~105-111Hz (convergindo, `ros2 topic hz`
  reporta a média subindo nos primeiros segundos — é a média cumulativa
  da janela, não a taxa instável).
- `/odom`: ~27,8Hz (perto do `odom_publish_frequency: 30` do URDF, não
  exato).
- `/scan`: 10,0Hz exato.
- `/pose`: **~0,2-0,8Hz, variável entre execuções** — ainda mais esparso
  que a estimativa de ~2Hz do agente de estatística, porque além do
  `minimum_time_interval: 0.5` também há `minimum_travel_distance: 0.1`m
  e `minimum_travel_heading: 0.1`rad (`slam.yaml`) — SLAM Toolbox só
  processa um novo scan depois do robô andar/girar o suficiente, então a
  taxa real depende de quão rápido o robô se move, não é uma constante.
  Com o robô parado, `/pose` não publica NENHUMA mensagem (confirmado:
  15s de espera sem nenhuma mensagem com o robô parado no spawn).

**Ação sugerida (prioridade alta, bloqueante pra campanha principal):** o
plano da campanha (`orquestracion.md`) prevê relançar a simulação inteira
antes de CADA uma das 30 réplicas. Se esse congelamento de cold-start
acontecer em toda réplica (não testei isso — só testei 1 boot, 2
replays), as 30 réplicas podem ter a mesma janela inicial de dados de
ground truth inválidos, contaminando a campanha inteira do mesmo jeito.
Antes de rodar a campanha de verdade: (a) confirmar se o congelamento
realmente se repete em todo boot fresco (testar mais algumas vezes), e
(b) se confirmado, decidir uma mitigação — ex.: um período de
"assentamento" (mover o robô um pouco e descartar esses dados antes de
começar a réplica oficial), ou detectar/descartar automaticamente
qualquer trecho inicial de ground truth com variância ~0 enquanto
`/odom` mostra movimento real. Não implementei nenhuma mitigação ainda —
só o diagnóstico. O RMSE de 43,96cm de `/pose` vs. ground truth do piloto
original **não deve ser usado nem citado** — é artefato do congelamento,
não um resultado real sobre a qualidade do SLAM.

### 2026-10-02 — Atualização do achado acima: provavelmente NÃO é um bug do ground truth

Testei 2 boots frescos adicionais, de propósito, pra confirmar se o
congelamento se repete em todo boot — e **não se repetiu em nenhum dos
dois**. Nos dois casos, `/ground_truth_pose_clean` acompanhou `/odom`
corretamente a gravação toda, com concordância quase perfeita
(odom=0,8423m vs gt=0,8424m no boot 1; odom=0,8340m vs gt=0,8340m no
boot 2 — mesma rota curta `dissertation_clean01`).

**O que mudou entre o piloto original (congelou) e esses 2 boots (não
congelaram):** antes de rodar os 2 boots novos, descobri e matei um
conjunto de processos **órfãos** de uma bateria de testes anterior
(bridges `parameter_bridge`/`image_bridge` de PIDs antigos, ainda vivos
~30min depois, competindo por CPU com a simulação nova — `uptime` chegou
a mostrar load average 14,16, caiu pra ~0,2 só depois de matar os
órfãos). É plausível — não comprovado com certeza absoluta, já que não
recriei o cenário exato do piloto original de propósito — que o
congelamento original tenha sido causado por essa mesma contenção de CPU
(órfãos disputando recursos com a simulação nova), não por um defeito
intrínseco do bridge/filtro de ground truth.

**Achado lateral, mas relevante:** numa 3a tentativa de boot fresco
(depois dos 2 boots limpos acima), a simulação travou de verdade —
parou de progredir por >2min em
`docking_server.rclcpp: failed to send response to /docking_server/change_state
(timeout)`, nunca chegou a "Managed nodes are active". Isso é uma
reprodução ao vivo do problema JÁ CONHECIDO e documentado em
`conhecimento/dds_tuning.md` (ativação sequencial com ~70% de taxa de
sucesso) — não é um achado novo, é confirmação de que o problema
continua acontecendo espontaneamente, mesmo numa máquina com load baixo
no momento do boot.

**Conclusão revisada:** o risco real pra campanha principal não é
"ground truth congela sistematicamente no cold-start" (evidência agora
pesa contra isso, 2 testes limpos OK) — é o problema JÁ CONHECIDO de
falha de ativação sequencial intermitente (dds_tuning.md). A mitigação
certa não é algo específico de ground truth; é a mesma que já estava
pendente pra esse outro problema: higiene de processo rigorosa entre
réplicas (matar TUDO antes de cada boot novo, não confiar que o processo
anterior terminou limpo) e/ou um mecanismo de detecção de
timeout-e-retry pra bringup que não progride. Ver `implementacao.md`.

### 2026-10-02 — O mundo real da simulação (`nav2_minimal_tb4_sim`) tem geometria diferente do mapa de referência do `turtlebot4_navigation`

Achado ao criar as rotas longa/loop do plano de campanha (`orquestracion.md`,
passo 3). O mapa estático em
`turtlebot4_navigation/maps/warehouse.yaml`/`.pgm` (pacote do fabricante,
usado como referência/comparação) **não é o mundo que esta simulação
realmente usa**. O mundo de verdade é
`nav2_minimal_tb4_sim/worlds/warehouse.sdf` — mesmo nome "warehouse", mas
pacote diferente, com layout de obstáculos diferente. Confirmei lendo o
SDF como XML (24 `<include>` com `<pose>` explícita: `shelf_big_0..4`,
`shelf_0..7`, `pallet_box_0`, `barrier_0..3`, `chair_0..1`,
`fchair_0..1`, `table0`, 2 pessoas). A região x:[0,4], y:[0,4] (próxima
ao spawn) está livre de qualquer um desses 24 modelos — o obstáculo mais
próximo é `shelf_7` em (0.4,-2,0), 2m ao sul da zona usada.

**Ação sugerida:** se alguma análise futura (desta sessão ou de um
agente) precisar verificar colisão/clearance de uma rota nova, usar o
SDF do mundo real (`nav2_minimal_tb4_sim/worlds/warehouse.sdf`), não o
`.pgm`/`.yaml` do `turtlebot4_navigation` — são mundos de nome igual,
conteúdo diferente. Não tentei (nem consegui, sem GUI) validar
visualmente com `headless:=False`; a validação foi analítica (geometria
do SDF) + empírica (gravação real sem avisos de colisão/recovery nos
logs do Nav2).

### 2026-10-03 — Mecanismo exato da perda de nome no bridge + limitações reais de `dynamic_pose/info` como ground truth (pergunta 1 do pedido)

Contexto: a campanha de ground truth (3 rotas × N=10) já rodou de verdade e
o resultado (RMSE de `/odom` crescendo 0→5,18cm→14,27cm; `/pose` estável em
~2-3cm) já está publicado na dissertação (Seção 8.6) usando exatamente este
mecanismo (`dynamic_pose/info` → `ground_truth_filter`). A pergunta era se
existe alguma limitação de fidelidade/latência/frequência desse tópico
específico, vs. um plugin de ground truth dedicado, que mereça virar ameaça
à validade no texto.

- **Causa raiz exata (não só "não tem fix no changelog", mas o mecanismo
  linha a linha) de por que o bridge perde o nome da entidade.** Li o
  código-fonte real dos dois lados:
  - `gz-sim` (`SceneBroadcaster.cc`, função `PoseUpdate`, repo
    `gazebosim/gz-sim`, branch `gz-sim8`, lido via `WebFetch` direto no
    `raw.githubusercontent.com`): para cada entidade,
    `dyPose->set_name(_nameComp->Data()); dyPose->set_id(_entity);` — ou
    seja, **o nome da entidade está lá**, no campo `pose.name()` de cada
    item do `Pose_V`. O timestamp real da simulação
    (`_info.simTime`) é escrito uma vez só, no header do `Pose_V` como um
    todo (`dyPoseMsg->mutable_header()->mutable_stamp()`), não em cada
    Pose individual.
  - `ros_gz_bridge` (`ros_gz_bridge/src/convert/geometry_msgs.cpp`, função
    `convert_gz_to_ros` especializada pra `gz::msgs::Pose` →
    `geometry_msgs::msg::TransformStamped`, lida via `WebFetch`): essa
    função **não lê `pose.name()` em nenhum momento**. Em vez disso, só
    preenche `child_frame_id` procurando uma chave `"child_frame_id"`
    dentro de `gz_msg.header().data()` (pares chave-valor genéricos do
    header de cada Pose individual) — campo que o `SceneBroadcaster`
    **nunca preenche** pra `dynamic_pose/info` (confirmado no mesmo trecho
    de `PoseUpdate`: não há nenhuma linha setando header/data em cada
    Pose). O mesmo vale pro timestamp: essa função delega
    `convert_gz_to_ros(gz_msg.header(), ros_msg.header)` usando o header da
    Pose INDIVIDUAL (vazio), não o header do `Pose_V` (que tem o
    `simTime` real) — isso explica exatamente o "`header.stamp` sempre
    zerado" que o achado de 2026-10-02 já tinha constatado empiricamente
    (`gz topic -e`), agora com o porquê exato no código.
  - **Conclusão**: não é falta de dado na fonte (o Gazebo manda o nome e
    manda um timestamp real), é um descompasso entre dois códigos que
    olham pra campos diferentes do protobuf — o `ros_gz_bridge` foi
    escrito pensando em mensagens que carregam `child_frame_id`/timestamp
    DENTRO do header de cada Pose (padrão usado por outros publishers),
    não no padrão que o `SceneBroadcaster` usa pra `dynamic_pose/info`
    (nome no campo `name()`, timestamp só no header externo do array).
    Reforça a conclusão já registrada em 2026-10-02: não vai vir uma
    correção upstream genérica pra isso tão cedo, porque não é "bug" no
    sentido de dado faltando — é incompatibilidade de convenção entre dois
    subsistemas de projetos diferentes (`gz-sim` vs. `ros_gz`).
  - Fontes primárias (lidas via `WebFetch` no conteúdo real, não resumo de
    busca):
    `https://raw.githubusercontent.com/gazebosim/gz-sim/gz-sim8/src/systems/scene_broadcaster/SceneBroadcaster.cc`,
    `https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_bridge/src/convert/geometry_msgs.cpp`,
    `https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_bridge/src/convert/tf2_msgs.cpp`.

- **`dynamic_pose/info` é limitado por padrão a 60Hz, e isso É uma
  característica real do tópico, não um detalhe irrelevante.** Confirmado
  no mesmo `SceneBroadcaster.cc`: `public: int dyPoseHertz{60};`, lido do
  SDF via `_sdf->Get<int>("dynamic_pose_hertz", 60)` (configurável por
  mundo, mas com esse default). A publicação só ocorre se há subscriber
  (`HasConnections()`), o que não é problema aqui (o bridge/filtro deste
  projeto sempre está assinando). **Isso é uma amostragem discreta da
  trajetória real, não um ground truth contínuo** — equivalente, em
  espírito, a qualquer plugin de ground truth dedicado que também
  precisaria escolher uma taxa de publicação (a física roda bem mais
  rápido, tipicamente passo de 1ms = 1000Hz) — ou seja, 60Hz não é uma
  limitação exclusiva deste mecanismo específico vs. um plugin dedicado,
  qualquer publisher teria essa mesma escolha de trade-off taxa-vs-custo.
  **Discrepância não resolvida**: as taxas medidas ao vivo em 2026-10-02
  (~55-111Hz em `/ground_truth_pose_clean`, pós-filtro) excedem o default
  de 60Hz documentado no código-fonte. Não investiguei se o SDF do mundo
  deste projeto (`nav2_minimal_tb4_sim/warehouse.sdf`, pacote vendor fora
  deste repositório, não localizado nesta sessão) define um
  `dynamic_pose_hertz` mais alto explicitamente, ou se o filtro por índice
  fixo deste projeto reamostra/duplica mensagens de alguma forma — **não
  confirmado**, registro como lacuna aberta, não como achado.

- **Limitação real a registrar como ameaça à validade (resposta à
  pergunta 1): o timestamp de `/ground_truth_pose_clean` usado pela
  campanha não é o instante exato em que a física calculou aquela pose,
  é o instante em que o nó `ground_truth_filter` recebeu a mensagem.**
  Isso decorre diretamente do achado acima — o timestamp real
  (`simTime`) existe no Gazebo mas se perde na conversão genérica do
  bridge, e o `ground_truth_filter` deste projeto contorna isso
  corretamente (usa `self.get_clock().now()` com `use_sim_time`, não
  wall-clock de verdade — isso já estava certo), mas ainda assim introduz
  uma pequena defasagem de pipeline (bridge + filtro) entre "quando a
  pose foi calculada" e "quando foi timestampada". Pra RMSEs na faixa de
  2-14cm com um robô se movendo a velocidade de navegação típica do Nav2
  (dezenas de cm/s), essa defasagem (sub-período de 60Hz ⇒ <17ms, mais
  processamento de bridge/filtro, provavelmente poucos ms adicionais) é
  pequena mas não nula — na mesma ordem de grandeza de "ruído de
  medição" que poderia, em teoria, contribuir um pouco para o RMSE medido
  (mais em `/odom`, que é mais rápido e mais sensível a pequenos
  deslocamentos, que em `/pose`, que já é esparso por natureza).
  **Ação sugerida**: considerar mencionar essa defasagem de pipeline
  (bridge→filtro) como uma ameaça à validade de medição menor na Seção
  8.6/Limitações — não invalida o resultado (a defasagem é pequena e
  sistemática, não teria por que favorecer uma rota sobre outra), mas é
  uma fonte de imprecisão do "ground truth" que hoje o texto (pelo que foi
  reportado a este agente) provavelmente trata como perfeito/instantâneo.
  Não é uma correção do experimento, é um reforço de honestidade
  metodológica — decisão de incluir ou não é do autor.

### 2026-10-03 — Reavaliação do `WheelSlip` (pergunta 2): dissertação é só-simulação, recomendação mudou

O item pendente em `implementacao.md` (origem: achado de 2026-10-02) estava
formulado como pergunta aberta ("vale o esforço pra este experimento, ou
fica como limitação documentada?"). Reavaliando à luz do fato confirmado
pelo pedido desta rodada — a dissertação nesta versão é só-simulação, sem
comparação com robô real —: **a recomendação muda para "não vale o
esforço agora, melhor ficar só como limitação documentada"**.

Raciocínio (não é pesquisa nova de fonte, é análise do que já foi
levantado): o plugin `WheelSlip` exige valores de `slip_compliance_lateral`/
`slip_compliance_longitudinal` (adimensionais) pra funcionar. Sem um robô
real (ou pelo menos uma medição/estimativa publicada de slip do TurtleBot4
real em piso similar) pra calibrar esses valores, qualquer número usado
seria arbitrário — e simular slip arbitrário não torna a simulação mais
fiel à realidade, só troca "o simulador não modela slip" (limitação clara
e defensável) por "o simulador modela slip, mas com um valor inventado"
(limitação na prática pior, porque parece mais rigoroso do que é). Esse
tipo de mitigação só faz sentido quando há dado real para calibrar — ou
seja, ficaria genuinamente valioso se o projeto algum dia ganhar uma etapa
de comparação com hardware real (não é o caso hoje). Até lá, a limitação
documentada ("DiffDrive não modela slip de roda") já é a descrição mais
honesta disponível. `implementacao.md` atualizado para refletir essa
reavaliação (item não movido para "Feito" nem "Em andamento" — a decisão
final de reformular ou não o texto da dissertação continua sendo do
autor).

### 2026-10-03 — Ruído Gaussiano de LiDAR (pergunta 3): confirmado que continua não usado, e nunca foi usado nem no vendor upstream

Verifiquei diretamente nos arquivos do projeto (não só memória de
2026-10-02): `fleet_ws/src/fleet_orchestrator/urdf/tb4/sensors/rplidar.urdf.xacro`
e o macro `ray_sensor` que ele usa, em
`fleet_ws/src/fleet_orchestrator/urdf/tb4/icreate/common_properties.urdf.xacro`
— nenhum dos dois tem elemento `<noise>` ou parâmetro relacionado a ruído.
Confirmado lendo o conteúdo real dos dois arquivos nesta sessão.

- **Achado novo: isso não é uma lacuna introduzida por este projeto — o
  pacote vendor de onde ele faz fork também nunca teve ruído no LiDAR.**
  Comparei com o upstream oficial do Nav2
  (`ros-navigation/nav2_minimal_turtlebot_simulation`, confirmado como o
  repositório real via busca — página ROS index cita esse repo e mantainer
  Steve Macenski, versão 1.2.0/2026-04-28): tanto
  `nav2_minimal_tb4_description/urdf/sensors/rplidar.urdf.xacro` quanto o
  macro `ray_sensor` em `.../icreate/common_properties.urdf.xacro`
  (lidos via `WebFetch` em
  `https://raw.githubusercontent.com/ros-navigation/nav2_minimal_turtlebot_simulation/main/...`)
  também não têm nenhum elemento de ruído. Ou seja: o achado de
  2026-10-02 ("ruído gaussiano é nativo do SDF, só não documentamos que dá
  pra usar") continua válido como possibilidade técnica, mas a ausência de
  uso neste projeto é herdada do vendor, não uma omissão específica deste
  fork.
- **Achado lateral: o IMU do mesmo robô TEM blocos de ruído Gaussiano
  estruturalmente presentes, mas zerados (sem efeito).**
  `fleet_ws/src/fleet_orchestrator/urdf/tb4/icreate/sensors/imu.urdf.xacro`
  tem `<noise type="gaussian"><mean>0.0</mean><stddev>0.0</stddev></noise>`
  nos 6 eixos (velocidade angular x/y/z, aceleração linear x/y/z) — também
  herdado do vendor (o comentário no topo do arquivo diz que a única
  mudança deste fork foi o parâmetro de namespace, não os blocos de
  ruído). `stddev=0.0` significa, na prática, ruído nulo — equivalente
  funcionalmente a não ter noise nenhum, mas estruturalmente mais fácil de
  "ativar" (bastaria mudar um número) do que o caso do LiDAR (que
  precisaria do elemento inteiro adicionado). Não testei nenhum efeito ao
  vivo — achado é só leitura estática dos arquivos XML.
