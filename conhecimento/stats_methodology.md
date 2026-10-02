# Conhecimento acumulado: Metodologia estatística para N pequeno em robótica repetida

## TL;DR

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
