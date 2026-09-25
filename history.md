# Histórico — branch `mission-coordinate-large-scale`

Log de trabalho da branch: o que foi feito, por quê, e a linha do tempo de
commits desde que ela divergiu de `main` (2026-09-17). Objetivo: qualquer
sessão futura (humana ou de IA) consegue reconstruir o raciocínio sem
precisar reler todos os diffs.

---

## 2026-09-25 (sessão da tarde) — modo single-robot: hang do backend + pose/mapa nunca apareciam

**Pedido:** rodar a simulação com 1 robô só (`mode=single`), nunca testado
ao vivo nesta branch antes (só multi-robô).

**Bug 1 — backend travava ao lançar `single`:** `/api/status` voltava
`robots:[]` e sem as chaves `nav2_ready`/`nav2_ready_robots` (ausentes, não
só vazias), mesmo com a simulação, Nav2 e orquestrador genuinamente vivos
(confirmado via `ros2 node list`/`ros2 action list` direto no container).
Causa real: durante o diagnóstico eu mesmo dei `pkill` no processo do
backend pra depurar, o que deixou resíduo de estado DDS/shared-memory no
container — o próximo `rclpy.init()` no mesmo domínio ficava pendurado
indefinidamente. **Fix:** nada de código — um `docker compose restart`
limpo (sem matar processo manualmente depois) resolveu; `nav2_ready`
voltou a `true` em <30s. Lição operacional: nesta branch, com
`AUTOSTART_SIM=false`, a simulação roda como processo-filho do *mesmo*
container do backend — `docker compose restart` mata os dois juntos agora
(diferente da arquitetura antiga, onde a sim tinha vida própria).

**Bug 2 — pose/mapa do robô único nunca ficavam disponíveis:** mesmo com o
backend saudável, `/api/status` retornava `pose.valid:false` pra sempre e
`/api/map` retornava `available:false`, apesar do robô navegando de
verdade (`go_to_point` funcionando, `tf2_echo map base_link` confirmando
posição real). Causa: `backend/main.py` só chamava `_setup_robot(rid)` — a
função que assina `/tf`, `/{id}/amcl_pose`, `/{id}/map` — para
`rid in _ROBOTS` (de `FLEET_ROBOTS`, default `tb1,tb2`). O modo single usa
`robot_id=""` (tópicos **sem** prefixo: `/tf`, `/map`, não `/tb1/tf`), que
nunca era registrado. **Fix:** chamar `_setup_robot("")` sempre, além do
loop em `_ROBOTS`. Depois, um segundo bug relacionado: o robô "padrão"
usado por `/api/map` e pelo campo `pose` (singular) de `/api/status`
dependia de `_sim_state["mode"] == "single"` — mas `_sim_state` é memória
do processo do backend, que eu tinha acabado de reiniciar pra carregar o
fix, então voltou a `None`. Troquei pra derivar de
`_fleet_status["robots"]` (populado ao vivo via tópico `/fleet/status`,
sobrevive a restart do backend): se só existe 1 robô reportado, usa o
`robot_id` dele.

**Bug 3 — frontend escondia o robô mesmo com o backend já certo:**
`App.jsx` calculava o robô "efetivo" a mostrar com
`status.robots?.[0]?.robot_id || 'tb1'` — `||` trata string vazia como
falsy, então `robot_id=""` (válido, modo single) sempre virava `'tb1'`
hardcoded, escondendo o robô mesmo com pose/mapa corretos vindo do
backend. **Fix:** trocado pra `??` (nullish coalescing), que só cai no
fallback se for `null`/`undefined` de verdade.

**Verificação:** confirmado visualmente no navegador — marcador do robô na
pose real, grid de SLAM (pontos brancos do lidar) renderizado sobre o
floor plan do warehouse, `/api/map` retornando grid 443×301px real.

**Nota solta, não é bug novo:** `nav2_ready` pisca `true`/`false` a cada
~3s porque o `ros2 action list` usado pra checar o Nav2 leva ~2,4s nesta
máquina (Ryzen 3 PRO 4350G, mais fraca que a máquina Linux nativa — ver
`orquestracion.md`), no limite do timeout de 3s do código. Cosmético, não
bloqueia nada; não mexido ainda.

**Arquivos alterados:** `backend/main.py` (`_setup_robot("")` sempre
chamado; `_default_robot_id()` novo, deriva de `_fleet_status["robots"]`
em vez de `_sim_state`), `frontend/src/App.jsx` (`??` em vez de `||` no
cálculo de `effectiveRobotId`).

---

## Linha do tempo de commits (resumida, mais antigo → mais recente)

### 2026-09-17 — camada de agentes de IA
- `76c48ee` Camada de orquestração por agentes de IA sobre a API do Fleet UI.
- `4d3e44f` Expõe a orquestração de agentes como endpoint do backend.
- `ae4768f` Agentes escopados por robô (cada agente só mexe no seu robô).

### 2026-09-18 — 3 robôs na simulação
- `62d8338` UI pra disparar e monitorar a frota de 3 agentes.
- `adb14e8` Suporte a simulação Gazebo com 3 robôs (tb1/tb2/tb3).
- `c77600f` Documenta a orquestração de agentes + simulação multi-robô.

### 2026-09-22 — multi-robô real: Docker, DDS, teto de robôs
- `ef2a287` Corrige build Docker no Windows; adiciona modo headless multi-robô.
- `7587d92` Corrige assinaturas de mapa/pose do backend pro caso multi-robô.
- `5dce304` Corrige flakiness de discovery DDS; troca sleeps fixos por polling.
- `c31b364` Reduz frequência do local_costmap pra sim de 3 robôs; documenta 2 becos sem saída (h_samples do lidar, controller_frequency).
- `762f5a4` Nº de robôs simulados vira configurável via `FLEET_ROBOTS`, default 2.
- `62f6fbe` Mapa/pose passam a ser rastreados por robô, não mais 1 robô fixo.
- `ccf859a` Fecha o ciclo planner→campanha→análise com `run_campaign`.
- `b20186a` Histórico de jobs dos agentes sobrevive a restart do backend.
- `b1a4b2f` Corrige NameError em `replay --repeat`; documenta arquitetura/qualidade.
- `de4f0c0` Testes automatizados pro lado ROS do trabalho multi-robô.
- `a9923df` `diagnose_experiment`: levanta hipótese de por que uma run falhou.
- `4849835` TL;DR em linguagem simples no `orquestracion.md`.
- `dae7245` MapView desenha todos os robôs, não só o selecionado.
- `a5db2c0` Corrige `/api/list_robots` e `/api/list_routes` sempre vazios.
- `c72a174` Corrige diagnóstico do teto de 3 robôs: GPU existe e está em uso (não é CPU-bound puro).
- `ec98248` Confirma identidade da GPU; Nav2/SLAM rodam só em CPU mesmo.
- `0013675` Documenta teste reprodutível de falha com 3 robôs → decisão de manter 2.
- `7c546fe` Corrige `analyze_runs.py`: auto-detecção ignorava a pose do SLAM Toolbox (inflava RMSE por deriva de odometria, não por falta de repetibilidade real).
- `207a9f4` Documenta validação da métrica de repetibilidade (pose vs odom, MPPI estocástico como fonte de variância esperada).

### 2026-09-23 — campanha real com 2 robôs
- `c6517b8` Documenta que record e replay navegam por mecanismos diferentes (go_to_point vs play_route) — explica gap de RMSE.
- `cdd6eff` Documenta campanha real com 2 robôs simultâneos + lição sobre processo órfão antigo.

### 2026-09-24 — CI de verdade, licença, painel de Simulação
- `187ce21` Job de CI com ROS 2 real: badge verde deixa de mentir sobre a parte ROS.
- `b1c3a6c` Corrige CI: job "checks" não instalava fastapi, quebrando 3 testes.
- `8acb500` Corrige job ros-checks: faltava `fix_ament_hooks.sh` após colcon build.
- `9900a07` Corrige job ros-checks: mesma lista de deps incompleta do job checks.
- `f5cc4ff` Adiciona LICENSE (MIT).
- `236d678` `backend/requirements.lock.txt` com versões exatas pinadas.
- `f4ba946` Documenta snapshot do ambiente exato testado (ROS Jazzy, Gazebo Harmonic...).
- `fc39799` README aponta pro `orquestracion.md`; badges de CI/licença; corrige lista de pacotes ROS.
- `54f882e` Painel "Simulação" no Fleet UI: escolher mapa/robô e lançar pela tela.
- `c9b07c7` Formação coordenada no painel (1 ponto de destino por robô).
- `d130f7d` Painel simplificado: 1 botão por formação, mais formatos, 2 ou 3 robôs.
- `2145672` Log técnico escondido por padrão no painel, atrás de um toggle.
- `253b4d9` Status/log da simulação move pro painel Output existente.
- `68f5714` Painel de Simulação ancorado fixo no canto superior direito.
- `bbe55e0` Painel de Simulação sempre visível, sem botão pra abrir/fechar.
- `d458c8c` Painel "Missão Coordenada" redesenhado: 1 dropdown, 3 robôs fixos, log simples.
- `291015d` Clicar-no-mapa-adiciona-waypoint desligado por padrão.
- `a720a1f` Rede de segurança no stop da simulação: mata processos órfãos.

### 2026-09-25 (manhã) — painel Missão Coordenada, arquitetura Docker
- `140c069` Corrige painel: robô com falha aparecia como "chegou" (falso positivo).
- `8bb6252` Documenta painel Missão Coordenada; reconfirma teto de 3 robôs.
- `a9ab502` Documenta falha do Nav2 com só 2 robôs sob carga alta da máquina.
- `3de8e2e` Simulação para de auto-lançar no boot do Docker; painel passa a ser dono do ciclo de vida dela — base pra poder reiniciar só o backend sem matar a sim (usado no bug 1 desta sessão).
- `6089c39` Painel Missão Coordenada volta a default de 2 robôs, não 3.
- `a511898` Corrige `/api/simulation/status` "ready" nunca virando `true` (log-scraping frágil → cruza com `nav2_ready_robots`, já confiável).
- `6fc0ea3` Alinha marcadores de pose multi-robô no mesmo mapa (corrige sobreposição no spawn — cada robô fazia SLAM em referencial próprio).
- `d2e42fd` Documenta que os testes de Docker/Windows de hoje rodaram numa máquina bem mais fraca que a documentada em `orquestracion.md` (não misturar os números de %CPU).

### 2026-09-25 (tarde) — este arquivo
- Ver seção "Sessão de hoje" no topo: fix de pose/mapa e hang no modo single-robot.
