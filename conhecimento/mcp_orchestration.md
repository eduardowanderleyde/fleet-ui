# Conhecimento acumulado: MCP e orquestração multi-agente pra robótica

## TL;DR

Primeira rodada de pesquisa (2026-10-02). Resumo em português simples:

- O spec do MCP **não ficou mais simples** — pelo contrário: desde a
  decisão registrada na dissertação já saíram 3 revisões maiores do
  protocolo (2025-06-18, 2025-11-25, 2026-07-28), e a última é uma
  reescrita de ruptura (remove sessão/handshake, adiciona RPC nova,
  depreca Sampling/Roots/Logging). Quem fosse implementar hoje um
  servidor MCP "completo" teria mais peças móveis, não menos. Mas o
  núcleo que interessaria aqui — `tools/list` + `tools/call` com schema
  JSON, sem autenticação — continua conceitualmente simples em todas as
  versões.
- Existem, sim, exemplos reais de servidores MCP expondo controle de
  robôs ROS~2 (ex.: `kakimochi/ros2-mcp-server`, usando FastMCP) e
  pesquisa acadêmica recente tratando MCP como camada de integração
  agente-robô (RoboNeuron, arXiv 2512.10394) — então a ideia não é
  hipotética, já tem precedente real, mas focado em expor tópicos/ações
  ROS~2 brutos, não num backend HTTP já estruturado como o deste projeto.
- O esforço de empacotar as `TOOL_SPECS` de `backend/agents/tools.py`
  como ferramentas MCP é baixo em termos de schema (já é JSON Schema,
  igual ao `inputSchema` do MCP, e os métodos do `Executor` já são
  funções assíncronas 1:1 com cada tool) — seria essencialmente um
  wrapper fino, não um redesenho. O trabalho real estaria em decidir
  transporte/autenticação/sessão, não em schema.
- Um artigo recente da própria Anthropic ("Code execution with MCP",
  nov/2025) argumenta que o ganho do MCP aparece quando há **muitas**
  ferramentas/clientes (contexto explode); com as ~12 tools fixas deste
  projeto e um único cliente (Planner interno), esse argumento a favor
  do MCP genérico é fraco — reforça, por uma razão diferente da
  dissertação, que tool-calling direto continua adequado ao escopo
  atual.
- Achados em tensão com a decisão já tomada (registrados como tal, não
  decidido aqui): há exemplos reais e pesquisa ativa (2025-2026)
  conectando MCP a ROS~2 especificamente, o que mostra que "servidor
  MCP pra robótica" é uma prática emergente real, não só uma ideia de
  próximo passo do projeto — mas nenhum desses exemplos resolve
  orquestração multi-robô coordenada, que é o ponto fraco desta frota
  hoje.

Este arquivo é mantido pelo agente `experiment-mcp-orchestration`
(`.claude/agents/experiment-mcp-orchestration.md`) — cada execução lê
isto primeiro, pesquisa o que falta, e acrescenta achados novos abaixo,
sem apagar o que já existe.

## Achados

### 2026-10-02

1. **Spec do MCP mudou 3 vezes desde revisões anteriores, e a última (2026-07-28) é uma ruptura grande.**
   Confirmado via `modelcontextprotocol.io/specification/{versão}/changelog`
   (fontes primárias, lidas diretamente):
   - `2025-06-18`: remove batching JSON-RPC, adiciona structured tool
     output, elicitation, resource links, classifica servidores MCP
     como OAuth Resource Servers.
   - `2025-11-25`: discovery via OpenID Connect, ícones em
     tools/resources/prompts, tool calling dentro de sampling, suporte
     experimental a "tasks" (polling de requisições longas).
   - `2026-07-28`: remove sessão de protocolo e o header
     `Mcp-Session-Id`; remove o handshake `initialize`/
     `notifications/initialized` (protocolo agora é stateless, versão e
     capacidades vão em `_meta` a cada request); adiciona RPC nova
     `server/discover`; substitui `resources/subscribe`/`unsubscribe`
     por `subscriptions/listen`; remove `ping`, `logging/setLevel`;
     depreca formalmente as features **Sampling, Roots e Logging**
     (orientação oficial: usar API do provedor LLM direto em vez de
     Sampling — o que é exatamente o que este projeto já faz).
   Link: https://modelcontextprotocol.io/specification/2026-07-28/changelog
   (compara com 2025-11-25); changelogs de 2025-06-18 e 2025-11-25 nos
   respectivos links `/specification/<data>/changelog`.
   **Leitura**: a tendência do spec é ficar mais explícito/robusto para
   multi-cliente e produção (auth, cache, discovery), não mais simples
   para um caso de uso único e controlado. Isso não enfraquece nem
   fortalece sozinho a decisão atual — mas mostra que "esperar o spec
   estabilizar" não é uma aposta segura: ainda está mudando de forma
   estrutural.

2. **Exemplo real confirmado: `kakimochi/ros2-mcp-server`.**
   Servidor MCP em Python usando FastMCP, roda como nó ROS~2, expõe a
   tool `move_robot` (linear velocity, angular velocity, duration) que
   publica `geometry_msgs/Twist` em `/cmd_vel`. ~83 stars, licença MIT.
   Confirmado por leitura direta do repositório. Referência de design
   útil mas num nível bem mais baixo (velocidade direta, não
   waypoints/Nav2/missões) do que as tools já expostas pelo `Executor`
   deste projeto.
   Outros achados na mesma busca que aparecem reais mas **não foram
   confirmados individualmente** nesta rodada (só vistos em resultado de
   busca, não abertos): `yutarop/ros-mcp`, `wise-vision/mcp_server_ros_2`,
   `gavindev14/mcp_server_ros_2`. Marcar como não confirmado até alguém
   abrir o repo.

3. **Paper real: RoboNeuron (arXiv 2512.10394), dez/2025, rev. abr/2026.**
   "RoboNeuron: A Middle-Layer Infrastructure for Agent-Driven
   Orchestration in Embodied AI" — Weifan Guan, Qinghao Hu, Huasen Xi,
   Chenxiao Zhang, Aosheng Li, Jian Cheng (Institute of Automation,
   Chinese Academy of Sciences). Confirmado via abstract no arXiv.
   Propõe middleware que deriva tools MCP automaticamente a partir de
   schemas ROS, com execução unificada (comando direto ou composição
   modular) e isolamento de mudanças de backend/runtime. Avaliado em
   simulação e hardware real (controle de base móvel, braço, grasping
   via VLA). Código aberto (não verificado o link exato do repo nesta
   rodada).
   **Relevância**: é evidência de que "derivar tools MCP de schema já
   existente" é uma prática ativa de pesquisa, não invenção — reforça
   que o esforço de wrapper fino estimado no item 4 abaixo é plausível
   mesmo em sistemas mais complexos que o deste projeto.

4. **Survey real: "Large Language Models for Multi-Robot Systems: A Survey" (arXiv 2502.03814).**
   Peihan Li, Zijian An, Shams Abrar, Lifeng Zhou. v1 fev/2025, revisão
   mais recente (v5) mai/2026. Confirmado via abstract no arXiv.
   Categoriza usos de LLM em sistemas multi-robô (alocação de tarefa,
   planejamento de movimento, geração de ação, intervenção humana) em
   domínios como robótica doméstica, construção, formação e rastreio de
   alvo. Lista desafios: limitação de raciocínio matemático,
   hallucination, latência, falta de benchmarks robustos.
   **Relevância pra pergunta de orquestração multi-agente**: é literatura
   real e recente sobre o tema, mas em nível de survey/categorização —
   não achei (nesta rodada) um framework único e citável de
   "orquestração multi-robô por múltiplos agentes LLM independentes"
   equivalente ao que a pergunta original busca; precisa de rodada
   futura dedicada a abrir esse survey e seguir as referências
   específicas de "formation control" / "task allocation" citadas nele.

5. **Fonte primária Anthropic: "Code execution with MCP" (anthropic.com/engineering, 04/11/2025).**
   Confirmado por leitura direta do artigo. Argumento central: MCP com
   tool-calling direto fica caro em contexto quando há muitas
   ferramentas conectadas e resultados intermediários grandes (exemplo
   deles: 150k tokens → 2k tokens trocando para execução de código sobre
   MCP). Recomenda tratar servidores MCP como API de código, não como
   lista de tools carregada inteira no contexto, quando o número de
   tools cresce.
   **Relevância pro fleet-ui**: o projeto tem ~12 tools fixas
   (`backend/agents/tools.py`) e um único cliente (Planner interno) — o
   cenário que motiva essa recomendação (muitas tools, muitos clientes)
   não se aplica aqui. Isso é um argumento a favor de manter tool-calling
   direto que **não** é o mesmo já usado na dissertação (lá foi "escopo
   de experimento único"; aqui é "a dor que o MCP resolve não existe
   neste tamanho de toolset").

6. **Esforço de wrapper MCP sobre o código atual: avaliação direta do código (não é achado web, é leitura de `backend/agents/tools.py` e `backend/agents/executor.py`).**
   `TOOL_SPECS` já usa `input_schema` no formato JSON Schema (igual ao
   formato de tool use da API Anthropic) — campo por campo compatível
   com o `inputSchema` que um servidor MCP precisa declarar por tool.
   Cada tool em `TOOL_SPECS` já mapeia 1:1 pra um método assíncrono de
   `Executor` (ex.: `move_robot`, `start_recording`, `run_campaign`),
   que por sua vez só faz `httpx` contra o backend FastAPI — não há
   lógica de negócio miscigenada com o protocolo de tool-calling.
   **Conclusão**: expor isso via MCP (usando o SDK oficial Python, ex.
   decorador `@mcp.tool()`) seria de fato um wrapper fino — iterar
   `TOOL_SPECS`, registrar cada entrada como tool MCP delegando pro
   método `Executor` correspondente. O esforço real não estaria no
   redesenho de schema/lógica, e sim em decidir transporte (stdio vs.
   Streamable HTTP, dado que a API do backend já é HTTP) e se vale a
   pena lidar com a camada de sessão/auth que o spec 2026-07-28 mudou
   recentemente (achado 1).

## Ação sugerida

Não editar código nesta rodada (regra do agente). Sugestão concreta pra
próxima vez que alguém for *decidir*, não só pesquisar:

- Se algum dia quiserem revisitar a decisão "tool-calling direto, não
  MCP genérico" (Cap. 04 da dissertação), o argumento mais forte pra
  manter como está não é mais só "escopo de experimento único" — é que
  o problema que o MCP resolve bem (muitas tools, muitos clientes,
  contexto explodindo) não existe neste projeto, segundo o próprio
  material oficial da Anthropic (achado 5). Vale citar isso como reforço
  adicional da escolha, se a banca perguntar "por que não MCP".
- Se decidirem prototipar mesmo assim, checar primeiro contra qual
  versão do spec (ex.: a RPC nova `server/discover` do 2026-07-28) —
  a versão que serviria de referência de implementação muda a cada
  poucos meses (achado 1), então vale fixar a versão alvo antes de
  escrever qualquer código.
- Pesquisa futura em aberto (não respondida nesta rodada): abrir o
  survey arXiv 2502.03814 e seguir citações específicas de orquestração
  multi-robô por múltiplos agentes LLM independentes (não um Executor
  único) — a resposta desta rodada ficou em nível de survey geral, não
  achou um framework específico e citável pra esse ponto.
- Pesquisa futura em aberto: confirmar individualmente
  `yutarop/ros-mcp`, `wise-vision/mcp_server_ros_2` e
  `gavindev14/mcp_server_ros_2` (vistos só em busca, não abertos) antes
  de citar qualquer um deles como referência de design.

### 2026-10-02 — Primeira execução real da camada de agentes (Planner/Executor) nesta sessão: 2 bugs de setup + 1 achado de repetibilidade

Não é pesquisa — é execução real, pela primeira vez nesta sessão, da
camada de orquestração por IA já existente (`backend/agents/`), motivada
pelo item de trabalho futuro "avaliar se a camada de agentes degrada a
repetibilidade pairwise" (ver `dissertacao` branch, Cap. 09). Dois bugs de
infraestrutura e um achado real de repetibilidade, nessa ordem:

1. **`backend/venv/` não existia** — `httpx`/`anthropic` não instalados
   (nem no sistema, nem em lugar nenhum). `requirements.txt` existe mas
   nunca tinha sido realmente usado pra criar o venv nesta máquina.
   Resolvido: `python3 -m venv --system-site-packages backend/venv`
   (`--system-site-packages` é necessário pra herdar `rclpy` do ROS) +
   `pip install -r backend/requirements.lock.txt` (não o `.txt` solto —
   ver achado 2).
2. **Bug real de incompatibilidade de versão, mascarado como erro de
   rede**: com `anthropic==1.11.0` (a versão mais nova, instalada por
   engano antes de notar o `requirements.lock.txt`), toda chamada à API
   falhava com `anthropic.APIConnectionError: Connection error.` — uma
   mensagem enganosa. A causa real, só visível com traceback completo:
   `httpx2/_decoders.py` (dependência interna do SDK) chama
   `brotli_decompressor.process(data, output_buffer_limit=...)`, e o
   pacote `brotli` herdado do sistema (`/usr/lib/python3/dist-packages/brotli.py`,
   via apt `python3-brotli`) é velho demais pra aceitar esse argumento —
   `TypeError: process() takes no keyword arguments`, capturado e
   re-levantado pelo SDK como erro de conexão genérico. Resolvido
   instalando `pip install --ignore-installed Brotli` (pacote PyPI,
   letra maiúscula, versão 1.2.0) dentro do venv, sobrescrevendo o do
   sistema só ali. Reinstalar com `requirements.lock.txt` sozinho **não
   resolveu** — o `brotli` do sistema nem está no lock file, é uma
   dependência transitiva opcional do `httpx`/`httpx2`.
3. **Achado real de repetibilidade** (N=5, rota curta ~1m nova
   `llm_pilot01`, não mexeu em `dissertation_clean01`): o Planner
   corretamente **recusou duas vezes** inventar parâmetros (`robot_id`
   e waypoints da rota) quando a instrução inicial era ambígua/incompleta
   — pediu esclarecimento em vez de alucinar, incluindo a frase explícita
   "Não vou inventar coordenadas, porque o robô se moveria de verdade."
   Com os parâmetros corretos, rodou `run_campaign` (1 baseline +
   5 réplicas) sem nenhuma falha operacional. O RMSE calculado pela
   própria ferramenta (`analyze_experiment`, que usa `/pose` como fonte,
   auto-detectado) comparando réplica vs. baseline ficou alto (~0,39m) —
   mas isso reproduz exatamente o gap de mecanismo de navegação já
   documentado na dissertação (`go_to_point` na baseline vs.
   `play_route`/`FollowWaypoints` no replay — durações de 3,7s vs. ~58s
   pra mesma rota nominal). Recalculando pairwise **entre réplicas**
   (mesmo mecanismo, metodologia já estabelecida na dissertação): 4 das
   5 réplicas ficaram entre 0,014 e 0,068m de RMSE entre si — mas a
   réplica 1 destoou das outras 4 em 0,42–0,45m, um outlier não
   explicado até o fim desta execução (não rodei `diagnose_experiment`
   pra investigar a causa).

**Ação sugerida:** N=5 com 1 outlier não explicado é pouco pra uma
conclusão — antes de considerar isso evidência real sobre o efeito do
LLM na repetibilidade, valeria (a) rodar `diagnose_experiment` no
run_id `llm_pilot01_4979c065` pra investigar a réplica 1 especificamente,
e (b) repetir com N maior (10+, como as outras campanhas desta sessão).
Autor decidiu (2026-10-02) manter isso só como registro de conhecimento
por enquanto, sem levar pra dissertação ainda.
