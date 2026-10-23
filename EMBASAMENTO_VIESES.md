# Embasamento teórico — vieses e melhorias de software

Conferido em 2026-10-23. Cada referência nova foi verificada na fonte (DOI,
editora ou PDF). As marcadas "já no .bib" já estão em
`dissertacao/referencias.bib`. Nenhuma das novas foi incluída no texto ainda.

## Base geral (validade)

- **Wohlin et al. (2012)**, *Experimentation in Software Engineering*,
  Springer, DOI 10.1007/978-3-642-29044-2. Classificação de ameaças à
  validade (conclusão, interna, construto, externa) usada na área.
- **Runeson & Höst (2009)**, "Guidelines for conducting and reporting case
  study research in software engineering", *Empirical Software Engineering*
  14(2):131–164, DOI 10.1007/s10664-008-9102-8. Base para o estudo de caso
  CBSoft e para o viés do pesquisador.

## Os 5 vieses

| Viés | Tipo de ameaça (Wohlin) | Embasamento | Evidência no próprio projeto |
|---|---|---|---|
| 1. Escolha da execução de referência | Conclusão | `maset2022` (já no .bib): comparar execuções nominalmente idênticas entre si; Zhang & Scaramuzza (2018): a métrica de trajetória depende de alinhamento e referência | RMSE contra replay 01 = 3,35 cm; média pairwise = 2,76 cm (mesmo `summary.json`) |
| 2. Fonte de posição (odometria) | Construto | `borenstein1996` (já no .bib): erro de odometria acumula; Sturm et al. (2012): ground truth de sistema externo e avaliação separada de deriva (RPE) e erro global (ATE) | /odom vs GT: 0,01 cm (rota curta) → 14,27 cm (loop) |
| 3. Simulação vs. realidade | Externa | Jakobi et al. (1995): *reality gap*; Afzal et al. (2021): desenvolvedores citam a distância simulação–realidade como desafio do teste em simulação; `takaya2016`, `amigoni2010` (já no .bib) | Toda a campanha em Gazebo; teste na UFPE pendente |
| 4. Sobrevivência (só execuções bem-sucedidas entram) | Interna / conclusão | Borji (2018): resultados negativos omitidos distorcem a avaliação; `bonsignorio2015`, `amigoni2014` (já no .bib): relatar o experimento de forma replicável | Ativação multi-robô 70%; mecanismo de nova tentativa; processos mortos por MCE |
| 5. Autor-avaliador e critério folgado | Construto / externa | Runeson & Höst (2009): viés do pesquisador; Wohlin et al. (2012): expectativa do experimentador; `amigoni2014`: poucos cenários | PP4 julgada pelos autores; limiar 25 cm ≫ 4,76 cm; 1 rota, N=10 |

## Melhorias de software / versionamento

- **Wilson et al. (2014)**, "Best Practices for Scientific Computing",
  *PLoS Biology* 12(1):e1001745, DOI 10.1371/journal.pbio.1001745 — controle
  de versão e reprodutibilidade de software científico.
- **Wilson et al. (2017)**, "Good enough practices in scientific computing",
  *PLoS Computational Biology* 13(6):e1005510, DOI 10.1371/journal.pcbi.1005510.
- **Semantic Versioning 2.0.0** (Preston-Werner), https://semver.org — versão
  0.y.z = desenvolvimento inicial, API instável (o projeto está todo em 0.1.0);
  versão publicada é imutável → tags por marco.
- `acm2020badging`, `guevaravega2024` (já no .bib) — artefato versionado e
  reexecutável por terceiros.
- Lier et al. (2017), "Can we Reproduce it? Toward the Implementation of good
  Experimental Methodology in Interdisciplinary Robotics Research", ICRA 2017
  Workshop on Reproducible Research in Robotics (workshop, não periódico).
- **Fowler (2018)**, *Refactoring*, 2ª ed., Addison-Wesley — *code smell*
  "Large Class" (`backend/main.py`, 1.703 linhas).
- `timperley2024`, `albonico2023` (já no .bib) — engenharia de software em ROS.

## BibTeX prontos

```bibtex
@book{wohlin2012,
  author    = {Wohlin, Claes and Runeson, Per and H{\"o}st, Martin and Ohlsson, Magnus C. and Regnell, Bj{\"o}rn and Wessl{\'e}n, Anders},
  title     = {Experimentation in Software Engineering},
  publisher = {Springer},
  year      = {2012},
  doi       = {10.1007/978-3-642-29044-2},
}
@article{runeson2009,
  author  = {Runeson, Per and H{\"o}st, Martin},
  title   = {Guidelines for conducting and reporting case study research in software engineering},
  journal = {Empirical Software Engineering},
  volume  = {14}, number = {2}, pages = {131--164}, year = {2009},
  doi     = {10.1007/s10664-008-9102-8},
}
@inproceedings{zhang2018trajectory,
  author    = {Zhang, Zichao and Scaramuzza, Davide},
  title     = {A Tutorial on Quantitative Trajectory Evaluation for Visual(-Inertial) Odometry},
  booktitle = {2018 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
  pages     = {7244--7251}, year = {2018},
  doi       = {10.1109/IROS.2018.8593941},
}
@inproceedings{sturm2012,
  author    = {Sturm, J{\"u}rgen and Engelhard, Nikolas and Endres, Felix and Burgard, Wolfram and Cremers, Daniel},
  title     = {A Benchmark for the Evaluation of {RGB-D} {SLAM} Systems},
  booktitle = {2012 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
  year      = {2012},
}
@inproceedings{jakobi1995,
  author    = {Jakobi, Nick and Husbands, Phil and Harvey, Inman},
  title     = {Noise and the Reality Gap: The Use of Simulation in Evolutionary Robotics},
  booktitle = {Advances in Artificial Life (ECAL 1995)},
  series    = {Lecture Notes in Computer Science}, volume = {929},
  publisher = {Springer}, year = {1995},
  doi       = {10.1007/3-540-59496-5_337},
}
@inproceedings{afzal2021simulation,
  author    = {Afzal, Afsoon and Katz, Deborah S. and Le Goues, Claire and Timperley, Christopher S.},
  title     = {Simulation for Robotics Test Automation: Developer Perspectives},
  booktitle = {14th IEEE Conference on Software Testing, Verification and Validation (ICST)},
  pages     = {263--274}, year = {2021},
}
@article{borji2018,
  author  = {Borji, Ali},
  title   = {Negative Results in Computer Vision: A Perspective},
  journal = {Image and Vision Computing},
  volume  = {69}, pages = {1--8}, year = {2018},
  doi     = {10.1016/j.imavis.2017.10.001},
}
@article{wilson2014,
  author  = {Wilson, Greg and others},
  title   = {Best Practices for Scientific Computing},
  journal = {PLoS Biology}, volume = {12}, number = {1}, pages = {e1001745}, year = {2014},
  doi     = {10.1371/journal.pbio.1001745},
}
@article{wilson2017,
  author  = {Wilson, Greg and Bryan, Jennifer and Cranston, Karen and Kitzes, Justin and Nederbragt, Lex and Teal, Tracy K.},
  title   = {Good enough practices in scientific computing},
  journal = {PLoS Computational Biology}, volume = {13}, number = {6}, pages = {e1005510}, year = {2017},
  doi     = {10.1371/journal.pcbi.1005510},
}
@misc{semver,
  author = {Preston-Werner, Tom},
  title  = {Semantic Versioning 2.0.0},
  howpublished = {\url{https://semver.org}},
}
@book{fowler2018,
  author    = {Fowler, Martin},
  title     = {Refactoring: Improving the Design of Existing Code},
  edition   = {2}, publisher = {Addison-Wesley}, year = {2018},
}
```

Status (2026-10-23): todas conferidas e inseridas no texto. DOI do Sturm 2012
= 10.1109/IROS.2012.6385773; autores completos do Wilson 2014 conferidos na
PLoS; SemVer 2.0.0 = 2013 (tag v2.0.0 no GitHub). Afzal: o texto cita o
preprint arXiv:2004.07368 (citação conferida no resumo), não o artigo do
ICST, cujo DOI não foi confirmado. Onde entrou: Cap. 7, Ameaças à Validade
(wohlin2012, runeson2009, sturm2012, borji2018, jakobi1995, afzal2020,
zhang2018trajectory, wilson2014); Cap. 9, Trabalhos Futuros (semver,
fowler2018, wilson2017).
