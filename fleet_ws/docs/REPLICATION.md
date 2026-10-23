# Como replicar a campanha oficial reportada no Capítulo 8

Este documento é diferente do [`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md)
(que explica o fluxo *genérico* de record/replay/analyze) e do
[`README.md`](../../README.md) (que explica como instalar/rodar o projeto em
desenvolvimento). Aqui o foco é **especificamente** a campanha controlada final
citada na dissertação (`dissertation_clean01`, Capítulo 8, Seções QA1/QA2),
estruturado nos 4 eixos de replicabilidade de Lier et al. (2017), "Can we
Reproduce it?" — a referência usada pelo agente `experiment-artifact-publishing`
(ver `conhecimento/artifact_publishing.md`).

## Os dados originais (recuperados em 2026-10-22)

Em 2026-10-02 este documento afirmava que os dados brutos da campanha
tinham sido perdidos. **Não tinham:** os arquivos de análise e de execução
(`summary.json`, CSVs de trajetória, exports JSON por replay, manifesto,
logs) estavam guardados num `git stash` local de 2026-09-17 (commit
`5b0a82e`, arquivos não rastreados), e foram restaurados em
`fleet_ws/runs/dissertation_clean01_final_manual/`. Os 10 bags MCAP
(`collections/default/2026-09-15_01-*`, listados em `rosbag_path` de cada
export) continuam no disco da máquina de desenvolvimento, fora do git
(`collections/` é gitignored) — **faça backup deles**.

**Reprodução verificada (2026-10-22):** rodando a análise de novo sobre esses
10 bags, os números do Capítulo 8 saem idênticos (diferença ≤ 4·10⁻¹⁵ m,
ruído de ponto flutuante), tanto com a versão do script da época (`14fc0d3`)
quanto com a atual, **desde que se force a fonte `/odom`**:

```bash
python3 scripts/analyze_runs.py <os 10 bags, na ordem dos replays> \
  --output-dir runs/reanalise/ --resample-mode time --resample-samples 100 \
  --trajectory-topic odom
```

Sem `--trajectory-topic odom`, a versão atual escolhe sozinha o `/pose` do
SLAM (mudança de 2026-09-22, `7c546fe`, posterior à campanha) e os números
mudam — não por erro, por ser outra fonte de trajetória.

O commit exato usado na campanha não foi registrado na época. A partir de
2026-10-02, toda execução de `experiment_repeatability.py` grava o commit e
se a árvore estava suja (`"git": {"commit": ..., "dirty": ...}` no JSON).

## 1. Artefatos técnicos exatos

- **Software:** ROS 2 Jazzy, Nav2, SLAM Toolbox, Gazebo Harmonic — ver lista
  completa de pacotes no [`README.md`](../../README.md#ros-2-simulation-packages).
  Essa mesma lista é validada em CI (`ros-checks`, `.github/workflows/ci.yml`)
  contra um container `osrf/ros:jazzy-desktop` limpo a cada push — é a
  garantia mais forte disponível de que a lista basta.
- **Commit:** não pinado para a campanha original (lacuna acima). Para
  qualquer campanha nova, o commit fica registrado automaticamente no JSON
  de export de cada replay — não é preciso anotar manualmente.
- **Rota:** `fleet_ws/routes/default/dissertation_clean01.yaml` (existe no
  repositório).
- **Mundo:** `warehouse` (default do `turtlebot4_sim.launch.py`).

## 2. Design do experimento

- **Protocolo:** 1 baseline + 10 replays independentes da mesma rota,
  `protocol_id=dissertation_clean01`, modo single-robot.
- **Métrica primária:** RMSE par-a-par entre execuções que compartilham o
  mesmo mecanismo de navegação (não RMSE contra uma baseline gravada por um
  mecanismo distinto) — decisão metodológica justificada na Seção
  "Validação Preliminar do Protocolo" do Capítulo 8, citando Maset et al.
  (2022) (`maset2022` em `referencias.bib`).
- **Por que N=10 e intervalo de confiança via t de Student, não bootstrap:**
  ver `conhecimento/stats_methodology.md` — bootstrap só supera o t de
  Student a partir de ~25 amostras.

## 3. Execução repetível

Pré-requisitos e instalação: [`README.md`](../../README.md). Com a stack de
pé (Terminais 1–3 do README), uma campanha nova e comparável roda assim:

```bash
cd ~/fleet-ui/fleet_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash

# baseline
python3 scripts/experiment_repeatability.py record \
  --single-robot --route dissertation_clean01 \
  --protocol-id dissertation_clean01 --condition baseline \
  --export runs/nova_campanha/baseline.json

# 10 replays independentes
python3 scripts/experiment_repeatability.py replay \
  --single-robot --route dissertation_clean01 \
  --repeat 10 --protocol-id dissertation_clean01 \
  --export runs/nova_campanha/replay.json
```

Cada replay relança a pilha (simulação, Nav2, orquestrador, coletor) antes de
rodar — mesmo procedimento descrito no Capítulo 8. Ver
[`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) para o fluxo genérico
passo a passo (inclui como lidar com estado inicial, rastrear o bag de cada
run, etc.) caso algo aqui precise de mais detalhe.

## 4. Avaliação reprodutível dos dados

```bash
python3 scripts/analyze_runs.py \
  collections/default/nova_campanha/*.mcap \
  --output-dir runs/nova_campanha/analysis/ \
  --resample-mode time --resample-samples 100 --trajectory-topic odom
```

(`--trajectory-topic odom`: a mesma fonte usada no Capítulo 8.)

Saída: `summary.json` (RMSE par-a-par, erro de endpoint),
`trajectory_overlay.png`. Esse é exatamente o par de arquivos citado nas
Tabelas do Capítulo 8 — só que gerados a partir da campanha nova, não da
original (perdida).

## O que fazer se os números não baterem exatamente com o Capítulo 8

Esperado: o MPPI do Nav2 é estocástico por padrão
(`regenerate_noises: true`, ver `conhecimento/nav2_tracking.md` e a env var
`NAV2_MPPI_REGENERATE_NOISES`) — repetir a campanha não deve reproduzir os
mesmos valores exatos de RMSE, só a mesma ordem de grandeza e as mesmas
conclusões qualitativas (RMSE entre réplicas << tolerância de 25cm do Nav2).
Isso é esperado e documentado, não um sinal de erro na replicação.
