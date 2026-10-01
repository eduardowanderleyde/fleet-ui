# Sugestões de conteúdo/argumentação — leitura tipo banca (2026-10-01)

Gerado por 9 agentes (um por capítulo, rodados em paralelo), cada um só lendo
e analisando — nenhuma edição foi feita nos capítulos. Isso é complementar à
revisão bibliográfica/redação já feita antes; aqui o foco é conteúdo e
argumentação, no papel de um avaliador de banca de mestrado. Nenhuma dessas
sugestões foi aplicada — são para o autor decidir.

## Achados cross-capítulo mais sérios (aparecem de forma independente em mais de um agente)

1. **Overclaiming de "multi-robô"**: a Tabela de Síntese Comparativa
   (`03_trabalhos_relacionados.tex`, linha 367) marca ✓ pleno pra
   "Multi-robô" nesta dissertação, mas o Capítulo 1 já declara
   explicitamente que a avaliação quantitativa foi single-robot. Overclaiming
   direto — fácil de a banca pegar comparando as duas páginas.
2. **Camada de agentes de IA (Planner/Executor/Analyst, CI) nunca é
   anunciada na Introdução**, apesar de aparecer com peso na Arquitetura
   (`04_arquitetura.tex`) e na Síntese de Contribuições da Conclusão
   (`09_conclusao.tex`). Achado de forma independente pelos agentes dos
   capítulos 01, 04 e 09 — é o ponto mais repetido de toda a rodada.
3. **Inconsistência "2 robôs resolvido" vs. "70% de sucesso"**: já corrigida
   nesta sessão (ver `TODO_REVISAO.md`), mas o agente da Conclusão notou que
   ainda existe uma tensão lógica residual — se os mecanismos arquiteturais
   "resolvem problemas concretos" de multi-robô, por que a tentativa real
   ainda falha 30% das vezes? Vale uma frase distinguindo problema de
   API/namespace (resolvido) de problema de sincronização temporal (não
   resolvido).
4. **Limiares numéricos sem justificativa própria, reaproveitados de outro
   contexto**: o 25cm de RMSE (critério QA2) é na verdade a tolerância de
   chegada a um ponto único do Nav2, não uma métrica desenhada para RMSE de
   trajetória inteira; e o CV_t teórico de 5% (cap. 02) virou 10% no
   critério de aceite (cap. 07) sem explicação. Dois agentes diferentes
   (05 e 07) chegaram a essa mesma classe de problema de ângulos distintos.
5. **QA4/H3 tem cheiro de HARKing**: foi formulada depois de já existirem os
   dados exploratórios que a confirmam. O texto já admite isso em uma frase,
   mas um avaliador vai cobrar uma defesa metodológica mais explícita
   (pesquisa exploratória/geradora de hipótese vs. confirmatória).
6. **AMCL é fundamentado no Cap. 2 com promessas de uso futuro que nunca se
   confirmam** — e outros capítulos (06, 07) dizem explicitamente que o
   projeto nunca usa AMCL. Candidato a maior contradição isolada de um
   capítulo só.

## Por capítulo

### 01 — Introdução
1. Desproporção entre a ênfase em "frota" (Seção 1.3) e a avaliação real
   (single-robot) — mover a restrição pra Escopo e Restrições, não deixar
   como cláusula subordinada em Objetivos.
2. H1 ("qualquer protocolo record-replay sem código adicional") é
   não-falseável como está — testado com 1 rota, 1 robô.
3. H2 tem critério numérico; H3 não tem nenhum limiar — assimetria de rigor
   entre hipóteses apresentadas como igualmente verificadas.
4. Camada de agentes de IA não aparece em Contribuições nem em Organização
   da Dissertação (ver achado cross-capítulo #2).
5. "Crise de orquestração experimental" é apresentada como termo próprio,
   mas a literatura já citada na mesma seção descreve as mesmas facetas —
   diferenciar melhor o que é de fato novo na formulação.

### 02 — Fundamentação Teórica
1. Seção de AMCL promete uso em "análises de sensibilidade do Cap. 8" que
   não existe no texto, e reaparece como "trabalho futuro" que também não
   está em Trabalhos Futuros (cap. 09) — ver achado cross-capítulo #6.
2. Falta fundamentação de coordenação multi-robô antes do Cap. 3 introduzir
   arquiteturas de frota — MUUT/FUUT aparece "do nada" no Cap. 4.
3. CV_t < 5% (cap. 02) vs. limiar de aceite de 10% (cap. 07) — ver achado
   cross-capítulo #4.
4. Redundância interna no próprio capítulo: mesma comparação grafos-vs-
   partículas repetida ~230 linhas depois, com a mesma citação.
5. EKF-SLAM citado no Cap. 3 como uma das "três famílias dominantes" sem
   ter sido introduzido como tal no Cap. 2.
6. Behavior Trees/recovery behaviors fundamentados mas nunca revisitados —
   oportunidade de fortalecer validade interna confirmando que nenhum
   recovery disparou durante os 10 replays.

### 03 — Trabalhos Relacionados
1. Tabela marca multi-robô com ✓ pleno — overclaiming (achado cross-capítulo
   #1).
2. "Síntese Comparativa" é só a tabela, sem parágrafo de análise dos
   padrões revelados.
3. As colunas da tabela não capturam a contribuição mais distintiva
   (papéis MUUT/FUUT/SU) — considerar substituir a coluna "Multi-robô".
4. Tabela mistura sistemas com artigos de survey/metodologia (amigoni2010,
   guevaravega2024), gerando linhas quase todas N/A.
5. "Essa lacuna não é acidental... escolha implícita da comunidade" é uma
   generalização sociológica forte, não sustentada pelas próprias
   referências citadas.
6. Limiar de H2 (30cm) não é ancorado nos números de referência que o
   próprio capítulo levanta (Pure Pursuit ~5cm, Maset2022 ~2cm).

### 04 — Arquitetura do Framework
1. Papéis MUUT/FUUT/SU descritos como "decisão mais importante", mas sem
   justificativa contra alternativas mais simples.
2. Trade-off REST-vs-rosbridge (custo real de latência) só aparece no
   capítulo de Implementação, não onde a decisão é tomada.
3. Redundância forte com o Cap. 6 — mesma informação sobre o painel de
   simulação e `Popen`/`setsid` repetida em 3 lugares diferentes ao todo.
4. Falta seção de requisitos/objetivos de projeto antes da proposta de 5
   camadas — hoje a narrativa é bottom-up mas se apresenta como top-down.
5. Camada de agentes não discute a alternativa MCP, que o próprio
   `orquestracion.md` já lista como "próximo passo natural".
6. Modelo de papéis estático (YAML editado manualmente) não é discutido
   como limite de design deliberado.

### 05 — Metodologia Experimental
1. N=10 justificado só descritivamente, sem cálculo formal de tamanho de
   amostra/poder estatístico.
2. "Comprimento de trajetória" é reportado e discutido no Cap. 8 mas nunca
   foi declarado como métrica no Cap. 5.
3. Nenhuma métrica trata orientação/heading, apesar do critério de chegada
   do Nav2 incluir tolerância angular.
4. Normalização temporal (vs. alternativas como DTW/Fréchet) não é
   justificada contra alternativas da literatura de comparação de
   trajetórias.
5. Limiar do filtro de saltos impossíveis (0,12m a 50Hz ≈ 6m/s) é muito
   acima da velocidade real do robô (~0,05m/s) — parece não calibrado.
6. Atrasos fixos de 8s/12s no fluxo de execução são específicos da máquina
   do autor, não discutidos como risco de replicabilidade.

### 06 — Implementação
1. A subseção que documenta o cálculo do RMSE mostra só as funções
   auxiliares — falta o laço pairwise e a agregação final (que vive em
   `backend/agents/analyst.py`, não em `analyze_runs.py`). É a lacuna de
   auditabilidade mais crítica encontrada, porque é sobre o número mais
   citado da dissertação.
2. `samples=100` na grade normalizada não tem justificativa de
   sensibilidade.
3. A correção `amcl_pose > pose > odom` é descrita como a contribuição mais
   consequente do capítulo, mas recebe tratamento em prosa corrida, sem
   código — desproporção frente a correções menos críticas que têm código
   e subseção própria.
4. "Desserialização CDR sem tipo registrado" (Considerações Finais) nunca é
   explicada no corpo do capítulo.
5. Redundância com Cap. 4 sobre o buffer de TF por robô.
6. Código de `start_record`/`stop_record` mostrado é mais longo do que o
   argumento exige (boilerplate repetido).

### 07 — Avaliação
1. QA4/H3 tem cheiro de HARKing — ver achado cross-capítulo #5.
2. Validade externa (sim-to-real) é ~9 linhas contra ~58 da validade de
   construto — desproporcionalmente rasa pra ameaça mais óbvia.
3. Limiar de 25cm reaproveitado do `goal_checker` sem justificativa própria
   para RMSE de trajetória — ver achado cross-capítulo #4.
4. Experimento exploratório de QA4 confunde dois fatores ao mesmo tempo
   (mecanismo de navegação + reset de pose), impedindo atribuição causal
   mesmo como evidência diagnóstica.
5. QA4 não tem critério de validação formal na lista de Critérios de
   Validação — implícito, não dito.

### 08 — Resultados
1. Nenhuma figura no capítulo, apesar do texto mencionar um gráfico de
   sobreposição de trajetórias que existe nos artefatos.
2. QA4 recebe tratamento muito mais fraco que QA1-QA3 (sem tabela, sem
   números sistematizados).
3. Síntese final do capítulo ("respondem afirmativamente às três primeiras
   questões") ignora QA4 completamente, apesar da seção dedicada.
4. Falta argumento contrafactual de que o limiar de 25cm não foi escolhido
   a posteriori pra garantir sucesso (resultado obtido é quase 1 ordem de
   grandeza menor que o limiar).
5. QA3 não amarra explicitamente o número obtido ao limiar de 10% definido
   no Cap. 7 (diferente de QA2, que faz essa amarração).
6. "Integridade dos Bags" fica em nível de checklist, sem conectar de volta
   à validade da reamostragem usada em QA2/QA3.

### 09 — Conclusão
1. "Crise de orquestração experimental" (termo cunhado na Introdução) nunca
   é retomado nominalmente na Conclusão.
2. Camada de agentes de IA aparece como contribuição relevante sem ter sido
   anunciada na Introdução — ver achado cross-capítulo #2.
3. Tensão entre "mecanismos resolvem problemas multi-robô" e a própria
   seção de Limitações (70% de sucesso) — ver achado cross-capítulo #3.
4. O papel do FUUT (motivado em seção inteira da Introdução) nunca é citado
   nominalmente como lacuna nas Limitações.
5. "Trabalhos Futuros" não reflete a prioridade de hardware real que o
   próprio texto declara ("extensão mais urgente") — considerar reestruturar
   em lista, abrindo com esse item.
6. Evidência de PP4 mistura "existência" da interface web com "uso" dela na
   campanha que gerou os números de PP1/PP2 — a campanha real rodou via
   linha de comando, não pela interface.
