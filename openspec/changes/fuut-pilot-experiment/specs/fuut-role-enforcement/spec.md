# Spec Delta

## Purpose

Garante que o papel de um robô declarado em `roles.yaml` (MUUT, FUUT ou SU)
restrinja de fato quais comandos esse robô pode receber, em vez de só
documentar uma intenção que nenhum código aplica.

## ADDED Requirements

### Requirement: Comando de movimento exige papel MUUT
O sistema SHALL rejeitar qualquer requisição que peça a um robô para navegar,
seguir waypoints ou executar record/replay quando o papel desse robô em
`roles.yaml` não for MUUT.

#### Scenario: Robô FUUT recebe comando de navegação
- **WHEN** uma requisição pede que um robô com papel FUUT execute
  `play_route`, `go_to_point` ou qualquer ação de navegação Nav2
- **THEN** o sistema rejeita a requisição sem despachar o comando ao robô,
  com um erro que identifica o papel declarado como motivo

#### Scenario: Robô SU recebe comando de navegação
- **WHEN** uma requisição pede que um robô com papel SU execute qualquer
  ação de navegação
- **THEN** o sistema rejeita a requisição pelo mesmo motivo do cenário
  anterior

#### Scenario: Robô MUUT recebe comando de navegação
- **WHEN** uma requisição pede que um robô com papel MUUT execute uma ação
  de navegação
- **THEN** o sistema despacha o comando normalmente, sem alteração de
  comportamento em relação ao que já existe hoje

### Requirement: Papel ausente ou desconhecido bloqueia movimento
O sistema SHALL tratar um robô sem entrada em `roles.yaml`, ou com um valor
de papel fora de {MUUT, FUUT, SU}, da mesma forma que um papel não-MUUT:
rejeitando comandos de movimento.

#### Scenario: Robô não declarado em roles.yaml
- **WHEN** uma requisição de navegação chega para um `robot_id` que não
  aparece em `roles.yaml`
- **THEN** o sistema rejeita a requisição, sem assumir MUUT como padrão
