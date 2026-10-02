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
