# Registro de problemas — testes com usuárias (Bia e Fernanda)

Este arquivo guarda **todo problema** que aparecer nos testes, para a dissertação.
Separe sempre de onde veio o problema:

- **FLEET UI** = falha do software (bug, travou, perdeu dado, tela confusa).
- **PROJETO** = falha no projeto/experimento das meninas (roteiro, mapa, robô, instrução mal dada, ambiente do PC).

Regra: anote na hora, mesmo que pareça pequeno. Depois a gente classifica.

---

## Antes de cada sessão (checklist)

- [ ] Rodar a versão da branch combinada (`git pull`) e anotar o commit: `git log -1 --oneline`
- [ ] Conferir se a pasta `fleet_ws/agent_runs/` existe (é onde ficam as conversas com os agentes)
- [ ] Anotar no início: data, quem testou, PC/sistema (Ubuntu, Windows, Docker ou não)
- [ ] Gravar a tela (OBS ou gravador do sistema). É o backup se tudo falhar

## Depois de cada sessão

- [ ] **Não** rodar `docker compose down` antes de copiar as conversas
- [ ] Copiar a pasta `fleet_ws/agent_runs/` inteira e mandar para o Eduardo (zip):
      `zip -r conversas-$(date +%F)-NOME.zip fleet_ws/agent_runs`
- [ ] Copiar também `fleet_ws/routes/` e `fleet_ws/collections/` se houve gravação de rota
- [ ] Preencher as linhas da sessão abaixo

---

## Problemas conhecidos

| # | Data | Quem | Tipo | O que aconteceu | Impacto | Status |
|---|------|------|------|-----------------|---------|--------|
| P01 | semana de 09/11/2026 | Bia / Fernanda | FLEET UI | As conversas com os agentes sumiram quando o PC/aplicação fechou. | Perda de dados do teste | Corrigido em `fix/salvar-conversas-agente` (ver abaixo) |
| P02 | semana de 09/11/2026 | — | FLEET UI | A interface não mostra conversas antigas: o backend tem `/api/agent/history`, mas nenhuma tela usa. Fechou a aba, a conversa some da tela. | Usuária acha que perdeu tudo | Aberto |
| P03 | | | | *(completar com os outros problemas da semana passada)* | | |

### Causa do P01 (análise do código em 15/11/2026)

1. Em Docker, a pasta `fleet_ws/agent_runs` não estava montada como volume. Ao recriar o container (`docker compose down/up`), as conversas eram apagadas junto.
2. A conversa só era gravada em disco **quando terminava**. Se o backend ou o PC fechasse no meio, ela existia só na memória e sumia.
3. A tela não lê o histórico salvo (ver P02).

Correção aplicada: volume `./fleet_ws/agent_runs` nos dois `docker-compose`, e gravação da conversa já no início (e de novo no fim). Ainda falta: gravar cada passo enquanto o agente roda, e uma tela de histórico.

---

## Sessões de teste

Copie este bloco para cada sessão.

### Sessão AAAA-MM-DD — NOME

- Commit do Fleet UI:
- PC / sistema / Docker?:
- Duração:
- Tarefas pedidas:
- Conversas salvas em `agent_runs`? (quantos arquivos):

| Hora | Tipo (FLEET UI / PROJETO) | O que fez | O que esperava | O que aconteceu | Print/vídeo |
|------|---------------------------|-----------|----------------|-----------------|-------------|
| | | | | | |

Comentários da usuária (frases dela, entre aspas):
