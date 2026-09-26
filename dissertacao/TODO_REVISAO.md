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
