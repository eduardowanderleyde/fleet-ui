# Tasks

## 1. Role enforcement

- [ ] 1.1 Criar `_require_muut(robot_id)` em `backend/main.py` — lê
  `_read_robot_roles()`, levanta HTTP 403 se papel != MUUT ou ausente.
  Verificar: teste unitário cobre FUUT, SU e robot_id ausente de
  `roles.yaml`, todos rejeitados.
- [ ] 1.2 Chamar `_require_muut` no topo de `/api/agent/run`,
  `/api/agent/run_fleet` e nos serviços de record/replay que despacham
  movimento. Verificar: requisição pra um robot_id MUUT continua
  funcionando sem mudança de comportamento (teste de regressão existente
  passa).
- [ ] 1.3 Escrever `tests/test_fuut_role_enforcement.py`: 403 pra
  FUUT/SU/ausente, 200 pra MUUT. Verificar: `python3 -m unittest
  tests.test_fuut_role_enforcement` passa.

## 2. Detecção do FUUT (subtração de referência)

- [ ] 2.1 Script `fleet_ws/scripts/fuut_reference_scan.py`: grava um scan
  de referência do `/scan` do FUUT parado, salva em
  `fleet_ws/runs/<run_id>/fuut_reference.json`. Verificar: arquivo gerado
  contém um array de ranges do tamanho esperado do LiDAR.
- [ ] 2.2 Função de detecção: compara scan vivo contra referência, agrupa
  pontos com diferença > 0,17m (raio do TurtleBot4), retorna centróide
  (`distance_m`, `bearing_deg`) do maior cluster. Verificar: teste unitário
  com scan sintético (obstáculo simulado numa posição conhecida) retorna
  distância/direção dentro de 5% do valor esperado.
- [ ] 2.3 Calibrar limiar manualmente na primeira réplica real (ver Riscos
  em design.md) e documentar o valor escolhido no próprio script.
  Verificar: detecção na réplica de calibração encontra exatamente um
  cluster, não zero nem múltiplos.

## 3. Orquestração do piloto

- [ ] 3.1 Editar `fleet_ws/src/fleet_orchestrator/config/roles.yaml`:
  tb2 volta a MUUT→FUUT só durante a execução do piloto (script reverte ao
  final). Verificar: `roles.yaml` lido por `_read_robot_roles()` reporta
  tb2=FUUT durante a execução.
- [ ] 3.2 Script `fleet_ws/scripts/run_fuut_pilot.py`: ativa Nav2 só pra
  tb1 (MUUT) via infraestrutura sequencial existente, mantém tb2 (FUUT)
  sem Nav2, dispara N=3-5 réplicas de record-replay em tb1. Verificar:
  `ros2 node list` confirma Nav2 ativo em tb1 e ausente em tb2 durante a
  execução.
- [ ] 3.3 Capturar a pose `/pose` do MUUT e o scan do FUUT por réplica,
  casados por vizinho mais próximo dentro de 200ms (ver Decisão 4 em
  design.md). Verificar: cada réplica produz um par (`MuutClaim`,
  `FuutObservation` ou "sem correspondência") salvo em
  `fleet_ws/runs/<run_id>/analysis/fuut_pairs.json`.

## 4. Verificação e relatório

- [ ] 4.1 Chamar `FuutVerifier.verify()` (já existe,
  `backend/agents/fuut_verify.py`) pra cada par da réplica. Verificar:
  `TYPESAFE_API_KEY` exportado no shell da execução (pré-requisito —
  shell state não persiste entre chamadas).
- [ ] 4.2 Salvar relatório por réplica (nível, confiança, discrepância
  geométrica/temporal) em
  `fleet_ws/runs/<run_id>/analysis/fuut_verification_report.json`.
  Verificar: arquivo tem uma entrada por réplica executada, nenhuma
  faltando.
- [ ] 4.3 Rodar o piloto completo fim-a-fim (N=3-5) e revisar o relatório
  manualmente. Verificar: ao menos uma réplica tem correspondência
  (nível > 0) — se todas vierem "sem correspondência", a calibração do
  limiar (task 2.3) precisa ser revisitada antes de seguir.

## Workflow follow-up

- Atualizar `dissertacao/chapters/09_conclusao.tex` (Seção Limitações):
  trocar "papel FUUT nunca exercitado, zero evidência empírica" por um
  relato do piloto e seu resultado — fora do escopo deste change de
  código, fica registrado aqui pra não ser esquecido.
- Arquivar este change (`/opsx:archive`) depois que o piloto rodar e o
  relatório for revisado.
