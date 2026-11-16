# Plano de revisão final da dissertação

Montado em 16/11/2026 a partir da compilação da branch `dissertacao` (commit 0ae5226).
O orientador, Breno Miranda, aprova no fim. Eduardo sobe o zip no Overleaf e manda o PDF para ele.

## Regras que valem para todo o time

1. **Toda afirmação que não sai dos dados do próprio trabalho tem citação**, e a citação foi conferida na fonte: o trecho citado sustenta o que o texto diz. A chave precisa existir em `referencias.bib`. Nunca se inventa chave, DOI ou resultado.
2. **Todo número vem de um `summary.json` ou `replay_NN.json` real.** Sem fonte, o número não entra.
3. **80–90 folhas é meta, não regra.** O corte tira repetição entre capítulos, explicação demais e detalhe de implementação que o apêndice ou o repositório já cobre. Conteúdo importante para o argumento fica, mesmo que passe da meta.
4. **A camada de agentes de IA está fora**, a pedido da banca (commit 1102972). Ela não volta.
5. **Nenhum corte grande sem aprovação do Eduardo.** Corte de seção inteira, ou de mais de 1 página num capítulo, vai primeiro para a tabela "Cortes propostos" abaixo.
6. **Enquanto as testadoras estiverem no CIn**, ninguém mexe no repositório `fleet-ui-ufpe`.

## Tamanho medido (compilação de 16/11/2026)

O PDF tem **121 páginas**. Os **capítulos 1 a 9 ocupam as páginas 1 a 85 (85 páginas)**, ou seja, já estão dentro da meta. O resto é parte pré-textual, glossário, apêndices e referências.

| Parte | Páginas hoje | Meta | O que fazer |
|-------|-------------:|-----:|-------------|
| 1 Introdução | 8 | 7 | Tirar repetição com os capítulos 2 e 3 |
| 2 Fundamentação | 11 | 10 | Encurtar o que é livro-texto (ROS 2, Nav2) e manter o que sustenta o método |
| 3 Trabalhos relacionados | 11 | 10 | Juntar trabalhos parecidos numa tabela comparativa |
| 4 Arquitetura | 6 | 6 | Corrigir a Figura 4.1 (a seta cruza o título da camada) |
| 5 Metodologia | 6 | 6 | Manter |
| 6 Implementação | 11 | 8–9 | Levar trechos de código longos para o apêndice |
| 7 Avaliação | 8 | 7 | Ameaças à validade: conferir se repete o capítulo 9 |
| 8 Resultados | 15 | 15–17 | Entra o teste com o TurtleBot4 real no CIn (seção 8.9) **depois** dos testes desta semana |
| 9 Conclusão | 9 | 7 | Limitações e trabalhos futuros: tirar o que já foi dito no capítulo 7 |
| **Capítulos 1–9** | **85** | **~80–85** | |
| Glossário | 9 | 4–5 | Manter só termos usados e não definidos no texto |
| Apêndices A e B | ~7 | ~7 | Recebem o código que sair do capítulo 6 |

### Depois dos cortes (compilação de 16/11/2026, linhas 1–21 aplicadas)

O PDF tem **110 páginas** (eram 121). Os **capítulos 1 a 9 ocupam as páginas 1 a 73 (73 páginas)**, eram 85. Início de cada capítulo tirado do `main.toc`.

| Parte | Começa na p. | Páginas | Antes |
|-------|-------------:|--------:|------:|
| 1 Introdução | 1 | 8 | 8 |
| 2 Fundamentação | 9 | 9 | 11 |
| 3 Trabalhos relacionados | 18 | 9 | 11 |
| 4 Arquitetura | 27 | 6 | 6 |
| 5 Metodologia | 33 | 6 | 6 |
| 6 Implementação | 39 | 8 | 11 |
| 7 Avaliação | 47 | 7 | 8 |
| 8 Resultados | 54 | 13 | 15 |
| 9 Conclusão | 67 | 7 | 9 |
| **Capítulos 1–9** | | **73** | **85** |
| Glossário | 74 | 2 | 4 |
| Referências | 76 | 5 | 5 |
| Apêndice A | 81 | 4 | |
| Apêndice B | 85 | 5 | |
| Apêndice C (novo, listagens do cap. 6) | 90 | 3 | |

Com a seção 8.9 do TurtleBot4 real (+1–2 p), os caps. 1–9 ficam em torno de 75 páginas.

## Visual

- A compilação gera **97 avisos de texto passando da margem** (*overfull hbox*), 23 deles bem visíveis. Quase todos vêm de nomes de arquivo, tópicos ROS e comandos em `\texttt`.
- A Figura 4.1 tem a seta atravessando o rótulo "Camada de orquestração e coleta".
- Há figuras prontas que nenhum capítulo usa: `matriz_pairwise.png`, `erro_endpoint.png`, `consistencia_temporal.png`, `sumario_metricas.png`, `overlay_val01.png` e `overlay_val02.png`. Elas podem substituir texto descritivo no capítulo 8.
- **Proposta do designer (16/11) para as figuras não usadas.** Nenhuma foi incluída; Eduardo decide. Todas mostram só a validação preliminar Val01/Val02 (§8.1). A Tab. 8.1 e a Fig. 8.1 já cobrem esses números, então o ganho é de leitura, não de conteúdo. Antes de incluir qualquer uma, conferir se os valores do PNG batem com a Tab. 8.1 e com `summary.json` de Val01/Val02.

| Figura | Onde caberia | O que poderia substituir | Observação |
|--------|--------------|--------------------------|------------|
| `rmse_comparacao.png` (RMSE vs baseline e entre réplicas, com a linha de 25 cm) | §8.1, no lugar da Fig. 8.2 que o corte 11 retirou | Os parágrafos que repetem os números da Tab. 8.1 | Duplica a tabela; só vale se a tabela for encurtada. |
| `erro_endpoint.png` (erro de chegada por réplica, com limiar de 25 cm) | §8.1 ou §8.2 (erro final) | A frase que lista o erro de endpoint de Val01 e Val02 | Mostra 20,5 e 23,2 cm em Val01: ficam perto do limiar e valem uma frase no texto. |
| `consistencia_temporal.png` (duração de cada execução, Val01 e Val02) | §8.4 (QA3), como ilustração da validação preliminar | Uma frase descritiva sobre a duração de Val01 e Val02 | Aparece a queda de 45,5 s (baseline) para 12,6 s (réplicas) em Val01, que o texto precisa explicar (mecanismo diferente). |
| `matriz_pairwise.png` (mapas de calor dos pares) | §8.1 ou §2.9 (como exemplo visual da matriz pairwise) | Descrição em prosa da matriz N×N | Ilustra bem o conceito de RMSE pairwise e o contraste baseline vs réplicas. |
| `overlay_val01.png` e `overlay_val02.png` | §8.1 | Nada: a Fig. 8.1 (`overlay_trajetorias.png`) já mostra as duas rotas lado a lado | Redundantes. Não recomendo incluir. |
| `sumario_metricas.png` (tabela como imagem) | Nenhum | Nada | Repete a Tab. 8.1 como imagem; evitar, a tabela em LaTeX é melhor. |

Recomendação: incluir no máximo `matriz_pairwise.png` (§2.9 ou §8.1) e `consistencia_temporal.png` (§8.4); descartar as outras.
- O organograma feito em 16/11 (artifact "Fleet UI — Organograma") pode virar figura, mas só na versão filtrada para o que existe nesta branch, sem os itens só de outras branches e sem a camada de agentes.

## Ordem de trabalho

| Fase | Quando | Quem | Saída |
|------|--------|------|-------|
| 1 | Agora | `dissertacao-editor` | Mapa de repetições entre capítulos e lista de cortes propostos, para Eduardo aprovar |
| 2 | Agora | `chapter-X-pesquisa` (caps. 1–7, 9) | Citações conferidas; candidatas em `referencias_candidatas.md` |
| 3 | Depois da aprovação dos cortes | `chapter-X` e `chapter-X-redacao` | Capítulos cortados e com o texto lapidado |
| 4 | Em paralelo | `dissertacao-designer` | Figura 4.1 corrigida, avisos de margem resolvidos, figuras não usadas avaliadas |
| 5 | Depois dos testes no CIn | `chapter-resultados` | Seção 8.9 com o teste real, a partir de `docs/ufpe/REGISTRO-PROBLEMAS.md` e dos dados copiados |
| 6 | No fim | `chapter-X-redacao` e depois `dissertacao-editor` | Leitura corrida inteira: voz única, transições e conferência cruzada |
| 7 | No fim | `dissertacao-montador` | Compilação limpa, zip para o Overleaf e PDF para o Breno |

## Cortes propostos (preenchido pelo `dissertacao-editor`; Eduardo aprova)

| # | Capítulo / seção | O que sai ou muda | Páginas | Por quê | Aprovado? |
|---|------------------|-------------------|--------:|---------|-----------|
| 1 | Cap. 1, §1.4 `sec:escopo` (l.144–158) e §1.5 `sec:objetivos` (l.172–175) | Encurtar o parágrafo "Embora a Seção~\ref{sec:frota}..." para 3–4 linhas: avaliação com uma MUUT, piloto FUUT em §8.8, multi-robô como trabalho futuro. Tirar a última frase de §1.5, que repete isso. | 0,3 | **P1, repetição.** A restrição a um robô aparece em §1.4, §1.5, no rodapé da Tab. 3.1 (cap. 3, l.386–390), em §9.1 (l.28–29 e 70–73) e em §9.4 (l.190–217). A versão completa fica em §9.4; aqui fica só o anúncio. || Sim (16/11) |
| 2 | Cap. 1, §1.6 `sec:perguntas_pesquisa`, H3 (l.244–256) | Cortar o trecho "Diferentemente de H2... análise descritiva" e deixar uma frase dizendo que H3 é qualitativa, sem limiar, com remissão a §7.2. PP1–PP4 e H1–H4 ficam intactas. | 0,3 | **P1, repetição.** O caráter exploratório de H3/QA4 é explicado três vezes: aqui, em §7.2 QA4 (cap. 7, l.47–54) e em §7.4 (cap. 7, l.111–114). O lugar dele é §7.2. || Sim (16/11) |
| 3 | Cap. 1, §1.8 `sec:organizacao` (l.346–380) | Juntar os nove parágrafos de uma frase em um parágrafo corrido. | 0,4 | **P1, formato.** Nenhum conteúdo sai. || Sim (16/11) |
| 4 | Cap. 2, §2.4.2 `sec:actions` (l.242–250) e §2.4.3 `sec:action_lifecycle` (l.252–277) | §2.4.2: o parágrafo sobre a diferença entre baseline e replay vira remissão a §5.1.2. §2.4.3: fica só a máquina de estados (1º parágrafo). O 2º parágrafo, sobre `_make_result_cb` e "o Código não mostra esse trecho", sai porque já está em §6.2 (cap. 6, l.83–86). | 0,7 | **P1, repetição.** A diferença NavigateToPose × FollowWaypoints aparece em §2.4.2, §5.1.2 (cap. 5, l.46–52), §7.5 (cap. 7, l.208–219), §8.1 (cap. 8, l.26–33 e 50–60) e §8.3.1 (cap. 8, l.211–222). Fica em §5.1.2 (método) e em §8.3.1 (dado). || Sim (16/11) |
| 5 | Cap. 2, §2.5 `sec:localizacao_bayes` (l.279–333) | Passar de ~1,8 para ~0,6 página. Ficam a definição de AMCL e filtro de partículas (com `kalman1960`, citado só aqui) e uma frase sobre por que o AMCL entra (trabalho futuro, §9.5). Sai o parágrafo sobre `hamer2025` (l.311–322), que repete §3.2.2 e continua citado lá. O parágrafo l.324–333 vira uma frase. | 1,1 | **P2, livro-texto.** É explicação longa de um componente que a dissertação não usa. Ver também o problema da l.324 ("preferir AMCL"). || Sim (16/11) |
| 6 | Cap. 2: §2.1.1 `sec:erro_odometria` (l.30–52), EKF em §2.2 (l.74–81), lista de §2.3.1 `sec:qos` (l.127–140) e §2.7 `sec:sensores` (l.362–392) | §2.1.1: fica só o último parágrafo (5–10% de deriva justificam o SLAM). EKF: uma frase. QoS: fica a Tab. 2.1 e sai a lista descritiva, que diz o mesmo. §2.7: as três subseções viram um parágrafo, porque as especificações já estão na Tab. 5.2. Todas as citações ficam. | 1,0 | **P2, livro-texto**, como o plano pede para o cap. 2. As especificações do LiDAR também se repetem no cap. 6 (§6.1, l.10–11) e na Tab. 5.2. || Sim (16/11) |
| 7 | Cap. 3, §3.4.1 `sec:rel_frota` (l.163–201) e §3.4.2 (l.216–232) | A lista MRTA/RobotKube/Resh/Robofleet/5G/formação vira um parágrafo de ~150 palavras, com todas as citações e a frase de posicionamento (l.203–206). Em §3.4.2, ALLIANCE e "mitigação de software" viram um único parágrafo. | 0,9 | **P2.** O plano pede juntar trabalhos parecidos. Hoje é uma frase por trabalho, sem comparação entre eles. Esses trabalhos podem virar linhas da Tab. 3.1, se Eduardo preferir. || Sim (16/11) |
| 8 | Cap. 3: §3.2.2 (l.90–92), §3.3.2 (l.134–144), §3.7 (l.343–345) e §3.8 (l.353–365) | Sai o parágrafo sobre o JBCS como veículo. O parágrafo sobre Thrun vira uma frase. Sai a frase sobre a rejeição do artigo na trilha de ferramentas da SBES. A justificativa para deixar amigoni/guevaravega fora da tabela cai para 2 linhas. | 0,6 | **P2.** Nada disso sustenta a lacuna. A menção à rejeição na SBES é bastidor e não ajuda diante da banca. || Sim (16/11) |
| 9 | Limiar de 25 cm: cap. 3 §3.10 `sec:rel_conclusao` (l.446–459), cap. 7 §7.4 `sec:criterios` (l.116–127) e §7.5 (l.169–172), cap. 8 §8.3 `sec:res_qa2` (l.148–156) | A justificativa fica em §7.4 (origem do limiar) e na ameaça de construto de §7.5. A comparação com RPP (5 cm) e maset2022 (2 cm) sai de §3.10 e vai para §7.4 em 2–3 frases. Em §8.3, o parágrafo l.148–156 vira uma frase com remissão. | 0,5 | **P1, repetição.** O limiar é justificado em quatro lugares, com números que não batem: 30 cm no cap. 3, "cerca de cinco vezes" no cap. 7 e "quase uma ordem de grandeza" no cap. 8. || Sim (16/11) |
| 10 | Cap. 7, §7.5 `sec:ameacas`, mecanismo de navegação (l.208–231) | Ficam a ameaça e o parágrafo do confundimento (l.232–247). Os números da campanha teste1 (0,02 × 0,14 m, 2,5×) e a explicação das paradas de 200 ms viram remissão a §5.1.2 e §8.3.1. | 0,5 | **P1, repetição** (ver linha 4). A ameaça à validade continua inteira; só deixa de repetir o resultado. || Sim (16/11) |
| 11 | Cap. 8, §8.1 `sec:res_validacao_preliminar` (l.55–80) | Ficam a Tab. 8.1 e a Fig. 8.1. Saem a Fig. 8.2 (`rmse_comparacao.png`), que mostra os mesmos números da tabela, e os parágrafos l.55–60 e l.71–80, que antecipam o achado de §8.3.1. | 0,9 | **P2.** Abre espaço no próprio cap. 8 para o teste com o robô real. A figura duplica a tabela. || Sim (16/11) |
| 12 | Cap. 8, §8.3.1 `sec:res_qa2_mecanismo` (l.211–234) e §8.6 `sec:res_exp_complementares` (l.321–340) | §8.3.1: ficam a tabela, a figura e os números; a explicação do mecanismo vira remissão a §5.1.2. §8.6: os dois últimos parágrafos viram um, porque justificam a mesma coisa duas vezes. | 0,4 | **P1, repetição** (ver linha 4). || Sim (16/11) |
| 13 | Fallback `amcl_pose > pose > odom`: cap. 6 §6.3 e §6.3.1 (l.297–332) e cap. 7 §7.5 (l.179–206) | A explicação completa fica no cap. 6. No cap. 7, ficam 3–4 frases: o risco existiu, foi corrigido (§6.3.1) e não afeta a campanha principal, que usa `/odom` de forma explícita. | 0,6 | **P1, repetição.** §7.5 repete quase palavra por palavra o texto de §6.3. || Sim (16/11) |
| 14 | Estocasticidade do MPPI: cap. 6 §6.3.1 (l.355–366), cap. 7 §7.5 (l.256–269), cap. 8 §8.3.1 (l.236–242), cap. 9 §9.4 (l.271–281) e §9.5 (l.369–373) | Fica em §7.5 (validade interna) e no item de trabalho futuro. Sai de §6.3.1. Em §8.3.1 e §9.4, vira uma frase com remissão a §7.5. | 0,5 | **P1, repetição.** O mesmo argumento aparece cinco vezes. || Sim (16/11) |
| 15 | Salto do relógio e ativação sequencial: cap. 4 §4.4.1 `sec:painel_simulacao` (l.277–292), cap. 6 §6.1 `sec:simulacao` (l.58–68) e cap. 9 §9.4 `sec:limitacoes` (l.190–245) | A narrativa completa fica só em §9.4, que também perde o histórico "sugeriu originalmente... invalidando essa conclusão" (l.198–209). Em §4.4.1, a decisão pela ativação sequencial cabe em 2 frases. Em §6.1, uma frase com remissão. | 0,9 | **P1, repetição.** O mesmo episódio é contado três vezes, e o Cyclone DDS aparece em dois desses lugares. || Sim (16/11) |
| 16 | Recapitulações: cap. 4, introdução (l.61–67) e §4.5 `sec:arq_conclusao` (l.297–301 e 317–321); cap. 6, §6.5 `sec:impl_conclusao` (l.512–522); cap. 9, §9.1 (l.56–60) | O argumento "o Painel foi construído sobre a API REST sem mexer no orquestrador" fica só em §4.5. A lista de decisões no 1º parágrafo de §4.5 e a de §6.5 viram uma frase cada. | 0,6 | **P1, repetição.** O argumento do Painel aparece três vezes, e as duas listas de decisões repetem §1.7 e §9.1. || Sim (16/11) |
| 17 | Cap. 6, listagens longas: `lst:start_stop_record` (l.118–164), `lst:backend_bridge` (l.201–222), `lst:pose_fallback` (l.334–347), `lst:rmse_pairwise` e `lst:rmse_mean` (l.428–468) | As cinco listagens vão para os apêndices (A, B ou um novo C). No texto ficam a explicação de cada uma e a remissão. No capítulo fica só `lst:rmse_impl`, que sustenta a métrica. Também sai o parágrafo l.230–238 de §6.2.2, que repete o custo de 1,2–3,2 s já tratado em §4.4. | 2,4 (sai do texto principal; ~2 p entram no apêndice) | **P1.** É o que o plano pede para o cap. 6. `lst:rmse_mean` já foi trocada em 16/11 pelo trecho de `analyze_runs.py` mais a Equação `eq:rmse_medio`, porque a camada de IA não entra na dissertação. || Sim (16/11) |
| 18 | Cap. 7, §7.1 `sec:arranjo` (l.7–25), e cap. 6, §6.1 (l.7–14) | Sai a lista de software de §7.1, que é a Tab. 5.2, e fica uma remissão. Sai também a frase sobre amigoni2010, já usada em §5.4 (cap. 5, l.189–191) e §8.6 (cap. 8, l.337–338). Em §6.1, saem as especificações que já estão na tabela. | 0,3 | **P1, repetição.** || Sim (16/11) |
| 19 | Cap. 8, §8.10 `sec:res_conclusao` (l.677–704); cap. 9, §9.1 `sec:sintese` (l.14–16, 38–47 e 62–88) | §8.10 vira um parágrafo curto, com QA1–QA4 em uma frase cada. A lição sobre a pose inicial sai, porque §9.6 diz o mesmo. Em §9.1, saem os números (estão em §9.2, PP2), o item de CI cai para 2 frases (repete §1.7) e o parágrafo final fica mais curto. | 0,9 | **P1, repetição.** O valor 3,35 cm aparece em §6.3.2, §7.5, §8.3, §8.10, §9.1, §9.2 e §9.6. || Sim (16/11) |
| 20 | Cap. 9: §9.2 PP4 (l.138–156), §9.3 `sec:repro_vs_repet` (l.161–166), §9.4 FUUT (l.247–269), §9.4 simulação (l.299–304) e §9.5 `sec:futuros`, itens de odom e multi-robô (l.332–345 e 375–393) | PP4: sai a segunda volta sobre "evidência funcional". §9.3: os termos não são redefinidos; fica a remissão a §1.1. FUUT: 3 linhas com remissão a §8.8.3, que já tem as três limitações. Simulação: uma frase com remissão a §7.5 (validade externa). Itens de trabalho futuro: sai a repetição dos resultados de §8.7 e de §9.4. | 1,4 | **P1, repetição.** O plano pede tirar do cap. 9 o que já está nos caps. 7 e 8. As limitações continuam todas listadas. || Sim (16/11) |
| 21 | Glossário `chap:glossario` (fora dos caps. 1–9) | Critério: ficam só (a) os termos usados e não definidos no texto e (b) o vocabulário próprio do trabalho. **Ficam 12 de 32:** Bag/MCAP, Behavior Tree, CDR, DiffDrive, Gazebo Harmonic, Goal Handle, OccupancyGrid, Waypoint, MUUT, FUUT, SU e Record–Replay. **Saem** os já definidos nos caps. 2–4: Action, AMCL, Artefato de Pesquisa, BEST_EFFORT, DDS, Dead Reckoning, Endpoint Error/Erro de Endpoint, Filtro de Partículas, IMU, Lifecycle, LiDAR, MPPI, Nav2, Odometria, QoS, RMSE, ROS 2, SLAM, SLAM Toolbox, TF2 e TRANSIENT_LOCAL. | ~2,5 (de 4 p para ~1,5 p) | Correção da tabela "Tamanho medido": o glossário ocupa só as págs. 86–89 (4 páginas), não 9. As págs. 90–94 são as referências. || Sim (16/11) |

**Total estimado:** cerca de 15 páginas nominais nos caps. 1–9 (P1 ≈ 10,7, P2 ≈ 4,5), das quais ~2 vão para o apêndice; mais ~2,5 no glossário. Na prática, com quebra de página e marcação LaTeX contadas como palavra, espere de 11 a 13 páginas a menos no texto principal. Aprovar só as linhas P1 já abre espaço para a seção do robô real (+1–2 p) e deixa os caps. 1–9 perto de 77–80 p. As linhas P2 são opcionais, se Eduardo quiser chegar mais perto de 75.
P1 = repetição ou formato, sem perda de conteúdo. P2 = encurtar livro-texto ou revisão, com todas as citações mantidas.
