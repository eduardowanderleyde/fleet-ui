# TODO de revisão — achados fora do escopo de um capítulo só

Cada entrada é de um agente `chapter-*` que encontrou um problema que não
podia corrigir dentro do próprio arquivo. Não apagar entradas de outros
capítulos; só remover quando o achado for resolvido (mover pra um commit
que resolve, com referência a ele).

## Resultados — 2026-09-25
- **Achado:** o capítulo (`08_resultados.tex`, seção "Integridade dos Bags
  de Sensores") afirma que a trajetória principal da campanha final
  (`dissertation_clean01_final_manual`, RMSE médio 3,35 cm / 10 réplicas —
  o número mais citado da dissertação inteira) foi extraída de `/odom`
  (odometria bruta), com `/pose` (SLAM Toolbox) apenas como dado auxiliar.
- **Por que está fora do escopo:** `orquestracion.md` já documenta (linhas
  ~384-391) que `fleet_ws/scripts/analyze_runs.py` tinha um bug real,
  corrigido no commit `7c546fe` (2026-09-22): o modo `auto` só reconhecia
  o tópico `amcl_pose` (que este projeto nunca usa, por rodar SLAM
  Toolbox em vez de AMCL) e caía direto pro fallback `/odom` — que deriva
  continuamente e infla o RMSE de forma artificial, sem isso ser
  repetibilidade real do robô. O próprio `orquestracion.md` alerta:
  *"Runs analisadas antes desta correção que caíram no fallback de
  `/odom` devem ser reconsideradas/re-analisadas antes de virarem número
  de dissertação, se a pose do SLAM tiver sido gravada."* A campanha
  `dissertation_clean01` não está documentada em `orquestracion.md` nem
  em nenhum commit rastreável, e os dados brutos (`fleet_ws/runs/...`) não
  existem na branch `dissertacao` — não dá pra confirmar se ela rodou
  antes/depois do fix nem re-analisar com `/pose` sem acesso a esses
  dados, que ficam em outra branch (provável: `mission-coordinate-large-scale`
  ou uma branch de experimentos).
- **Sugestão:** localizar os bags MCAP reais de `dissertation_clean01`
  (branch/máquina onde a campanha rodou), rodar
  `analyze_runs.py --trajectory-topic auto` (versão pós-fix) ou
  `--trajectory-topic slam_pose` explicitamente, e comparar o RMSE médio
  resultante com os 3,35 cm atuais. Se o número mudar, atualizar
  `08_resultados.tex`, `09_conclusao.tex` e `disserta-apresenta/` (deck +
  fala) juntos, já que os três citam o mesmo valor.

- **Resolução (2026-09-25):** os bags MCAP originais de `dissertation_clean01`
  não foram localizados nesta máquina (buscado em `fleet_ws/runs/`,
  `~/Documentos/ros2_ws` e em outras branches — só o arquivo de rota
  `dissertation_clean01.yaml` sobrevive, sem os bags). Como verificação
  independente, foi reconstruída uma campanha nova (1 baseline + 10
  réplicas, restart completo da simulação antes de cada uma, mesmos
  waypoints do arquivo de rota salvo) usando o `analyze_runs.py` já
  corrigido — confirmado que os 10 replays usaram `/pose` (SLAM) em 100%
  dos casos, não caíram no fallback `/odom`. A duração média resultante
  (17,55 s, desvio 0,36 s, via métrica de alta taxa `/odom`) bateu quase
  exatamente com os 17,51 s / 0,36 s citados no capítulo, indicando que é
  fisicamente a mesma rota. O RMSE médio dessa campanha nova ficou em
  6,79 cm (desvio 0,96 cm, mín 4,50 cm, máx 8,20 cm) — quase o dobro dos
  3,35 cm citados.
  Consultada, a autoria decidiu **manter 3,35 cm como está** — o valor se
  refere à gravação/bag inicial (baseline) daquela campanha específica, e
  o ambiente foi reiniciado depois dela para outros trabalhos (sessão de
  hoje incluiu retrabalho considerável no orquestrador multi-robô e no
  painel de simulação); a divergência é mais provavelmente explicada por
  essa diferença de estado do sistema entre as duas campanhas do que por
  contaminação de `/odom`. Fica registrado aqui como contexto e não como
  pendência: nenhuma alteração foi feita em `08_resultados.tex`,
  `09_conclusao.tex` ou `disserta-apresenta/`.

## Revisão geral (leitura de capítulos 04/06/07/08/09) — 2026-09-30

### 1. Contradição ainda não resolvida: /odom explícito vs. a seção que corrige o viés de /odom
- **Achado:** `07_avaliacao.tex` (Procedimento, passo 9) diz literalmente
  "usando `/odom` como fonte da trajetória", e `08_resultados.tex` (linha
  ~172, "Integridade dos Bags") confirma: "A trajetória principal da
  análise foi extraída de `/odom`; `/pose` ... foi preservado como dado
  auxiliar." Isso está a poucos parágrafos de distância da própria seção
  "Ameaças à Validade" que descreve, em detalhe, o bug de detecção
  automática que fazia a análise cair erroneamente em `/odom` quando
  deveria usar a pose do SLAM, e como ele foi corrigido.
- **Por que importa:** um leitor atento (ou um avaliador de banca) vai
  perguntar diretamente: "se vocês corrigiram esse bug, por que a
  campanha principal diz explicitamente que usou `/odom`?" Isso já estava
  registrado como resolvido no achado anterior deste arquivo (a autoria
  decidiu manter 3,35cm), mas o TEXTO em si ainda apresenta essa tensão
  sem nenhuma nota explicando por que o `/odom` explícito não é o mesmo
  problema que a seção de ameaças descreve. Vale pelo menos uma frase de
  transição conectando os dois pontos, mesmo mantendo o número como está.

### 2. Afirmação "2 robôs funcionam sem interferência" está desatualizada
- **Achado:** `09_conclusao.tex` (Limitações) afirma: "Um teste funcional
  preliminar... confirmou que dois robôs simultâneos (tb1+tb2) executam
  ciclos completos de gravação e reprodução sem interferência cruzada...
  três robôs simultâneos falharam de forma reproduzível." `08_resultados`
  (Trabalhos Futuros) repete isso como premissa para o trabalho futuro
  multi-robô.
- **Por que está desatualizado:** essa afirmação reflete o entendimento
  do projeto até ~22/09. Trabalho posterior (sessão de 25 a 30/09,
  `orquestracion.md`, seção "Missão Coordenada — opção B" e as que a
  sucedem) encontrou e reproduziu repetidamente o MESMO sintoma de "jump
  back in time" com **2 robôs simultâneos**, não só com 3 — inclusive
  numa medição formal de 5 tentativas com o fluxo mais seguro (1 robô com
  Nav2 ativo por vez, não os dois simultâneos como o texto descreve): taxa
  de sucesso de 70% (7/10), com falhas no 1º robô tanto quanto no 2º. Ou
  seja, a arquitetura inteira foi redesenhada essa semana (de "2 robôs
  Nav2 simultâneos" pra "1 robô Nav2 por vez, trocando") exatamente porque
  a premissa "2 robôs funcionam sem interferência" não se sustentou sob
  investigação mais a fundo.
- **Sugestão:** atualizar `09_conclusao.tex` (Limitações) e
  `08_resultados.tex` (Trabalhos Futuros) pra refletir o achado mais
  recente — não é "2 robôs ok, 3 não", é "mesmo 2 robôs simultâneos têm
  risco real de instabilidade, mitigado nesta semana por uma arquitetura
  de ativação sequencial, ainda com ~70% de taxa de sucesso medida, não
  100%". Isso é trabalho posterior à campanha quantitativa reportada e
  não afeta o RMSE de 3,35cm (que é single-robot), mas afeta diretamente o
  texto de Limitações e Trabalhos Futuros, que cita esse teste preliminar
  como já relativamente resolvido.

### 3. Descrição do "Painel de Simulação" não corresponde ao código atual
- **Achado:** `04_arquitetura.tex` (Seção "O Painel de Simulação") e
  `06_implementacao.tex` (Seção "Interface Web") descrevem o painel como:
  escolher mapa, modo (robô único/frota) e quais robôs incluir via
  checkboxes, com start/stop simples. Essa é a versão ANTERIOR ao
  redesenho desta semana.
- **Por que está desatualizado:** o componente atual (`SimulationPanel.jsx`,
  branch `mission-coordinate-large-scale`) é o painel "Missão Coordenada":
  um dropdown de formação (L/I/V/\barra), 2 robôs fixos, 1 botão, e por
  baixo uma arquitetura de ativação sequencial (`activate_robot`/
  `deactivate_robot`) que liga a navegação de 1 robô por vez — não o
  seletor de mapa/modo/robôs que o texto descreve.
- **Sugestão:** como esse componente evoluiu bastante depois da campanha
  quantitativa (e inclusive depois dos capítulos terem sido escritos),
  vale decidir: (a) atualizar a descrição pra bater com o painel atual, ou
  (b) deixar explícito que a descrição se refere a uma versão anterior do
  componente, já substituída. Hoje o texto descreve algo que não existe
  mais no repositório.
