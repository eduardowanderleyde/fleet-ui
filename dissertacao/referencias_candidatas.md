# Referências candidatas — Orquestração/Coordenação Multi-Robô

Levantamento feito em 2026-09-25 para expandir o eixo "Sistemas de Orquestração
para Frotas" (`chapters/03_trabalhos_relacionados.tex`, `\label{sec:rel_frota}`)
e a fundamentação teórica correlata em `chapters/02_fundamentacao.tex`.
**Nenhuma entrada foi adicionada a `referencias.bib` — este arquivo é só para
revisão do autor.** As 29 chaves já existentes em `referencias.bib` foram
conferidas antes da busca; nenhuma referência abaixo duplica uma chave já
presente.

> **Atualização 2026-09-30:** 15 dos 18 candidatos abaixo (itens 1–10, 14, 16,
> 18, mais os itens 3 e 5 usados em outro trecho do capítulo) foram promovidos
> para `referencias.bib` e citados em `chapters/03_trabalhos_relacionados.tex`
> (seções "Sistemas de Orquestração para Frotas" e "Engenharia de Software").
> Os itens 11 (Athira et al., 2024), 12 (Rizk et al., 2019) e 17 (Ren & Beard,
> 2005) **não** foram promovidos nesta rodada — a própria nota de relevância de
> cada um já apontava `chapters/02_fundamentacao.tex` como destino mais
> apropriado, fora do escopo desta rodada (que tratou só do capítulo 3). Um
> novo candidato (item 21, Parte 4) foi adicionado nesta rodada e ainda não
> promovido.

## Resumo

- **Lista original (7 itens recebidos de outra IA):** 7/7 **CONFIRMADOS** como
  artigos reais. Nenhum foi descartado por invenção — mas em 2 casos os
  metadados da tabela original estavam incompletos/levemente errados e foram
  corrigidos abaixo (autoria do item 2, título completo do item 7).
- **Novas referências encontradas (Passo 2):** 11 candidatos adicionais, todos
  **CONFIRMADOS** contra fonte primária (DOI/IEEE Xplore/ACM DL/Springer/arXiv).
- **Total de candidatos confirmados neste arquivo:** 18.

---

## Parte 1 — Verificação da lista recebida (7 itens)

### 1. Multi-Robot Coordination Analysis, Taxonomy, Challenges and Future Scope
- **Status:** CONFIRMADO
- **Autores:** Janardan Kumar Verma, Virender Ranga
- **Ano:** 2021
- **Venue:** Journal of Intelligent & Robotic Systems, vol. 102, artigo 10
- **DOI:** 10.1007/s10846-021-01378-2
- **Relevância:** Taxonomia de coordenação multi-robô organizada por 6 dimensões
  (comunicação, planejamento, arquitetura de controle, escalabilidade, decisão).
  Serve como referência de enquadramento teórico logo no início da
  Seção "Sistemas de Orquestração para Frotas" (`sec:rel_frota`), complementando
  a discussão de arquitetura de frota já presente.

```bibtex
@article{verma2021,
  author    = {Verma, Janardan Kumar and Ranga, Virender},
  title     = {Multi-Robot Coordination Analysis, Taxonomy, Challenges and Future Scope},
  journal   = {Journal of Intelligent \& Robotic Systems},
  year      = {2021},
  volume    = {102},
  number    = {1},
  pages     = {10},
  publisher = {Springer},
  doi       = {10.1007/s10846-021-01378-2}
}
```

### 2. Coordinated Control of Multi-Robot Systems: A Survey
- **Status:** CONFIRMADO (autoria da tabela original estava incompleta — o
  candidato listava só "J. Cortés (2017)", mas o artigo é de dois autores)
- **Autores:** Jorge Cortés, Magnus Egerstedt
- **Ano:** 2017
- **Venue:** SICE Journal of Control, Measurement, and System Integration,
  vol. 10, n. 6, pp. 495–503
- **URL:** http://terrano.ucsd.edu/jorge/publications/data/2017_CoEg-jcmsi.pdf
  (ver também ADS: https://ui.adsabs.harvard.edu/abs/2017JCMSI..10..495C)
- **Relevância:** Survey de referência sobre controle/coordenação descentralizada
  em sistemas multi-robô (formação de geometria, algoritmos baseados em
  descida de gradiente sobre custos de time). Bom contraponto teórico ao
  enfoque mais aplicado (ROS 2) já citado na Seção 3.4.

```bibtex
@article{cortes2017,
  author    = {Cort{\'e}s, Jorge and Egerstedt, Magnus},
  title     = {Coordinated Control of Multi-Robot Systems: A Survey},
  journal   = {SICE Journal of Control, Measurement, and System Integration},
  year      = {2017},
  volume    = {10},
  number    = {6},
  pages     = {495--503},
  doi       = {10.9746/jcmsi.10.495}
}
```

### 3. A Critical Review of Communications in Multi-robot Systems
- **Status:** CONFIRMADO
- **Autores:** Jennifer Gielis, Ajay Shankar, Amanda Prorok
- **Ano:** 2022
- **Venue:** Current Robotics Reports, vol. 3, pp. 213–225
- **DOI:** 10.1007/s43154-022-00090-9 (preprint: arXiv:2206.09484)
- **Relevância:** Cobre comunicação em sistemas multi-robô sob duas óticas
  (aplicações robóticas vs. tecnologias de rede) — conecta-se ao ponto de
  mismatch de QoS entre coletor/orquestrador já discutido em
  `sec:rel_frota` (linha ~230 do capítulo 3).

```bibtex
@article{gielis2022,
  author    = {Gielis, Jennifer and Shankar, Ajay and Prorok, Amanda},
  title     = {A Critical Review of Communications in Multi-robot Systems},
  journal   = {Current Robotics Reports},
  year      = {2022},
  volume    = {3},
  pages     = {213--225},
  publisher = {Springer},
  doi       = {10.1007/s43154-022-00090-9}
}
```

### 4. RobotKube: Orchestrating Large-Scale Cooperative Multi-Robot Systems with Kubernetes and ROS
- **Status:** CONFIRMADO
- **Autores:** Bastian Lampe, Lennart Reiher, Lukas Zanger, Timo Woopen,
  Raphael van Kempen, Lutz Eckstein
- **Ano:** 2023
- **Venue:** 2023 IEEE 26th International Conference on Intelligent
  Transportation Systems (ITSC), pp. 2719–2725
- **DOI:** 10.1109/ITSC57777.2023.10422370 (preprint: arXiv:2308.07053)
- **Relevância:** Diretamente comparável ao framework de orquestração da
  dissertação — usa Kubernetes+ROS para orquestrar componentes de software em
  sistemas multi-robô cooperativos de larga escala, com detector de eventos e
  gerenciador de aplicação. Referência forte para a subseção "Arquiteturas de
  Frota em ROS 2" (`sec:rel_frota`), como contraponto de orquestração baseada
  em infraestrutura de contêineres versus a abordagem do framework proposto.

```bibtex
@inproceedings{lampe2023,
  author    = {Lampe, Bastian and Reiher, Lennart and Zanger, Lukas and Woopen, Timo and van Kempen, Raphael and Eckstein, Lutz},
  title     = {{RobotKube}: Orchestrating Large-Scale Cooperative Multi-Robot Systems with {K}ubernetes and {ROS}},
  booktitle = {2023 IEEE 26th International Conference on Intelligent Transportation Systems (ITSC)},
  year      = {2023},
  pages     = {2719--2725},
  publisher = {IEEE},
  doi       = {10.1109/ITSC57777.2023.10422370}
}
```

### 5. OROS: Online Operation and Orchestration of Collaborative Robots using 5G
- **Status:** CONFIRMADO
- **Autores:** Arnau Romero, Carmen Delgado, Lanfranco Zanzi, Xi Li,
  Xavier Costa-Pérez
- **Ano:** 2023
- **Venue:** IEEE Transactions on Network and Service Management, vol. 20,
  n. 4, pp. 4216–4230
- **DOI:** 10.1109/TNSM.2023.3281976 (preprint: arXiv:2205.03256)
- **Relevância:** Orquestração conjunta de robôs ROS + rede 5G, validada com
  ROS/Gazebo. Tangencial ao tema central (orienta-se mais a infraestrutura de
  rede do que a experimentos de navegação), mas relevante como exemplo de
  "orquestração" no sentido amplo de coordenação de recursos robô+infra —
  pode entrar como referência secundária/contraste na introdução da Seção 3.4.

```bibtex
@article{romero2023,
  author    = {Romero, Arnau and Delgado, Carmen and Zanzi, Lanfranco and Li, Xi and Costa-P{\'e}rez, Xavier},
  title     = {{OROS}: Online Operation and Orchestration of Collaborative Robots using {5G}},
  journal   = {IEEE Transactions on Network and Service Management},
  year      = {2023},
  volume    = {20},
  number    = {4},
  pages     = {4216--4230},
  publisher = {IEEE},
  doi       = {10.1109/TNSM.2023.3281976}
}
```

### 6. The Resh Programming Language for Multirobot Orchestration
- **Status:** CONFIRMADO
- **Autores:** Martin D. Carroll, Kedar S. Namjoshi, Itai Segall (Nokia Bell Labs)
- **Ano:** 2021
- **Venue:** 2021 IEEE International Conference on Robotics and Automation
  (ICRA), pp. 4026–4032
- **DOI:** 10.1109/ICRA48506.2021.9561133 (preprint: arXiv:2103.13921)
- **Relevância:** Linguagem de programação declarativa dedicada à orquestração
  de times heterogêneos de robôs, com runtime que abstrai lógica de
  sequenciamento de tarefas. Bom contraste conceitual: mostra uma abordagem de
  "orquestração como linguagem" versus a abordagem de "orquestração como
  framework/ferramenta" da dissertação — cabe na discussão de trabalhos
  relacionados de `sec:rel_frota`.

```bibtex
@inproceedings{carroll2021,
  author    = {Carroll, Martin D. and Namjoshi, Kedar S. and Segall, Itai},
  title     = {The Resh Programming Language for Multirobot Orchestration},
  booktitle = {2021 IEEE International Conference on Robotics and Automation (ICRA)},
  year      = {2021},
  pages     = {4026--4032},
  publisher = {IEEE},
  doi       = {10.1109/ICRA48506.2021.9561133}
}
```

### 7. Multi-robot cooperative autonomous exploration via task allocation
- **Status:** CONFIRMADO (título completo é mais longo do que o da tabela
  original: "... in terrestrial environments")
- **Autores:** Xiangda Yan, Zhe Zeng, Keyan He, Huajie Hong
- **Ano:** 2023
- **Venue:** Frontiers in Neurorobotics, vol. 17, artigo 1179033
- **DOI:** 10.3389/fnbot.2023.1179033
- **Relevância:** Estratégia de exploração cooperativa terrestre com alocação
  de tarefas e recuperação de falhas de robôs (self-healing). Робôs terrestres
  (não aéreos), alinhado ao escopo pedido — conecta-se à subseção "Arquiteturas
  de Frota em ROS 2" como exemplo de alocação dinâmica de tarefas.

```bibtex
@article{yan2023,
  author    = {Yan, Xiangda and Zeng, Zhe and He, Keyan and Hong, Huajie},
  title     = {Multi-robot cooperative autonomous exploration via task allocation in terrestrial environments},
  journal   = {Frontiers in Neurorobotics},
  year      = {2023},
  volume    = {17},
  pages     = {1179033},
  doi       = {10.3389/fnbot.2023.1179033}
}
```

---

## Parte 2 — Novas referências encontradas (Passo 2)

### 8. A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems
- **Status:** CONFIRMADO
- **Autores:** Brian P. Gerkey, Maja J. Matarić
- **Ano:** 2004
- **Venue:** International Journal of Robotics Research, vol. 23, n. 9,
  pp. 939–954
- **DOI:** 10.1177/0278364904045564
- **Relevância:** Referência fundacional (>1700 citações) para o problema de
  alocação de tarefas multi-robô (MRTA) — taxonomia domain-independent citada
  por praticamente todo trabalho subsequente da área, incluindo Verma&Ranga
  (item 1) e Khamis et al. (item 13). Essencial como base teórica antes de
  discutir arquiteturas de despacho de tarefas em `sec:rel_frota`.

```bibtex
@article{gerkey2004,
  author    = {Gerkey, Brian P. and Matari{\'c}, Maja J.},
  title     = {A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems},
  journal   = {The International Journal of Robotics Research},
  year      = {2004},
  volume    = {23},
  number    = {9},
  pages     = {939--954},
  doi       = {10.1177/0278364904045564}
}
```

### 9. Multi-Robot Systems: A Classification Focused on Coordination
- **Status:** CONFIRMADO
- **Autores:** Alessandro Farinelli, Luca Iocchi, Daniele Nardi
- **Ano:** 2004
- **Venue:** IEEE Transactions on Systems, Man, and Cybernetics, Part B, vol. 34,
  n. 5, pp. 2015–2028
- **DOI:** 10.1109/TSMCB.2004.832155
- **Relevância:** Taxonomia clássica de coordenação multi-robô (cooperação
  fraca/forte, consciência de outros robôs, arquitetura centralizada vs.
  distribuída) — complementa diretamente a taxonomia de Verma&Ranga (item 1)
  com uma perspectiva mais antiga e amplamente citada; útil para historicizar
  a discussão de coordenação centralizada vs. descentralizada.

```bibtex
@article{farinelli2004,
  author    = {Farinelli, Alessandro and Iocchi, Luca and Nardi, Daniele},
  title     = {Multi-Robot Systems: A Classification Focused on Coordination},
  journal   = {IEEE Transactions on Systems, Man, and Cybernetics, Part B (Cybernetics)},
  year      = {2004},
  volume    = {34},
  number    = {5},
  pages     = {2015--2028},
  publisher = {IEEE},
  doi       = {10.1109/TSMCB.2004.832155}
}
```

### 10. ALLIANCE: An Architecture for Fault Tolerant Multirobot Cooperation
- **Status:** CONFIRMADO
- **Autores:** Lynne E. Parker
- **Ano:** 1998
- **Venue:** IEEE Transactions on Robotics and Automation, vol. 14, n. 2,
  pp. 220–240
- **DOI:** 10.1109/70.681242
- **Relevância:** Arquitetura clássica (behavior-based, totalmente distribuída)
  para cooperação tolerante a falhas em times heterogêneos de robôs. Referência
  histórica importante para contextualizar arquiteturas de coordenação
  descentralizadas antes da era ROS — âncora útil na subseção
  "Comportamento Determinístico em Sistemas Multi-Robô" (`sec:rel_frota`,
  linha ~162), que discute robustez/determinismo em frotas.

```bibtex
@article{parker1998,
  author    = {Parker, Lynne E.},
  title     = {{ALLIANCE}: An Architecture for Fault Tolerant Multirobot Cooperation},
  journal   = {IEEE Transactions on Robotics and Automation},
  year      = {1998},
  volume    = {14},
  number    = {2},
  pages     = {220--240},
  publisher = {IEEE},
  doi       = {10.1109/70.681242}
}
```

### 11. A Systematic Literature Review on Multi-Robot Task Allocation
- **Status:** CONFIRMADO
- **Autores:** Athira K. A., Divya Udayan J., Umashankar Subramaniam
- **Ano:** 2024 (publicado 2025 conforme issue da ACM CSUR)
- **Venue:** ACM Computing Surveys, vol. 57, n. 3
- **DOI:** 10.1145/3700591
- **Relevância:** Revisão sistemática recente (a mais atual do lote) sobre
  MRTA, cobrindo abordagens de alocação de tarefas mais modernas — bom
  complemento atualizado ao clássico Gerkey&Matarić (item 8) e ao survey de
  Khamis et al. de 2015 (item 13), fechando a lacuna temporal até 2024.

```bibtex
@article{athira2024,
  author    = {Athira, K. A. and Divya Udayan, J. and Subramaniam, Umashankar},
  title     = {A Systematic Literature Review on Multi-Robot Task Allocation},
  journal   = {ACM Computing Surveys},
  year      = {2024},
  volume    = {57},
  number    = {3},
  doi       = {10.1145/3700591}
}
```

### 12. Cooperative Heterogeneous Multi-Robot Systems: A Survey
- **Status:** CONFIRMADO
- **Autores:** Yara Rizk, Mariette Awad, Edward W. Tunstel
- **Ano:** 2019
- **Venue:** ACM Computing Surveys, vol. 52, n. 2, artigo 29 (31 pp.)
- **DOI:** 10.1145/3303848
- **Relevância:** Survey amplo sobre cooperação em times heterogêneos
  (UAV+UGV+humanoides), cobrindo decomposição de tarefas, formação de
  coalizões, alocação de tarefas, percepção e planejamento/controle
  multiagente — bom pano de fundo teórico para a fundamentação (cap. 02) antes
  de entrar no caso específico ROS 2/terrestre da dissertação.

```bibtex
@article{rizk2019,
  author    = {Rizk, Yara and Awad, Mariette and Tunstel, Edward W.},
  title     = {Cooperative Heterogeneous Multi-Robot Systems: A Survey},
  journal   = {ACM Computing Surveys},
  year      = {2019},
  volume    = {52},
  number    = {2},
  pages     = {29},
  doi       = {10.1145/3303848}
}
```

### 13. Multi-robot Task Allocation: A Review of the State-of-the-Art
- **Status:** CONFIRMADO
- **Autores:** Alaa Khamis, Ahmed Hussein, Ahmed Elmogy
- **Ano:** 2015
- **Venue:** Capítulo em *Cooperative Robots and Sensor Networks*, série
  Studies in Computational Intelligence, vol. 604, pp. 31–51, Springer
- **DOI:** 10.1007/978-3-319-18299-5_2
- **Relevância:** Revisão de MRTA de meio de década — complementa
  cronologicamente Gerkey&Matarić (2004, item 8) e o survey mais recente de
  Athira et al. (2024, item 11), formando uma linha do tempo completa de MRTA
  para citar em sequência.

```bibtex
@incollection{khamis2015,
  author    = {Khamis, Alaa and Hussein, Ahmed and Elmogy, Ahmed},
  title     = {Multi-robot Task Allocation: A Review of the State-of-the-Art},
  booktitle = {Cooperative Robots and Sensor Networks},
  series    = {Studies in Computational Intelligence},
  volume    = {604},
  year      = {2015},
  pages     = {31--51},
  publisher = {Springer},
  doi       = {10.1007/978-3-319-18299-5_2}
}
```

### 14. Robofleet: Open Source Communication and Management for Fleets of Autonomous Robots
- **Status:** CONFIRMADO
- **Autores:** Kavan Singh Sikand, Logan Zartman, Sadegh Rabiee, Joydeep Biswas
- **Ano:** 2021
- **Venue:** 2021 IEEE/RSJ International Conference on Intelligent Robots and
  Systems (IROS), pp. 406–412
- **DOI:** 10.1109/IROS51168.2021.9635830 (preprint: arXiv:2103.06993)
- **Relevância:** Sistema open-source leve para comunicação/monitoramento/
  tasking remoto de frotas de robôs ROS, com foco em resiliência de rede e
  segurança — muito próximo em espírito ao framework de orquestração da
  dissertação (mesmo ecossistema ROS, mesmo problema de gestão de frota
  terrestre). Um dos candidatos mais diretamente comparáveis ao trabalho
  proposto; forte candidato para `sec:rel_frota`.

```bibtex
@inproceedings{sikand2021,
  author    = {Sikand, Kavan Singh and Zartman, Logan and Rabiee, Sadegh and Biswas, Joydeep},
  title     = {Robofleet: Open Source Communication and Management for Fleets of Autonomous Robots},
  booktitle = {2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
  year      = {2021},
  pages     = {406--412},
  publisher = {IEEE},
  doi       = {10.1109/IROS51168.2021.9635830}
}
```

### 15. Managing a Fleet of Autonomous Mobile Robots (AMR) using Cloud Robotics Platform
- **Status:** CONFIRMADO (publicado como preprint arXiv; não localizada versão
  de conferência com DOI formal — tratar com atenção extra na citação)
- **Autores:** Aniruddha Singhal, Nishant Kejriwal, Prasun Pallav,
  Soumyadeep Choudhury, Rajesh Sinha, Swagat Kumar (TCS Research)
- **Ano:** 2017
- **Venue:** arXiv:1706.08931 [cs.RO]
- **URL:** https://arxiv.org/abs/1706.08931
- **Relevância:** Gestão de frota de AMRs via plataforma cloud robotics —
  aborda diretamente "fleet management system", termo central do eixo
  pedido. Nota: por ser só preprint arXiv (sem confirmação de publicação
  revisada por pares encontrada), sugiro citar com ressalva ou buscar se foi
  publicado formalmente antes de usar.

```bibtex
@misc{singhal2017,
  author       = {Singhal, Aniruddha and Kejriwal, Nishant and Pallav, Prasun and Choudhury, Soumyadeep and Sinha, Rajesh and Kumar, Swagat},
  title        = {Managing a Fleet of Autonomous Mobile Robots (AMR) using Cloud Robotics Platform},
  year         = {2017},
  howpublished = {\url{https://arxiv.org/abs/1706.08931}},
  note         = {arXiv:1706.08931 [cs.RO]}
}
```

### 16. Multi-robot Formation Control and Object Transport in Dynamic Environments via Constrained Optimization
- **Status:** CONFIRMADO
- **Autores:** Javier Alonso-Mora, Stuart Baker, Daniela Rus
- **Ano:** 2017
- **Venue:** International Journal of Robotics Research, vol. 36, n. 9,
  pp. 1000–1021
- **DOI:** 10.1177/0278364917719333
- **Relevância:** Controle de formação multi-robô via otimização com restrições,
  incluindo planejamento local e global — cobre o subtema "formação de robôs"
  pedido explicitamente no escopo, que não está representado no
  `referencias.bib` atual.

```bibtex
@article{alonsomora2017,
  author    = {Alonso-Mora, Javier and Baker, Stuart and Rus, Daniela},
  title     = {Multi-robot Formation Control and Object Transport in Dynamic Environments via Constrained Optimization},
  journal   = {The International Journal of Robotics Research},
  year      = {2017},
  volume    = {36},
  number    = {9},
  pages     = {1000--1021},
  doi       = {10.1177/0278364917719333}
}
```

### 17. Consensus Seeking in Multiagent Systems Under Dynamically Changing Interaction Topologies
- **Status:** CONFIRMADO
- **Autores:** Wei Ren, Randal W. Beard
- **Ano:** 2005
- **Venue:** IEEE Transactions on Automatic Control, vol. 50, n. 5, pp. 655–661
- **DOI:** 10.1109/TAC.2005.846556
- **Relevância:** Referência fundacional de teoria de controle para consenso
  em sistemas multiagente sob topologias de comunicação variáveis — base
  matemática citada por praticamente toda a literatura de coordenação
  descentralizada/formação (inclusive Cortés&Egerstedt, item 2, e
  Alonso-Mora et al., item 16). Mais teórica que os demais itens; útil para o
  capítulo de fundamentação (cap. 02) se o autor quiser aprofundar a base de
  controle por trás da coordenação descentralizada.

```bibtex
@article{ren2005,
  author    = {Ren, Wei and Beard, Randal W.},
  title     = {Consensus Seeking in Multiagent Systems Under Dynamically Changing Interaction Topologies},
  journal   = {IEEE Transactions on Automatic Control},
  year      = {2005},
  volume    = {50},
  number    = {5},
  pages     = {655--661},
  publisher = {IEEE},
  doi       = {10.1109/TAC.2005.846556}
}
```

### 18. A Comprehensive Taxonomy for Multi-Robot Task Allocation
- **Status:** CONFIRMADO
- **Autores:** G. Ayorkor Korsah, Anthony Stentz, M. Bernardine Dias
- **Ano:** 2013
- **Venue:** International Journal of Robotics Research, vol. 32, n. 12,
  pp. 1495–1512
- **DOI:** 10.1177/0278364913496484
- **Relevância:** Estende a taxonomia de Gerkey&Matarić (item 8) para
  problemas de alocação com dependências de tarefas e restrições de
  interrelação (in-schedule dependencies) — referência muito citada que fecha
  a lacuna entre 2004 (item 8) e os surveys mais recentes (itens 11, 13).
  Apareceu de forma incidental nas buscas acima e vale a pena incluir dado o
  alto número de citações e a proximidade temática.

```bibtex
@article{korsah2013,
  author    = {Korsah, G. Ayorkor and Stentz, Anthony and Dias, M. Bernardine},
  title     = {A Comprehensive Taxonomy for Multi-Robot Task Allocation},
  journal   = {The International Journal of Robotics Research},
  year      = {2013},
  volume    = {32},
  number    = {12},
  pages     = {1495--1512},
  doi       = {10.1177/0278364913496484}
}
```

---

## Itens pesquisados mas NÃO incluídos (para registro)

- **Open-RMF (Open Robotics Middleware Framework):** projeto de código aberto
  amplamente relevante para o tema (interoperabilidade de múltiplas frotas
  ROS 2), mas não foi localizado um artigo acadêmico primário (com DOI) que o
  descreva formalmente — apenas documentação, blogs e um artigo de terceiros
  ("Behavioral Analysis of ROS motion planners integrated with RMF", IEEE,
  10.1109/... — esse sim é um artigo real, mas avalia RMF em vez de
  apresentá-lo). Se o autor quiser citar Open-RMF, recomendo citar via
  documentação oficial/repositório (`@misc`) em vez de forçar uma citação de
  artigo, ou usar esse artigo de análise comportamental como citação indireta.

---

## Parte 3 — Fundamentação teórica (`chapters/02_fundamentacao.tex`), levantamento de 2026-09-30

Levantamento feito para embasar duas afirmações do capítulo de fundamentação que
hoje não têm citação: a cadeia de referenciais TF do ROS~2
(`\label{sec:cadeia_tf}`) e as especificações do LiDAR RPLIDAR S2
(`subsection` "LiDAR 2D (RPLIDAR S2)", `\label{sec:sensores}`). Nenhuma chave
abaixo existe em `referencias.bib`; nenhuma foi adicionada ao capítulo.

### 19. tf: The transform library
- **Status:** CONFIRMADO contra fonte primária (IEEE Xplore, DOI resolvido)
- **Autor:** Tully Foote
- **Ano:** 2013
- **Venue:** 2013 IEEE International Conference on Technologies for Practical
  Robot Applications (TePRA), pp. 1–6
- **DOI:** 10.1109/TePRA.2013.6556373 (ISSN 2325-0526)
- **Relevância:** É a referência canônica da biblioteca `tf`/`tf2`, que
  implementa exatamente a cadeia de referenciais `map` → `odom` →
  `base_link` descrita na Seção "A Cadeia TF no ROS~2" (`sec:cadeia_tf`) —
  hoje essa seção inteira não tem nenhuma citação. O abstract do artigo
  descreve literalmente o problema que a seção apresenta: manter o controle
  de referenciais de coordenadas em todo o sistema para que cada componente
  confie que os dados estão no referencial esperado, sem precisar conhecer
  todos os referenciais do sistema — e cita o rastreamento incorreto de
  transformações como fonte comum de bugs, o que conecta diretamente à
  discussão de `odom`→`base_link` vs. `map`→`odom` do capítulo.

```bibtex
@inproceedings{foote2013,
  author    = {Foote, Tully},
  title     = {{tf}: The Transform Library},
  booktitle = {2013 IEEE International Conference on Technologies for Practical Robot Applications (TePRA)},
  year      = {2013},
  pages     = {1--6},
  publisher = {IEEE},
  doi       = {10.1109/TePRA.2013.6556373}
}
```

### 20. Datasheet oficial do RPLIDAR S2 (Slamtec)
- **Status:** CONFIRMADO contra fonte primária — página oficial de
  especificações do fabricante (não é artigo acadêmico, então tratar como
  referência técnica/datasheet, não como citação de pesquisa)
- **Fabricante:** Shanghai Slamtec Co., Ltd.
- **Ano:** especificação vigente consultada em 2026-09-30 (datasheet PDF
  também existe com versionamento próprio, ex. "S2 v2.0")
- **Fonte:** https://www.slamtec.com/en/s2/spec (página oficial de specs);
  PDF: datasheet `SLAMTEC_rplidar_datasheet_S2_v2.0_en.pdf` hospedado em
  `bucket-download.slamtec.com`
- **Relevância:** O capítulo (subseção "LiDAR 2D (RPLIDAR S2)") afirma que o
  sensor "opera a frequências de até 32\,kHz de amostragem e 10\,Hz de
  rotação" sem nenhuma citação. Confirmei os dois números exatamente contra
  a página oficial do fabricante: "32000 times per second" (sample rate) e
  "10Hz" (scan rate) para o modelo S2. Se o autor quiser citar, o formato
  mais adequado é `@misc` com `howpublished`/`note` de acesso, no mesmo
  padrão já usado em `referencias.bib` para `acm2020badging`.

```bibtex
@misc{slamtec2024rplidars2,
  author       = {{Shanghai Slamtec Co., Ltd.}},
  title        = {{RPLIDAR S2} Specifications},
  howpublished = {\url{https://www.slamtec.com/en/s2/spec}},
  note         = {Acessado em: 2026-09-30}
}
```

### Item pesquisado mas não confirmado (registrado para transparência)
- **IMU do Create3 — taxa de publicação "até 200\,Hz":** o capítulo (subseção
  "IMU") afirma que a IMU do Create3 publica a até 200\,Hz. A documentação
  oficial (`iroboteducation.github.io/create3_docs`) confirma apenas que o
  tópico `/imu` existe com tipo `sensor_msgs/msg/Imu`, mas a página de API
  consultada não especifica a taxa de publicação em Hz, e a página de
  hardware elétrico tampouco traz esse número. Não encontrei uma página
  oficial do Create3 que confirme ou contradiga especificamente os 200\,Hz
  citados no capítulo — por isso não registro candidato nem marco a
  afirmação como incorreta; fica para o autor confirmar com a documentação
  completa do Create3 (ou com `ros2 topic hz /imu` no robô real) antes de
  decidir se cita algo.

---

## Parte 4 — Capítulo 03, subseção "Comportamento Determinístico em Sistemas
Multi-Robô" (`sec:rel_frota`), levantamento de 2026-09-30

### 21. Response-Time Analysis of ROS 2 Processing Chains Under Reservation-Based Scheduling
- **Status:** CONFIRMADO contra fonte primária (Dagstuhl/LIPIcs, DOI resolvido
  em `drops.dagstuhl.de`)
- **Autores:** Daniel Casini, Tobias Blaß, Ingo Lütkebohle, Björn B. Brandenburg
- **Ano:** 2019
- **Venue:** 31st Euromicro Conference on Real-Time Systems (ECRTS 2019),
  Leibniz International Proceedings in Informatics (LIPIcs), vol. 133, pp. 6:1–6:23
- **DOI:** 10.4230/LIPIcs.ECRTS.2019.6
- **Relevância:** É um artigo de pesquisa de tempo-real que modela formalmente
  o escalonamento de cadeias de processamento no ROS~2 (executor, QoS,
  reservas de CPU) e deriva análise de tempo de resposta sob escalonamento
  baseado em reservas — exatamente o tipo de "trabalho de pesquisa de
  tempo-real" que a primeira frase da subseção "Comportamento Determinístico
  em Sistemas Multi-Robô" (`sec:rel_frota`, linha ~164 do capítulo 3) menciona
  de forma genérica e sem citação: "A dificuldade de garantir comportamento
  determinístico em sistemas multi-robô com ROS~2 é documentada em trabalhos
  de pesquisa de tempo-real." Ainda não promovido a `referencias.bib` nem
  citado no capítulo nesta rodada — conforme a regra do processo, um
  candidato encontrado via busca nova só é registrado aqui, a promoção para
  o `.bib` e o `\cite{}` ficam para uma rodada de revisão seguinte, após
  confirmação adicional do autor.

```bibtex
@inproceedings{casini2019,
  author    = {Casini, Daniel and Bla{\ss}, Tobias and L{\"u}tkebohle, Ingo and Brandenburg, Bj{\"o}rn B.},
  title     = {Response-Time Analysis of {ROS} 2 Processing Chains Under Reservation-Based Scheduling},
  booktitle = {31st Euromicro Conference on Real-Time Systems (ECRTS 2019)},
  series    = {Leibniz International Proceedings in Informatics (LIPIcs)},
  volume    = {133},
  year      = {2019},
  pages     = {6:1--6:23},
  publisher = {Schloss Dagstuhl--Leibniz-Zentrum f{\"u}r Informatik},
  doi       = {10.4230/LIPIcs.ECRTS.2019.6}
}
```

### Item pesquisado mas NÃO confirmado (registrado para transparência)
- **"Durrant-Whyte, Rye e Nebot (1996)" como origem da estrutura/nomenclatura
  do SLAM:** a Seção "A Taxonomia do SLAM" (`sec:rel_slam`, logo após
  `\citeonline{durrantwhyte2006}` e `\citeonline{bailey2006}`) afirma que "a
  estrutura, resultado de convergência e nomenclatura" do problema SLAM
  "haviam sido propostos originalmente por Durrant-Whyte, Rye e Nebot em
  1996", sem nenhuma citação. Tentei localizar um artigo de 1996 com esses
  três autores e esse conteúdo (busca web por título/venue), mas não
  encontrei um artigo correspondente — os resultados mais próximos desses
  mesmos autores no período são de 1997 (ex. "Ultra-High Integrity
  Navigation Systems for Large Autonomous Vehicles", ISRR'97, com um quarto
  e quinto coautor). Não é possível descartar que o artigo exista (pode ser
  um trabalho de ISRR'95/96 pouco indexado), mas também não consegui
  confirmá-lo contra fonte primária, então não registro como candidato
  (regra: não citar é melhor que citar errado) e não corrijo a frase —
  registrei o achado em `TODO_REVISAO.md` para o autor verificar a atribuição
  diretamente contra a seção de referências históricas de
  `\citeonline{durrantwhyte2006}`/`\citeonline{bailey2006}`, de onde essa
  atribuição provavelmente foi extraída.

---

## Parte 5 — Capítulo 04 (arquitetura), subseção "A Camada de Agentes de IA"
(`sec:agentes`), levantamento de 2026-09-30

Três afirmações nessa subseção descrevem conceitos com embasamento teórico
consolidado na literatura de agentes baseados em LLM, mas sem nenhuma
citação no texto atual. Não existe, em `referencias.bib` ou nos capítulos
02/03, nenhuma chave sobre agentes de LLM, \textit{tool use}/\textit{function
calling} ou grounding de ações — é um eixo totalmente novo, então os três
candidatos abaixo são registrados aqui (não promovidos nesta rodada, por
estar fora do escopo deste agente promover chaves novas ao `.bib`).

### 22. ReAct: Synergizing Reasoning and Acting in Language Models
- **Status:** CONFIRMADO contra fonte primária (arXiv, versão camera-ready
  ICLR 2023)
- **Autores:** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran,
  Karthik Narasimhan, Yuan Cao
- **Ano:** 2022 (v1 em out/2022; versão camera-ready ICLR 2023 em mar/2023)
- **Venue:** International Conference on Learning Representations (ICLR 2023)
- **arXiv:** 2210.03629
- **Relevância:** É a referência canônica do padrão "laço de raciocínio +
  ação" (intercalar decisão e chamada de ferramenta) que o capítulo descreve
  sem citação em `chapters/04_arquitetura.tex`, linhas ~201–204: "O
  \texttt{Planner} [...] implementa o laço de \textit{tool calling} da API
  da Anthropic: recebe uma instrução, decide uma sequência de chamadas de
  ferramenta e devolve o texto final mais o histórico de passos executados."
  Essa é exatamente a estrutura formalizada por ReAct.

```bibtex
@inproceedings{yao2023react,
  author    = {Yao, Shunyu and Zhao, Jeffrey and Yu, Dian and Du, Nan and Shafran, Izhak and Narasimhan, Karthik and Cao, Yuan},
  title     = {{ReAct}: Synergizing Reasoning and Acting in Language Models},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2023},
  eprint    = {2210.03629},
  archiveprefix = {arXiv}
}
```

### 23. Do As I Can, Not As I Say: Grounding Language in Robotic Affordances (SayCan)
- **Status:** CONFIRMADO contra fonte primária (arXiv + página oficial
  Google Research; venue confirmada via mlanthology.org/corl/2022)
- **Autores:** Michael Ahn, Anthony Brohan, Noah Brown, Yevgen Chebotar,
  Omar Cortes, Byron David, Chelsea Finn, Chuyuan Fu, Keerthana
  Gopalakrishnan, Karol Hausman, Alex Herzog, Daniel Ho, Jasmine Hsu, Julian
  Ibarz, Brian Ichter, Alex Irpan, Eric Jang, Rosario Jauregui Ruano, Kyle
  Jeffrey, Sally Jesmonth, Nikhil J. Joshi, Ryan Julian, Dmitry Kalashnikov,
  Yuheng Kuang, Kuang-Huei Lee, Sergey Levine, Yao Lu, Linda Luu, Carolina
  Parada, Peter Pastor, Jornell Quiambao, Kanishka Rao, Jarek Rettinghouse,
  Diego Reyes, Pierre Sermanet, Nicolas Sievers, Clayton Tan, Alexander
  Toshev, Vincent Vanhoucke, Fei Xia, Ted Xiao, Peng Xu, Sichun Xu, Mengyuan
  Yan, Andy Zeng
- **Ano:** 2022
- **Venue:** Conference on Robot Learning (CoRL 2022)
- **arXiv:** 2204.01691
- **Relevância:** Embasa teoricamente a afirmação de linhas ~196–199 de
  `chapters/04_arquitetura.tex` — "a execução em si continua passando pelos
  mesmos endpoints REST que o frontend já usa [...] o que limita o raio de
  ação de uma eventual alucinação do modelo ao conjunto de ferramentas
  explicitamente exposto a ele". SayCan é a referência central sobre
  restringir (\textit{grounding}) a saída de um modelo de linguagem a um
  conjunto fixo de ações/afordances executáveis para reduzir planos
  inviáveis ou incorretos.

```bibtex
@inproceedings{ahn2022saycan,
  author    = {Ahn, Michael and Brohan, Anthony and Brown, Noah and Chebotar, Yevgen and Cortes, Omar and David, Byron and Finn, Chelsea and Fu, Chuyuan and Gopalakrishnan, Keerthana and Hausman, Karol and Herzog, Alex and Ho, Daniel and Hsu, Jasmine and Ibarz, Julian and Ichter, Brian and Irpan, Alex and Jang, Eric and Jauregui Ruano, Rosario and Jeffrey, Kyle and Jesmonth, Sally and Joshi, Nikhil J. and Julian, Ryan and Kalashnikov, Dmitry and Kuang, Yuheng and Lee, Kuang-Huei and Levine, Sergey and Lu, Yao and Luu, Linda and Parada, Carolina and Pastor, Peter and Quiambao, Jornell and Rao, Kanishka and Rettinghouse, Jarek and Reyes, Diego and Sermanet, Pierre and Sievers, Nicolas and Tan, Clayton and Toshev, Alexander and Vanhoucke, Vincent and Xia, Fei and Xiao, Ted and Xu, Peng and Xu, Sichun and Yan, Mengyuan and Zeng, Andy},
  title     = {Do As {I} Can, Not As {I} Say: Grounding Language in Robotic Affordances},
  booktitle = {Conference on Robot Learning (CoRL)},
  year      = {2022},
  eprint    = {2204.01691},
  archiveprefix = {arXiv}
}
```

### 24. Design Patterns for Securing LLM Agents against Prompt Injections
- **Status:** CONFIRMADO contra fonte primária (arXiv)
- **Autores:** Luca Beurer-Kellner, Beat Buesser, Ana-Maria Crețu, Edoardo
  Debenedetti, Daniel Dobos, Daniel Fabian, Marc Fischer, David Froelicher,
  Kathrin Grosse, Daniel Naeff, Ezinwanne Ozoani, Andrew Paverd, Florian
  Tramèr, Václav Volhejn
- **Ano:** 2025
- **arXiv:** 2506.08837
- **Relevância:** Embasa a afirmação de linhas ~225–230 de
  `chapters/04_arquitetura.tex` — "O isolamento entre robôs é uma restrição
  estrutural, não uma convenção que depende do modelo 'se comportar'" (sobre
  \texttt{\_scope\_input()} reescrever à força o \texttt{robot\_id} antes de
  qualquer chamada real). O artigo propõe exatamente padrões de design que
  restringem estruturalmente as ações de um agente de LLM (em vez de
  depender do modelo obedecer a instruções de prompt) para obter resistência
  comprovável a desvios de escopo.

```bibtex
@article{beurerkellner2025designpatterns,
  author    = {Beurer-Kellner, Luca and Buesser, Beat and Cre{\c{t}}u, Ana-Maria and Debenedetti, Edoardo and Dobos, Daniel and Fabian, Daniel and Fischer, Marc and Froelicher, David and Grosse, Kathrin and Naeff, Daniel and Ozoani, Ezinwanne and Paverd, Andrew and Tram{\`e}r, Florian and Volhejn, V{\'a}clav},
  title     = {Design Patterns for Securing {LLM} Agents against Prompt Injections},
  journal   = {arXiv preprint},
  year      = {2025},
  eprint    = {2506.08837},
  archiveprefix = {arXiv}
}
```

---

## Parte 6 — Capítulo 05 (metodologia), seção "Intervalo de Confiança para
$N \geq 5$" (`sec:ic_estatistico`), levantamento de 2026-09-30

A subseção estatística do capítulo de metodologia (fórmula do IC~95\% via
distribuição $t$ de Student, Equação~\ref{eq:ic_95}) não tinha nenhuma citação
até esta rodada. Adicionei `\cite{amigoni2014}` ao texto (chave já aprovada,
usada como justificativa de rigor metodológico, não como fonte do método
estatístico em si). A fórmula do IC via $t$ de Student e a prática de reportar
incerteza estatística em experimentos de repetibilidade de robôs não têm chave
correspondente em `referencias.bib`; os dois candidatos abaixo foram
confirmados contra fonte primária, mas **não promovidos** nesta rodada (fora do
escopo deste agente promover chaves novas ao `.bib`).

### 25. The Probable Error of a Mean
- **Status:** CONFIRMADO contra fonte primária (DOI resolve para JSTOR/Biometrika;
  dados bibliográficos cruzados com Wikipedia e Fermat's Library)
- **Autor:** "Student" (pseudônimo de William Sealy Gosset)
- **Ano:** 1908
- **Venue:** Biometrika, vol. 6, n. 1, pp. 1–25
- **DOI:** 10.2307/2331554
- **Relevância:** É a referência primária e canônica da distribuição $t$ para
  intervalos de confiança com amostra pequena e variância populacional
  desconhecida — exatamente a justificativa dada no texto para usar $t$ em vez
  da normal ("mais apropriada para amostras pequenas ($N < 30$), onde a
  variância populacional é desconhecida e estimada a partir da própria
  amostra"). Nenhuma chave de estatística existe hoje em `referencias.bib`.

```bibtex
@article{student1908,
  author  = {Student},
  title   = {The Probable Error of a Mean},
  journal = {Biometrika},
  year    = {1908},
  volume  = {6},
  number  = {1},
  pages   = {1--25},
  doi     = {10.2307/2331554}
}
```

### 26. Rethink Repeatable Measures of Robot Performance with Statistical Query
- **Status:** CONFIRMADO contra fonte primária (arXiv + publicação formal em
  IEEE Transactions on Robotics, DOI resolvido)
- **Autores:** Bowen Weng, Linda Capito, Guillermo A. Castillo, Dylan Khor
- **Ano:** 2025
- **Venue:** IEEE Transactions on Robotics
- **DOI:** 10.1109/TRO.2025.3645934 (preprint: arXiv:2505.08216)
- **Relevância:** Trata diretamente do problema de medir repetibilidade de
  desempenho de robôs com algoritmos de consulta estatística (SQ) que estimam
  valores esperados a partir de amostras, propondo uma modificação que garante
  repetibilidade com limites de acurácia/eficiência — é literatura de
  metodologia estatística de repetibilidade robótica publicada em 2025,
  diretamente no eixo de `sec:ic_estatistico` e `sec:metricas` (que hoje citam
  apenas `maset2022` para a prática de comparação entre execuções). Mais
  próximo do tema do que o item 25 (que é a fonte estatística genérica), mas
  também não promovido nesta rodada — prefiro que o autor avalie se o foco em
  "statistical query algorithms" (mais amplo que RMSE/IC simples) se encaixa
  no enquadramento desta dissertação antes de promover.

```bibtex
@article{weng2025repeatable,
  author  = {Weng, Bowen and Capito, Linda and Castillo, Guillermo A. and Khor, Dylan},
  title   = {Rethink Repeatable Measures of Robot Performance with Statistical Query},
  journal = {IEEE Transactions on Robotics},
  year    = {2025},
  doi     = {10.1109/TRO.2025.3645934}
}
```
