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

### Ação sugerida

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
