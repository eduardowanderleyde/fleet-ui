# Referências candidatas — Orquestração/Coordenação Multi-Robô

Levantamento feito em 2026-09-25 para expandir o eixo "Sistemas de Orquestração
para Frotas" (`chapters/03_trabalhos_relacionados.tex`, `\label{sec:rel_frota}`)
e a fundamentação teórica correlata em `chapters/02_fundamentacao.tex`.
**Nenhuma entrada foi adicionada a `referencias.bib` — este arquivo é só para
revisão do autor.** As 29 chaves já existentes em `referencias.bib` foram
conferidas antes da busca; nenhuma referência abaixo duplica uma chave já
presente.

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
