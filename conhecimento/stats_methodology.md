# Conhecimento acumulado: Metodologia estatística para N pequeno em robótica repetida

## TL;DR

**Atualização (2026-10-03, terceira rodada — avaliação retrospectiva da
Seção 8.6 já publicada):**

- A campanha de 3 fontes (`/odom` vs. `/pose` vs. ground truth) já rodou e
  já está na dissertação (Cap. 08, Seção 8.6 "Fonte de Trajetória"). O item
  "bloqueante" da rodada anterior (escolher o enquadramento ANTES do
  piloto) está **fechado/obsoleto** — não dá mais pra decidir antes,
  decidiram na prática.
- **O que foi de fato usado é defensável, e não é nem Bland-Altman nem
  ANOVA/Friedman — é RMSE escalar por réplica + IC 95% t de Student (N=10),
  comparando cada fonte contra o ground truth separadamente.** Isso é, na
  prática, o padrão-ouro da área de robótica/SLAM (erro de trajetória tipo
  ATE/RMSE, o mesmo usado em benchmarks como TUM RGB-D e KITTI), não uma
  adaptação da estatística clínica (Bland-Altman). É também exatamente a
  mesma metodologia já usada e já justificada no Cap. 05 pra QA2 — ou seja,
  é uma análise nova mas com método **já validado no resto da
  dissertação**, não inventado especificamente pra essa seção.
  Além disso, essa análise seguiu à risca duas recomendações da rodada
  anterior deste agente: interpolar só o ground truth (a série densa) para
  os timestamps da fonte esparsa, e usar 1 RMSE por réplica (não pontos
  agrupados) — ambas reduzem riscos reais que tinham sido sinalizados antes
  do piloto.
- **Mas achei um problema real e concreto, de baixo esforço pra corrigir:**
  o texto afirma que `/pose` fica "estatisticamente equivalente" entre as
  3 rotas só porque os IC 95% se sobrepõem visualmente — isso não é um
  teste de equivalência de verdade (nenhum ANOVA/Kruskal-Wallis/teste de
  equivalência foi rodado em lugar nenhum da dissertação, confirmado por
  busca no texto). "IC se sobrepõem" é uma heurística estatisticamente
  **não confiável** pra concluir "sem diferença" — é um erro documentado
  na literatura (Gelman & Stern, 2006). **Recomendo trocar a palavra
  "estatisticamente equivalente" por uma frase mais honesta** (ex. "não
  indica diferença perceptível com os dados disponíveis") — é uma correção
  de texto, sem precisar rodar nada de novo, e dá pra fazer antes da
  defesa com baixo risco.

**Atualização (2026-10-02, segunda rodada — sincronização temporal pré-piloto):**

- **Taxa de `/odom` confirmada com fonte real do próprio projeto: 30Hz
  exato** (`odom_publish_frequency` no plugin DiffDrive, não é "típico
  30-50Hz" genérico). Taxa do `ground_truth_pose_clean` tem **números
  conflitantes dentro do próprio `orquestracion.md`** (~51-55Hz no bridge
  bruto vs. ~100Hz relatado no nó filtrado, que não deveria publicar mais
  rápido do que recebe) — precisa ser remedida ao vivo no piloto, não
  assumida.
- **Não existe um número mágico de "Hz mínimo seguro" na literatura pra
  interpolação linear de trajetória de robô móvel.** O que existe é um
  princípio geral (fora da robótica): interpolação linear sempre
  subestima distância percorrida e "corta curva", e o viés cresce com o
  tamanho do intervalo entre amostras E com a curvatura/mudança de direção
  no intervalo — não só com Hz isolado.
- **Isso é um problema real e específico pra este projeto:** as rotas
  planejadas têm curvas de 90-180° e um loop — justamente onde uma
  amostra de `/pose` a cada 0,5s pode "cortar a curva" ao interpolar,
  criando uma divergência vs. ground truth que é artefato de
  reamostragem, não erro real do SLAM. Isso ameaça diretamente a pergunta
  de pesquisa da campanha ("a divergência entre fontes cresce com a
  complexidade da rota?") — **achado em tensão direta com o objetivo da
  campanha**, ver achado 11 abaixo.
- **Recomendação (minha, não fato estabelecido): não reamostrar as 3
  fontes pra uma grade arbitrária comum.** Em vez disso, interpolar
  linearmente só o ground truth (a série densa, onde interpolar é mais
  seguro) para os timestamps nativos de cada fonte a avaliar (`/odom` a
  30Hz, `/pose` a ~2Hz) — concentra o erro de interpolação na série onde
  ele é menor, em vez de inventar posição que o `/pose` nunca mediu.
- **Isso NÃO muda a recomendação geral da primeira rodada (Bland-Altman
  por fonte vs. ground truth, não ANOVA/Friedman simétrico) — mas
  reforça com força total uma restrição que a primeira rodada não tinha
  detalhado:** não pode tratar cada ponto-tempo resampleado de cada
  réplica como uma observação independente pro Bland-Altman (isso infla
  artificialmente o N e estreita os limites de concordância — achado
  confirmado com fonte primária de Martin Bland). A unidade de análise
  defensável continua sendo 1 observação por réplica (N=10 por
  geometria), igual já é feito hoje pro RMSE em `analyze_runs.py`.

Primeira rodada de pesquisa (2026-10-02). Resumo em português simples:

- **IC com N=10 (t de Student): a escolha atual está certa.** Bootstrap só
  fica melhor que o t de Student a partir de uns 25+ amostras (e com
  milhares de reamostragens); abaixo disso o t de Student é a opção mais
  confiável. Não há argumento forte pra trocar com N=10.
- **Dá pra estimar N a priori usando o desvio-padrão já observado (1,10cm),
  mas não é "poder estatístico" clássico — é cálculo de precisão.** Existe
  método consagrado (fórmula $n=(z_{\alpha/2}\cdot s/E)^2$) pra decidir
  quantas réplicas são precisas pra um IC com largura-alvo, usando o
  desvio-padrão de uma campanha piloto. É diferente de calcular poder
  pra detectar uma diferença entre grupos — serve pro objetivo real do
  projeto (reportar um IC enxuto), não precisa inventar uma hipótese nula.
- **Comparar /odom vs. /pose vs. ground truth na mesma réplica pode não
  ser o problema de "ANOVA de medidas repetidas vs. Friedman" que a
  pergunta original supunha.** Como ground truth é referência (não é só
  "mais um grupo"), a pergunta real do projeto ("quanto cada fonte se
  desvia do ground truth, e isso cresce com a rota") se parece mais com
  um problema de *concordância entre métodos de medição* (estilo
  Bland-Altman: /odom vs. ground truth, /pose vs. ground truth,
  separadamente) do que com um teste simétrico de "as três fontes são
  diferentes entre si". ANOVA de medidas repetidas/Friedman ainda cabem
  se a pergunta for sobre variabilidade entre fontes, mas não substituem
  a análise de concordância contra a referência. **Isto está em tensão
  com a formulação original da pergunta — registrado como tal, não
  decidido aqui.**
- Confirmado que o padrão da robótica industrial adjacente (ISO 9283,
  repetibilidade de pose de manipulador) usa **N=30 ciclos** por
  configuração — bem mais que o N=10 do projeto, mas é outro domínio
  (posição estática do efetuador, não trajetória contínua de robô móvel).
  Útil como contraponto na discussão de limitação, não como alvo direto.
- Nenhuma referência nova encontrada dá um número mínimo de N
  específico pra "campanha de repetibilidade de trajetória de robô móvel"
  equivalente ao que o projeto já usa (amigoni2010/2014, bonsignorio2015,
  maset2022) — a literatura de robótica tende a discutir *que* a prática
  é fraca, não *quanto* seria suficiente.

## Achados

### 2026-10-02

1. **IC com N=10: t de Student é a escolha certa, bootstrap não ajuda
   neste tamanho de amostra.** Confirmado via discussão estatística geral
   (lista r-help, consenso de métodos): bootstrap tende a ter desempenho
   fraco abaixo de ~25 amostras, e intervalos BCa (os melhores da família
   bootstrap) só funcionam bem com N>25 e milhares de reamostragens. Para
   N=10, o t de Student é descrito como a opção mais confiável, desde que
   normalidade ou quase-normalidade seja razoável — o que já é assumido na
   Eq. `eq:ic_95` do Cap. 05 da dissertação. **Conclusão prática: não há
   base na literatura pra sugerir bootstrap como alternativa ao IC atual
   com N=10.** Fonte: discussão consolidada de métodos estatísticos sobre
   bootstrap vs. t (não é um único paper citável, é consenso de referência
   — registrado como tal, sem link único "primário").

2. **Existe método defensável pra estimar N a priori a partir do
   desvio-padrão já observado — mas é cálculo de precisão, não poder
   estatístico clássico.** Paper confirmado: Sorzano, C.O.S. et al.,
   "Sample Size for Pilot Studies and Precision-Driven Experiments",
   arXiv (submetido jul/2017, revisado mar/2018),
   https://arxiv.org/pdf/1707.00222. O paper nota que tamanhos de piloto
   de 5–20 "disregard any statistical consideration" e propõe fórmulas
   e tabelas de projeto pra decidir N visando uma precisão-alvo (largura
   de IC) ao estimar média, desvio-padrão, proporção, correlação ou tempo
   até evento. A fórmula clássica de tamanho amostral por precisão é
   $n = \lceil (z_{\alpha/2}\cdot s/E)^2 \rceil$, onde $s$ é o
   desvio-padrão do piloto e $E$ a margem de erro desejada no IC —
   confirmada de forma independente em material didático-padrão de
   estatística (não é exclusiva do Sorzano et al., é fórmula-livro-texto).
   **Aplicação ao projeto:** usando o desvio-padrão de RMSE de 1,10cm já
   observado como $s$-piloto, é possível calcular quantas réplicas por
   geometria de rota seriam necessárias pra um IC de 95% com largura-alvo
   escolhida (ex.: ±0,5cm) — isso é diferente de "poder pra detectar
   diferença entre /odom e ground truth", que exigiria antes definir um
   tamanho de efeito mínimo relevante (não definido ainda no projeto).
   **Ação sugerida:** ver seção abaixo.

3. **A pergunta "ANOVA de medidas repetidas vs. Friedman" pode estar mal
   enquadrada para o caso de 3 fontes de pose — concordância contra
   referência (Bland-Altman) é mais apropriada que teste de diferença
   simétrico.** Confirmado: Bland-Altman é descrito na literatura (PMC,
   revisões sobre o método) como a técnica padrão pra avaliar
   concordância entre dois métodos de medição aplicados aos mesmos
   sujeitos — compara diferença vs. média dos pares, calcula limites de
   concordância, e pergunta "podem ser usados de forma intercambiável",
   não "são estatisticamente diferentes". Extensões pra mais de dois
   métodos existem na literatura (ex. revisão citada por
   oalib-perpustakaan.upi.edu/doaj — abordagem de três passos pra
   acurácia/precisão/concordância), mas eu não confirmei uma extensão
   "canônica" de Bland-Altman pra 3 métodos simultâneos — **registrado
   como não totalmente confirmado nesse ponto específico.**
   **Por que isso importa pro plano de 30 réplicas:** a pergunta de
   pesquisa documentada em `orquestracion.md` ("até que ponto a fonte
   usada influencia a avaliação de repetibilidade, tomando o ground
   truth como referência") é uma pergunta de concordância-com-referência,
   não de simetria entre 3 grupos. Rodar /odom-vs-ground-truth e
   /pose-vs-ground-truth como dois pares (Bland-Altman ou equivalente)
   responde essa pergunta mais diretamente do que uma ANOVA de medidas
   repetidas de 3 níveis seguida de post-hoc. ANOVA/Friedman continuam
   relevantes se a pergunta secundária for "a variabilidade entre fontes
   é estatisticamente diferente de zero" — mas isso é um teste
   complementar, não o principal. **Isto está em tensão direta com a
   formulação original da pergunta motivadora deste agente (que supunha
   ANOVA/Friedman como candidatos principais) — registrado como tensão,
   decisão não tomada aqui.**

4. **Sphericity em ANOVA de medidas repetidas com 3 níveis e N=10: o
   teste de Mauchly tem pouco poder pra detectar violação nesse tamanho
   de amostra.** Confirmado via material-padrão de estatística
   (StatTrek, GraphPad): com exatamente 2 níveis a esfericidade é
   automaticamente satisfeita; com 3+ níveis (o caso de /odom, /pose,
   ground truth) é uma restrição real que precisa ser testada, mas o
   teste de Mauchly perde poder estatístico justamente nas amostras
   pequenas onde o problema mais importa — ou seja, com N=10 o teste pode
   não detectar uma violação real. **Implicação prática: se a ANOVA de
   medidas repetidas for usada mesmo assim (ponto 3 acima), convém aplicar
   correção de Greenhouse-Geisser por padrão em vez de confiar no
   resultado do teste de esfericidade, ou preferir Friedman direto.**

5. **Confirmado: ISO 9283 (repetibilidade de pose de robô manipulador)
   usa 30 ciclos por configuração de teste — não aplicável diretamente,
   mas referência útil de "convenção do campo".** Confirmado via múltiplas
   fontes concordantes (RoboDK, Hexagon, artigo técnico MDPI) que a norma
   especifica repetir a medição de pose 30 vezes por configuração (cubo
   ISO, 5 pontos de medição) para calcular repetibilidade como
   desvio-padrão das distâncias entre posições medidas e a posição média.
   É um domínio diferente do projeto (posição estática do efetuador de um
   braço industrial, não trajetória contínua de um robô móvel em
   navegação), então não é uma recomendação diretamente transferível para
   N de réplicas de trajetória — mas é um dado concreto pra citar na
   discussão de limitação do N=10: "mesmo no domínio adjacente mais
   maduro e padronizado da robótica (manipuladores industriais), a
   convenção aceita é 3x o N usado nesta dissertação."

6. **Dois papers recentes de robótica sobre repetibilidade/reprodutibilidade
   confirmados como reais, mas sem recomendação numérica de N — candidatos
   a citação adicional, não substitutos de amigoni/bonsignorio/maset.**
   (a) Norton, A.; Flynn, B., "Towards Using Multiple Iterated, Reproduced,
   and Replicated Experiments with Robots (MIRRER) for Evaluation and
   Benchmarking", ICRA 2024 Workshop on Ontologies and Standards for
   Robotics and Automation (WOSRA), NERVE Center/UMass Lowell,
   https://arxiv.org/abs/2408.04736 — framework conceitual pra unir
   avaliação de desempenho, benchmarking e experimentos
   reproduzidos/replicados; não contém (verificado no PDF completo, na
   medida em que o texto pôde ser extraído) recomendação numérica de N.
   (b) Weng, B.; Capito, L.; Castillo, G.A.; Khor, D., "Rethink Repeatable
   Measures of Robot Performance with Statistical Query", IEEE
   Transactions on Robotics, DOI 10.1109/TRO.2025.3645934 (preprint
   arXiv maio/2025, versão final out/2025),
   https://arxiv.org/html/2505.08216v3 — framework de "statistical query"
   pra garantir limites de acurácia/eficiência em testes repetidos;
   domínios cobertos: manipuladores, veículos autônomos, locomoção de
   humanoides — não trajetória de robô móvel com Nav2/SLAM. Nenhum dos
   dois dá um N mínimo específico pra campanha de repetibilidade de
   trajetória; registrados aqui como literatura adjacente, não como
   resposta à pergunta original.

7. **Não confirmado / descartado como pouco aplicável:** um guia comercial
   (claru.ai, "How to Evaluate Robot Policy Performance") dá números
   concretos de N (ex. "50 trials" pra estimar taxa de sucesso com ±14pp
   de IC 95%), mas é conteúdo de empresa (não revisado por pares) e trata
   de taxa de sucesso binária de políticas de manipulação (Bernoulli),
   não de RMSE contínuo de trajetória — paradigma estatístico diferente
   (IC de proporção, não IC de média). **Registrado como não aplicável a
   este projeto, não usar como referência.**

8. **Confirmado: livro-texto Wohlin et al., "Experimentation in Software
   Engineering", 2ª edição, Springer, 2012 — existe e é um texto padrão
   de metodologia experimental em Engenharia de Software, mas não
   consegui verificar o conteúdo específico de capítulo sobre análise de
   "small data sets"/testes não-paramétricos (Mann-Whitney, Wilcoxon) sem
   acesso ao texto completo (paywall/sem preview suficiente nas buscas
   realizadas). **Registrado como "não confirmado" o conteúdo específico
   — apenas a existência e edição do livro foram confirmadas.**

### 2026-10-02 (segunda rodada — sincronização temporal pré-piloto)

Contexto desta rodada: antes do piloto da campanha /odom vs /pose vs ground
truth, confirmar se a diferença enorme de taxa de publicação entre as 3
fontes (`/pose` do SLAM Toolbox pode ser tão lenta quanto ~2Hz) compromete a
reamostragem/interpolação usada hoje em `analyze_runs.py --resample-mode
time` e/ou muda a recomendação estatística da primeira rodada.

9. **Confirmado com fonte primária do próprio projeto: `/odom` publica a
   30Hz exatamente, não "30-50Hz típico de plugin".** Fonte:
   `fleet_ws/src/fleet_orchestrator/urdf/tb4/icreate/create3.urdf.xacro`,
   linha 137 — plugin `gz::sim::systems::DiffDrive` com
   `<odom_publish_frequency>30</odom_publish_frequency>` explícito. Isso é
   o URDF que o fork do projeto usa (comentário no topo do arquivo explica
   o motivo do fork: propagar namespace nos tópicos gz-transport). Resolve
   a lacuna "não confirmado o valor exato deste projeto" da pergunta
   motivadora desta execução.

10. **`minimum_time_interval: 0.5` do SLAM Toolbox confirmado de novo
    (`/opt/ros/jazzy/share/turtlebot4_navigation/config/slam.yaml`, linha
    27) — mas é só um dos 3 limiares, e a lógica de combinação deles
    (E/OU com `minimum_travel_distance: 0.1` e `minimum_travel_heading:
    0.1`, linhas 36-37) não foi confirmada nesta sessão.** Busquei a lógica
    exata (`shouldProcessScan` / equivalente) no código-fonte do
    slam_toolbox e em buscas web e não encontrei uma confirmação clara de
    como os 3 limiares se combinam (todos precisam ser satisfeitos? só o
    de tempo é obrigatório e os outros são "OR" complementares?).
    **Registrado como não confirmado.** Implicação prática: a taxa real de
    `/pose` durante o piloto pode ser MENOR que 2Hz se o robô andar devagar
    ou ficar parado em trechos do percurso (o parâmetro de tempo é só o
    teto de velocidade de publicação, não uma garantia de taxa mínima).
    **Ação sugerida:** medir `ros2 topic hz /pose` ao vivo durante o
    próprio piloto (réplica única, 3 fontes sobrepostas) em vez de assumir
    2Hz a priori — é rápido e remove a incerteza antes de desenhar a
    reamostragem da campanha de 30 réplicas.

11. **`/ground_truth_pose_clean`: números conflitantes já registrados no
    próprio `orquestracion.md` (seção "Plano: campanha...", item 1) são
    reais (não erro de digitação desta execução) e continuam sem
    resolução.** O texto do projeto registra o bridge bruto
    `/ground_truth_pose` confirmado a ~51-55Hz via `ros2 topic hz`, e
    separadamente registra `/ground_truth_pose_clean` (nó
    `ground_truth_filter.py`, lido nesta sessão) publicando a ~100Hz.
    Logicamente isso é estranho: `ground_truth_filter` só republica 1:1
    cada `TFMessage` recebido (sem buffer, sem upsampling, ver
    `_on_tf` em `ground_truth_filter.py`) — não deveria conseguir publicar
    mais rápido do que a taxa de entrada. Não investiguei a causa (pode
    ser medição em momentos/condições diferentes, ou um dos dois números
    estar errado). **Registrado como "achado em tensão interna, não
    resolvido" — ação sugerida: remedir as duas taxas simultaneamente
    (`ros2 topic hz /ground_truth_pose /ground_truth_pose_clean` ao mesmo
    tempo) no piloto antes de assumir qualquer um dos dois números pra
    desenhar a reamostragem.**

12. **Não existe (não encontrei) um número consagrado de "Hz mínimo
    seguro" na literatura para interpolação linear de trajetória de robô
    móvel sem viés — mas existe um princípio geral bem estabelecido fora
    da robótica que se aplica aqui.** Confirmado: Dekker, L. et al.,
    "Interpolating Location Data with Brownian Motion", arXiv (submetido
    jun/2022), https://arxiv.org/abs/2207.01618 — mostra que preencher um
    intervalo de dados de localização esparsos com uma linha reta "leva a
    erros sistemáticos como subestimação da distância percorrida", e
    propõe uma ponte Browniana como alternativa menos tendenciosa (não é
    paper de robótica — é de rastreamento de localização genérico tipo
    GPS, mas o mecanismo do viés é o mesmo problema geométrico). Fonte
    adjacente de processamento de sinais (domínio diferente, só ilustra o
    princípio geral de Nyquist/reconstrução, não dá número aplicável a
    robótica): Jaming, P.; Negreira, F.; Romero, J.L., "The Nyquist
    sampling rate for spiraling curves", arXiv (nov/2018),
    https://arxiv.org/abs/1811.01771 — é sobre amostragem de trajetórias
    espirais no k-space de MRI, não trajetória de robô; citado aqui só
    como evidência de que "taxa mínima de amostragem segura" depende da
    curvatura/conteúdo de frequência do sinal, não é uma constante
    universal — **não é uma fonte de robótica, não deve ser citada como
    se fosse.**
    **Conclusão prática (minha recomendação explícita, não fato da
    literatura):** o problema real não é "Hz" isolado, é "quanto o robô
    girou/andou entre duas amostras consecutivas de `/pose`, relativo à
    curvatura da rota nesse trecho". Como as 3 geometrias do plano
    (`orquestracion.md`) incluem curvas de 90-180° e um loop
    especificamente para testar se a divergência entre fontes cresce com
    a complexidade da rota, uma amostra de `/pose` a cada ~0,5s que cai
    "antes" e "depois" de uma curva rápida vai, ao ser interpolada
    linearmente, cortar a curva — produzindo uma divergência vs. ground
    truth que é artefato da reamostragem, não erro real de localização do
    SLAM. **Isto está em tensão direta com o objetivo da campanha** (medir
    se a divergência cresce com a complexidade da rota) — se não for
    tratado, o piloto pode "confirmar" que `/pose` diverge mais nas rotas
    com curva mesmo que o SLAM esteja igualmente preciso, só porque a
    reamostragem introduz mais erro exatamente nos trechos de curva.
    Registrado como tensão, não decidido aqui.

13. **Confirmado com fonte primária (página pessoal de Martin Bland) e com
    o paper original: pooled de múltiplos pontos não-independentes por
    réplica infla artificialmente a precisão aparente de um Bland-Altman.**
    (a) Fórmula confirmada — erro-padrão de um limite de concordância de
    95% ≈ $\sqrt{3s^2/n}$; Bland recomenda **n≈100** como "bom tamanho de
    amostra" (IC≈±0,34s), **n=12** dá um IC "grande" (≈±s), **n=200** é
    "ainda melhor" (≈±0,24s). Fonte: Bland, J.M., "How can I decide the
    sample size for a study of agreement between two methods of
    measurement?", https://www-users.york.ac.uk/~mb55/meas/sizemeth.
    (b) Confirmado que existe tratamento formal específico pro caso deste
    projeto (múltiplos pontos-tempo dentro da MESMA réplica/trajetória, não
    independentes entre si): Bland, J.M.; Altman, D.G., "Agreement between
    methods of measurement with multiple observations per individual",
    *Journal of Biopharmaceutical Statistics*, 17(4):571-82, 2007, PMID
    17613642 (PDF confirmado em
    https://www-users.york.ac.uk/~mb55/meas/bland2007.pdf) — o paper
    confirma que tratar observações repetidas/agrupadas por sujeito como
    independentes "produz limites de concordância incorretos e
    artificialmente estreitos", e recomenda decompor a variância em
    componente entre-sujeito e dentro-sujeito em vez de agrupar
    ingenuamente todos os pontos.
    **Aplicação direta ao projeto:** `analyze_runs.py` já calcula o RMSE
    como **um escalar por réplica** (não pontos pooled) — isso já está
    alinhado com a prática certa (ver `_rmse()`, que faz
    `sqrt(mean(...))` dentro de uma réplica, resultando numa linha por
    réplica na matriz `pairwise_rmse_m`). A recomendação abaixo é manter
    essa mesma lógica ao desenhar o Bland-Altman do piloto.

14. **Resposta à pergunta 2 (alinhamento: interpolação / nearest-neighbor
    com limite / outra abordagem) — a prática real na literatura/
    ferramentas de SLAM é mista, não um padrão único.** Confirmado: o
    benchmark clássico TUM RGB-D (Sturm et al., 2012 — ferramenta
    `associate.py`, documentada em
    https://cvg.cit.tum.de/data/datasets/rgbd-dataset/tools) usa
    **nearest-neighbor com limite máximo de diferença de tempo**
    (`--max_difference`, default 0.02s) e **descarta** os pares fora desse
    limite — não interpola. Busquei se a ferramenta `evo` (sucessora mais
    usada hoje, `MichaelGrupp/evo`) documenta explicitamente interpolação
    vs. nearest-neighbor e **não consegui confirmar o mecanismo exato**
    nesta sessão (a wiki do projeto no GitHub retornou erro de
    carregamento nas páginas relevantes) — registrado como não confirmado,
    não inventado.
    **Minha recomendação pro piloto (julgamento explícito deste agente,
    não fato estabelecido):** interpolar linearmente **só o ground truth**
    (a série mais densa, ~50-100Hz — ainda não confirmado qual exatamente,
    achado 11) para os timestamps **nativos** de cada fonte a avaliar
    (timestamps nativos do `/odom` a 30Hz; timestamps nativos do `/pose` a
    ~2Hz), em vez de reamostrar as 3 fontes pra uma grade arbitrária comum
    de N amostras (o que `--resample-mode time` faz hoje). Lógica
    explícita: o erro de interpolar uma série densa e suave (ground truth)
    pra um timestamp próximo é pequeno; o erro de interpolar a série mais
    pobre em informação (`/pose` a ~2Hz) pra uma grade arbitrária é onde o
    viés do achado 12 se concentra — evitar interpolar justamente a série
    mais vulnerável. Isso é uma mudança de abordagem em relação ao modo
    `time` atual do script, não uma crítica a ele — o modo atual foi feito
    pra comparar pares de MESMA taxa aproximada (baseline vs. replay, achado
    de contexto do agente), não pra esse caso de taxas muito diferentes.

15. **Resposta à pergunta 3 (isso muda a recomendação estatística
    anterior?) — não muda o enquadramento geral, mas adiciona uma restrição
    prática que a primeira rodada não tinha.** A recomendação de
    Bland-Altman por fonte vs. ground truth (achado 3 da primeira rodada)
    continua a mais defensável — nada nesta rodada contradiz isso. O que
    muda: com `/pose` a ~2Hz (taxa máxima, não garantida — achado 10) num
    percurso de ~10s, há só ~15-20 amostras nativas de `/pose` por réplica.
    Isso **não invalida** o Bland-Altman (mesmo n pequeno por réplica
    ainda dá N=10 réplicas válidas se cada réplica contar como 1
    observação — achado 13a), mas **reforça com força total** a
    recomendação do achado 13b especificamente pro caso de `/pose`: é
    tentador "aproveitar" os poucos pontos de `/pose` agrupando-os de
    todas as réplicas num único scatter Bland-Altman pra parecer que há
    mais dados — isso é exatamente o erro que Bland & Altman (2007)
    descrevem como produzindo limites de concordância artificialmente
    estreitos. Com `/pose`, a tentação é maior (poucos pontos por réplica
    tornam o pooling mais atraente visualmente) — por isso a regra "1
    observação por réplica" merece ser decidida e documentada
    explicitamente ANTES do piloto, não descoberta como problema depois de
    já ter rodado as 30 réplicas.

## Ação sugerida

(Nenhuma alteração de código feita por este agente — apenas registro de
pesquisa, conforme regra do papel.)

- **Antes do piloto da campanha de 30 réplicas** (`orquestracion.md`,
  seção "Plano: campanha /odom vs. /pose vs. ground truth"): considerar
  calcular N por geometria de rota usando a fórmula de precisão
  $n=(z_{\alpha/2}\cdot s/E)^2$ (achado 2), com $s$ = desvio-padrão de RMSE
  já observado (1,10cm) e um $E$ (largura de IC desejada) escolhido
  explicitamente e justificado no texto — mesmo que o resultado confirme
  N=10 como "suficiente", isso transforma a escolha de N de "prática" para
  "prática E verificada contra um critério de precisão", o que responde
  de forma mais forte à autocrítica já presente no Cap. 05.
- **Ao desenhar a análise do piloto de 3 fontes** (passo 2 do plano em
  `orquestracion.md`): considerar explicitamente se a pergunta é
  "concordância de /odom e /pose contra ground truth" (→ Bland-Altman ou
  equivalente, achado 3) ou "diferença estatística entre as 3 fontes" (→
  ANOVA de medidas repetidas com correção Greenhouse-Geisser ou Friedman,
  achados 3–4) — e documentar essa escolha explicitamente antes de rodar
  a campanha de 30 réplicas, não depois. Isto é uma sugestão de pesquisa,
  não uma decisão — quem decide é o autor do projeto.
- Manter N=10 como está para a campanha já reportada (não há achado aqui
  que invalide a escolha já feita nem a forma como o IC é relatado no
  Cap. 05); os achados acima se aplicam à campanha *futura* ainda não
  executada.

**Segunda rodada (2026-10-02, sincronização temporal — ver achados 9-15):**

- **Antes do piloto:** medir ao vivo `ros2 topic hz /pose` e, simultaneamente,
  `ros2 topic hz /ground_truth_pose /ground_truth_pose_clean` — as taxas
  usadas até agora (2Hz pro `/pose`, ~51-55Hz vs. ~100Hz conflitantes pro
  ground truth) não estão totalmente confirmadas (achados 10-11) e o
  desenho da reamostragem depende delas.
- **Antes do piloto:** decidir explicitamente a unidade de análise do
  Bland-Altman (1 observação por réplica, não pontos-tempo pooled de
  todas as réplicas — achados 13b e 15) e documentar essa decisão, não só
  tomá-la implicitamente ao escrever o código de análise.
- **Antes do piloto:** avaliar se `analyze_runs.py` precisa de um modo de
  reamostragem novo pro caso de 3 fontes com taxas muito diferentes —
  interpolar só o ground truth (série densa) pros timestamps nativos de
  cada fonte a avaliar, em vez de reamostrar as 3 pra uma grade arbitrária
  comum (achado 14). Isto é uma sugestão de desenho de análise, não uma
  implementação — quem decide e quem muda o código é o autor.
- **Risco concreto pro objetivo da campanha, sinalizado não resolvido**
  (achado 12): nas rotas com curva/loop, uma amostra de `/pose` a cada
  ~0,5s pode cortar a curva ao ser interpolada, inflando artificialmente a
  divergência `/pose` vs. ground truth justamente nos trechos de maior
  curvatura — podendo produzir uma falsa confirmação de que "a divergência
  cresce com a complexidade da rota" quando na verdade é um artefato de
  reamostragem. Recomendo decidir o tratamento disso (achado 14) antes de
  interpretar qualquer resultado do piloto sobre essa pergunta específica.

### 2026-10-02 — Campanha completa rodada (30 réplicas, 3 rotas): resultado real da pergunta de pesquisa, e um bug sério de alinhamento temporal corrigido no caminho

Não é achado de literatura — é o resultado real da campanha
/odom vs /pose vs ground truth (10 réplicas × 3 rotas, ver
`implementacao.md` e `run_ground_truth_campaign.py`), rodada pela primeira
vez nesta sessão, com a análise feita por `analyze_ground_truth_campaign.py`
(novo).

**Bug sério achado e corrigido antes de confiar em qualquer número:**
`_read_traj_xy` (`analyze_runs.py`) calculava o tempo de cada tópico
RELATIVO à primeira mensagem DAQUELE tópico (`t - t[0]`). Isso é correto
pra comparar a MESMA trajetória entre bags diferentes (uso original da
função), mas é **errado** pra comparar tópicos diferentes dentro do MESMO
bag quando eles não começam a publicar no mesmo instante absoluto —
`/pose` só começa a publicar ~8-10s depois do ground truth (SLAM Toolbox
tem um `TimerAction` de 8s no próprio launch, mais o tempo até o robô
andar os 10cm mínimos exigidos por `minimum_travel_distance`). Rebasear
cada fonte pro seu próprio t=0 antes de comparar produzia um RMSE de
`/pose` vs. ground truth de **~50-66cm** — um número grande, suspeito, e
sistematicamente ~constante entre rotas (não crescia com a complexidade),
o que por si só já era um sinal de artefato, não de erro real. Busca por
deslocamento temporal que minimiza o erro confirmou: deslocar `/pose` por
+7,5 a +10,5s (variável entre execuções, mas constante DENTRO de cada
execução — não é acúmulo de processamento, é desalinhamento de
referencial) derruba o RMSE pra 1-6cm. **Corrigido** adicionando um
parâmetro `rebase` a `_read_traj_xy` (default `True`, preserva o
comportamento original; `rebase=False` retorna tempo absoluto, usado
pelas comparações cross-tópico).

**Resultado real da campanha, com a correção aplicada (N=10 por rota, IC
95% via t de Student):**

| Rota | Comprimento | RMSE odom vs. GT | RMSE pose vs. GT |
|---|---|---|---|
| Curta (`dissertation_clean01`) | ~0,9m | 0,01cm (IC [0,01; 0,01]) | 3,28cm (IC [0,80; 5,75]) |
| Longa (`rota_longa_curva`) | ~7,7m, 1 curva 90° | 5,18cm (IC [4,93; 5,43]) | 2,25cm (IC [1,46; 3,03]) |
| Loop (`loop_fechado`) | ~11,3m, 4 curvas 90° | 14,27cm (IC [13,78; 14,76]) | 2,45cm (IC [1,83; 3,07]) |

**Interpretação:** o erro de `/odom` vs. ground truth cresce claramente
com o comprimento/complexidade da rota (deriva de odometria acumula com a
distância percorrida, como esperado fisicamente). O erro de `/pose`
(corrigido pelo SLAM) vs. ground truth fica baixo e **praticamente
constante** independente da rota — o SLAM Toolbox efetivamente limita o
erro de localização, enquanto a odometria crua não. Isso responde
diretamente à pergunta que motivou a campanha (ver
`orquestracion.md`): a fonte usada para representar a trajetória importa
cada vez mais conforme a rota fica mais longa/complexa — numa rota curta
a diferença é desprezível (ambas < 4cm), mas numa rota de ~11m com curvas
a diferença chega a ~12cm (14,27 vs. 2,45cm), o que pode mudar
qualitativamente a conclusão sobre repetibilidade dependendo de qual
fonte for usada.

**Ação sugerida:** este resultado parece maduro o suficiente pra entrar
na dissertação (Cap. 08, talvez como nova seção QA3, ou integrado à
Seção~\ref{sec:res_validacao_preliminar}) — decisão do autor, não tomada
aqui. Recomendo também considerar se a decisão metodológica já tomada
(RMSE pairwise entre execuções de mesmo mecanismo, citando maset2022)
deveria ser revisitada à luz deste resultado, já que agora há dados reais
mostrando que `/odom` sozinho pode estar superestimando a divergência
real em rotas longas.

### 2026-10-03 — Avaliação retrospectiva da Seção 8.6 já publicada: enquadramento é defensável, mas achei uma frase estatisticamente frágil

Contexto desta rodada: a campanha de 3 fontes (achado acima) já rodou e já
está na dissertação (`dissertacao/chapters/08_resultados.tex`, Seção 8.6
"Fonte de Trajetória: Odometria, SLAM e *Ground Truth*", label
`sec:res_fonte_trajetoria`). Esta rodada NÃO é mais uma decisão a tomar
antes do piloto — é checar se o que foi de fato escrito se sustenta frente
a uma banca.

**Nota de método desta rodada:** a branch `dissertacao` não está checked
out neste worktree (`mission-coordinate-large-scale`), e esta execução não
teve acesso a uma ferramenta de shell/git para trocar de branch ou rodar
`git show`. O texto da Seção 8.6, da Seção 2.3.1 do Cap. 05
(`eq:ic_95`) e uma varredura do Cap. 09 foram obtidos via
`raw.githubusercontent.com/eduardowanderleyde/fleet-ui/dissertacao/...`
(fetch HTTP do conteúdo real da branch no GitHub, repositório remoto
confirmado em `.git/config`) — é o conteúdo real do repositório remoto,
não uma reconstrução a partir de memória ou de PDFs antigos no disco (o
PDF local mais recente, `~/Downloads/dissertacao_overleaf_2026_10_01.pdf`,
é de antes da campanha ter rodado e NÃO contém a Seção 8.6 — não foi usado
como fonte dos achados abaixo).

17. **O enquadramento de fato usado é defensável — não é literalmente
    Bland-Altman nem ANOVA/Friedman (a tensão da primeira rodada, achado 3),
    é a métrica padrão-ouro de erro de trajetória em robótica/SLAM (RMSE
    escalar por réplica) aplicada separadamente a cada fonte contra o
    ground truth, com IC 95% t de Student (N=10) — a MESMA metodologia já
    justificada no Cap. 05 pra QA2.** Texto confirmado verbatim (Seção 8.6):
    "A Tabela~\ref{tab:fonte_trajetoria} ... resumem o RMSE médio de cada
    fonte contra o *ground truth*, com intervalo de confiança de 95\% (t de
    Student, $N=10$, mesma justificativa estatística de QA2)." A
    justificativa do Cap. 05 (Seção 2.3.1, `eq:ic_95`, confirmada verbatim)
    diz que $t$ é usado "por ser mais apropriada para amostras pequenas
    ($N<30$), onde a variância populacional é desconhecida" — é a mesma
    justificativa genérica já avaliada como correta na primeira rodada
    deste agente (achado 1), não uma justificativa nova específica pra
    Seção 8.6. **Isto não é Bland-Altman** (que reporta viés/bias médio +
    limites de concordância a partir da diferença pareada ponto-a-ponto) —
    é RMSE (que combina viés² + variância num único escalar), o que é a
    convenção padrão de avaliação de trajetória em robótica/SLAM (erro
    estilo ATE/RMSE, o mesmo paradigma de benchmarks consagrados como TUM
    RGB-D e KITTI — não confirmado nesta rodada se a Seção 8.6 cita
    explicitamente esses benchmarks, só que o *tipo* de métrica usada é o
    mesmo). **Conclusão: isto resolve, na prática, a tensão sinalizada no
    achado 3 da primeira rodada** — não porque o autor escolheu entre as
    duas opções que eu tinha levantado, mas porque usou uma terceira opção
    (a própria métrica já validada no resto da dissertação), que cumpre o
    mesmo objetivo metodológico (comparar cada fonte contra a referência,
    separadamente, não um teste simétrico de 3 grupos) com consistência
    interna ao texto. **Isto também confirma, com o texto real publicado,
    que as duas recomendações concretas da segunda rodada foram seguidas**:
    (a) interpolar só o ground truth (a série densa) para os timestamps da
    fonte esparsa a avaliar — texto confirmado: "o RMSE de cada fonte ...
    foi calculado interpolando o *ground truth* ... para os instantes de
    tempo exatos de cada amostra da fonte mais esparsa, em vez do inverso";
    (b) 1 observação (RMSE) por réplica, não pontos-tempo agrupados — a
    Tabela~\ref{tab:fonte_trajetoria} reporta N=10 por rota, consistente
    com o que já estava em `analyze_ground_truth_campaign.py`. Não achei
    nada nesta rodada que enfraqueça a validade dos números já registrados
    no achado anterior (RMSE 0,01/5,18/14,27cm pra `/odom`, 3,28/2,25/2,45cm
    pra `/pose`).

18. **Achado real e concreto: a frase "estatisticamente equivalente" no
    texto da Seção 8.6 não é sustentada por nenhum teste formal — só por
    sobreposição visual de IC 95%, uma heurística estatisticamente não
    confiável.** Texto confirmado verbatim: "o erro de `/pose` permanece
    baixo e estatisticamente equivalente entre as três rotas ($\approx$2–3
    cm, intervalos de confiança sobrepostos)". Os três IC realmente se
    sobrepõem par-a-par (Curta [0,80;5,75], Longa [1,46;3,03], Loop
    [1,83;3,07] — todos os pares têm interseção não-vazia), então a
    observação factual está correta, mas a palavra "estatisticamente
    equivalente" implica um teste de equivalência formal (ex. TOST) ou, no
    mínimo, um teste de diferença (ex. ANOVA one-way ou Kruskal-Wallis
    comparando as 3 rotas como grupos independentes — **não** ANOVA de
    medidas repetidas/Friedman, porque aqui rota é um fator
    *entre-grupos*: cada réplica pertence a uma única rota, não é a mesma
    réplica medida nas 3 rotas) — e nenhum desses testes foi rodado.
    Confirmado por busca no Cap. 09 (`09_conclusao.tex`, fetch do conteúdo
    real da branch): nenhuma menção a "Bland-Altman", "ANOVA", "Friedman"
    ou "equivalência estatística" em lugar nenhum do texto pesquisado — a
    afirmação de equivalência se apoia inteiramente na sobreposição visual
    dos IC. **"IC se sobrepõem" não é um teste de (não-)diferença
    confiável** — é um erro estatístico documentado na literatura:
    Gelman, A.; Stern, H., "The Difference Between 'Significant' and 'Not
    Significant' is not Itself Statistically Significant", *The American
    Statistician*, 60(4):328-331, 2006 (confirmado real via busca web;
    DOI/link exato não verificado nesta sessão, mas a citação bibliográfica
    — autores, título, periódico, volume, páginas, ano — está confirmada
    por múltiplas fontes concordantes na busca) — o paper mostra que
    sobreposição/não-sobreposição de IC não equivale de forma confiável a
    significância/não-significância de uma diferença, podendo errar nos
    dois sentidos.
    **Isto é urgente mas de baixíssimo risco/esforço pra corrigir antes da
    defesa, sem precisar rodar nenhum experimento de novo.**

    **Ação sugerida (mínima, recomendada antes da defesa):** trocar a
    frase "permanece baixo e estatisticamente equivalente entre as três
    rotas" por uma formulação que não implique teste formal — ex. "permanece
    baixo e não indica diferença perceptível entre as três rotas, com
    intervalos de confiança sobrepostos" ou "permanece baixo e dentro da
    mesma faixa de incerteza nas três rotas". É só uma mudança de texto em
    `dissertacao/chapters/08_resultados.tex` (branch `dissertacao`), não
    muda nenhum número da Tabela~\ref{tab:fonte_trajetoria} nem a
    interpretação central da seção (que `/odom` cresce com a rota e
    `/pose` fica baixo e estável).

    **Ação sugerida (opcional, mais trabalho, não necessária antes da
    defesa):** se o autor quiser sustentar a afirmação de equivalência com
    um teste de verdade, rodar um ANOVA one-way (ou Kruskal-Wallis, dado
    N=10 por grupo e possível não-normalidade de RMSE) comparando o RMSE de
    `/pose` vs. GT entre as 3 rotas como grupos independentes — **não**
    Friedman/ANOVA de medidas repetidas (rota aqui é entre-grupos, não
    dentro-do-sujeito, ao contrário do caso de 3 *fontes* na mesma réplica
    discutido nos achados 3-4 da primeira rodada, que continua sendo um
    cenário diferente). Isto é uma sugestão de análise adicional, não uma
    decisão — o autor pode preferir simplesmente suavizar o texto (opção
    acima) dado o prazo da defesa.

19. **Não achei nenhum outro problema estatístico na Seção 8.6 além do
    achado 18.** Especificamente verifiquei e não encontrei: (a) nenhuma
    alegação de causalidade além do que os dados sustentam; (b) nenhuma
    comparação pareada entre `/odom` e `/pose` que devesse ter sido testada
    formalmente e não foi (o texto compara cada um contra o ground truth
    separadamente e deixa a comparação `/odom` vs. `/pose` implícita na
    magnitude dos números, sem alegar significância estatística entre
    eles — isso é apropriado, a diferença de 14,27cm vs. 2,45cm na rota
    Loop, com IC que não se sobrepõem [13,78;14,76] vs. [1,83;3,07], é
    suficientemente grande pra não precisar de teste formal pra ser
    convincente); (c) nenhum problema de múltiplas comparações não
    endereçado que pareça grave (6 IC reportados — 2 fontes × 3 rotas —
    sem correção, mas a seção é explicitamente descritiva/exploratória,
    "fora do desenho formal QA1–QA4 ... sem hipótese de pesquisa nem
    critério de aceitação pré-registrado associado", texto confirmado
    verbatim — essa transparência já mitiga a crítica de "fishing", é uma
    prática editorial honesta que uma banca dificilmente vai penalizar).
    **Veredito geral: a Seção 8.6, como um todo, é estatisticamente
    defensável para N=10 por rota — o único ponto fraco real e concreto é
    a palavra "estatisticamente equivalente" do achado 18.**

## Ação sugerida (consolidado desta rodada, 2026-10-03)

- **Baixo esforço, recomendado antes da defesa:** trocar a frase
  "estatisticamente equivalente" na Seção 8.6
  (`dissertacao/chapters/08_resultados.tex`) por uma formulação que não
  implique teste formal de equivalência — ver texto sugerido no achado 18.
  Decisão e execução são do autor (ou de uma tarefa de implementação na
  branch `dissertacao`, fora do escopo deste agente que trabalha na branch
  de código).
- **Opcional, não bloqueante:** considerar rodar um ANOVA one-way/
  Kruskal-Wallis comparando RMSE de `/pose` entre as 3 rotas (grupos
  independentes) se o autor quiser sustentar a alegação de equivalência
  com um teste formal em vez de só suavizar o texto (achado 18).
- **Item "bloqueante" da rodada anterior em `implementacao.md`
  (decidir Bland-Altman vs. ANOVA antes do piloto) está obsoleto — o
  piloto e a campanha completa já rodaram usando uma terceira abordagem
  (RMSE + IC t-Student por fonte, já validada no resto da dissertação),
  que cumpre o mesmo objetivo metodológico. Fechado nesta rodada em
  `implementacao.md`, substituído por um item novo e mais específico (a
  correção de texto do achado 18).**
