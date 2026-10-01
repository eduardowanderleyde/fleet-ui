# Sugestões de conteúdo/argumentação — leitura tipo banca (2026-10-01)

Gerado por 9 agentes (um por capítulo, rodados em paralelo), cada um só lendo
e analisando — complementar à revisão bibliográfica/redação já feita antes.
Foco em conteúdo e argumentação, no papel de um avaliador de banca de
mestrado.

**Atualização (2026-10-01):** quase todos os itens abaixo foram aplicados
diretamente, em duas rodadas: primeiro os 6 achados cross-capítulo, depois
o restante das sugestões por capítulo (também em paralelo, um agente por
arquivo). Em todos os casos a regra foi: nunca inventar número, figura,
cálculo estatístico ou citação que não pôde ser confirmada contra o código
real, `orquestracion.md` ou `referencias.bib` — onde não havia como
confirmar, a opção foi reconhecer a limitação honestamente em vez de
fabricar rigor. Só **3 itens** ficaram de fora (marcados ⏭️ abaixo),
por exigirem decisão de reestruturação maior do autor.

## Achados cross-capítulo mais sérios

1. ✅ **Overclaiming de "multi-robô"** na Tabela de Síntese Comparativa —
   célula trocada de ✓ pleno para "Parcial" + nota de rodapé.
2. ✅ **Camada de agentes de IA nunca anunciada na Introdução** — adicionada
   em Contribuições de Engenharia e na Organização da Dissertação.
3. ✅ **Tensão "2 robôs resolvido" vs. "70% de sucesso"** — frase
   distinguindo problema de API/namespace (resolvido) de sincronização
   temporal (mitigado, não resolvido pelos mesmos mecanismos).
4. ✅ **Limiares reaproveitados sem justificativa própria** (25cm do
   `goal_checker`; CV_t 5%→10%) — relação entre os números explicitada.
5. ✅ **QA4/H3 com cheiro de HARKing** — reforçada defesa metodológica como
   *hypothesis-generating*, não confirmatória.
6. ✅ **AMCL com promessas de uso futuro que nunca se confirmavam** —
   afirmação falsa removida; proposta adicionada de fato em Trabalhos
   Futuros.

## Por capítulo

### 01 — Introdução — ✅ todos os 5 itens aplicados
Restrição single-robot tornada proeminente em Escopo e Restrições; H1
restringido à classe de protocolos efetivamente testada (generalização
movida para trabalho futuro); H3 explicitamente marcada como
qualitativa/exploratória, diferente do critério numérico de H2; camada de
agentes anunciada (cross-capítulo #2); parágrafo novo diferenciando a
"crise de orquestração experimental" da literatura já citada na mesma
seção.

### 02 — Fundamentação Teórica — ✅ 5 de 6 aplicados
AMCL corrigido (cross-capítulo #6); nova seção curta de Coordenação
Multi-Robô (centralizado/descentralizado, MRTA) antes de Métricas de
Repetibilidade; CV_t explicitado (cross-capítulo #4); redundância
grafos-vs-partículas removida da primeira menção; EKF-SLAM introduzido
como terceira família, preparando o Cap. 3.
- ⏭️ **Item 6 pendente** (Behavior Trees/recovery nunca revisitados): exigiria
  confirmar nos logs/bags reais que nenhum recovery disparou nos 10
  replays — dado que não tenho acesso direto nesta sessão. Fica para o
  autor verificar e adicionar, se confirmado.

### 03 — Trabalhos Relacionados — ✅ 5 de 6 aplicados
Overclaiming corrigido (cross-capítulo #1); parágrafo de síntese analítica
adicionado após a tabela; linhas de amigoni2010/guevaravega2024 removidas
da tabela (survey ≠ sistema comparável); generalização sociológica
reformulada como leitura do autor, ancorada mais estreitamente em
albonico2023; limiar de H2 (30cm) conectado aos números de referência do
capítulo (Pure Pursuit ~5cm, Maset2022 ~2cm), como observação em aberto.
- ⏭️ **Item 3 pendente** (colunas da tabela não capturam a contribuição mais
  distintiva — MUUT/FUUT/SU): deixado de propósito, por ser reestruturação
  de tabela que muda o que está sendo comparado — decisão do autor.

### 04 — Arquitetura do Framework — ✅ 5 de 6 aplicados
Tricotomia MUUT/FUUT/SU justificada contra alternativa mais simples;
redundância com o Cap. 6 removida (painel de simulação: mantida só a
decisão/razão, mecânica movida pra implementação); parágrafo de requisitos
não-funcionais adicionado antes das 5 camadas; alternativa MCP discutida
na seção de agentes (citando o texto real de `orquestracion.md`); modelo
estático de papéis (`roles.yaml`) reconhecido como fronteira de design
deliberada.
- ⏭️ **Item 2 pendente** (trade-off REST-vs-rosbridge no capítulo errado):
  não movido. Caberia um parágrafo de custo/benefício na Seção do Backend
  REST (hoje só diz "simplicidade"), com o número de latência que hoje só
  existe no Cap. 6 — decisão do autor sobre mover ou duplicar.

### 05 — Metodologia Experimental — ✅ todos os 6 itens aplicados
N=10 reconhecido como escolha prática (custo/tempo), não cálculo de poder
estatístico; "comprimento de percurso" adicionado como 5ª métrica, com
definição confirmada no código real (`_path_length` em `analyze_runs.py`);
exclusão de heading/orientação justificada (rota retilínea); normalização
temporal justificada contra DTW/Fréchet; limiar do filtro de saltos
(0,12m@50Hz) reconhecido como desproporcional à velocidade real (~0,05m/s,
confirmada na Tabela 8.1); atrasos fixos 8s/12s reconhecidos como risco de
replicabilidade entre máquinas.

### 06 — Implementação — ✅ todos os 6 itens aplicados
Código real da agregação do RMSE médio adicionado (confirmado em
`backend/agents/analyst.py` e `analyze_runs.py` — inclusive uma ressalva
nova: a média é sobre RMSE-vs-referência, não sobre a matriz pairwise
completa); lacuna de `samples=100` reconhecida sem teste fabricado; cadeia
de fallback `amcl_pose > pose > odom` ganhou subseção própria com código
real; afirmação de "desserialização CDR sem tipo registrado" **removida**
por ser factualmente incorreta (código real sempre usa tipo conhecido —
achado novo, não estava em SUGESTOES_BANCA originalmente); redundância do
buffer de TF com o Cap. 4 reduzida a uma remissão; boilerplate de
`start_record`/`stop_record` elidido.

### 07 — Avaliação — ✅ todos os 5 itens aplicados
HARKing de QA4 endereçado (cross-capítulo #5); Validade Externa expandida
com discussão real de sim-to-real/reality gap (slip de roda, ruído de
LiDAR, jitter de MPPI — sem citação nova, pois não há nenhuma aprovada
sobre o tema em `referencias.bib`); limiar de 25cm explicitado
(cross-capítulo #4); confundimento de dois fatores em QA4 nomeado
explicitamente como limitação de desenho, com desenho fatorial mínimo
esboçado como trabalho futuro; ausência de critério formal para QA4
explicada.

### 08 — Resultados — ✅ todos os 6 itens aplicados
Figura ausente reconhecida com frase honesta (sem fabricar gráfico);
QA4 reconhecido como tratado qualitativamente, sem números fabricados para
os 2 conjuntos sem dado confirmável; síntese final fecha o ciclo de QA4;
argumento contrafactual do limiar de 25cm adicionado; QA3 amarrado ao
limiar de 10% (CV calculado a partir dos números reais já no texto,
~2,1%); Integridade dos Bags conectada à validade da reamostragem
(variação real de ~7,6% entre bags).

### 09 — Conclusão — ✅ todos os 6 itens aplicados
"Crise de orquestração experimental" retomada explicitamente na Síntese
das Contribuições; camada de IA anunciada (cross-capítulo #2); tensão
mecanismos-vs-70% endereçada (cross-capítulo #3); papel do FUUT nunca
exercitado adicionado como limitação nomeada; "Trabalhos Futuros, Curto
prazo" reestruturado de prosa corrida para lista, abrindo com hardware
real; PP4 esclarecido como evidência de disponibilidade, não de uso
efetivo na campanha que gerou os números de PP1/PP2.

## O que ainda fica para o autor decidir

Só 3 itens, todos de reestruturação (não de fato/argumento):
1. Behavior Trees/recovery (Cap. 02) — precisa confirmar nos logs reais.
2. Colunas da tabela comparativa (Cap. 03) — mudaria o que é comparado.
3. Mover trade-off REST-vs-rosbridge pro capítulo certo (Cap. 04) — decisão
   de onde cada coisa deveria viver.
