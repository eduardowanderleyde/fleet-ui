# Proposal

## Why

A dissertação (`dissertacao/chapters/09_conclusao.tex`, Seção Limitações)
admite que o papel FUUT (unidade fixa sob teste) nunca foi exercitado:
existe só como arquitetura verificada em software, sem nenhuma evidência
empírica. `roles.yaml` hoje tem os três robôs como MUUT, com o papel
original (FUUT pra tb2, SU pra tb3) preservado só em comentário.

**Correção pós-escrita deste proposal**: a frase original aqui dizia que
"nenhum endpoint ou serviço realmente rejeita um robô FUUT/SU" — isso
estava errado. Só foi checado `backend/main.py` (camada HTTP); o
enforcement real já existe em
`fleet_ws/src/fleet_orchestrator/fleet_orchestrator/main.py::_motion_allowed`
(nó ROS2), com teste (`test_fleet_orchestrator_logic.py`) confirmando
`tb2`/`tb3` já rejeitados — e a própria dissertação (Cap. 6,
06_implementacao.tex) já documenta isso (`ROLE_NOT_ALLOWED`). O gap real
e específico é outro: `_motion_allowed` usa
`self._roles.get(robot_id, "MUUT")` — um `robot_id` não declarado em
`roles.yaml` é tratado como MUUT por padrão (fail-open), não rejeitado.
É esse fail-open que motiva a capability `fuut-role-enforcement` abaixo,
não a ausência total de enforcement.

Fechar essa lacuna antes da defesa, mesmo com N pequeno, muda a frase de
"zero evidência empírica" pra "evidência preliminar" — mudança que pesa
mais numa banca do que qualquer ajuste de texto.

## What Changes

- Papéis FUUT/SU passam a ser **aplicados**, não só declarados: qualquer
  endpoint que emita comando de navegação/movimento rejeita um robô cujo
  papel em `roles.yaml` não seja MUUT.
- Um script de campanha roda um piloto MUUT+FUUT real: tb1 (MUUT) executa
  record-replay normal na infraestrutura de ativação sequencial já
  existente (`activate_robot_nav.launch.py`); tb2 (FUUT) fica com Nav2
  nunca ativado, só sensores/SLAM coletando, observando a cena.
- As observações do FUUT e as poses reivindicadas pelo MUUT, por réplica,
  alimentam o `FuutVerifier` já existente (`backend/agents/fuut_verify.py`)
  — construído nesta sessão, nunca antes rodado contra dados reais de uma
  campanha.
- Um relatório de verificação por réplica (nível de corroboração,
  confiança, z-score geométrico) é gerado e salvo junto aos artefatos da
  campanha, no mesmo padrão de `fleet_ws/runs/<run_id>/analysis/`.

## Capabilities

### New Capabilities
- `fuut-role-enforcement`: papéis declarados em `roles.yaml` (MUUT/FUUT/SU)
  passam a restringir de fato quais robôs podem receber comandos de
  movimento/navegação, em vez de só documentar a intenção.
- `fuut-pilot-campaign`: execução de uma campanha com MUUT ativo e FUUT
  observando, coleta sincronizada das duas fontes, e geração de um
  relatório de verificação via `FuutVerifier` por réplica.

### Modified Capabilities
(nenhuma — não há spec existente para modificar; este é o primeiro change
do projeto.)

## Impact

- `backend/main.py`: endpoints que hoje aceitam `robot_id` pra comandos de
  movimento (`/api/agent/run`, `/api/agent/run_fleet`, serviços de
  record/replay) precisam checar o papel antes de despachar.
- `fleet_ws/src/fleet_orchestrator/config/roles.yaml`: ao menos um robô
  (tb2) precisa voltar a ser declarado FUUT pra rodar o piloto — hoje está
  temporariamente MUUT "pra demo multi-robô".
- Novo script em `fleet_ws/scripts/` pra orquestrar o piloto e chamar o
  `FuutVerifier` sobre os dados coletados.
- `dissertacao/chapters/09_conclusao.tex` (Seção Limitações): a frase sobre
  "papel FUUT nunca exercitado" precisa ser atualizada depois que o piloto
  rodar — fora do escopo deste change (é trabalho de redação, não de
  código), fica registrado aqui pra não ser esquecido.
