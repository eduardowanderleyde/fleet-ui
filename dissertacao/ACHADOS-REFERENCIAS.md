# Achados da conferência de referências (16/11/2026)

Dez agentes conferiram a dissertação depois dos cortes P1 e P2. Nove eram de capítulo e conferiram se cada afirmação tem citação e se a citação sustenta a frase; os dos capítulos 6, 7 e 8 também compararam o texto com o código e os números com os dados. O décimo conferiu as 66 entradas do `.bib`. Cada agente de capítulo só podia acrescentar citação com chave que já está no `.bib`. Nenhum tirou citação nem mudou número ou texto. A compilação continua sem erro, com 110 páginas.

Muitos artigos (IEEE, Elsevier, MDPI, Springer) bloquearam a leitura automática. Nesses casos o agente conferiu pelo resumo e pelos metadados, e o achado está marcado como "precisa conferir no PDF".

## Conferido à mão pelo Claude

- **Cap. 4, l.222 (QoS): erro.** A combinação que falha é a contrária: publisher `BEST_EFFORT` (o Gazebo) com subscriber `RELIABLE`. Além disso, o ROS 2 atual emite aviso de QoS incompatível, então "nenhum erro é reportado" não vale mais.
- **Painel "Missão Coordenada" (caps. 4 e 6): código de outra branch.** Formações L/I/V e `activate_robot`/`deactivate_robot` não existem no código da branch `dissertacao`. Estão em `origin/mission-coordinate-large-scale`.
- **Cap. 9, l.284 ("mais de 1.700 linhas"): o número não confere.** O backend todo tem 1269 linhas nesta branch.
- **70% (cap. 9) × "três de dez" (cap. 7): não há contradição.** Sete sucessos em dez são três falhas em dez. Só a palavra muda ("ativações" × "tentativas").
- **`neves2026ble`:** é o artigo da Fernanda e da Beatriz no CBSoft 2026. Não está indexado, por isso o agente não o achou.


---

# Relatório: 01

# 01_introducao.tex — pesquisa de citações

Obs.: nenhuma das chaves já citadas tem PDF/nota em referencias_pdfs/; as páginas das editoras (Elsevier/IEEE) redirecionam e não foram lidas. Avaliações abaixo vêm do título/escopo conhecido de cada obra e precisam de conferência do autor contra o texto.

## Citações adicionadas (chave existente)
- koenig2004gazebo: "simuladores de alta fidelidade" (Contexto).
- omgdds2015: políticas de QoS determinam entrega/descarte de dados (Problema Central).
- verma2021: tendência de frotas de agentes coordenados (Seção Frota), junto de macenski2022ros2.
- sturm2012, zhang2018trajectory: RMSE/ATE como métricas clássicas (Escopo), junto de amigoni2010.
- runeson2009, wohlin2012: estudo exploratório de engenharia de software experimental (fim de PP).
- toris2015: ROSBridge (Contribuições de Engenharia).
Não adicionadas (nada adequado no .bib): lifecycle ROS 2 além de macenski2022ros2, TurtleBot4/RPLIDAR, executor multithreaded/deadlock, buffers TF por robô, patch de YAML do Nav2 (são descrições da própria implementação; ok sem citação); papéis MUUT/FUUT (conceito de outra fonte/protocolo do grupo - ver Problemas).

## Citação que não sustenta a frase
- albonico2023 (l.93 e l.99-100): é mapeamento sistemático de pesquisa de engenharia de software sobre ROS; não caracteriza "conhecimento tácito não documentado" em experimentos. Provável desajuste (confirmar).
- macenski2020marathon (l.83): descreve arquitetura do Nav2; não sustenta "chamada prematura ao servidor de ações resulta em timeout sem mensagem de erro clara" (observação prática do autor).
- macenski2021slam (l.85-86): artigo JOSS apresenta a ferramenta; não afirma que são necessários scans suficientes/intervalo varia com ambiente.
- macenski2022ros2 (l.118): artigo de arquitetura do ROS 2; sustentar "tendência de robótica de serviço/logística em frotas" é fraco (por isso adicionado verma2021).
- amigoni2010 (l.36, 153, 259): trata de metodologia experimental e simulação; não é fonte de "métricas RMSE clássicas" nem de "estudo exploratório de ES experimental" (mitigado com novas chaves). Para a definição de reprodutibilidade ("mesmo artefato: código, dados, protocolo") a fonte mais direta é acm2020badging, já citado antes.
- bonsignorio2015 (l.64): editorial; sustenta falta de reprodutibilidade/benchmarks, mas "obstáculo para transferência de tecnologia industrial" precisa ser conferido no texto.
- amigoni2014 (l.24): sustenta metodologia informal; "quase nunca transferíveis" é ênfase do autor.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
Nenhum candidato verificado (páginas de editoras não abriram). Lacunas sem chave: (a) tendência de frotas em robótica de serviço/logística (ideal: survey de multi-robô em logística, ex.: sobre AMR/warehouse); (b) comportamento de timeout do action server do Nav2 e do SLAM Toolbox (melhor: documentação oficial Nav2/slam_toolbox); (c) TurtleBot4 e RPLIDAR (documentação do fabricante); (d) Gazebo Harmonic (koenig2004gazebo é o Gazebo clássico).

## Problemas de conteúdo
- l.4-6 epígrafe "adaptado de Max Planck": a frase ("avança um funeral de cada vez") é paráfrase de Planck, mas o complemento sobre práticas experimentais é invenção; atribuição "adaptado" é frágil.
- l.28-29: "há mais de uma década" com bonsignorio2015 (2015) — hoje são ~11 anos, ok; manter.
- l.95-96: "A literatura já citada" remete a amigoni2014/bonsignorio2015/albonico2023; a caracterização de albonico2023 provavelmente não procede (ver acima).
- Origem do conceito MUUT/FUUT/SU não é citada na introdução (l.119-122); se vier de norma/artigo (ex.: neves2026ble?), citar.

---

# Relatório: 02

# Pesquisa 02_fundamentacao.tex

## Citações adicionadas (chave existente)
(15 \cite novos/ampliados; nenhum removido)
- Dead reckoning/odometria de roda: siegwart2011
- Causas do erro de odometria: + borenstein1996 (Borenstein & Feng tratam erros sistemáticos/não sistemáticos)
- ROS 2 sobre DDS: + macenski2022ros2; QoS: + omgdds2015
- Planners NavFn/Theta*: macenski2020marathon; BT navigator: + macenski2020marathon
- MPPI "paralelizável em GPU": williams2016
- Actions ROS 2 (protocolo assíncrono): macenski2022ros2
- AMCL "padrão do Nav2": macenski2020marathon; "filtro de partículas": thrun2005
- SLAM Toolbox itens 1, 2 e 3: macenski2021slam
- Grade de tempo comum: + zhang2018trajectory (moderada confiança; só Zhang trata de associação temporal)
- Definição de RMSE: sturm2012, maset2022 (RMSE como métrica de trajetória; maset2022 usa RMSE em repetibilidade)

## Citação que não sustenta a frase
- bailey2006 (§2.6): "abordagens baseadas em grafos superam filtros de partículas em ambientes de médio a grande porte". Bailey & Durrant-Whyte Parte II é survey de 2006 (complexidade, associação de dados, representação); não demonstra superioridade de grafos. Também tensiona com §2.5, que diz (via hamer2025) que o custo depende mais da implementação do que da família.
- amigoni2010 (§2.8.1): trata de metodologia experimental e simulação, não de normalização para grade de tempo comum. (Acrescentei zhang2018trajectory ao lado.)
- siegwart2011 (§2.1.1): "5–10% do percurso" não é figura que eu confirme em Siegwart; sem fonte para o número. 5 m -> 50 cm é só aritmética de 10%. Verificar página ou usar outra fonte.
- siegwart2011 (§2.7, IMU): "variância da aceleração indica instabilidade (superfícies irregulares...)" é critério do autor, não do livro.
- macenski2022ros2 (§2.3.1): "incompatibilidade de QoS é silenciosa, nenhum erro reportado" não consta no artigo; além disso, em ROS 2 recentes (Jazzy) rclcpp/rmw emitem warning e evento de QoS incompatível. Frase factualmente duvidosa.
- quigley2009 (§2.3): suporta só ROS 1; "desenvolvida desde 2014 para corrigir limitações do ROS 1" não vem dele (agora também cita macenski2022ros2 no trecho DDS, mas não nesta frase).
- koenig2004gazebo (§2.7): é o artigo do Gazebo clássico; não suporta Gazebo Harmonic, plugin DiffDrive nem ros_gz bridge (citação genérica, aceitável se assim entendida).
- kalman1960 (§2.5): é filtro de Kalman; a leitura "recursão bayesiana" vem de thrun2005 (adicionado ao trecho do filtro de partículas, não nessa frase).
- hamer2025 (§2.5): confirmei no resumo da página do JBCS que Cartographer teve piores resultados em energia e CPU e Karto foi o mais eficiente. NÃO confirmei "cerca de 43% num Raspberry Pi 4" nem "ambos baseados em grafos" (resumo não cita). Conferir no PDF.
- macenski2023survey: conteúdo é o artigo Regulated Pure Pursuit (correto para RPP); só o nome da chave é enganoso.
- farinelli2004 e gerkey2004: OK (farinelli: strongly/weakly centralized e decentralized confirmado no PDF local).

## Afirmação sem referência e sem chave no .bib (candidato verificado)
Nenhum candidato foi confirmado em fonte primária nesta rodada (não escrevi em referencias_candidatas.md). Lacunas sem chave:
- Cadeia TF map/odom/base_link (§2.2.1): REP 105 (ros.org/reps/rep-0105.html) e Foote, "tf: The transform library", TePRA 2013 (DOI 10.1109/TePRA.2013.6556373, não verificado nesta rodada).
- Estados do lifecycle e máquina de estados de actions (§2.3.2, §2.4.3): design docs do ROS 2 (design.ros2.org: node_lifecycle, actions). Documentação, não artigo.
- Comportamentos do Nav2 (lifecycle_manager, timeout em chamada prematura, controlador padrão): docs.nav2.org.
- Coeficiente de variação e RMSE como definição geral: livro de estatística (sem candidato).
- "variações de até 5% na duração são comuns" (§2.8.1) e "CV_t<5%": afirmações empíricas/próprias sem fonte; ligar a dado do Cap. de resultados ou assumir como critério do autor.
- Fórmula do erro de endpoint: sem fonte.
- Epígrafe "princípio da engenharia de qualidade": sem atribuição.

## Problemas de conteúdo
- §2.4.3: diz "três futures assíncronos" mas descreve só dois (aceite/rejeição e resultado). Se o terceiro for o de cancelamento, faltou descrever. Além disso REJECTED não é GoalStatus em ROS 2 (rejeição é resposta; status são UNKNOWN, ACCEPTED, EXECUTING, CANCELING, SUCCEEDED, CANCELED, ABORTED).
- §2.1: equações v=(vR+vL)/2, ω=(vR-vL)/L são cinemática direta, não "inversa". Além disso TurtleBot4 (base Create 3) tem caster dianteiro, rodas motrizes no meio; "traseiras" é impreciso.
- §2.4.1: "Na versão Jazzy o controlador padrão é MPPI": fontes secundárias indicam DWB no nav2_params.yaml padrão de Jazzy; conferir em nav2_bringup/params/nav2_params.yaml (branch jazzy) e nos params do TurtleBot4.
- §2.4.2: "pesos inversamente proporcionais ao custo" está incorreto: MPPI usa pesos exponenciais exp(-custo/λ) (softmax). Também o MPPI do Nav2 é implementado em CPU (a GPU é o artigo de Williams).
- §2.2: p(x_t, m | z, u) é o posterior online; "SLAM completo" usa x_{1:t}. Menor.
- §2.6: "consistência absoluta" no modo síncrono é exagero.
- §2.3.1: ver acima, QoS "silenciosa".
- §2.5: o texto de trabalho futuro usa "Seção sec:futuros" e hamer2025 (43% RPi4) a conferir.

---

# Relatório: 03

# Cap. 03 Trabalhos Relacionados — pesquisa de referências

## Citações adicionadas (chave existente)
- "Behavior Trees" (Nav2/Marathon 2) -> \cite{colledanchise2018}
- Gmapping -> \cite{grisetti2007}
- SLAM Toolbox -> \cite{macenski2021slam}

## Citação que não sustenta a frase
- macenski2023survey (RPP), sec. 1.2: o texto diz que o artigo "demonstra rastreamento de trajetória com erro lateral médio abaixo de 5 cm em curvas acentuadas" e que "avalia o desempenho de rastreamento". No PDF (arXiv 2305.20026) o erro médio de 0,03 m do RPP (vs 0,10 APP, 0,19 PP) vem de UMA simulação (Turtlebot3/Gazebo, ground truth), e o próprio artigo diz "the main contribution of this work is not an improvement on path tracking": o foco é segurança (regulação de velocidade por curvatura/proximidade). Na tabela de corredor, distância média ao caminho 0,052 m (RPP). Sugestão: dizer "em simulação ideal" e que o foco é segurança.
- macenski2020marathon: confirmado 37,4 milhas (~60 km), Tiago+RB-1, 0 colisões, <23 h. Mas o artigo reporta distância, colisões e recuperações, não "número de intervenções humanas" como métrica agregada (diz que não houve intervenção humana). Pequeno desajuste de descrição.
- thrun2005 (sec. 2.1, "três famílias ... dominantes"): Thrun (2005) não cobre Gmapping/Cartographer/SLAM Toolbox (posteriores, Cartographer 2016, SLAM Toolbox 2021) nem trata AMCL como SLAM (AMCL é localização). A citação sustenta as famílias (partículas/EKF/grafos), não a lista de pacotes nem "dominantes hoje". O Toolbox/Gmapping agora têm cite próprio; Cartographer (Hess et al. 2016) não está no .bib.
- gielis2022 (sec. 4.2 / 6): usada para "mismatch de QoS ... mesma classe discutida na literatura sobre comunicação em multi-robô". A revisão trata de formatos/tecnologias de comunicação em MRS, não de incompatibilidade de QoS DDS/ROS 2. Sustenta apenas de forma ampla.
- toris2015 (sec. 5): Robot Web Tools (2015) é rosbridge; a frase "Foxglove Studio e Robot Web Tools [toris2015]" atribui Foxglove ao artigo, que é de 2015 e não menciona Foxglove. Foxglove também não exige exatamente ROSBridge (tem foxglove_bridge). Ver "Problemas de conteúdo".
- santos2024 (Holter): Holter monitora PRÁTICAS de CI (métricas/maturidade de CI) em repositórios; o texto diz "observabilidade de builds" e "tornar comportamentos regressivos observáveis". Aproximação frouxa; verificar o texto do paper.
- macenski2022ros2: as 5 case studies (Ghost Robotics, Mission Robotics, Auterion, VIPER, OTTO) conferem (post dos autores). Verificar se o paper é "referência primária" para QoS/lifecycle/DDS (plausível, mas não conferi o PDF: o PDF tem >10 MB e não pôde ser lido).
- timperley2024: 221 bugs/7 sistemas confere. NÃO consegui confirmar nos textos acessíveis que os 7 são todos ROS 1 nem a lista (kobuki, mavros, geometry, turtlebot, motoman) e as categorias de causas-raiz (concorrência, tamanho de fila de publicador). Conferir no PDF (arXiv 2404.03629).
- albonico2023: 63 estudos confere. NÃO consegui confirmar 47/63, 46/63, 19, 15, 8/63 ROS 2 nem "fim do suporte ao ROS 1 em 2025" (a busca só confirmou "relevância industrial predominantemente baixa" e rigor baixo-médio por validade). Conferir no PDF (acesso aberto CC BY). Esses números também reaparecem na sec. Lacuna (46 de 63).
- amigoni2014: confere o corpus AAMAS 2002-2012 (95 artigos de robótica; sem 2004 e 2007 segundo slides). NÃO confirmei os percentuais ("pouco mais de um terço", "maioria dos links quebrada", "comparação só com variantes próprias"). Note também que "pouco mais de um terço dos artigos que reportam apenas médias" está ambíguo.
- hamer2025: confirmado venue/ano (JBCS 2025) e que Cartographer teve pior energia/CPU e Gmapping foi mais sensível a parâmetros. NÃO confirmei: lista exata dos 4 algoritmos (Karto), "cenários ponto-a-ponto e circulares", nem a afirmação de que "não há métricas RMSE" e a marca "Open-source $\times$" na tabela.
- maset2022: não consegui acessar (MDPI 403). Os números (3 aquisições robóticas, 3 manuais, TLS referência, ~2 cm, robótico menos ruído) e a marca "Record-Replay: checkmark" na Tabela precisam de conferência manual. Em especial, a Tabela marca record-replay como presente, o que pode ser exagero (é repetição de aquisições, não record-replay de bags).
- verma2021: "seis dimensões" — abstract confirma seis dimensões; o texto lista cinco itens + "entre outras" (ok).
- parker1998, farinelli2004, sikand2021, lampe2023, carroll2021, romero2023, yan2023, singhal2017, cortes2017, gerkey2004, korsah2013, khamis2015, burgard2000, fox2006, alonsomora2017: descrições conferem com abstracts em referencias_pdfs/*.md (Robofleet "sem protocolo de repetibilidade" é afirmação do autor, ok). yan2023 "recuperação de falhas" ok; singhal2017 "cloud robotics" ok.
- coulter1992, dissanayake2001, durrantwhyte2006/bailey2006, kohlbrecher2011: metadados batem com o .bib; durrantwhyte/bailey: "Vinte anos depois" (2006 -> 2026) ok; dissanayake2001 "demonstrados formalmente convergência" ok (prova de convergência no artigo).
- amigoni2010: "propõem simulação e experimentação física como complementares" — não verifiquei texto; título (Good Experimental Methodologies and Simulation) é compatível.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
(não verifiquei fonte primária para nenhum candidato abaixo além da existência conhecida; autor decide)
- "RViz2 ... requer instalação local do ROS 2 e não oferece acesso remoto nativo" (sec. 5): sem citação; falta chave (RViz/ROS docs).
- "Foxglove Studio" e rosbridge: sem chave no .bib; documentação oficial Foxglove (docs.foxglove.dev) seria fonte. Também para "requerem o ROSBridge".
- "Fleet Management do Open RMF despacha tarefas e otimiza rotas" (sec. 4.1): sem chave; candidato: Open-RMF docs / Chen et al. (ver abaixo). Não verifiquei.
- Cartographer (Hess, Kohler, Rapp, Andor, ICRA 2016, "Real-time loop closure in 2D LIDAR SLAM", doi 10.1109/ICRA.2016.7487258): sem chave.
- Nav2 como software (Macenski et al. 2020 é o Marathon 2, ok).
- "Ardent Apalone, dezembro de 2017" (sec. 1.3): sem citação (ROS 2 release docs).
- "jitter do DDS, scheduling do SO ... contribuem para variabilidade" (sec. 4.2): atribuído a macenski2022ros2, mas o texto diz "documentado em trabalhos de pesquisa de tempo-real": candidato real: Casini et al., "Response-time analysis of ROS 2 processing chains under reservation-based scheduling" (ECRTS 2019) e Maruyama et al. "Exploring the performance of ROS2" (EMSOFT 2016). Não verificados.
- "fim do suporte de longo prazo ao ROS 1 previsto para 2025" (atribuído a Albonico): ROS 1 Noetic EOL maio 2025 é fato público (REP/ROS docs).
- "Esse diagnóstico ... permanece pertinente em 2026": afirmação sem cite recente; bonsignorio2015 (já no .bib, "Toward Replicable and Measurable Robotics Research") poderia sustentar a necessidade de protocolos padronizados -> sugestão: adicionar \cite{bonsignorio2015} nessa frase (não adicionei por ser decisão de mérito; chave existe).
- "tendência da comunidade a priorizar contribuição algorítmica" (Lacuna): marcada como interpretação do autor; sem cite (ok por ser explícita).
- "ausência de trabalhos publicados que adotem FastAPI + canvas + Nav2 sem ROSBridge" (sec. 5): afirmação negativa sem protocolo de busca; fraca.

## Problemas de conteúdo
1. Sec. 2.1 lista "AMCL" como filtro de partículas de SLAM: AMCL é localização Monte Carlo, não SLAM.
2. Sec. 5: Foxglove não é "baseado em rosbridge" necessariamente (foxglove_bridge/WebSocket próprio); e toris2015 não cobre Foxglove.
3. Sec. 1.2: RPP é descrito como avaliação de rastreamento; o foco é segurança (ver acima). O número "5 cm" não aparece como tal no artigo (0,03 m em simulação; 0,052 m na tabela do corredor).
4. Sec. 4.1: "seis dimensões ... comunicação, planejamento, arquitetura, escalabilidade e decisão, entre outras" lista só 5 (o abstract do Verma lista também mecanismo de comunicação, estratégia de planejamento, arquitetura de controle, escalabilidade, tomada de decisão); ok, mas a taxonomia proposta tem 6 dimensões "broad" — não confundir parâmetros com dimensões.
5. Sec. 4.2: o parágrafo inicial atribui a macenski2022ros2 a "variabilidade observada em experimentos de navegação" por jitter de DDS e SO; o artigo é sobre arquitetura e usos, provavelmente não documenta isso (conferir).
6. Tabela: marcas "Record-Replay $\checkmark$" para maset2022 e "Parcial" para hamer2025, "Open-source $\times$" para hamer2025/maset2022 e "Métricas RMSE $\times$/Parcial" não estão sustentadas por citação nem verificadas; o texto da tabela é comparativo e deveria ser conferido contra os artigos.
7. Sec. 3.1 "AAMAS" (amigoni2014): ok. Mas amigoni2014 é capítulo de livro, não "artigo".
8. Tabela/texto: "Os dois objetivos são ortogonais" e "nenhum cobre mais de dois eixos" — afirmação comparativa própria, depende da verificação da tabela (item 6).

---

# Relatório: 04

# 04_arquitetura.tex — pesquisa de referências

Nenhum dos 8 keys citados tem nota/PDF em referencias_pdfs/; verificação via arXiv/Springer/web e código.

## Citações adicionadas (chave existente)
- "action client Nav2" (seção Orquestrador): + \cite{macenski2020marathon} (Nav2).
- "descoberta automática de nós do DDS": + pardocastellote2003dds (visão de arquitetura/discovery do DDS) ao lado de macenski2022ros2.
- Considerações Finais, "plugin DiffDrive do Gazebo, o Nav2, o SLAM Toolbox": + koenig2004gazebo, macenski2020marathon, macenski2021slam.

## Citação que não sustenta a frase
- macenski2022ros2 em "callbacks de serviço com wait_for_server precisam ocorrer em threads separadas ... (deadlock)": o artigo só lista "swappable executor" numa tabela; NÃO trata de executores multithread nem deadlock. Afirmação é de fato do sistema do autor (código: MultiThreadedExecutor em fleet_orchestrator/main.py:576); a citação só sustenta "DDS tem descoberta distribuída". Sugestão: manter como suporte do DDS, e apoiar o deadlock no código/doc do rclpy.
- macenski2022ros2 em "incompatibilidade silenciosa de QoS ... nenhum erro é reportado": o artigo (Seção III-F) descreve reliability/durability/history mas NÃO discute incompatibilidade nem silêncio. Não sustenta a frase.
- macenski2021slam (JOSS) na frase de QoS do SLAM Toolbox ("usa RELIABLE + VOLATILE"): o artigo não menciona QoS; sustenta só a identidade da ferramenta. O perfil vem do código (data_collector/main.py:95-100).
- timperley2024: OK (ROBUST, concorrência 20 bugs, falhas de comunicação/timing; exemplos são ROS 1). Frase adequada.
- toris2015 (rosbridge), elfes1989 (occupancy grid), garlan1995architectural, pardocastellote2003dds, omgdds2015: coerentes com as frases. Obs.: garlan1995architectural no .bib está sem pages/doi (IEEE Software 12(6), pp. 17-26, doi 10.1109/52.469757).

## Afirmação sem referência e sem chave no .bib (candidato verificado)
- Backend REST / "REST" como estilo: Fielding, R. T. (2000), "Architectural Styles and the Design of Network-based Software Architectures", tese de doutorado, UC Irvine (existência confirmada em ics.uci.edu/~fielding/pubs/dissertation/).
- TF por robô / lookups map->base_link: Foote, T. (2013), "tf: The transform library", IEEE TePRA, pp. 1-6, doi 10.1109/TePRA.2013.6556373 (confirmado em múltiplas fontes).
- Executores multithread/deadlock com wait_for_server no ROS 2: sem artigo verificado; usar a documentação oficial do rclpy/ROS 2 executors (não pesquisada a fundo). Candidato não verificado: Casini et al., ECRTS 2019 (executores ROS 2) — NÃO confirmado.
- FastAPI, React, MCAP, AMCL, nav2 action servers: citados sem referência (FastAPI/React são documentação de software; AMCL = Fox, Thrun et al. — não verificado e o bib só tem fox1997 que é DWA, não AMCL).

## Problemas de conteúdo
1. Direção do exemplo de QoS invertida (seção Coletor): "Assinar um tópico RELIABLE com um subscriber BEST_EFFORT resulta em incompatibilidade": em DDS/ROS 2, publisher RELIABLE + subscriber BEST_EFFORT é COMPATÍVEL; o incompatível é publisher BEST_EFFORT + subscriber RELIABLE (caso do Gazebo, que é BEST_EFFORT, como o próprio comentário do código diz). Corrigir a frase.
2. "nenhum erro é reportado": desde ROS 2 Foxy/Galactic o rclpy/rmw emite warning/evento de QoS incompatível (usa-se Jazzy). Afirmação "silenciosa" está desatualizada/exagerada.
3. roles.yaml atual (fleet_orchestrator/config/roles.yaml): tb1, tb2 e tb3 são todos MUUT ("temporariamente", tb2 era FUUT, tb3 era SU). O capítulo descreve FUUT/SU como papéis operacionais; verificar consistência com a campanha. Além disso _motion_allowed só permite MUUT, então rejeita também SU (o texto diz "rejeitando comandos para FUUTs").
4. Número "1,2 a 3,2 s" por chamada subprocess (Docker, 2026): sem medição encontrada no repositório (grep em backend/docs); fonte do número precisa ser confirmada. Fórmula "(Docker, 2026)" lembra citação mas não é.
5. Frase "sete serviços" (orquestrador) confere com o código (7 create_service); "10 services / 2 msgs" confere (10 .srv, 2 .msg). Polling 300 ms (useFleetStatus) e 1500 ms (App.jsx fetchMap) conferem. Cores do mapa: livre = creme, ocupado = azul-escuro, desconhecido = azul-cinza: conferem. Tabela de transições: confere com o código.
6. "pose (/tf)" no backend: o backend assina amcl_pose/pose além de manter buffer TF; confere parcialmente.
7. Camada de agentes de IA: o capítulo NÃO menciona agentes (nenhuma ocorrência). Mas o repositório ainda tem backend/agents/, frontend/src/components/AgentFleetPanel.jsx e hooks/useAgentFleet.js — resíduo de código fora do capítulo.

---

# Relatório: 05

# 05_metodologia.tex — achados (pesquisa)

## Citações adicionadas (chave existente)
- l.~66 (RMSE pairwise): `\cite{sturm2012,zhang2018trajectory}` — ambos definem RMSE como métrica de erro de trajetória (ATE). Ressalva: usam ground truth/alinhamento, não RMSE pairwise entre replays; suporte é para "RMSE como métrica de trajetória". Não confirmei o texto dos PDFs (sem notas locais), só título/DOI.
- Tabela do ambiente: ROS 2 `macenski2022ros2`; Gazebo `koenig2004gazebo` (Gazebo clássico/origem; não descreve Harmonic 8.x especificamente); Nav2 `macenski2020marathon`; MPPI `williams2016`; SLAM Toolbox `macenski2021slam` (mesmas chaves que o Cap. 2 usa para esses itens).

## Citação que não sustenta a frase
- l.~65 `\cite{amigoni2010}` (interpolar trajetórias para grade de tempo normalizada): Amigoni & Schiaffonati 2010 trata de metodologia experimental e papel da simulação; nada indica que proponha interpolação em grade temporal. Suporte fraco/inadequado (mesmo problema em 02_fundamentacao l.331). Não removida; sugerir citar como justificativa só de "avaliação controlada", ou trocar por fonte de avaliação de trajetória (sturm2012/zhang2018trajectory já adicionadas).
- l.~177 `\cite{bonsignorio2015}` (pose inicial igual como pré-condição de repetibilidade): é editorial de guest editors sobre pesquisa replicável/mensurável; suporta o tema geral, não o requisito específico. Suporte fraco.
- l.~166 e ~191 `amigoni2010` (controle de variáveis em simulação): consistente com a descrição do Cap. 3 (simulação permite controle completo). OK.
- l.~88-90 `maset2022`: confere (repetições do robô comparadas entre si e com referência TLS). OK. l.~149 e ~271 `amigoni2014`: coerente com Cap. 1/3 (comparação estatística fraca; procedimentos informais). OK.
Observação: verificação apenas via resumos/metadados (Springer e MDPI bloqueiam acesso automático); não li as passagens no texto integral.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
- l.68-78 DTW e distância de Fréchet "existem para lidar com desalinhamento de fase/velocidade": candidatos conhecidos, NÃO verificados contra fonte primária nesta sessão: Sakoe & Chiba 1978, IEEE Trans. ASSP, doi 10.1109/TASSP.1978.1163055; Eiter & Mannila 1994, "Computing Discrete Fréchet Distance", TR CD-TR 94/64, TU Wien.
- l.144-146 distribuição t para N pequeno / variância desconhecida: candidato Student 1908, Biometrika 6(1):1-25, doi 10.2307/2331554 (não verificado nesta sessão); alternativa: livro-texto de estatística.
- l.36-38 tolerâncias de chegada do Nav2 (0,25 m / 0,25 rad): documentação do Nav2 (nav2_params / SimpleGoalChecker, docs.nav2.org); não é artigo. Valor vem do pacote nav2_minimal_tb4_sim, não está no repo.
- Itens da tabela sem chave: TurtleBot4, OAK-D Pro, RPLIDAR, rosbag2/MCAP, mundo warehouse (documentação de fabricante/projeto).

## Problemas de conteúdo
- Duas definições de consistência temporal: Cap.5 l.105 ("desvio padrão das durações", em segundos) vs Cap.2 §consistencia_temporal / Cap.1 l.218 / Cap.8 (CV_t = σ_t/média ×100%, limiar 10%). Cap.8 reporta CV (2,2%) e σ (0,38 s). Unificar: definir como CV_t e referenciar a Eq.~\ref{eq:cv_temporal}. Além disso, analyze_runs.py só emite `duration_sec` e `duration_ratio_vs_ref`; não achei cálculo de σ_t/CV_t em código (provavelmente feito fora do script).
- Cap.5 diz "cinco métricas" e lista 5, mas Cap.1 l.152 cita três (RMSE, endpoint, consistência temporal) — coerência a conferir.
- Fórmula do IC (t de Student) não encontrada implementada nos scripts do repo (grep por t.ppf/ci95 sem resultado); confirmar onde é calculada.
- Verificado no código: record 5 Hz, min_dist 0,10 m, min_yaw 5° (single_robot_sim.yaml/main.py); atrasos de 8 s (SLAM) e 12 s (Nav2) em turtlebot4_sim.launch.py; uso de FollowWaypoints. NÃO verificados no repo: wait_at_waypoint 200 ms, tolerâncias 0,25 m/rad, odom a 30 Hz (parâmetros externos ao repo).
- "Nenhuma métrica trata heading" é coerente com analyze_runs.py (usa só x,y).

---

# Relatório: 06

# Capítulo 06 (Implementação) — pesquisa/verificação (2026-11-16)
Código verificado no checkout atual (branch `dissertacao`) de /Users/Wander/fleet-ui-dissertacao. Nenhum arquivo do repositório foi alterado (nenhum \cite adicionado).

## Citações adicionadas (chave existente)
Nenhuma aplicada (escopo: só reportar). Sugestões com chave já no .bib, para o autor aplicar:
- l.196 "RMSE pairwise após reamostragem em tempo normalizado \cite{amigoni2010}": acrescentar \cite{zhang2018trajectory} (tutorial de avaliação quantitativa de trajetória; já usado em 02_fundamentacao l.331 para a mesma ideia de grade temporal comum) e/ou \cite{sturm2012} (ATE/RMSE).
- l.264 "RMSE \cite{thrun2005}": ver seção seguinte; \cite{sturm2012}/\cite{zhang2018trajectory} sustentam melhor o RMSE de trajetória.
- l.9 simulação antes do robô físico: \cite{amigoni2010} e \cite{koenig2004gazebo} (Gazebo) já estão no .bib e são usados em 05_metodologia (l.65, 168, 193). Gazebo (l.7-11) sem citação no capítulo: \cite{koenig2004gazebo}.
- l.69-70 ROS 2: \cite{macenski2022ros2} já presente; \cite{quigley2009} é ROS 1 (não usar para ROS 2).
- l.255-256: Nav2 como sistema (MPPI/DWB/RPP vivem no Nav2): \cite{macenski2020marathon} (Marathon 2) cabe aqui; o capítulo cita Nav2 sem referência (aparece só em 05 l.211).

## Citação que não sustenta a frase
- l.196 \cite{amigoni2010} (Good Experimental Methodologies and Simulation...): é sobre metodologia experimental/repetibilidade; NÃO define RMSE pairwise nem reamostragem em tempo normalizado. Sustenta no máximo a ideia de métrica reprodutível. Frase é decisão de projeto do autor (código analyze_runs.py), não resultado da literatura.
- l.264 \cite{thrun2005}: Probabilistic Robotics é livro-texto de localização/SLAM; não é referência para o RMSE de trajetória entre execuções (a fórmula é a definição estatística padrão). Sustentação fraca; trocar/complementar por sturm2012 ou zhang2018trajectory.
- l.340 \cite{elfes1989}: Elfes define grades de ocupação (conceito), mas NÃO os campos `resolution/origin_x/origin_y` da mensagem ROS `nav_msgs/OccupancyGrid`/`MapMetaData`. Metadados citados são da API do ROS (docs.ros.org nav_msgs/MapMetaData), sem chave no .bib. Citação apoia só "OccupancyGrid" como conceito.
- l.141 \cite{toris2015}: Robot Web Tools/rosbridge é artigo de 2015 (ROS 1). A frase "entre o navegador e o ROS~2" extrapola; rosbridge_suite tem port ROS 2, mas o artigo não cobre isso.
- l.70 \cite{macenski2022ros2} para `MultiThreadedExecutor`: o artigo descreve a arquitetura/executores do ROS 2 em linhas gerais; o detalhe do MultiThreadedExecutor em rclpy é da documentação do rclpy (não verificado no artigo; PDF não está em referencias_pdfs/). Aceitável, marcar como "parcial".
- l.255-257 \cite{fox1997} para "DWB": fox1997 é o DWA original; DWB é a implementação do Nav2 (sem artigo próprio). Aceitável, mas a frase poderia dizer "baseado em DWA". \cite{macenski2023survey} (chave com nome "survey") é na verdade o artigo Regulated Pure Pursuit (Autonomous Robots 2023) — correto para RPP, só o nome da chave é enganoso.
- l.8 \cite{takaya2016}: título (Simulation Environment for Mobile Robots Testing Using ROS and Gazebo) é compatível com "validar em simulação antes do robô físico"; PDF não disponível, verificar o resumo no DOI 10.1109/ICSTCC.2016.7790647 (não confirmado texto).
- l.45, 214, 341 \cite{macenski2021slam}: OK (SLAM Toolbox JOSS; scan matching, publica pose e mapa). Pequena ressalva: tópico `pose` curto não vem do artigo, é do `fleet_data_collector`.
- l.255 \cite{williams2016}: MPPI — OK.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
- l.9-10 "Gazebo Harmonic, versão de suporte estendido pareada com o ROS 2 Jazzy": confirmado em https://gazebosim.org/docs/harmonic/ros_installation/ (Jazzy + Harmonic = combinação recomendada; Harmonic é LTS). Candidato: essa página de documentação (REP-2000 também lista Jazzy). Sem chave no .bib.
- l.17-20 "irobot_create_gz_plugins projetados para Ignition Fortress; Harmonic renomeou ignition.msgs -> gz.msgs": NÃO verificado (a renomeação ocorreu na transição Ignition->Gazebo; checar o guia de migração Gazebo e o repo iRobot create3_sim). Sem fonte no repo.
- l.23-25 "onze nós" com `enable_stamped_cmd_vel`: contagem NÃO verificável no repositório (nav2.yaml é do pacote turtlebot4_navigation, de fora). O override estático em config/nav2_minimal_override.yaml lista 5 nós (bt_navigator, controller_server, velocity_smoother, collision_monitor, waypoint_follower); o patch dinâmico em turtlebot4_sim.launch.py/turtlebot4_multi_sim.launch.py é genérico (varre todas as chaves). Citar documentação do Nav2 ou issue #94 do turtlebot4_simulator (referida no próprio yaml).
- l.46-49 "convenção padrão do Nav2 para multi-robô" (TF por robô, frame_id sem prefixo): sem fonte; candidato: docs Nav2 (navigation2 multi-robot / nav2_bringup `tb3_simulation` com namespace). Não verificado em fonte primária.
- l.88-91 "`TransformListener` não permite escutar tópico diferente do /tf global": VERIFICADO em https://github.com/ros2/geometry2 (jazzy, tf2_ros_py/transform_listener.py): construtor só tem buffer,node,spin_thread,qos,static_qos; tópicos fixos '/tf' e '/tf_static'. Citar o código-fonte do tf2_ros (jazzy) em nota.
- l.164-168 `subprocess.Popen(preexec_fn=os.setsid)` / `os.killpg`: sem referência; documentação Python (subprocess, os.setsid/killpg) é a fonte natural. Sem chave.
- l.145-149 `shlex.quote`: documentação Python shlex. Sem chave.
- l.191-194 formato CDR/MCAP, rosbag2_py: sem referência (docs rosbag2/MCAP). Sem chave.
- l.9-14 mundo warehouse "nav2_minimal_tb4_sim": pacote ROS (documentação), sem chave.

## Texto que não bate com o código
1. **l.74-78 (pending_goal_pose) — a verificar/corrigir.** Código (fleet_orchestrator/main.py l.337, 374-399): `pending_goal_pose = poses[0]` é atribuído em `_send_nav_poses` (a META enviada, apenas a PRIMEIRA pose se for rota com várias) e, no callback de resultado, se `status == STATUS_SUCCEEDED` e `is_recording`, essa pose-meta é anexada a `route_poses`. O texto diz que é adicionada "a pose real confirmada pelo Nav2 ... melhor estimativa da posição atingida": ERRADO — não é pose medida/confirmada; é a pose COMANDADA (goal) em frame `map`. O comentário do código diz "salva waypoint atingido diretamente (não depende de TF)". Também, em caso de rota com N poses (FollowWaypoints) só `poses[0]` é guardada. Nos outros resultados (`else`) limpa para None. "Imediatamente" ok.
2. l.80-84 (record_tick): 5 Hz, 10 cm, 5° batem com os defaults dos parâmetros (`record_rate_hz=5.0`, `min_dist_m=0.10`, `min_yaw_deg=5.0`), mas são parâmetros ROS configuráveis, não constantes. A primeira amostra (last_saved=None) é sempre salva. A justificativa "cobrindo os casos em que o Nav2 não reporta SUCCEEDED (e.g., controlador para dentro da tolerância antes de publicar o callback)" é inferência sem respaldo no código/comentários — o tick roda sempre que `is_recording`, independentemente do Nav2.
3. l.92: "um `Buffer` e uma inscrição por robô, uma para cada /tb{1,2,3}/tf": o código cria DUAS inscrições por robô (`/<id>/tf` VOLATILE e `/<id>/tf_static` TRANSIENT_LOCAL), `_setup_robot_tf`. Também cria robô "" (namespace vazio) sob demanda.
4. l.110-118 papéis: `_motion_allowed` bate (True só para MUUT; ROLE_NOT_ALLOWED antes de wait_for_server; ordem real: UNKNOWN_ROBOT -> ROLE_NOT_ALLOWED -> ...). Porém o `roles.yaml` atual marca tb1, tb2 e tb3 todos como MUUT ("temporariamente MUUT p/ demo multi-robô"); logo, na configuração versionada, nenhum robô é bloqueado — o texto pode induzir a ler que FUUT é rejeitado no setup padrão. Não há `_cb_go_to_point` com `_motion_allowed`? (há; ok).
5. l.176: "mantendo um buffer circular": em main.py `_sim_append_line` usa lista truncada em 500 linhas (não deque/circular de fato; comportamento equivalente). Menor.
6. l.349-364 (**painel "Missão Coordenada"**, `SimulationPanel`, formações L/I/V/barra invertida, `activate_robot`, `deactivate_robot`, despacho sequencial): NÃO existe no checkout atual (branch `dissertacao`). `frontend/src/components/SimulationPanel.jsx` aqui tem título "Simulação (Gazebo + Nav2 + frota)", só escolhe modo single/multi, mundo e robôs, e inicia/para (117 linhas); sem formações, sem despacho, e `grep activate_robot` não acha nada em backend/frontend/fleet_ws desta branch. A implementação existe em `origin/mission-coordinate-large-scale` (backend/main.py `/api/simulation/activate_robot`, `deactivate_robot`; SimulationPanel.jsx com título "Missão Coordenada"). Também: o texto descreve `/api/simulation/status`, start, stop (existem aqui). Decidir qual código é o do capítulo (a dissertação descreve o branch missão-coordenada).
7. l.5-14 / l.202-210 e números: confirmados contra `fleet_ws/runs/dissertation_clean01_final_manual/analysis/summary.json` (em origin/new-way-samsung, não no checkout atual): resampling = {mode: time, samples: 100, time_grid: normalised_0_1}; média vs. referência 3,35 cm (9 réplicas contra replay_01); média da matriz pairwise 2,76 cm; todos os traj_topic = /odom. OK.
8. l.231 "nove testes": tests/test_analyze_runs.py tem 12 testes; os 9 do tópico de pose (slam_pose/auto) batem (l.66-125). OK. (3 outros são de reamostragem.)
9. Listagens: `lst:rmse_impl` idêntica a `_normalised_time_grid`/`_resample_xy_by_time`/`_rmse`; `lst:pose_fallback` bate (comentário encurtado); `lst:backend_bridge` idêntica a `RosBridge.run_service`; `lst:rmse_pairwise` idêntico ao laço de `main`; `lst:rmse_mean` = versão reduzida de `vs_reference` (omite `final_endpoint_error_m`, `duration*`, `mean_pointwise_distance_vs_ref_m` — o `...` indica elisão, mas a legenda não diz "elidido"); `lst:start_stop_record` bate (omite `resp.error_code=""` e o bloco UNKNOWN_ROBOT de stop — indicado no comentário; faltou `resp.error_code = ""` sem aviso). Legenda cita `fleet_ws/scripts/analyze_runs.py` com `analyze_runs.py` escrito como `analyze\_runs.py` sem \allowbreak em lst:rmse_mean (só estética).
10. l.133-143: afirmação "main.py mantém `_run_ros2_service`, que delega a `RosBridge.run_service`; RosBridge também reaproveitado por análise de bags e descoberta de robôs": correto (`analyze_bags`, `discover_robots`, `test_ssh`).
11. l.38-45 (fork do xacro): confirmado em `urdf/tb4/icreate/create3.urdf.xacro` (cmd_vel, odom, tf, joint_states com `tb_prefix`), mais scan (rplidar), imu e rgbd_camera = 7 tópicos. OK. CI: job `ros-checks` com `osrf/ros:jazzy-desktop` valida xacro; `tests/test_xacro_multirobot.py` testa tb1/tb2 (conferir se testa também "" e tb3).

## Problemas de conteúdo
- **Camada de agentes de IA ainda presente no repositório** (não no texto de 06): `backend/agents/` (analyst.py, executor.py, planner.py, tools.py, __init__.py), `from agents import Analyst, Executor, Planner` em backend/main.py l.32, endpoints `/api/agent/run`, `/api/agent/job/{id}`, `/api/agent/run_fleet`, `/api/agent/fleet_job/{id}`, `/api/agent/history` (l.895-990), `frontend/src/components/AgentFleetPanel.jsx` + `hooks/useAgentFleet.js` (importado em App.jsx l.3, estado `agentPanel`), `tests/test_agent_*.py`, `test_agents_*.py`. O capítulo 06 NÃO menciona agentes (nenhuma ocorrência de "agente", Planner, Executor, Analyst — conferido). Se o código-fonte entregue ao comitê é este, a remoção ainda não foi feita no repo. Também outros capítulos devem ser checados por outro agente.
- l.255-258: MPPI "determinístico vs. aleatório": coerente com 05 l.211 e 02 l.181; DWB é descrito como determinístico — correto.
- l.237-240: datas (campanha 15/09/2026; correção 22/09/2026) não verificadas contra git (não conferido).
- l.60-64: afirma validação por CI "para os namespaces vazio, tb1, tb2 e tb3" — conferir `tests/test_xacro_multirobot.py` (só vi `_run_xacro("tb1")` e comparação tb1 x outro); possível divergência.
- l.134 e 156: "Seção sec:backend_web", "sec:rel_web", "sec:limitacoes", "sec:ameacas", "sec:res_fonte_trajetoria" existem (04, 03, 09, 07, 08). Tabela `tab:ambiente_hw` existe em 05. OK.
- l.326: "3,35 cm / 2,76 cm" conferidos (ver item 7).

---

# Relatório: 07

# Pesquisa de referências — 07_avaliacao.tex (2026-11-16)

## Citações adicionadas (chave existente)
- `\cite{acm2020badging}` na frase "resultados processados, scripts de campanha e de análise estão versionados para conferência por terceiros" (Validade de construto). Chave existe no .bib; o documento ACM define "Artifacts Available/Reproduced". Não li o texto da chave (sem PDF local) — autor deve conferir se o encaixe é desejado.

## Citação que não sustenta a frase
- `macenski2023survey` ("RPP isolado tem erro lateral médio inferior a 5 cm"): o artigo é o RPP (arXiv 2305.20026). Lido em HTML: erro médio 3 cm (sim, TB3), 4,3 cm (rota completa em hardware), mas 5,2 cm no corredor confinado (PP 10,0, APP 5,9). Portanto "inferior a 5 cm" vale para 2 de 3 experimentos; sugestão: "da ordem de 3--5 cm". (A tabela do paper rotula mm, mas magnitudes são metros×100; o resumo foi feito por modelo de extração, conferir no PDF.)
  Obs.: a chave se chama "survey", mas a entrada é o RPP — nome enganoso, só estético.
- `maset2022` ("distância cloud-to-cloud da ordem de 2 cm"; "comparar execuções nominalmente idênticas entre si"): NÃO consegui verificar. MDPI devolve 403 e não há PDF local; o abstract (Crossref) confirma apenas que comparam nuvens do robô vs. portátil vs. TLS (ground truth) e avaliam repetibilidade; não cita 2 cm nem a lógica de "execuções entre si". Precisa conferir manualmente nas tabelas do artigo.
- `amigoni2010` ("simulação isola variabilidade dos algoritmos da variabilidade ambiental"): título do capítulo trata de metodologia experimental e simulação; plausível, mas não verificado o trecho (Springer paywall).
- `sturm2012`, `borenstein1996`, `runeson2009` (pág. de "viés subjetivo/confiabilidade"), `borji2018` (computer vision, usado para resultados negativos em geral — adequado como "perspectiva", mas domínio é visão computacional), `timperley2024`, `afzal2020`, `jakobi1995`, `zhang2018trajectory`, `wilson2014`, `williams2016`, `fox1997`, `macenski2020marathon` (afirmação de "dezenas de km, intervenções humanas"): não conferidos contra o texto (sem PDFs locais, paywall/tempo). Encaixes parecem coerentes com títulos/abstracts.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
- Limiar 25 cm / 0,25 rad do `general_goal_checker` do Nav2: valor de documentação do Nav2 (docs.nav2.org), sem chave no .bib; sugerir entrada @misc da documentação do Nav2. Não verificado nesta rodada.
- Critério de 10% para QA3 e "N=10 melhora a estimativa de variabilidade": limiares de projeto sem referência; o capítulo já os declara como critério mínimo do autor. Nenhum candidato verificado.
- "LiDAR/odometria simulados menos ruidosos que reais": sem citação; `koenig2004gazebo` (já no .bib) poderia embasar descrição do Gazebo, mas não a afirmação de ruído — não adicionei.
- "MPPI regenera ruído a cada ciclo a 20 Hz": configuração do projeto, não literatura (williams2016 já cobre o método).

## Número que não bate com os dados
- Não há `summary.json`/`replay_NN.json` no repositório (fleet_ws/runs inexistente; só fleet_ws/{docs,scripts,src}); não pude conferir 3,35 cm, 4,76 cm, 2,76 cm, 14,27 cm contra dados brutos.
- Consistência interna com cap. 8: 4,76 aparece na tabela (Replay 08), 3,35 média e 1,65/4,76 mín/máx batem; 25/4,76 = 5,25, "cerca de cinco vezes" correto; 14,27 cm (loop) bate. O valor 2,76 cm (média de todos os pares) NÃO aparece no cap. 8 (grep sem resultados) — verificar se está lá em outro formato. O cap. 8 usa 2,00 cm para "RMSE residual entre réplicas" (exploratório teste1), diferente de 2,76 (campanha final) — são campanhas distintas, mas vale conferir.
- "cinco vezes" vs "quase uma ordem de grandeza": o cap. 8 hoje só usa "ordem de grandeza" para outra razão (duração 29,47/11,70 ≈ 2,5×) — inconsistência anterior não aparece mais.
- 0,25 rad ≈ 14° correto (14,3°).

## Problemas de conteúdo
- "Os valores brutos... (Tabela tab:campanha_final)" e "erro final médio e máximo < 25 cm": ok. 
- Limiar 25 cm admitidamente não calibrado e permissivo; o capítulo já reconhece (bom). Comparar com RPP (controlador isolado) e Maset (sensor/mapeamento 3D) é comparação entre grandezas distintas — o texto já ressalva.
- Seção "Considerações Finais" e "Arranjo Experimental" têm pouca citação metodológica (só amigoni2010): afirmações sobre trade-off simulação×realismo poderiam usar afzal2020/jakobi1995 (já no .bib, usadas em Validade externa).
- Chave `macenski2023survey` aponta para o artigo RPP, não survey.

---

# Relatório: 08

# Cap. 8 (08_resultados.tex) — pesquisa de embasamento e conferência numérica

Dados brutos NÃO estão no checkout atual (branch dissertacao); foram extraídos de `git archive origin/new-way-samsung-v2 fleet_ws/runs` (commits 6e2484d, ec563fd) para o scratchpad e recalculados.

## Citações adicionadas (chave existente)
- l.28 `\cite{macenski2020marathon}` após "tolerância padrão de 25 cm do Nav2" (atribui o Nav2; o artigo NÃO traz o valor 25 cm, que vem da documentação/parâmetro xy_goal_tolerance — fonte do número continua sendo a seção criterios do cap. 7).
- l.322 `\cite{sturm2012}` em "RMSE ... contra o ground truth" (ATE/benchmark com GT externo).
- l.542 `\cite{macenski2022ros2}` em "ROS 2 Humble".

## Citação que não sustenta a frase
- l.186-188: "como recomendam \citeonline{maset2022}" (RMSE par-a-par entre execuções do mesmo mecanismo) — Maset et al. 2022 é estudo empírico de repetibilidade de mapeamento 3D (nuvens de pontos vs TLS), não "recomenda" métrica de trajetória nem fala de mecanismo de navegação. Só o abstract foi conferido (MDPI/PDF deram 403). Sugerir "na mesma lógica de" (como o cap. 7 já escreve).
- l.113-116: "prática, adotada por maset2022, de reportar a dispersão entre execuções" — não confirmado (texto completo inacessível); mesma ressalva.
- l.187-188: "prática que \citeonline{amigoni2014} criticam" (média contra uma referência) — amigoni2014 é levantamento sobre metodologia experimental (rigor, replicabilidade, estatística fraca), não critica especificamente comparar contra uma referência única. Reformular ou trocar a atribuição. (Springer bloqueou; baseado no uso do próprio cap. 3 l.113 e EMBASAMENTO_VIESES.md.)
- l.384 `borenstein1996`: ok para erro sistemático de odometria; o texto "erro acumula com distância e curvas" é interpretação razoável, mas o artigo trata erros sistemáticos (UMBmark), não "deriva por integração" em geral. Aceitável, ressalva leve.

## Afirmação sem referência e sem chave no .bib (candidato verificado)
- Nenhum candidato verificado. Pendentes sem chave: AMCL/QoS (l.566-567), FUUT/observação exógena por subtração de referência (l.432-438), "ruído de sensor esperado" (l.483), actions Nav2 Humble x Jazzy (l.606; é verificação do autor nas definições, ok sem cite).

## Número que não bate com os dados
Tudo abaixo CONFERE com summary.json/replay_NN.json (recalculado): tabela campanha_final (duração, comprimento, RMSE, erro final dos 10 replays), RMSE médio 3,35, dp 1,16, min 1,65, max 4,76, erro final médio 1,64 e máx 3,26, duração média 17,51 e dp 0,38 (CV 2,17%), comprimento 0,826 e dp 0,011, start_xy dif. ~1e-18, tabela sensor_bags (msgs médias, faixas, Hz), 10/10 success; teste1: 13,90 / 2,00 / razão 6,95 ("quase sete vezes" ok), durações 29,47 e 11,70 (razão 2,52); tabela fonte_trajetoria (médias e IC 95% das 3 rotas), comprimentos ~0,9/7,7/11,3 (0,86/7,66/11,35), 30 réplicas com 0 retries; FUUT 3,06/5,88/4,76 e discrep. temporal 0,00.
Divergências:
1. Tab. val_rmse, Val01, erro de endpoint "20,5 cm": a figura erro_endpoint.png mostra Val01 = 20,5 (réplica 1) e 23,2 (réplica 2); Val02 = 5,8 e 9,3 (a tabela usa faixa 5,8–9,3 para Val02 mas valor único para Val01). Deveria ser "20,5--23,2".
2. Val01/Val02: não há dado bruto (summary/replay) em nenhum branch; os valores foram lidos de figuras (commit 8b6a1fd). Conferem com rmse_comparacao.png (6,2; 8,1; 158,4/156,7 → "~157,5" é a média 157,55; 9,2–16,7). Tag: sem fonte de dado primária.
3. l.246-250: "variação de cerca de 7,6% em torno da média" — 7,6% é a amplitude total (máx−mín)/média (odom 7,59; scan 7,41; imu 7,59); em torno da média seria ±3,8%. Número certo, formulação imprecisa.
4. l.388: "pose ≈2–3 cm entre as rotas": Curta = 3,28 (IC 0,80–5,75); Longa 2,25; Loop 2,45. Aproximação aceitável, mas Curta fica acima de 3.
5. Campanha teste1: summary usa traj_topic /pose (não /odom, como nas demais análises); o capítulo não informa isso. Os 2,00/13,90 são portanto de /pose.
6. l.451-455: distância detectada "2,0–2,15 m" pré-correção não verificável; o relatório pós-correção traz 1,98/2,08/2,01 m.

## Problemas de conteúdo
- H3 / QA4 (§8.10 l.624-628): consistente em texto com cap. 1 l.230-239 ("compatível com H3, insuficiente para causalidade") e cap. 7 QA4 / cap. 9 tabela (l.85). Porém o cap. 8 não traz NENHUM número exploratório que sustente "compatível com H3". Dados existentes (RMSE vs ref; CV duração): route01 15,16 cm / 3,9%; route01_controlled 23,78 cm / 3,1%; route01_controlled_reset 178,16 cm / 13,7%; vs. campanha final 3,35 cm / 2,2%. RMSE é muito maior (H3 ok), mas a variabilidade de duração só é claramente maior em um dos três (H3 fala em RMSE E duração). Sugestão: citar os números e a ressalva. Além disso, §8.10 diz que os dados "confundem mecanismo de navegação com variação de pose inicial", mas a §8.5 só discute pose inicial (mecanismo está na §8.3.1, outra campanha).
- "quase uma ordem de grandeza": NÃO existe mais no cap. 8 (a única "ordem de grandeza" é a razão de durações, l.183, correta). Cap. 7 l.159 diz "cerca de cinco vezes" (25/4,76=5,25 sobre o máximo; ~7,5x sobre a média 3,35). Consistente; o cap. 8 diz só "substancialmente abaixo".
- 70% (7/10): não aparece no cap. 8; só no cap. 9 l.167 ("70%, sete em dez ativações individuais, cinco tentativas"). O cap. 8 l.430 diz "ativação sequencial já validada funcionalmente na Seção limitações" — o cap. 9 mostra 70% de sucesso, então "validada" é forte; e l.315-319 relata 0 retries nas 30 réplicas (compatível). Dados dos pilotos (fleet_pilot_*) não foram recontados.
- l.336 "atraso deliberado de 8 s ... Seção~\ref{sec:res_qa1}": a seção QA1 não menciona os 8 s; a fonte é 05_metodologia (sec:fluxo_protocolo, l.230). Referência cruzada errada.
- fig:overlay_teste1 (l.174) NÃO é referenciada no texto (nem fig:overlay_val? — esta é, l.13). Falta \ref{fig:overlay_teste1} na §8.3.1 (a legenda alude à Tabela). Também há 2 figuras em figuras/ (rmse_comparacao.png etc.) não usadas no cap. 8.
- l.77-80: gráfico de sobreposição da campanha final existe (trajectory_overlay.png) mas não entra; ok, declarado.
- Caption da tab. val_rmse diz "todos abaixo da tolerância de 25 cm exceto onde indicado": só Val01 vs baseline excede, e só a nota indica — ok.
- Neves et al. 2026 (neves2026ble): entrada sem páginas/DOI; números da tab. cbsoft_tabela3 (artigo) não foram conferidos (sem acesso ao artigo/dados).

---

# Relatório: 09

# Pesquisa cap. 09 (Conclusão) — 2026-11-16
Obs.: referencias_pdfs/ não contém PDFs das chaves deste capítulo; verificação feita contra o texto do .bib (título/DOI) e contra a descrição dos mesmos trabalhos em 02/03/01. Não foi aberto o texto integral das fontes.

## Citações adicionadas (chave existente)
- l.~267 (AMCL com mapa pré-construído): `\cite{thrun2005}` (Probabilistic Robotics, cobre MCL/AMCL; chave já usada no 02).

## Citação que não sustenta a frase
- l.134-135 `\cite{acm2020badging, bonsignorio2015}` após "que a literatura costuma tratar como sinônimas": o documento da ACM faz justamente a distinção (repeatability / reproducibility / replicability) e não trata como sinônimos; serve para a distinção, não para "costuma tratar como sinônimas". Mesmo padrão em 01 (l.29-31). bonsignorio2015 (editorial sobre pesquisa replicável) pode sustentar a falta de uso consistente, mas isso precisa ser lido. Sugestão: reformular a atribuição (ex.: citar a ACM para a distinção, bonsignorio para a inconsistência de uso).
- l.222-224 `\cite{amigoni2014}` para "comparação estatística concentrada em poucos cenários e pouca variação de condições": o cap. 03 (l.113-121) descreve amigoni2014 como achando comparação estatística fraca, links de código quebrados e comparação só com variantes do próprio sistema; "poucos cenários / pouca variação de condições" não aparece lá. Verificar no texto de Amigoni et al. ou ajustar a descrição.
- l.140-141 `guevaravega2024`: o artigo propõe estrutura de artefatos baseada em badges ACM para experimentos com humanos em engenharia de software (cap. 03 l.283); "badges da ACM aplicados por" é aceitável, mas o domínio não é robótica (nota apenas).
- Sem problema: maset2022 (repetibilidade 3D, cap. 03 l.92), hamer2025 (variabilidade entre execuções SLAM 2D, sem record-replay/RMSE, cap. 03 l.80), amigoni2010 (simulação x hardware complementares), williams2016, fox1997, macenski2023survey (chave diz "survey", título é Regulated Pure Pursuit: só nome da chave), semver, fowler2018, wilson2017, bonsignorio2015 (l.324).

## Afirmação sem referência e sem chave no .bib (candidato verificado)
Nenhum candidato verificado (sem busca web exaustiva). Afirmações sem fonte formal, aceitáveis por serem resultados próprios ou de repositório:
- l.188-192 (tf2_ros/geometry2 limpa buffer com recuo >=1 ns): fonte é código-fonte do geometry2 (jazzy); não há chave no .bib. Sugestão: citar o repositório (URL/commit) como \cite de software se o autor criar entrada.
- l.176-180 Cyclone DDS vs Fast DDS: sem chave para Cyclone DDS/Fast DDS/RMW; só `pardocastellote2003dds`/`omgdds2015` (usados no 04) existem para DDS em geral.
- l.264-265 ground truth externo (mocap, RTK-GPS) e l.308 Roboflow/HuggingFace: sem referência.
- l.320 pacote via `apt` / ecossistema ROS 2: sem referência.

## Número inconsistente
- Taxa 70%: 09 l.166-169 diz "cinco tentativas: 70% (sete em dez ativações individuais)"; 07 l.242-243 diz "falhou em três de dez tentativas". Unidade muda (tentativas x ativações; 5 tentativas x 2 robôs = 10 ativações). Padronizar.
- l.181-183: "duas baterias de cinco tentativas (dez de dez)" contra "20% (uma de cinco)": se tentativas = 5 por bateria e 2 robôs, as ativações seriam 20, não 10; o denominador do controle (cinco) não é comparável ao (dez). Verificar contra os dados.
- l.284: "módulo principal do backend, com mais de 1.700 linhas": backend/main.py tem 1008 linhas (orchestrator main.py 589; soma backend/*.py ~1.270). Não confere.
- 3,35 cm, 4,76 cm, 1,64 cm, 25 cm, N=10: conferem com 08 (l.101-132) e 07.
- Pacotes em 0.1.0: confere (package.xml).
- CI: não há tempo de CI em 01 (só l.289, sem tempo); 09 l.319 diz "executor de CI com GPU e tempo de execução maior que o atual" sem dado do ci.yml (que roda em ubuntu-24.04 com container ROS Jazzy, sem métrica de tempo). A inconsistência com 01 ~l.304 indicada não foi encontrada na versão atual do 01.

## Problemas de conteúdo
- "Painel de Simulação": 09 l.48-49 diz que dispensa terminais para subir a simulação (ok, igual ao 04 l.261-270); 04 l.265 chama o painel de "Missão Coordenada" e 06 l.352 fala em "formação" (L, I, V, barra invertida); 04 l.277 diz "no modo com múltiplos robôs". Resta o rótulo "modo" x "formação" sem definição única; 09 não usa "modo", então nada a corrigir aqui.
- l.54-55 e 315-316: o CI é descrito como validando compilação/xacro/launch; ci.yml também roda py_compile, testes unitários e build do frontend (job checks) — 09 e 01 subestimam o escopo (sem erro factual).
- Epígrafe (01_introducao.tex l.4-6, não neste capítulo): "A ciência avança um funeral de cada vez... adaptado de Max Planck". A frase real de Planck (Autobiografia científica, 1948) é que uma nova verdade científica triunfa porque seus opositores morrem e uma nova geração cresce familiarizada com ela; a parte "não porque os cientistas mudam de ideia" é paráfrase comum, e o complemento sobre "práticas experimentais ao alcance de todos" é invenção do autor, não de Planck. "adaptado de" cobre, mas convém anotar fonte (Planck, Scientific Autobiography and Other Papers, 1949) ou trocar por citação literal. Não verificada contra a fonte primária aqui.

---

# Relatório: bib

# Auditoria de referencias.bib (66 entradas) — somente leitura

Metodo: DOI -> API Crossref (api.crossref.org/works/<doi>) comparada campo a campo (autores, titulo, ano, venue, vol., num., paginas); sem DOI -> pagina do editor/arXiv/repositorio. Citacao: todas as 66 chaves aparecem em chapters/*.tex ou frontmatter/ (nenhuma chave nao citada; nenhuma \cite sem entrada no .bib; sem \nocite).

Resumo: OK = 53 | erro de metadado = 11 | nao encontrado = 1 (neves2026ble) | nao confirmado em fonte primaria (OK parcial) = 1 (quigley2009, ver tabela)

## Problemas graves
| key | status | o que esta errado | valor correto / fonte |
|---|---|---|---|
| borenstein1996 | erro de metadado | `number = {5}` errado; faltam paginas e DOI | number 6, pp. 869--880, doi 10.1109/70.544770 — https://api.crossref.org/works/10.1109/70.544770 |
| neves2026ble | nao encontrado | Titulo/autores/evento (CBSoft 2026, SBES Trilha de Ideias Inovadoras) nao encontrados em SOL/SBC nem busca web; sem pages/address/doi. O SBES 2025 (sol.sbc.org.br/index.php/sbes/article/view/37070) traz outro trabalho do grupo (Araujo & Miranda, "Mobile Robotics for Throughput Testing in a Reconfigurable Test Environment", pp. 859--864), nao este | nao confirmado — confirmar com os autores se ja foi aceito/publicado; senao tratar como "no prelo"/"em submissao" |
| quigley2009 | erro de metadado (provavel) | Falta autor "Berger, Eric" (lista de 9 autores: Quigley, Conley, Gerkey, Faust, Foote, Leibs, Berger, Wheeler, Ng). `volume={3}`, `pages={5}` — numero real e "3.2" (vol. 3, no. 3.2, p. 5), nao confirmado em PDF primario (download falhou) | existencia confirmada (workshop ICRA 2009, Kobe); autor Berger: fonte secundaria (pagina de curso McGill, via busca). Conferir em https://www.willowgarage.com/papers/ros-open-source-robot-operating-system ou no PDF |
| sturm2012 | erro de metadado | falta `pages` e `address` | pp. 573--580, Vilamoura, Portugal — https://doi.org/10.1109/IROS.2012.6385773 (Crossref: P 573-580) |
| garlan1995architectural | erro de metadado | faltam paginas e DOI | pp. 17--26, doi 10.1109/52.469757 — https://api.crossref.org/works/10.1109/52.469757 |
| koenig2004gazebo | erro de metadado (omissao) | falta DOI | doi 10.1109/IROS.2004.1389727 (vol. 3, pp. 2149--2154 conferem) |
| burgard2000exploration | erro de metadado (omissao) | falta DOI e address | doi 10.1109/ROBOT.2000.844100 (vol. 1, pp. 476--481 conferem; Crossref nao da local) |
| jakobi1995 | erro de metadado | faltam `pages` e `address` | pp. 704--720 (Crossref), doi confere; address nao confirmado |
| amigoni2014 | OK com ressalva | Crossref data issued = 2013 (online); bib diz 2014 | confirmar no Springer (https://doi.org/10.1007/978-3-319-00272-9_3) qual ano de capa usar; titulo/autores/paginas conferem |
| runeson2009 | OK com ressalva | Crossref issued 2008 (online first); 2009 e o ano do vol. 14(2) — correto | manter 2009 |
| gerkey2003playerstage | OK | confere: ICAR 2003, Coimbra, pp. 317--323 (https://robotics.usc.edu/publications/288). Sem DOI | — |
| macenski2023survey | OK (chave enganosa) | chave diz "survey", obra e "Regulated Pure Pursuit"; falta `number = {6}` (Crossref: v47 n6) | doi confere |

## Todas as entradas
| key | status | what is wrong | correct value / source |
|---|---|---|---|
| macenski2020marathon | OK | — | Crossref 10.1109/IROS45743.2020.9341207 |
| macenski2022ros2 | OK | — | Crossref (Steven no Crossref; Steve na obra, aceitavel) |
| borenstein1996 | erro de metadado | ver acima | ver acima |
| macenski2021slam | OK | — | JOSS 6(61) 2783 |
| quigley2009 | erro de metadado (provavel) | ver acima | ver acima |
| maset2022 | OK | — | Robotics 11(3) 54 |
| hamer2025 | OK | — | JBCS 31(1) 229-261 |
| siegwart2011 | OK | ISBN, 2a ed., MIT Press 2011 conferem (varias livrarias; pagina do editor nao aberta) | — |
| thrun2005 | OK (nao reaberto na MIT Press) | ISBN 978-0-262-20162-9 plausivel | nao confirmado em fonte primaria |
| bailey2006 | OK | — | MRA 13(3) 108-117 |
| colledanchise2018 | OK | — | CRC Press, doi confere |
| elfes1989 | OK | — | Computer 22(6) 46-57 |
| kalman1960 | OK | — | J. Basic Eng. 82(1) 35-45 |
| williams2016 | OK | — | ICRA 2016 pp. 1433-1440 |
| macenski2023survey | OK (falta number=6; chave enganosa) | ver acima | — |
| fox1997 | OK | — | MRA 4(1) 23-33 |
| coulter1992 | OK | — | CMU-RI-TR-92-01, jan. 1992 (https://www.ri.cmu.edu/publications/implementation-of-the-pure-pursuit-path-tracking-algorithm/) |
| durrantwhyte2006 | OK | — | MRA 13(2) 99-110 |
| amigoni2010 | OK | `doi` com `\_` escapado dentro do campo (ver formatacao) | Crossref confere, vol. 314 da serie nao verificado |
| amigoni2014 | OK com ressalva (ano 2013 vs 2014) | ver acima | — |
| kohlbrecher2011 | OK | — | SSRR 2011 pp. 155-160 |
| grisetti2007 | OK | — | T-RO 23(1) 34-46 |
| albonico2023 | OK | — | JSS 197, 111574 |
| timperley2024 | OK | — | EMSE 29(3) 57 |
| santos2024 | OK | booktitle em ingles misto ("Anais do 38th Brazilian Symposium...") | Crossref: "Anais do XXXVIII Simposio Brasileiro de Engenharia de Software (SBES 2024)", pp. 775-781 |
| guevaravega2024 | OK | sem publisher (opcional) | JSS 218, 112187 |
| acm2020badging | erro de metadado (formato) | @misc com `howpublished`+`note={Accessed: ...}` em ingles; abntex2 espera `url` + `urldate`/"Acesso em: 17 ago. 2026"; sem publisher/local. Pagina existe (resultados de busca; WebFetch retornou 403 do acm.org) | titulo da pagina "Artifact Review and Badging – Current" (v1.1, 24-08-2020) — https://www.acm.org/publications/policies/artifact-review-and-badging-current; data de acesso nao verificavel por mim |
| bonsignorio2015 | OK | — | MRA 22(3) 32-35 |
| toris2015 | OK | — | IROS 2015 pp. 4530-4537 |
| takaya2016 | OK | — | ICSTCC 2016 pp. 96-101 |
| verma2021 | OK | — | JIRS 102(1) 10 |
| cortes2017 | OK | — | SICE JCMSI 10(6) 495-503 |
| gielis2022 | OK | falta `number={4}` (opcional) | Crossref v3 n4 |
| lampe2023 | OK | — | ITSC 2023 pp. 2719-2725 |
| romero2023 | OK | — | TNSM 20(4) 4216-4230 |
| carroll2021 | OK | — | ICRA 2021 pp. 4026-4032 |
| yan2023 | OK | — | Front. Neurorobot. 17, 1179033 |
| gerkey2004 | OK | — | IJRR 23(9) 939-954 |
| farinelli2004 | OK | titulo: bib "Multi-Robot Systems", IEEE/Crossref "Multirobot Systems" | grafia do editor |
| parker1998 | OK | — | T-RA 14(2) 220-240 |
| sikand2021 | OK | — | IROS 2021 pp. 406-412 |
| singhal2017 | erro de metadado (formato) | arXiv confirmado (titulo, 6 autores, 27-jun-2017, DOI 10.48550/arXiv.1706.08931; sem publicacao em periodico listada). @misc sem urldate; `howpublished` URL + `note` | usar `eprint`/`archivePrefix` ou url+urldate — https://arxiv.org/abs/1706.08931 |
| alonsomora2017 | OK | — | IJRR 36(9) 1000-1021 |
| khamis2015 | OK | `doi` com `_` sem escape | Crossref confere (serie vol. 604) |
| korsah2013 | OK | — | IJRR 32(12) 1495-1512 |
| dissanayake2001 | OK | — | T-RA 17(3) 229-241 |
| koenig2004gazebo | erro de metadado (falta DOI) | ver acima | ver acima |
| eugster2003pubsub | OK | — | CSUR 35(2) 114-131 |
| pardocastellote2003dds | OK | — | ICDCSW 2003 pp. 200-206 (Crossref sem ano; 2003 correto) |
| garlan1995architectural | erro de metadado | ver acima | ver acima |
| omgdds2015 | erro de metadado (formato) | @misc sem publisher/address nem urldate; URL responde 200 (https://www.omg.org/spec/DDS/1.4/); "formal/2015-04-10" nao reconferido na pagina | adicionar `publisher={Object Management Group}`, `address`, urldate; confirmar numero formal |
| gerkey2003playerstage | OK | ver acima | — |
| fox2006multirobot | OK | — | Proc. IEEE 94(7) 1325-1339 |
| burgard2000exploration | erro de metadado | ver acima | ver acima |
| neves2026ble | nao encontrado | ver acima | ver acima |
| wohlin2012 | OK | — | Springer, doi confere |
| runeson2009 | OK | ver acima | — |
| sturm2012 | erro de metadado | ver acima | ver acima |
| zhang2018trajectory | OK | — | IROS 2018 pp. 7244-7251 |
| jakobi1995 | erro de metadado | ver acima | ver acima |
| afzal2020 | OK (formato) | arXiv:2004.07368 existe; autores/titulo/ano 2020 conferem (https://arxiv.org/abs/2004.07368); DOI 10.48550 nao resolve no Crossref (e DataCite, normal). @misc com `howpublished` "arXiv:..." sem url/urldate; sem venue publicado | usar eprint/url+urldate |
| borji2018 | OK | — | IVC 69, 1-8 |
| wilson2014 | OK | — | PLoS Biol 12(1) e1001745 (13 autores conferem) |
| wilson2017 | OK | — | PLoS CB 13(6) e1005510 |
| semver | OK (formato) | site responde 200 (https://semver.org/); autor/ano 2013 nao reconferidos na pagina; mistura `howpublished` + `note` PT "Acesso em: 23 out. 2026" (inconsistente com acm2020badging em ingles); sem `urldate` | padronizar para url + urldate |
| fowler2018 | OK | sem ISBN; Pearson/InformIT: publicado 20-nov-2018, copyright 2019; ISBN 978-0-13-475759-9 (https://www.informit.com/title/0134757599) | ano 2018 aceitavel |

## Formatacao abntex2 (geral)
- DOI com underscore: amigoni2010/2014 usam `\_` dentro de `doi={}` (pode quebrar o link/`\url`), khamis2015 e jakobi1995 usam `_` cru — padronizar (abntex2 normalmente imprime `\url{}`; testar compilacao).
- @misc (acm2020badging, singhal2017, omgdds2015, afzal2020, semver): usam `howpublished={\url{}}`+`note`; faltam `urldate`/data de acesso padronizada em PT, `publisher`/`address` onde aplicavel.
- Entradas sem `publisher`/`address` (aceitavel, mas abntex2-alf imprime "[S.l.: s.n.]" em proceedings): sturm2012, zhang2018trajectory? (tem so pages, sem address), jakobi1995, burgard2000exploration, quigley2009 (sem publisher), koenig2004gazebo.
- Chaves com tipos corretos (inproceedings/article/book/incollection/techreport); sem entrada com tipo errado. Chave `macenski2023survey` nome enganoso.
- Chaves nao citadas: nenhuma.
