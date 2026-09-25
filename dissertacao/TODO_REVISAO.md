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
