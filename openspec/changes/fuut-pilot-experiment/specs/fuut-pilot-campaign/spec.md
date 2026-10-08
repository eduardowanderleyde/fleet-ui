# Spec Delta

## Purpose

Define o comportamento de uma campanha piloto com um robô MUUT em
record-replay e um robô FUUT parado observando, cruzando as duas fontes de
dado no `FuutVerifier` pra produzir evidência empírica do papel FUUT, hoje
inexistente.

## ADDED Requirements

### Requirement: Campanha roda com FUUT parado e MUUT navegando
O sistema SHALL executar cada réplica da campanha piloto com o robô FUUT
sem Nav2 ativo (sensores e SLAM ligados, sem movimento) enquanto o robô
MUUT executa o protocolo normal de record-replay.

#### Scenario: Réplica da campanha piloto
- **WHEN** uma réplica da campanha piloto é iniciada
- **THEN** o robô FUUT permanece parado durante toda a réplica e o robô
  MUUT completa o ciclo de record-replay normalmente

### Requirement: Dados de MUUT e FUUT ficam sincronizados por réplica
O sistema SHALL associar, para cada réplica, a pose reivindicada pelo MUUT
e a observação geométrica correspondente do FUUT ao mesmo identificador de
réplica, de forma que ambas possam ser lidas juntas depois.

#### Scenario: Leitura pós-réplica
- **WHEN** uma réplica termina e seus dados são persistidos
- **THEN** é possível recuperar, pelo identificador da réplica, tanto a
  pose reivindicada pelo MUUT quanto a observação do FUUT referente à
  mesma réplica

### Requirement: Relatório de verificação por réplica
O sistema SHALL gerar, para cada réplica da campanha piloto, um relatório
de verificação produzido pelo `FuutVerifier` existente, contendo o nível de
corroboração, a confiança reportada e o erro geométrico entre a pose
reivindicada e a observação do FUUT.

#### Scenario: Relatório de uma campanha completa
- **WHEN** todas as réplicas de uma campanha piloto terminam
- **THEN** existe um relatório de verificação por réplica, salvo junto aos
  demais artefatos da campanha (mesmo diretório padrão de
  `fleet_ws/runs/<run_id>/analysis/`), legível sem precisar re-executar o
  piloto

#### Scenario: FUUT não observa nada compatível com a pose reivindicada
- **WHEN** a observação do FUUT não tem nenhuma correspondência geométrica
  plausível com a pose reivindicada pelo MUUT naquela réplica
- **THEN** o relatório dessa réplica reporta explicitamente a ausência de
  correspondência, em vez de atribuir um nível de corroboração arbitrário
