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

## Campanha /odom vs. /pose vs. ground truth — 2026-09-30
- **Achado:** `09_conclusao.tex` (Trabalhos Futuros, curto prazo) já citava
  a comparação `/odom` vs. pose SLAM vs. *ground truth* do Gazebo como
  trabalho futuro. Nesta sessão essa comparação deixou de ser só uma
  frase de trabalho futuro: a infraestrutura de coleta do ground truth
  (bridge `/world/<world>/dynamic_pose/info` do Gazebo, sem plugin novo,
  + nó `ground_truth_filter` pra extrair a pose do robô por índice, já que
  o bridge não preserva nome de entidade) foi implementada e validada ao
  vivo (`mission-coordinate-large-scale`, ver `orquestracion.md` seção
  "Plano: campanha /odom vs. /pose vs. ground truth"). Adicionada uma
  frase em `09_conclusao.tex` registrando isso.
- **Por que está pendente, não resolvido:** só a infraestrutura de coleta
  existe. Faltam: réplicas pra modo multi-robô, as duas geometrias de rota
  novas (longa com curvas, loop fechado), o piloto obrigatório (1 replay,
  3 fontes sobrepostas, pra pegar erro de frame/timestamp antes de
  escalar), e só então a campanha completa (30 replays). Nenhum número
  novo existe ainda — não decidir se o RMSE de 3,35cm (achado 1 da seção
  "Revisão geral" acima) muda, fica como está, ou passa a ser apresentado
  ao lado dos outros dois, até essa campanha rodar.
- **Sugestão:** quando a campanha (ou ao menos o piloto) rodar, revisitar
  esta entrada e decidir se os capítulos 07/08 ganham uma seção nova de
  resultados ou só uma nota comparativa — e só então remover esta entrada.

## Metodologia (05_metodologia.tex) — 2026-09-30
- **Achado:** a Seção "Fase 1 — Gravação do Baseline" (`sec:record_replay`, linhas
  ~32-34) afirma: "o Nav2 para quando a pose está dentro da tolerância
  configurada (tipicamente 25\,cm em posição e 25\,cm em ângulo)". A unidade
  "cm" para a tolerância angular está incorreta/incompatível dimensionalmente
  --- ângulo não se mede em centímetros.
- **Por que está fora do escopo:** não é falta de citação, é um erro técnico de
  conteúdo (unidade errada), e corrigir o valor é decisão de conteúdo, não de
  bibliografia. Além disso, `07_avaliacao.tex` (linha ~192) já descreve a
  mesma tolerância do Nav2 corretamente, com unidades consistentes: "o
  critério de chegada do Nav2 (\texttt{general\_\allowbreak goal\_\allowbreak checker})
  aceita até 0,25\,m de erro de posição e 0,25\,rad (aproximadamente 14°) de
  erro angular" --- ou seja, o valor numérico (0,25) está certo, mas a unidade
  em `05_metodologia.tex` deveria ser "rad" (ou "~14°"), não "cm".
- **Sugestão:** trocar "25\,cm em ângulo" por "0,25\,rad (aproximadamente 14°)
  em ângulo" em `05_metodologia.tex`, alinhando com a descrição já correta de
  `07_avaliacao.tex`. Não alterei a frase porque mudar o valor/unidade é
  fora do escopo deste agente (que só adiciona citação, não corrige
  conteúdo técnico).

## Metodologia (05_metodologia.tex) — 2026-10-01
- **Achado:** `01_introducao.tex` (Objetivos, item 5, linha ~161) promete
  "Validar o framework em dois cenários de simulação". Porém a Seção "Design
  dos Experimentos de Validação" de `05_metodologia.tex` (título no plural,
  `sec:design_experimentos`) descreve apenas **um** cenário/campanha
  (\texttt{dissertation\_clean01}), e `07_avaliacao.tex` (linha ~210, Validade
  de conclusão) é explícito: a campanha reportada está "restrit[a] a um único
  cenário, uma única rota curta, um único robô simulado e uma única
  configuração de Nav2".
- **Por que está fora do escopo:** é uma contradição entre o objetivo
  declarado no Capítulo 1 e o que os Capítulos 5/7 efetivamente descrevem e
  reportam — decisão de conteúdo (o que foi ou não executado/prometido), não
  de redação. Não é o mesmo achado já registrado abaixo sobre a unidade
  "25\,cm em ângulo" (esse é um erro de unidade; este é uma divergência de
  escopo entre capítulos). Não tenho visibilidade se um segundo cenário foi
  planejado e descartado, rodou em outra branch, ou se o objetivo do
  Capítulo 1 está simplesmente desatualizado.
- **Sugestão:** decidir entre (a) atualizar `01_introducao.tex` para refletir
  que a validação quantitativa final cobriu um único cenário controlado
  (mencionando as campanhas exploratórias/\texttt{dissertacao\_teste1} como
  complementares, não como o "segundo cenário"), ou (b) se um segundo
  cenário de fato foi executado em algum momento, localizá-lo e incorporá-lo
  a `05_metodologia.tex`/`08_resultados.tex`. Vale também revisar o título da
  Seção "Design dos Experimentos de Validação" (plural) à luz da decisão.

## Implementação (06_implementacao.tex) — 2026-10-01
- **Achado:** a Seção "Ambiente de Simulação" de `06_implementacao.tex`
  (linhas ~51-62) afirma que "uma campanha completa com dois robôs
  simultâneos gravou uma rota real no `tb1` ... enquanto o `tb2` navegava
  para outro alvo ao mesmo tempo, sem interferência mútua entre os dois", e
  que o "teto prático de escala... revelou-se ser de CPU": o relógio
  simulado só "salta para trás" ao subir **três** robôs simultâneos, com
  `tb1`+`tb2` (dois robôs) descrito como "o alvo suportado e validado por
  padrão".
- **Por que está fora do escopo:** é a mesma classe de achado já registrada
  no item "2. Afirmação '2 robôs funcionam sem interferência' está
  desatualizada" da entrada "Revisão geral (leitura de capítulos
  04/06/07/08/09) — 2026-09-30" deste arquivo, mas aquela entrada cita
  apenas `09_conclusao.tex` e `08_resultados.tex` como os textos afetados —
  não lista esta passagem de `06_implementacao.tex`, que faz a mesma
  afirmação (dois robôs sem interferência mútua) de forma ainda mais
  específica e tecnicamente factual, atribuindo o "jump back in time" só a
  três robôs. Trabalho posterior (sessão de 25–30/09, `orquestracion.md`,
  seção "Missão Coordenada") reproduziu o mesmo sintoma de salto do
  `/clock` **com dois robôs**, não só com três, levando ao redesenho para
  ativação sequencial (~70% de taxa de sucesso medida). Corrigir isso é
  decisão de conteúdo/dados experimentais, não de citação bibliográfica —
  fora do meu escopo como agente de referências.
- **Sugestão:** ao atualizar `09_conclusao.tex`/`08_resultados.tex` conforme
  a sugestão já registrada no item 2 de "Revisão geral — 2026-09-30",
  revisar também esta passagem de `06_implementacao.tex` (Seção "Ambiente de
  Simulação"), já que ela faz a mesma promessa de estabilidade com dois
  robôs e atribui o limite de escala exclusivamente a três robôs — o que o
  trabalho mais recente não confirma.

## Trabalhos Relacionados (03_trabalhos_relacionados.tex) — 2026-09-30
- **Achado:** a Seção "A Taxonomia do SLAM" (`sec:rel_slam`) afirma, logo
  após citar `\citeonline{durrantwhyte2006}` e `\citeonline{bailey2006}`,
  que "a estrutura, resultado de convergência e nomenclatura" do problema
  SLAM "haviam sido propostos originalmente por Durrant-Whyte, Rye e Nebot
  em 1996" — uma atribuição histórica específica (autores + ano) sem
  nenhuma citação própria.
- **Por que está fora do escopo:** não é falta de citação que eu possa
  simplesmente promover — é uma afirmação factual específica (quem
  propôs o quê, em que ano) que eu não consegui confirmar contra fonte
  primária depois de buscar na web. Os resultados mais próximos desses
  mesmos autores (Durrant-Whyte, Nebot) no período são de 1997, com outros
  coautores e outro título ("Ultra-High Integrity Navigation Systems for
  Large Autonomous Vehicles", ISRR'97), não exatamente o que o capítulo
  descreve. Corrigir ou remover essa atribuição é decisão de conteúdo, não
  de bibliografia — por isso não toquei na frase (ver regra: "sem
  referência adequada... é melhor não citar do que citar errado").
  Registrado também em `referencias_candidatas.md` (Parte 4, item "não
  confirmado") para rastreabilidade.
- **Sugestão:** o autor (ou quem escreveu a frase originalmente) deveria
  verificar essa atribuição direto na seção de referências históricas de
  `durrantwhyte2006`/`bailey2006` — é provável que a frase tenha sido
  parafraseada de lá, e a citação correta pode já estar nas referências
  desses dois tutoriais. Se a atribuição de 1996 não se confirmar, trocar
  por uma formulação mais genérica (ex. atribuir a `\citeonline{durrantwhyte2006}`
  mesmo, que já está citado na frase anterior) ou remover o ano/autoria
  específicos.
