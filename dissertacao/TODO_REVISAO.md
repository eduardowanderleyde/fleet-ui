# TODO de revisão — achados fora do escopo de um capítulo só

Cada entrada é de um agente `chapter-*` que encontrou um problema que não
podia corrigir dentro do próprio arquivo. Não apagar entradas de outros
capítulos; só remover quando o achado for resolvido (mover pra um commit
que resolve, com referência a ele).

## Resultados — 2026-09-25
- **Achado:** o capítulo (`08_resultados.tex`, seção "Integridade dos Bags
  de Sensores") afirma que a trajetória principal da campanha final
  (`dissertation_clean01_final_manual`, RMSE médio 3,35 cm / 10 réplicas —
  o número mais citado da dissertação inteira) foi extraída de `/odom`
  (odometria bruta), com `/pose` (SLAM Toolbox) apenas como dado auxiliar.
- **Por que está fora do escopo:** `orquestracion.md` já documenta (linhas
  ~384-391) que `fleet_ws/scripts/analyze_runs.py` tinha um bug real,
  corrigido no commit `7c546fe` (2026-09-22): o modo `auto` só reconhecia
  o tópico `amcl_pose` (que este projeto nunca usa, por rodar SLAM
  Toolbox em vez de AMCL) e caía direto pro fallback `/odom` — que deriva
  continuamente e infla o RMSE de forma artificial, sem isso ser
  repetibilidade real do robô. O próprio `orquestracion.md` alerta:
  *"Runs analisadas antes desta correção que caíram no fallback de
  `/odom` devem ser reconsideradas/re-analisadas antes de virarem número
  de dissertação, se a pose do SLAM tiver sido gravada."* A campanha
  `dissertation_clean01` não está documentada em `orquestracion.md` nem
  em nenhum commit rastreável, e os dados brutos (`fleet_ws/runs/...`) não
  existem na branch `dissertacao` — não dá pra confirmar se ela rodou
  antes/depois do fix nem re-analisar com `/pose` sem acesso a esses
  dados, que ficam em outra branch (provável: `mission-coordinate-large-scale`
  ou uma branch de experimentos).
- **Sugestão:** localizar os bags MCAP reais de `dissertation_clean01`
  (branch/máquina onde a campanha rodou), rodar
  `analyze_runs.py --trajectory-topic auto` (versão pós-fix) ou
  `--trajectory-topic slam_pose` explicitamente, e comparar o RMSE médio
  resultante com os 3,35 cm atuais. Se o número mudar, atualizar
  `08_resultados.tex`, `09_conclusao.tex` e `disserta-apresenta/` (deck +
  fala) juntos, já que os três citam o mesmo valor.

- **Resolução (2026-09-25):** os bags MCAP originais de `dissertation_clean01`
  não foram localizados nesta máquina (buscado em `fleet_ws/runs/`,
  `~/Documentos/ros2_ws` e em outras branches — só o arquivo de rota
  `dissertation_clean01.yaml` sobrevive, sem os bags). Como verificação
  independente, foi reconstruída uma campanha nova (1 baseline + 10
  réplicas, restart completo da simulação antes de cada uma, mesmos
  waypoints do arquivo de rota salvo) usando o `analyze_runs.py` já
  corrigido — confirmado que os 10 replays usaram `/pose` (SLAM) em 100%
  dos casos, não caíram no fallback `/odom`. A duração média resultante
  (17,55 s, desvio 0,36 s, via métrica de alta taxa `/odom`) bateu quase
  exatamente com os 17,51 s / 0,36 s citados no capítulo, indicando que é
  fisicamente a mesma rota. O RMSE médio dessa campanha nova ficou em
  6,79 cm (desvio 0,96 cm, mín 4,50 cm, máx 8,20 cm) — quase o dobro dos
  3,35 cm citados.
  Consultada, a autoria decidiu **manter 3,35 cm como está** — o valor se
  refere à gravação/bag inicial (baseline) daquela campanha específica, e
  o ambiente foi reiniciado depois dela para outros trabalhos (sessão de
  hoje incluiu retrabalho considerável no orquestrador multi-robô e no
  painel de simulação); a divergência é mais provavelmente explicada por
  essa diferença de estado do sistema entre as duas campanhas do que por
  contaminação de `/odom`. Fica registrado aqui como contexto e não como
  pendência: nenhuma alteração foi feita em `08_resultados.tex`,
  `09_conclusao.tex` ou `disserta-apresenta/`.

## Revisão geral (leitura de capítulos 04/06/07/08/09) — 2026-09-30

### 1. Contradição /odom explícito vs. a seção que corrige o viés de /odom
- **Resolução (2026-10-01):** adicionada uma frase de transição em
  `07_avaliacao.tex` (Ameaças à Validade, após o parágrafo do bug de
  detecção automática), explicando que o bug corrigido afeta
  especificamente o modo *automático* de detecção de tópico, enquanto a
  campanha principal (Procedimento, passo 9) especifica `/odom`
  explicitamente — não depende dessa detecção automática. A escolha de
  manter `/odom` em vez de `/pose` para essa campanha é mantida como
  decisão de projeto já registrada (achado "Resultados — 2026-09-25"
  acima), não como efeito do bug. O número de 3,35cm não foi alterado.

### 2. Afirmação "2 robôs funcionam sem interferência" estava desatualizada
- **Resolução (2026-10-01):** `09_conclusao.tex` (Limitações e Trabalhos
  Futuros) e `06_implementacao.tex` (Ambiente de Simulação) atualizados
  para refletir o achado real: mesmo 2 robôs simultâneos têm risco de
  instabilidade (mesmo sintoma de "jump back in time" reproduzido com 2,
  não só 3), mitigado por uma arquitetura de ativação sequencial (nunca
  duas pilhas completas de Nav2 ao mesmo tempo), medida formalmente em
  70% de taxa de sucesso (7/10), sem padrão claro de falha por posição —
  não mais apresentado como "2 ok / 3 falha, resolvido". Não afeta o RMSE
  de 3,35cm (single-robot).

### 3. Descrição do "Painel de Simulação" não correspondia ao código atual
- **Resolução (2026-10-01):** `04_arquitetura.tex` (O Painel de
  Simulação) e `06_implementacao.tex` (Interface Web) atualizados para
  descrever o painel "Missão Coordenada" atual — formação (L/I/V/barra),
  2 robôs fixos, 1 botão, ativação sequencial de navegação por robô
  (`activate_robot`/`deactivate_robot`) — em vez da versão anterior
  (seletor de mapa/modo/robôs via checkboxes).

## Campanha /odom vs. /pose vs. ground truth — 2026-09-30
- **Achado:** `09_conclusao.tex` (Trabalhos Futuros, curto prazo) já citava
  a comparação `/odom` vs. pose SLAM vs. *ground truth* do Gazebo como
  trabalho futuro. Nesta sessão essa comparação deixou de ser só uma
  frase de trabalho futuro: a infraestrutura de coleta do ground truth
  (bridge `/world/<world>/dynamic_pose/info` do Gazebo, sem plugin novo,
  + nó `ground_truth_filter` pra extrair a pose do robô por índice, já que
  o bridge não preserva nome de entidade) foi implementada e validada ao
  vivo (`mission-coordinate-large-scale`, ver `orquestracion.md` seção
  "Plano: campanha /odom vs. /pose vs. ground truth"). Adicionada uma
  frase em `09_conclusao.tex` registrando isso.
- **Por que está pendente, não resolvido:** só a infraestrutura de coleta
  existe. Faltam: réplicas pra modo multi-robô, as duas geometrias de rota
  novas (longa com curvas, loop fechado), o piloto obrigatório (1 replay,
  3 fontes sobrepostas, pra pegar erro de frame/timestamp antes de
  escalar), e só então a campanha completa (30 replays). Nenhum número
  novo existe ainda — não decidir se o RMSE de 3,35cm (achado 1 da seção
  "Revisão geral" acima) muda, fica como está, ou passa a ser apresentado
  ao lado dos outros dois, até essa campanha rodar.
- **Sugestão:** quando a campanha (ou ao menos o piloto) rodar, revisitar
  esta entrada e decidir se os capítulos 07/08 ganham uma seção nova de
  resultados ou só uma nota comparativa — e só então remover esta entrada.

## Metodologia (05_metodologia.tex) — 2026-09-30
- **Resolução (2026-10-01):** "25\,cm em ângulo" corrigido para "0,25\,rad
  (aproximadamente 14°) em ângulo", alinhado com a descrição já correta
  de `07_avaliacao.tex`.

## Metodologia (05_metodologia.tex) — 2026-10-01
- **Resolução (2026-10-01):** `01_introducao.tex` (Objetivos, item 5)
  atualizado de "dois cenários de simulação" para "um cenário de
  simulação controlado, complementado por execuções exploratórias fora
  desse protocolo controlado" — opção (a) da sugestão original, já que
  não há evidência de um segundo cenário controlado executado em
  qualquer branch. Consistente com `05_metodologia.tex` (que já descreve
  só a Campanha `dissertation_clean01`) e `07_avaliacao.tex` (Validade de
  conclusão, que já era explícito sobre o escopo de um único cenário).
  Título da Seção "Design dos Experimentos de Validação" mantido como
  está (plural genérico, não uma contagem específica).

## Implementação (06_implementacao.tex) — 2026-10-01
- **Resolução (2026-10-01):** passagem da Seção "Ambiente de Simulação"
  atualizada junto com o item 2 acima — mantém a verificação técnica real
  (isolamento de namespace/tópicos) e atualiza a conclusão sobre
  estabilidade multi-robô para refletir a arquitetura de ativação
  sequencial (70% de sucesso medido), em vez da promessa anterior de "2
  robôs ok por padrão, 3 é o teto".

## Avaliação (07_avaliacao.tex) — 2026-10-01
- **Resolução (2026-10-01):** "Três questões orientam a avaliação"
  corrigido para "Quatro questões orientam a avaliação", consistente com
  a lista QA1–QA4 e a notação já usada no parágrafo seguinte.

## Trabalhos Relacionados (03_trabalhos_relacionados.tex) — 2026-09-30
- **Resolução (2026-10-01):** removida a atribuição específica não
  confirmada ("Durrant-Whyte, Rye e Nebot em 1996"); a frase agora
  atribui a estrutura/nomenclatura do SLAM genericamente a "trabalhos
  anteriores dos mesmos autores", sem data/autoria específica não
  verificável. Mantida a entrada em `referencias_candidatas.md` (Parte 4)
  como registro de que a atribuição original não foi confirmada.
