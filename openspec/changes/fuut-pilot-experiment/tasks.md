# Tasks

## 1. Role enforcement

- [x] 1.1 Criar `_require_muut(robot_id)` em `backend/main.py` — lê
  `_read_robot_roles()`, levanta HTTP 403 se papel != MUUT ou ausente.
  Verificar: teste unitário cobre FUUT, SU e robot_id ausente de
  `roles.yaml`, todos rejeitados.
- [x] 1.2 Chamar `_require_muut` no topo de `/api/agent/run`,
  `/api/agent/run_fleet` e nos serviços de record/replay que despacham
  movimento. Verificar: requisição pra um robot_id MUUT continua
  funcionando sem mudança de comportamento (teste de regressão existente
  passa).

  Nota de implementação: o check foi colocado nos 4 endpoints de baixo
  nível (`start_record`, `stop_record`, `play_route`, `go_to_point`), não
  dentro de `/api/agent/run`/`run_fleet` diretamente — confirmado em
  `backend/agents/executor.py` que o agente despacha movimento via HTTP
  pra esses mesmos 4 endpoints, então o enforcement cobre os dois
  caminhos (UI direta e camada de agente) num único ponto, como o
  design.md já pretendia ("chamado no topo de cada endpoint que
  despacha movimento").
- [x] 1.3 Escrever `tests/test_fuut_role_enforcement.py`: 403 pra
  FUUT/SU/ausente, 200 pra MUUT. Verificar: `python3 -m unittest
  tests.test_fuut_role_enforcement` passa. (8/8 passou, suíte completa
  92 testes sem regressão.)

## 2. Detecção do FUUT (subtração de referência)

- [x] 2.1 Script `fleet_ws/scripts/fuut_reference_scan.py`: grava um scan
  de referência do `/scan` do FUUT parado, salva em
  `fleet_ws/runs/<run_id>/fuut_reference.json`. Verificar: arquivo gerado
  contém um array de ranges do tamanho esperado do LiDAR. (Verificado com
  rclpy real — `tests/test_fuut_reference_scan.py` publica um `/scan`
  fake num nó separado e confirma a captura; não precisa de Gazebo pra
  isso, só de um tópico `/scan` publicando.)
- [x] 2.2 Função de detecção: compara scan vivo contra referência, agrupa
  pontos com diferença > 0,17m (raio do TurtleBot4), retorna centróide
  (`distance_m`, `bearing_deg`) do maior cluster. Verificar: teste unitário
  com scan sintético (obstáculo simulado numa posição conhecida) retorna
  distância/direção dentro de 5% do valor esperado. (5/5 testes,
  `fleet_ws/scripts/fuut_detection.py` + `tests/test_fuut_detection.py`.)
- [x] 2.3 Calibrar limiar manualmente na primeira réplica real (ver Riscos
  em design.md) e documentar o valor escolhido no próprio script.
  Verificar: detecção na réplica de calibração encontra exatamente um
  cluster, não zero nem múltiplos.

  Resultado real (3 réplicas, runs/fuut_pilot01/): o limiar de 0,17m
  (raio do TurtleBot4) encontrou exatamente 1 cluster em todas as 3
  réplicas. Primeira rodada completa (sem correção) deu discrepância
  geométrica de ~2,7-2,9m, consistente entre réplicas — não era ruído
  aleatório, era sistemático. Decompondo o erro por componente: a
  distância detectada já batia com a geometria real (~2,0-2,15m); só a
  direção (bearing) estava sempre ~87-90° fora do esperado nas 3
  réplicas (87,2°/88,5°/89,7° — ver cálculo), assinatura clara de
  offset de montagem do LiDAR relativo ao eixo frontal do `base_link`,
  nunca verificado contra o URDF. Aplicada uma correção empírica de
  +90° (`FUUT_LIDAR_YAW_OFFSET_DEG` em run_fuut_pilot.py, documentada
  como medida empiricamente, não lida do URDF) e re-executado: a
  discrepância geométrica caiu pra 3,1-5,9cm nas 3 réplicas — dentro do
  ruído de sensor esperado. TypeSafe reclassificou as 3 réplicas de
  "correspondência fraca" (confiança 0,1-0,41) para "correspondência
  forte" (confiança 0,86-0,96). Fica como trabalho futuro imediato
  (não bloqueante): confirmar os 90° contra o transform real
  `lidar_link` → `base_link` do URDF, em vez de depender só da
  calibração empírica feita aqui.

## 3. Orquestração do piloto

- [x] 3.1 Editar `fleet_ws/src/fleet_orchestrator/config/roles.yaml`:
  tb2 volta a MUUT→FUUT só durante a execução do piloto (script reverte ao
  final). Verificar: `roles.yaml` lido por `_read_robot_roles()` reporta
  tb2=FUUT durante a execução. (`_RolesOverride` em run_fuut_pilot.py —
  troca no `__enter__`, restaura no `__exit__` mesmo em exceção; conteúdo
  original confirmado restaurado ao final de todas as 5 execuções reais.)
- [x] 3.2 Script `fleet_ws/scripts/run_fuut_pilot.py`: ativa Nav2 só pra
  tb1 (MUUT) via infraestrutura sequencial existente, mantém tb2 (FUUT)
  sem Nav2, dispara N=3-5 réplicas de record-replay em tb1. Verificar:
  `ros2 node list` confirma Nav2 ativo em tb1 e ausente em tb2 durante a
  execução.

  Verificado por evidência indireta, não por `ros2 node list` ao vivo
  durante a execução (os processos já tinham sido mortos no `finally` do
  script quando a verificação foi escrita): `activate_tb1_attempt0.log`
  mostra "Managed nodes are active" só pra tb1 (único namespace que o
  script chama em `activate_robot_nav.launch.py namespace:=tb1`); tb2
  nunca teve esse launch chamado, então nunca teve Nav2 ativado — decorre
  da lógica do script, não de uma observação ao vivo do estado dos nós.
- [x] 3.3 Capturar a pose `/pose` do MUUT e o scan do FUUT por réplica,
  casados por vizinho mais próximo dentro de 200ms (ver Decisão 4 em
  design.md). Verificar: cada réplica produz um par (`MuutClaim`,
  `FuutObservation` ou "sem correspondência") salvo em
  `fleet_ws/runs/<run_id>/analysis/fuut_pairs.json`.

  Desvio deliberado do caminho: salvo em `fleet_ws/runs/<run_id>/
  fuut_verification_report.json` (sem subdiretório `analysis/`), com o
  par `muut_claim`/`fuut_observation` embutido em cada entrada do
  relatório, não num `fuut_pairs.json` separado — simplificação que
  ainda satisfaz o requisito (par recuperável por `replicate_id`), só
  não literalmente o caminho descrito aqui. Scans crus do FUUT por
  réplica também persistidos separadamente em `fuut_samples_r0N.json`
  (não previsto originalmente nesta task, adicionado ao perceber que a
  observação do FUUT só existia em memória — ver nota do commit
  `3844c6a`).

## 4. Verificação e relatório

- [x] 4.1 Chamar `FuutVerifier.verify()` (já existe,
  `backend/agents/fuut_verify.py`) pra cada par da réplica. Verificar:
  `TYPESAFE_API_KEY` exportado no shell da execução (pré-requisito —
  shell state não persiste entre chamadas). (5 execuções reais, todas
  com a env var exportada manualmente na mesma chamada do launch.)
- [x] 4.2 Salvar relatório por réplica (nível, confiança, discrepância
  geométrica/temporal) em
  `fleet_ws/runs/<run_id>/analysis/fuut_verification_report.json`.
  Verificar: arquivo tem uma entrada por réplica executada, nenhuma
  faltando. (Mesmo desvio de caminho da 3.3 — sem `analysis/`. 3
  entradas pra 3 réplicas executadas, nenhuma faltando.)
- [x] 4.3 Rodar o piloto completo fim-a-fim (N=3-5) e revisar o relatório
  manualmente. Verificar: ao menos uma réplica tem correspondência
  (nível > 0) — se todas vierem "sem correspondência", a calibração do
  limiar (task 2.3) precisa ser revisitada antes de seguir.

  Resultado final real (`fleet_ws/runs/fuut_pilot01/fuut_verification_report.json`,
  após a correção de bearing da task 2.3): 3/3 réplicas com
  correspondência, todas classificadas "correspondência forte" pelo
  TypeSafe — níveis 2,87/2,95/2,95 (escala 0-3), confiança 0,86/0,95/0,96,
  discrepância geométrica 3,1cm/5,9cm/4,8cm (bem dentro do ruído de sensor
  esperado), discrepância temporal 0,0s nas 3. Primeira evidência empírica
  real do papel FUUT nesta dissertação — fecha a lacuna "zero evidência"
  do Cap. 9 com evidência preliminar forte, não ambígua.

## Workflow follow-up

- Atualizar `dissertacao/chapters/09_conclusao.tex` (Seção Limitações):
  trocar "papel FUUT nunca exercitado, zero evidência empírica" por um
  relato do piloto e seu resultado — fora do escopo deste change de
  código, fica registrado aqui pra não ser esquecido.
- Arquivar este change (`/opsx:archive`) depois que o piloto rodar e o
  relatório for revisado.
