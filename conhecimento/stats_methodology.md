# Conhecimento acumulado: Metodologia estatística para N pequeno em robótica repetida

## TL;DR

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
