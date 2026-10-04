# Conhecimento acumulado: Bugs e configuração do SLAM Toolbox

## TL;DR

**Atualização 2026-10-03**: a dissertação encontrou que o erro do `/pose`
(SLAM Toolbox) fica baixo e praticamente constante (~2-3cm) entre uma
rota curta e um loop de 11,3m, enquanto o erro do `/odom` cresce até
14cm. Isso é real e bem analisado nos dados que existem, mas eu pesquisei
se dá pra confiar que isso continua valendo em rotas bem mais longas — a
resposta é: **não necessariamente, e isso vale a pena registrar como
limitação antes da defesa**. O motivo do resultado atual é real (o SLAM
Toolbox corrige a pose a cada poucos centímetros andados, não só quando
fecha um loop), mas isso foi testado numa escala pequena (máx. 11,3m,
mapa pequeno, sem corredores repetidos) e existem 3 mecanismos conhecidos
que poderiam fazer o erro voltar a crescer em mapas maiores ou rotas bem
mais longas: (1) a "janela" onde o SLAM procura a melhor correspondência
do laser é limitada — se o erro de odometria entre duas correções ficar
grande demais (rotas longas, mais chance de derrapagem de roda), a
correção pode falhar; (2) ambientes com estrutura repetida (tipo
corredores de armazém iguais um atrás do outro — que é o tipo de mundo
usado no projeto) podem confundir o SLAM; (3) a rota em loop fechado pode
estar se beneficiando de uma correção especial que só acontece quando o
robô volta pertinho de onde começou — isso não prova que o erro ficaria
baixo numa rota longa que NÃO fecha loop. Também reconfirmei que o bug de
lifecycle achado na rodada anterior (#884) continua sem nenhum release
novo que o inclua.

Pesquisamos as três perguntas originais (2026-10-02), direto no GitHub
oficial do SLAM Toolbox. Resumo em português simples:

1. **Buffer de TF do consumidor após restart**: o SLAM Toolbox já é um
   lifecycle node nativo (desde 2024) e reseta parte do próprio estado
   interno ao reativar, mas isso é o estado *dele*, não o buffer de TF
   de quem consome (o orquestrador do fleet-ui). Não existe config
   nativa que resolva isso do lado do consumidor — o reset manual do
   buffer que já fazemos (`_reset_robot_pose_tracking`) continua sendo
   o caminho certo, sem alternativa documentada.
2. **Timestamp "velho demais" depois do restart**: existe um parâmetro,
   `restamp_tf`, que parece feito exatamente pra esse tipo de problema
   (troca o timestamp do TF publicado pelo tempo atual em vez do
   timestamp do scan). Mas achamos um issue aberto e não resolvido de
   outro usuário mostrando que `restamp_tf: true` **não** garantiu a
   solução — então isso é uma hipótese a testar, não um substituto
   comprovado do reset manual de buffer que já usamos.
3. **Sinal de "pronto" sem esperar 8s fixos**: não existe um
   serviço/tópico oficial de "mapa->odom já está válido". Mas o nó
   publica `/pose` e eventos (`/slam_toolbox/new_node_event`,
   `/slam_toolbox/loop_closure_event`) que dão um sinal baseado em
   evento (esperar a primeira mensagem) em vez de um atraso fixo —
   ainda não testado nem implementado.
4. **Multi-robô na mesma máquina**: o SLAM Toolbox usa tópicos globais
   (`/scan`, `/map`) **por decisão de design**, não por bug — o
   mantenedor confirmou isso em 2023 e disse que não vai mudar. Pra
   multi-robô é preciso remapear os tópicos manualmente no launch.
   **Não achamos nenhuma issue ou relato confirmando conflito de
   performance/recursos** ao rodar várias instâncias na mesma máquina
   — essa pergunta específica continua sem resposta.
5. Achado lateral interessante: o próprio SLAM Toolbox teve, em agosto
   de 2026, um bug real de estado que não resetava direito numa
   transição de lifecycle (pausa que "trava" silenciosamente depois de
   reativar) — corrigido no código mas ainda não lançado em nenhum
   release. É o mesmo tipo de problema (estado preso após reativação)
   que já documentamos e corrigimos no nosso lado, só que dentro do
   próprio SLAM Toolbox.

Este arquivo é mantido pelo agente `experiment-slam-toolbox-tracking`
(`.claude/agents/experiment-slam-toolbox-tracking.md`) — cada execução lê
isto primeiro, pesquisa o que falta, e acrescenta achados novos abaixo,
sem apagar o que já existe.

**Atualização 2026-10-03** — resultado novo da dissertação (Cap. 08, Seção
8.6, campanha de ground truth N=10×3 rotas) mostra que o erro de `/pose`
(SLAM Toolbox) fica baixo e estatisticamente constante (~2-3cm) entre uma
rota de 0,9m e um loop de 11,3m, enquanto `/odom` cresce de ~0 a 14,27cm.
Pesquisei se essa conclusão ("scan matching zera o efeito de distância")
se sustenta pra rotas bem mais longas / mapas maiores. **Resposta curta:
não há garantia de que se sustente** — o mecanismo que explica o
resultado atual (correção contínua por scan-matching a cada novo nó, não
só no fechamento do loop) é real e documentado, mas tem no mínimo três
limites conhecidos (janela de busca da correlação, aliasing perceptual em
ambientes repetitivos, e o fato de o loop fechado se beneficiar de uma
correção de loop closure no fim) que não foram testados pelas 2 rotas
atuais (a maior tem só 11,3m). Isso é uma ameaça à validade real, não
hipotética — ver achado detalhado abaixo. Também reconfirmei que o bug de
lifecycle #884 (achado de 2026-08) **continua sem release** pra Jazzy.

## Achados

### 2026-10-02

- **Lifecycle node nativo existe desde 2024, mas não cobre o buffer do
  consumidor.** PR
  [#561 "Convert nodes to lifecycle nodes"](https://github.com/SteveMacenski/slam_toolbox/pull/561)
  (merged 2024-01-04, branch `ros2`) converteu os nós do SLAM Toolbox
  pra `LifecycleNode` de verdade, com reset de threads e do
  `loop_closure_assistant` em `on_activate`/`on_deactivate`. Confirmado
  lendo a mensagem de commit real via API do GitHub. Isso resolve o
  estado *interno* do SLAM Toolbox, não o `tf2_ros.Buffer` de quem
  consome a TF (nosso orquestrador) — não achei nenhum mecanismo nativo
  do lado do SLAM Toolbox que avise o consumidor "limpa seu buffer, eu
  reiniciei". Conclusão: nossa solução atual
  (`_reset_robot_pose_tracking` antes de reativar) não tem substituto
  documentado — é mesmo responsabilidade da aplicação consumidora.

- **Bug real recente e muito parecido com o nosso, mas dentro do SLAM
  Toolbox.** Issue
  [#884](https://github.com/SteveMacenski/slam_toolbox/issues/884)
  ("`PausedState state_` survives lifecycle transitions and desyncs
  from `paused_new_measurements`, leaving the node silently paused"),
  aberta 2026-08-13 e fechada 2026-08-17, reproduzida em ROS 2 Jazzy
  com o binário oficial `ros-jazzy-slam-toolbox` 2.8.5. Rodando como
  lifecycle node sob o `lifecycle_manager` do Nav2, o ciclo
  `deactivate → cleanup → configure → activate` deixava o nó
  "silenciosamente" preso descartando scans, mesmo o parâmetro
  reportando que não estava mais pausado. Corrigido pelas PRs
  [#885 (branch `jazzy`)](https://github.com/SteveMacenski/slam_toolbox/pull/885),
  #886 (branch principal) e #887 (branch `lyrical`), todas merged em
  2026-08-17. **Importante**: o release mais recente pra Jazzy
  (`2.8.5`, publicado 2026-04-29, confirmado via API de releases do
  GitHub) é de ANTES desse fix — ou seja, quem instala via apt ainda
  não tem essa correção. Não é o mesmo bug que documentamos (o nosso é
  no buffer de TF do consumidor, este é no `paused_new_measurements`
  interno do SLAM Toolbox), mas é evidência de que "estado que não
  reseta direito numa transição de lifecycle, travando silenciosamente
  depois de reativar" é um padrão de bug conhecido e recorrente no
  próprio projeto — reforça a plausibilidade da nossa hipótese, sem
  provar que o bug seja o mesmo.

- **Parâmetro `restamp_tf` existe pro problema de timestamp antigo, mas
  tem tensão com um relato de usuário que não conseguiu resolver com
  ele.** Confirmado no README oficial
  (`SteveMacenski/slam_toolbox`, branch `ros2`): `restamp_tf` — "Whether
  to restamp the TF messages with the current time or use the scan's
  message. Default False." Isso é exatamente o tipo de ajuste que
  poderia ajudar no cenário "buffer antigo rejeita dado novo com
  timestamp mais baixo do SLAM recém-reiniciado". **Mas** issue
  [#799](https://github.com/SteveMacenski/slam_toolbox/issues/799)
  ("Unable to map offline, timestamp earlier than all data in
  transform cache", aberta 2025-08-01, sem resolução até hoje) mostra
  um usuário que tentou `restamp_tf: true` e ainda assim bateu no mesmo
  tipo de erro. Issue
  [#717](https://github.com/SteveMacenski/slam_toolbox/issues/717)
  ("TF timestamp problem", também sem resolução) mostra histórico de
  que trocar pra usar `now()` em vez do timestamp do scan já causou
  problemas de localização em outro contexto. **Registro como achado
  em tensão com a decisão já tomada**: `restamp_tf` é candidato a
  testar no nosso setup, mas não é uma solução comprovada — não
  substitui o reset manual de buffer sem validação própria.

- **Não existe sinal oficial de "mapa→odom pronto", mas há tópicos de
  evento que podem substituir o atraso fixo de 8s.** Confirmado no
  README oficial: tópicos publicados incluem `pose`
  (`geometry_msgs/PoseWithCovarianceStamped`),
  `/slam_toolbox/new_node_event` (`slam_toolbox/NewNodeEvent`,
  disparado a cada nó novo no pose-graph) e
  `/slam_toolbox/loop_closure_event`. Não há serviço nem tópico
  documentado que sirva estritamente como "sinal de pronto" pra TF
  map→odom. **Ação sugerida** (não implementada por mim): trocar o
  `TimerAction` fixo de 8s por uma espera orientada a evento — assinar
  `/pose` (ou `/slam_toolbox/new_node_event`) com timeout e seguir no
  primeiro valor recebido, em vez de confiar num atraso fixo.

- **Tópicos globais em multi-robô são decisão de design confirmada pelo
  mantenedor, não bug.** Issue
  [#620 "Poor Topic Namespacing Practices"](https://github.com/SteveMacenski/slam_toolbox/issues/620)
  (aberta 2023-06-29, fechada no mesmo dia). O autor relatou que
  `/scan`, `/map`, `/map_metadata` usam caminho absoluto por padrão, o
  que colide entre robôs num setup multi-robô. Resposta do mantenedor
  (Steve Macenski), citação real confirmada via API: "They can still
  be just as easily remapped, but they're set in the global namespace
  so you can namespace slam toolbox without the main topics
  disconnecting. [...] Given this is how its been for ~5 years, I'm
  hesitant to changing it". Ou seja: **não vai mudar o default**, o
  caminho é remapear explicitamente `scan_topic` e os demais tópicos
  por robô no launch. Confirmado também no README atual: "`scan_topic`
  - scan topic, *absolute* path, i.e. `/scan` not `scan`" — documentado
  como comportamento intencional. Ação sugerida: conferir se o launch
  multi-robô do fleet-ui já remapeia esses tópicos explicitamente por
  namespace (não depender do push-down automático de namespace do
  ROS 2 pra esses tópicos específicos).

- **Não confirmado**: conflito de performance/recursos ao rodar várias
  instâncias de SLAM Toolbox (uma por robô, namespaced) na mesma
  máquina. Pesquisei via WebSearch e via busca de issues no GitHub
  oficial (`SteveMacenski/slam_toolbox`) e não encontrei nenhuma issue,
  PR ou relato que confirme ou documente esse tipo de problema
  especificamente. A issue mais próxima em tema,
  [#645 "Multi robot environment not working"](https://github.com/SteveMacenski/slam_toolbox/issues/645)
  (aberta 2023-11-08), foi fechada pelo mantenedor no mesmo dia só com
  "Please don't cross post with question sites" — sem conteúdo técnico,
  não serve como resposta. Pergunta permanece aberta pra próximas
  execuções.

- **Releases recentes confirmados via API do GitHub** (não inventados):
  `2.8.0` (2024-06-24, "Initial Jazzy release"), `2.8.1` (2024-06-25),
  `2.8.2` (2024-12-13), `2.8.3` (2025-04-15), `2.8.4` (2026-01-24),
  `2.8.5` (2026-04-29, release Jazzy mais recente até hoje), `2.9.0`
  (2025-05-29, primeiro release Kilted), `2.10.0` (2026-07-21, primeiro
  release do novo distro "Lyrical" — confirmei que a branch `lyrical`
  existe de fato no repositório, não é invenção). Não consegui ler o
  changelog detalhado de cada versão (página de release não carregou o
  texto completo na ferramenta de fetch) — fica pendente pra uma
  próxima execução conferir item a item se há algo relevante além do
  que já registrado aqui sobre `paused_new_measurements`.

### 2026-10-03

- **Reconfirmado: o bug de lifecycle #884 ainda não foi lançado em
  release pra Jazzy — sem mudança desde 2026-10-02.** Consultei a API de
  releases do GitHub (`api.github.com/repos/SteveMacenski/slam_toolbox/releases`)
  de novo: a lista de releases é a mesma de antes — `2.8.5` (2026-04-29)
  continua sendo o release Jazzy mais recente, e `2.10.0` (2026-07-21,
  branch `lyrical`) é o release mais recente de qualquer distro. As PRs
  #885/#886/#887 (fix do #884) foram merged em 2026-08-17, ou seja,
  DEPOIS do último release de qualquer distro relevante. Quem instala
  `ros-jazzy-slam-toolbox` via apt continua sem essa correção. Não achei
  nenhum release novo entre as duas execuções deste agente (2026-10-02 →
  2026-10-03) — a situação é estável, não "parada" por falta de atenção
  do mantenedor (o projeto segue ativo, só não empacotou um sync novo pra
  Jazzy ainda). Ação sugerida (reforça a de 2026-10-02): se o orquestrador
  usar `pause_new_measurements` em algum ponto do ciclo de vida, vale
  checar a versão instalada (`ros2 pkg xml slam_toolbox` ou
  `apt show ros-jazzy-slam-toolbox`) antes de assumir que esse bug está
  corrigido no ambiente do projeto.

- **Ameaça à validade: "scan matching zera o efeito de distância" não é
  garantido para rotas muito mais longas ou mapas muito maiores — é uma
  afirmação válida apenas dentro da escala testada (≤11,3m, mapa pequeno,
  ambiente com estrutura suficiente para scan matching).** Investiguei a
  pergunta usando a fonte primária mais forte disponível: o próprio paper
  do JOSS do SLAM Toolbox, já citado na dissertação como `macenski2021slam`
  (Macenski & Jambrecic, 2021, DOI
  [10.21105/joss.02783](https://doi.org/10.21105/joss.02783), lido na
  íntegra via PDF oficial). Achados relevantes, com texto exato do paper:

  1. **O problema "erro de localização cresce com a distância/escala" é
     real e conhecido na literatura de SLAM em geral** — o próprio paper
     cita isso como motivação pra existir: "GMapping is not well suited
     for large spaces and fails to accurately close loops at an
     industrial scale" e "[HectorSLAM] can cause inaccurate pose and map
     updates when lidar scans arrive at a lower rate, or when mapping
     large or featureless spaces". Ou seja, o próprio gênero de problema
     que a dissertação está testando (erro cresce com distância/
     complexidade) É o motivo histórico de existirem SLAMs melhores que
     odometria pura — não é uma hipótese exótica, é o problema central do
     campo. O SLAM Toolbox foi desenhado especificamente pra mitigar
     isso em escala (benchmark citado no paper: mapeamento em tempo real
     de até 24.000m²/250.000ft² "by non-expert technicians"), mas
     "mitigar em escala" é sobre viabilidade computacional
     (tempo real em CPU móvel), não uma garantia formal de que o erro de
     pose fica constante independente da distância — o paper não faz essa
     afirmação em nenhum lugar.
  2. **Mecanismo real por trás do resultado da dissertação**: o SLAM
     Toolbox corrige a pose continuamente por scan-matching a cada novo
     nó do pose-graph (controlado por `minimum_travel_distance`/
     `minimum_travel_heading`, confirmado no README oficial), não só no
     fechamento de um loop geométrico (`do_loop_closing`,
     `loop_search_maximum_distance`, `loop_match_minimum_chain_size` —
     também confirmados no README). Isso é consistente com o próprio dado
     da dissertação: a rota `rota_longa_curva` (7,66m, 1 curva, NÃO é um
     loop fechado) já teve erro baixo (2,25cm), parecido com a rota curta
     — se o mecanismo fosse só "fechamento de loop", essa rota não-loop
     deveria ter ficado mais parecida com o odom. Isso é uma evidência a
     favor da interpretação da dissertação, não contra.
  3. **Mas há 3 limites conhecidos que as 2 rotas atuais não testam,
     porque nenhuma passa de ~11,3m nem revisita o mesmo trecho duas
     vezes de ângulos diferentes**:
     - **Janela de busca da correlação limitada.** O README documenta
       `correlation_search_space_dimension` e
       `correlation_search_space_resolution` como os parâmetros que
       definem a região em torno da pose estimada (seed dado pela
       odometria) onde o scan matcher procura a melhor correlação —
       textualmente "Search grid size to do scan correlation over".
       **Não confirmei o valor numérico default diretamente no código/
       README** (só achei `0,3m` em fontes secundárias de terceiros, sem
       conseguir confirmar na fonte primária — registro como "não
       confirmado"), mas o mecanismo em si é confirmado: se o erro
       acumulado de odometria entre dois nós consecutivos (um incremento
       de `minimum_travel_distance`) ultrapassar essa janela, o
       scan-matcher pode não encontrar a correlação certa. Em rotas muito
       mais longas, com mais oportunidade de slip de roda acumulado
       (achado já documentado pelo agente `gazebo_tracking` sobre o
       plugin DiffDrive não modelar slip), esse risco cresce — não
       aparece nos 11,3m testados, mas pode aparecer em dezenas/centenas
       de metros.
     - **Aliasing perceptual em ambientes repetitivos.** É um risco
       genérico de SLAM (confirmado via busca geral, não específico do
       slam_toolbox): ambientes com estrutura repetida/simétrica (ex.:
       corredores de estante de armazém repetidos, que é exatamente o
       tipo de mundo usado no projeto, `warehouse.sdf`) podem fazer o
       scan matcher ou o loop closure convergir pra uma correlação errada
       que parece boa localmente. O mapa usado no experimento (x:[0,4],
       y:[0,4], validado como livre de obstáculos pelo autor) é pequeno
       e não tem essa repetição ainda — mas se o experimento crescer pra
       um mapa maior reaproveitando os corredores reais do warehouse
       (que têm estantes repetidas, confirmado pelo agente ao mapear o
       mundo pra desenhar as rotas, ver `implementacao.md`), esse risco
       deixa de ser hipotético.
     - **O loop fechado pode estar se beneficiando de uma correção de
       loop closure no final, não só de scan-matching contínuo.** A rota
       `loop_fechado` retorna pertíssimo do ponto inicial (confirmado:
       "última pose a 21cm do início"); isso é exatamente a condição que
       dispara `do_loop_closing` contra o nó inicial do grafo. Se parte
       do baixo erro reportado nessa rota vier de uma correção de loop
       closure que "estica" o resto do grafo pra se ajustar na volta
       (comportamento documentado em qualquer SLAM baseado em grafo,
       incluindo no próprio paper do JOSS, que descreve o solver Ceres
       fazendo exatamente isso), então o resultado desta rota específica
       não deveria ser generalizado pra rotas longas que NÃO fecham loop
       — só a `rota_longa_curva` (não-loop) testa esse caso, e só até
       7,66m.
     **Conclusão desta pesquisa**: a interpretação do Cap. 08 ("scan
     matching limita o erro independente da distância") é plausível e tem
     uma explicação mecanística real e verificável — não é uma afirmação
     inventada nem contraintuitiva. Mas ela foi testada numa escala muito
     pequena (máx. 11,3m, mapa pequeno e sem repetição estrutural) e os 3
     mecanismos acima são formas documentadas/plausíveis de ela parar de
     valer em escala maior. **Recomendo registrar isso explicitamente como
     ameaça à validade/trabalho futuro no Cap. 09**, não como uma
     correção do Cap. 08 (o resultado em si, nos dados que existem, está
     correto e bem analisado) — é uma questão de escopo de generalização,
     não de erro na análise feita.

### Ação sugerida (2026-10-03, não implementada)

1. Considerar adicionar ao Cap. 09 (Limitações/Trabalho futuro) uma nota
   explícita de que a constância do erro de `/pose` foi observada só até
   ~11,3m num mapa pequeno sem estrutura repetitiva, e que 3 mecanismos
   conhecidos (janela de busca da correlação, aliasing perceptual em
   ambientes repetitivos tipo corredores de armazém, e o efeito específico
   de loop closure na rota em loop) poderiam fazer a conclusão não se
   sustentar em rotas mais longas ou mapas maiores — com a citação do
   próprio `macenski2021slam` (já citado na dissertação) como evidência de
   que "erro cresce com escala" é um problema conhecido do campo, não
   específico desta implementação.
2. Se o autor quiser testar isso de verdade (não só documentar como
   limitação): rodar a campanha de ground truth numa rota bem mais longa
   (ex. >30-50m) e, separadamente, numa rota não-loop que passe duas vezes
   perto do mesmo trecho de corredores repetidos do `warehouse.sdf`, pra
   isolar se o erro realmente se mantém constante ou começa a crescer.
   Não fiz essa validação experimental — é só a pesquisa de literatura/
   documentação, não substitui o teste real.

### Ação sugerida (resumo, não implementada)

1. Não alterar o reset manual de buffer no orquestrador — não há
   alternativa nativa documentada do lado do SLAM Toolbox.
2. Testar `restamp_tf: true` isoladamente como experimento, sabendo que
   não é garantia (achado em tensão, ver acima) — não trocar a
   mitigação atual sem validar.
3. Avaliar substituir o `TimerAction` de 8s por uma espera orientada a
   evento na primeira mensagem de `/pose` (ou
   `/slam_toolbox/new_node_event`), com timeout de segurança.
4. Conferir se o launch multi-robô remapeia `scan_topic` (e `/map`,
   `/map_metadata` se aplicável) explicitamente por namespace — o
   default global é intencional e não vai mudar.
5. Verificar qual versão do SLAM Toolbox está instalada no ambiente do
   projeto; se for `<= 2.8.5` e o orquestrador usar
   `pause_new_measurements`, há um bug conhecido (#884) ainda sem
   release — considerar build from source do branch `jazzy` se isso
   afetar o experimento.
