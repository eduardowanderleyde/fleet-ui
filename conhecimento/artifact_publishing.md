# Conhecimento acumulado: Publicação de artefato de pesquisa (FAIR/replicação)

## TL;DR

Este arquivo é mantido pelo agente `experiment-artifact-publishing`
(`.claude/agents/experiment-artifact-publishing.md`) — cada execução lê
isto primeiro, pesquisa o que falta, e acrescenta achados novos abaixo,
sem apagar o que já existe.

Resumo em português simples (atualizado 2026-10-02), respondendo às três
perguntas que motivaram o agente:

1. **Selo formal de "artefato avaliado" (ACM/IEEE) não existe nas
   conferências de robótica (ICRA/IROS) como processo padrão** — isso é
   coisa de conferências de engenharia de software/sistemas (SIGMOD,
   ICSE, PPoPP, SIGCOMM etc.), que têm comitê de avaliação de artefato
   (AEC) formal. Não achei evidência de que ICRA/IROS tenham essa
   trilha. **Conclusão prática: perseguir um selo ACM formal é
   desproporcional pro escopo — não tem comitê pra submeter.** Vale sim
   adotar os *princípios* (FAIR4RS, badges ACM como inspiração de
   documentação), sem buscar o selo em si.
2. **Arquivar release do GitHub no Zenodo pra gerar DOI é simples, processo
   confirmado e documentado oficialmente tanto pelo GitHub quanto pelo
   Zenodo** — repo precisa ser público e ter licença, conecta via login
   Zenodo-com-GitHub, liga o toggle do repo, e cada novo "Release" no
   GitHub gera automaticamente uma versão arquivada com DOI próprio (mais
   um DOI "guarda-chuva" do projeto todo). **Dá pra fazer antes da
   defesa, é rápido e de baixo risco** — não exige mudar nada no código,
   só criar uma Release do repo atual.
3. **Não existe um checklist padrão e amplamente aceito de "como replicar
   um experimento de robótica" equivalente ao que SE/sistemas têm.** O
   mais próximo e diretamente relacionado às referências já citadas na
   dissertação (amigoni2010, bonsignorio2015) é o workshop ICRA 2017
   "Reproducible Research in Robotics" e o paper de Lier et al. (2017)
   "Can we Reproduce it?" — que propõe 4 eixos que podem estruturar um
   README de replicação: (a) artefatos técnicos reprodutíveis, (b) design
   de experimento explícito/compreensível, (c) execução repetível/
   reprodutível do experimento, (d) avaliação reprodutível dos dados
   obtidos. Isso pode ser usado como estrutura prática pro README que
   falta (ver Ação sugerida).

**Atualização 2026-10-03** (responde a duas perguntas novas, sem contradizer
os 3 pontos acima): (a) **o pacote certo pro Zenodo é o repositório git
completo, sem os bags brutos** — isso já seria automático ao criar uma
Release no GitHub (ainda não existe nenhuma, confirmado nesta data), mas
falta um ajuste antes: os arquivos de rota (`fleet_ws/routes/*.yaml`) usados
pelas campanhas já commitadas (`gt01_curta/longa/loop`, pilotos de IA) nunca
foram versionados (gitignorados) — sem eles, quem baixar o artefato do
Zenodo teria os resultados processados, mas não a entrada exata (a rota)
que os gerou. Ver o roteiro passo-a-passo completo no achado "O que deveria
entrar no pacote de replicação mínimo..." mais abaixo. (b) **O achado de
2026-10-02 sobre "dados brutos da campanha oficial perdidos" continua
válido e não foi corrigido** — os bags da campanha original do Cap. 8
continuam irrecuperáveis, nada mudou aí. Mas a mitigação aplicada então
(gravar commit git em cada export) está agora **confirmada funcionando de
verdade** em campanhas novas e reais (`gt01_curta` etc., verificado lendo o
JSON committed), não só testada isoladamente como antes. Em compensação,
apareceu uma lacuna nova e menor do mesmo tipo: as rotas dessas campanhas
novas também não estão versionadas (ver item (a)).

## Achados

### 2026-10-02 — ACM Artifact Review and Badging: definições oficiais

Fonte primária: `https://www.acm.org/publications/policies/artifact-review-badging`
(confirmada via busca; página retornou HTTP 403 ao fetch direto, então as
definições abaixo vêm de descrição consistente entre múltiplas fontes
secundárias confiáveis que citam a política — `casrai.org/dictionary/term/
acm-artifact-review-and-badging` e CFPs de conferências como PPoPP 2025).
A página oficial no título aparece como "Version 1.0 (not current)",
indicando que existe versão mais nova, mas não consegui confirmar o
conteúdo exato da versão atual via fetch direto (bloqueado por 403).
**Registro como não totalmente confirmado em fonte primária direta —
confirmado só por citação de terceiros confiáveis.**

Badges existentes: *Artifacts Available* (artefato publicamente acessível
em repositório permanente, idealmente com DOI), *Artifacts Evaluated —
Functional* (artefato executa e se comporta como descrito), *Artifacts
Evaluated — Reusable* (bem documentado, fácil de reusar/adaptar),
*Results Reproduced* (equipe independente reproduziu os resultados
centrais usando o artefato dos autores), *Results Replicated* (equipe
independente verificou os resultados construindo artefato próprio, sem
usar o dos autores). A submissão é voluntária e não afeta aceite do
paper — é avaliada por um "Artifact Evaluation Committee" (AEC) dedicado.

**Tensão com a pergunta original:** esse processo pressupõe existir um
AEC ligado a uma conferência/journal que o projeto esteja submetendo.
Não encontrei evidência de que ICRA/IROS tenham essa trilha (ver achado
seguinte). Logo, buscar formalmente um selo ACM não se aplica a uma
dissertação de mestrado sem veículo de publicação com AEC.

### 2026-10-02 — ICRA/IROS não têm trilha de Artifact Evaluation confirmada

Busquei especificamente "ICRA 2025 artifact evaluation" e "IROS 2025
artifact evaluation call for papers" — não encontrei nenhuma página
oficial de `ieee-icra.org` ou do site do IROS 2025 mencionando uma
trilha formal de avaliação de artefato/reprodutibilidade (ao contrário
de conferências de SE/sistemas como ICSE, PPoPP, SIGCOMM, que têm isso
institucionalizado há anos, com AEC e badges). Achei apenas um evento
avulso "Supporting Reproducibility in Soft Robotics: a community
discussion" na ICRA 2025 (discussão, não trilha de avaliação) —
**não confirmado como processo formal**, registrado aqui só como sinal
de que o tema é discutido informalmente na comunidade de robótica, sem
infraestrutura de badge equivalente à da ACM.

Também tentei o IEEE RAS Resource Center (`resourcecenter.ieee-ras.org/
group/4897`) buscando algo robótica-específico — o grupo encontrado era
um formulário de avaliação da IEEE Industrial Electronics Society (IES),
não relacionado a reprodutibilidade de pesquisa. **Não confirmado**
qualquer selo IEEE-RAS equivalente ao ACM badging para robótica.

Badges IEEE genéricos existem (fora do contexto RAS): categorias
"Available" (artefato arquivado publicamente com DOI), "Reviewed"
(revisado por critério do emissor do selo) e "Reproducible" (parte
independente regerou os resultados computacionais) — mas são do IEEE
geral, não específicos de conferência de robótica, e não achei uso deles
em ICRA/IROS.

### 2026-10-02 — Zenodo + GitHub: processo de arquivamento confirmado em fonte primária

Fonte primária confirmada via fetch direto: página oficial do GitHub
Docs (`docs.github.com/en/repositories/archiving-a-github-repository/
referencing-and-citing-content`). Passos exatos documentados pelo
próprio GitHub:

1. Login em Zenodo com "Log in with GitHub".
2. Autorizar o app Zenodo (revisar permissões, "Authorize zenodo").
3. Ir à página de configurações do GitHub dentro do Zenodo e ligar o
   toggle ("On") ao lado do repositório desejado.
4. Zenodo arquiva automaticamente e emite um novo DOI a cada nova
   *Release* criada no GitHub — **requer repo público**, e o GitHub
   recomenda ter uma licença no repo "para os leitores saberem como
   podem reusar o trabalho".

Cada release individual recebe um DOI de versão; o projeto como um todo
também recebe um DOI "guarda-chuva" (concept DOI) que sempre resolve pra
versão mais recente — isso é descrito em fontes secundárias consistentes
(Cornell Research Data Services, LASP developer guide) mas não
recapturado literalmente da página oficial do GitHub nesta consulta —
registro esse detalhe como proveniente de fonte secundária, não primária
direta.

**Relevante pro fleet-ui:** o repositório já é público no GitHub
(`github.com/eduardowanderleyde/fleet-ui`), então o único passo que falta
é (a) confirmar que há uma licença no repo, (b) conectar a conta Zenodo
via GitHub, (c) criar uma GitHub Release da versão que corresponde ao
experimento reportado no Capítulo 8.

### 2026-10-02 — CITATION.cff: suporte nativo do GitHub, não visto no repo

Fonte primária confirmada via fetch direto: GitHub Docs, "About
citation files" (`docs.github.com/.../about-citation-files`). Um arquivo
`CITATION.cff` na raiz do repositório (branch padrão) faz o GitHub
mostrar automaticamente um link "Cite this repository" na barra lateral,
com citação em APA e BibTeX geradas a partir do conteúdo do arquivo.
Outros nomes aceitos: `CITATION`, `CITATIONS`, `CITATION.bib`,
`CITATION.md` (e variantes), na raiz do repo. Dá pra usar
`preferred-citation` no CFF pra apontar pra um artigo/tese em vez do
próprio software, caso o objetivo seja "cite a dissertação, não o
código". **Não verifiquei neste agente se o repo fleet-ui já tem esse
arquivo** (fora do escopo desta execução, que só edita este .md) — fica
como item a checar/sugerir.

### 2026-10-02 — FAIR4RS Principles (FAIR para software de pesquisa): confirmado, mas conteúdo detalhado não acessado

Fonte primária parcialmente confirmada: `zenodo.org/records/6623556`
("FAIR Principles for Research Software (FAIR4RS Principles)",
publicado por working group conjunto RDA + FORCE11 + Research Software
Alliance, 2022). Confirma que existe uma adaptação formal e
com endosso de comunidade do FAIR original (Findable, Accessible,
Interoperable, Reusable) especificamente para software, reconhecendo que
software tem características diferentes de dados (executável, composto,
versionado continuamente). **Não consegui extrair o detalhe de cada
sub-princípio** (o PDF completo não foi aberto nesta execução) — fica
como próximo passo de leitura, não como achado fechado.

### 2026-10-02 — Paper mais próximo de um "checklist" de replicação pra robótica

Fonte primária confirmada via crossref (DOI `10.1145/3173386.3176963`,
confirmado em `api.crossref.org/works/10.1145%2F3173386.3176963`): Lier,
F.; Lücking, P.; de Leeuw, J.; Wachsmuth, S.; Šabanović, S.; Goldstone,
R. "Can we Reproduce it? Toward the Implementation of good Experimental
Methodology in Interdisciplinary Robotics Research" — ICRA 2017 Workshop
on Reproducible Research in Robotics: Current Status and Road Ahead,
Singapura, 2017. Propõe estruturar reprodutibilidade em robótica em 4
eixos: (a) reprodutibilidade dos artefatos técnicos (código, configs,
containers), (b) design de experimento explícito e compreensível
(hipótese, variáveis, protocolo), (c) execução repetível/reprodutível do
experimento (mesmas condições, scripts de execução), (d) avaliação
reprodutível dos dados obtidos (scripts de análise, dados brutos
publicados). **Relevante porque é da mesma linhagem de discussão que
amigoni2010/bonsignorio2015, já citados na dissertação** — dá pra citar
como terceira referência na mesma frase sobre prática de publicar
artefato, e os 4 eixos servem de esqueleto pro README de replicação do
Capítulo 8 que ainda não existe. Não li o paper completo (paywall/acesso
institucional bloqueado via Bielefeld Anubis), só confirmei metadados via
crossref/bibsonomy — conteúdo detalhado do paper em si **não
confirmado**, só o resumo circulado em múltiplas fontes de indexação.

## Ação sugerida

(Pesquisa, não código — decisões abaixo ficam pro usuário/orientador.)

1. **Não perseguir selo ACM/IEEE formal de artefato.** Não há AEC em
   ICRA/IROS pra submeter a isso; o esforço não tem onde "pousar". Em vez
   disso, adotar informalmente os critérios de "Artifacts Available" e
   "Artifacts Evaluated — Reusable" como padrão de qualidade (repo
   público, documentado, com DOI, fácil de rodar) sem buscar o badge.
2. **Fazer o arquivamento Zenodo antes da defesa** — baixo custo, processo
   confirmado: (a) checar/add licença no repo fleet-ui se faltar, (b)
   conectar conta Zenodo via GitHub login, (c) criar uma GitHub Release
   correspondente ao estado do experimento do Capítulo 8, (d) citar o DOI
   resultante na dissertação (reforça a reivindicação de
   reprodutibilidade com uma evidência concreta e citável).
3. **Criar um `CITATION.cff` na raiz do repo** apontando (via
   `preferred-citation`) pra dissertação, não só pro software — facilita
   quem quiser citar o trabalho formalmente.
4. **Escrever um README específico de replicação do Capítulo 8**
   (separado do README de desenvolvimento), estruturado nos 4 eixos de
   Lier et al. (2017): artefatos técnicos exatos usados (versões
   ROS 2 Jazzy/Nav2/Gazebo Harmonic, commit/tag exato), design do
   experimento (hipóteses, variáveis, protocolo da campanha), passos de
   execução repetível (comandos exatos, seeds, configs), e scripts/dados
   de avaliação (como os números do capítulo foram gerados a partir dos
   logs brutos). Isso cita Lier et al. 2017 ao lado de amigoni2010/
   bonsignorio2015 como prática reconhecida na comunidade de robótica.
5. Próxima execução deste agente: ler o PDF completo do FAIR4RS
   (`zenodo.org/records/6623556`) pra extrair os sub-princípios
   detalhados, e tentar confirmar a versão atual (não "1.0 not current")
   da política ACM via fonte primária (tentar Google cache ou outra
   rota, já que o fetch direto deu 403).
6. **(2026-10-03) Antes de criar a Release/Zenodo:** versionar os arquivos
   de rota em `fleet_ws/routes/` que correspondem às campanhas já
   commitadas (ver achado "Pacote de replicação mínimo" abaixo) — hoje
   eles ficam de fora do que a integração Zenodo-GitHub arquiva.

### 2026-10-02 — Ação aplicada: `CITATION.cff` criado

Item 3 (acima) sobre `CITATION.cff` foi feito: arquivo criado na raiz do
repositório (`CITATION.cff`, `cff-version: 1.2.0`), autor confirmado
diretamente com o autor do projeto (Eduardo Wanderley, consistente com o
`@eduardowanderleyde` do GitHub), licença MIT (já existente em
`LICENSE`), `repository-code` apontando pro GitHub. **Não tem DOI ainda**
— isso depende do item 2 (Zenodo), que segue pendente porque exige login
do próprio autor no Zenodo, não pode ser feito por um agente. Ver
`implementacao.md` ("Feito" e "Pendente").

### 2026-10-02 — Achado real (não é pesquisa externa): dados brutos da campanha oficial foram perdidos

Ao escrever o README de replicação (item 4 da lista de "Ação sugerida"
acima), confirmei diretamente no disco e no histórico git: os dados brutos
da campanha oficial citada no Capítulo 8 (`protocol_id=dissertation_clean01`,
pasta esperada `fleet_ws/runs/dissertation_clean01_final_manual/` — bags
MCAP, exports JSON por replay, manifesto) **não existem em lugar nenhum
rastreável** — nem no working tree atual, nem em nenhum commit do git (as
pastas `fleet_ws/runs/`/`collections/` nunca foram versionadas). Só restou
o YAML da rota (`fleet_ws/routes/default/dissertation_clean01.yaml`). O
commit git exato que gerou esses números também nunca foi registrado em
lugar nenhum. Perguntei ao autor diretamente (2026-10-02) se havia cópia em
outro lugar — resposta: não sabe, podem ter sido perdidos mesmo.

**Isto está em tensão com a própria motivação deste agente** (reprodutibilidade
como contribuição central da dissertação) — não é um achado de literatura,
é uma lacuna real do próprio projeto. Mitigação aplicada: todo export de
`experiment_repeatability.py` agora grava commit + dirty-flag automaticamente
(`_git_provenance()`, ver `implementacao.md`), então essa lacuna específica
não deve se repetir em campanhas futuras — mas os dados da campanha original
permanecem irrecuperáveis. Não decidi se isso precisa de uma nota explícita
na dissertação (Cap. 8 ou Limitações) — isso é decisão do autor.

**Ação sugerida:** o autor decidir se quer adicionar uma nota breve na
dissertação (Seção de Limitações, Cap. 09) mencionando que os dados brutos
da campanha original não foram preservados — por ora a dissertação não
afirma explicitamente que os dados estão disponíveis, então não há uma
afirmação falsa a corrigir, só uma omissão a considerar.

### 2026-10-03 — Zenodo: limites de upload confirmados em fonte primária

Fonte primária confirmada via fetch direto (200 OK, sem bloqueio desta vez):
`support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo`.
Limites atuais: **50GB por registro** (soma de todos os arquivos), **máximo
100 arquivos por registro**, com possibilidade de solicitar aumento único de
quota até 200GB por registro (caso a caso). Zenodo explicitamente proíbe
dividir um dataset grande em vários registros só pra contornar o limite de
50GB. **Relevante pro fleet-ui:** irrelevante como bloqueio — mesmo somando
tudo que existe hoje (`fleet_ws/runs/*` committed + os ~36MB de
`collections/` ainda fora do git), fica muito abaixo de 50GB. Quota não é
motivo pra excluir nada do pacote de replicação.

### 2026-10-03 — Zenodo: como adicionar arquivos extras a um depósito já criado via GitHub (não confirmado em fonte primária direta)

Tentei `help.zenodo.org/docs/deposit/manage-files/quota-increase` (fonte
primária) — retornou HTTP 404 (página não existe mais nesse caminho, ou
mudou de URL). **Não confirmado em fonte primária direta desta vez.** Via
busca, encontrei convergência entre fontes secundárias consistentes
(documentação do `zenodo-client` em `zenodo-client.readthedocs.io`, FAIR
Cookbook da ELIXIR-Europe em `faircookbook.elixir-europe.org`): depois que
um registro Zenodo é publicado, os arquivos dele não podem mais ser editados
diretamente; pra adicionar arquivos novos ao mesmo registro (por exemplo,
depois que a integração GitHub→Zenodo já criou o depósito a partir de uma
Release), o caminho é usar a função "New version" do próprio Zenodo (cria
uma nova versão do mesmo registro, com DOI de versão novo, mas ligado ao
mesmo DOI "guarda-chuva"), e fazer upload manual dos arquivos extras ali —
não precisa de uma nova GitHub Release pra isso. **Registro como achado
plausível, mas não confirmado por fonte primária Zenodo nesta rodada** —
se isso for decisivo pra uma ação do autor, vale confirmar direto na UI do
Zenodo antes de depender disso.

### 2026-10-03 — Confirmado: ainda não existe nenhuma GitHub Release no fleet-ui

Verificado via fetch direto de `github.com/eduardowanderleyde/fleet-ui/releases`
(2026-10-03): a página mostra "There aren't any releases here" — nenhuma
Release foi criada ainda. Consistente com o item "Pendente" já registrado em
`implementacao.md` desde 2026-10-02 (segue pendente, sem mudança).

### 2026-10-03 — Achado real do projeto (não é pesquisa externa): as rotas YAML usadas pelas campanhas já commitadas NÃO estão no git

Ao avaliar o que exatamente entraria no arquivamento Zenodo via a integração
GitHub (que arquiva o conteúdo exato do repositório git na tag da Release,
não o working tree local), confirmei no disco (`fleet_ws/.gitignore` ainda
lista `routes/` como ignorado, consistente com o que uma sessão anterior já
havia documentado em `implementacao.md`) que **os arquivos de rota em
`fleet_ws/routes/default/` e `fleet_ws/routes/tb1|tb2/` nunca foram
versionados** — incluindo `dissertation_clean01.yaml`, `rota_longa_curva.yaml`,
`loop_fechado.yaml`, `llm_pilot01.yaml`, `fleet_pilot_tb1_v2.yaml`,
`fleet_pilot_tb1_v3.yaml`, `fleet_pilot_tb2_v2.yaml`, `fleet_pilot_tb2_v3.yaml`
— exatamente os nomes de rota referenciados dentro dos resultados que ESTÃO
commitados (`fleet_ws/runs/gt01_curta|gt01_longa|gt01_loop/*.json`,
`fleet_ws/runs/fleet_pilot_tb*_v*/analysis/*`). Essas rotas existem hoje só
no working tree local de quem já as gravou — **um clone novo do GitHub (ou o
zip que o Zenodo arquiva a partir de uma Release) não traria esses arquivos**.

Isso é diferente do caso dos bags MCAP brutos (`collections/`): os bags são
*saída* da execução do protocolo (regenerável relançando a simulação com a
mesma rota), enquanto o YAML da rota é *entrada* do desenho experimental —
não existe como "regerar" `dissertation_clean01.yaml` exatamente igual sem o
próprio arquivo (os waypoints de `rota_longa_curva` e `loop_fechado` felizmente
estão documentados em texto dentro de `implementacao.md`, mas os de
`dissertation_clean01` não estão escritos em lugar nenhum fora do YAML
gitignored). **Isso é uma lacuna real, do mesmo tipo (mas de magnitude menor)
do que o achado de 2026-10-02 sobre os dados da campanha original perdidos**
— ver "Ação sugerida" abaixo e reavaliação logo a seguir.

**Tensão com `REPLICATION.md`:** o documento afirma, na Seção 1, que a rota
"existe no repositório" — isso é verdade só no sentido de "existe no
working tree de quem está lendo isto no disco", não no sentido de "está no
histórico git / seria baixado num clone fresco". Vale o autor decidir se
quer corrigir essa frase pra deixar isso explícito, ou (melhor) resolver a
causa versionando os arquivos (ver Ação sugerida).

### 2026-10-03 — Reavaliação do achado "dados brutos da campanha oficial perdidos" (2026-10-02), à luz do que foi commitado desde então

Resposta direta à pergunta: **a omissão original não foi corrigida — ela
continua real e específica da campanha `dissertation_clean01_final_manual`
do Capítulo 8**. Nada recuperou esses bags; nenhum commit novo os contém.
Isso não mudou.

O que mudou de fato, verificado diretamente nesta rodada (não é inferência,
é leitura de arquivo): **o padrão geral do projeto em preservar dados de
campanhas novas melhorou, e a mitigação aplicada em 2026-10-02
(`_git_provenance()`) está empiricamente confirmada funcionando num
commit real**, não só testada isoladamente como o achado anterior registrava.
Li diretamente `fleet_ws/runs/gt01_curta/replay_r01.json` (committed) e
confirmei o campo populado:
```
"git": {"commit": "628d08146f30778bfdc4ff6c0ee5ea099c1c8839", "dirty": true}
```
— ou seja, qualquer um que baixe o repositório hoje sabe exatamente de qual
commit (e se a árvore estava suja) cada réplica da campanha `gt01_curta` veio.
Isso NÃO existia pra campanha original do Cap. 8 (causa raiz do achado de
2026-10-02) e agora existe de verdade pras campanhas novas (`gt01_curta`,
`gt01_longa`, `gt01_loop`) e pros pilotos de agente multi-robô mais recentes
(`fleet_ws/agent_runs/fleet_*.json`, também com o campo `git` populado,
confirmado por busca). **Nuance que ainda fica como lacuna residual pequena**:
`dirty: true` significa que havia mudanças não commitadas no momento do
registro — o commit sozinho não reconstitui 100% do estado exato (o diff
sujo em si não é capturado em lugar nenhum). Os pilotos mais antigos
(`fleet_ws/agent_runs/single_*.json`, da primeira execução da camada de
agentes em 2026-10-02) não têm o campo `git` — rodaram antes da mitigação
existir no código, consistente com a cronologia já registrada.

**Conclusão prática:** o achado de 2026-10-02 continua válido tal como
escrito (específico à campanha original) — não precisa ser marcado como
desatualizado, só complementado. O que esta rodada acrescenta é: (a) a
mitigação funciona de verdade, não só em teste isolado; (b) existe uma
lacuna *nova e distinta* a reportar (as rotas YAML não versionadas, achado
acima) que é do mesmo "sabor" (artefato de entrada não preservado), mas
afeta as campanhas *novas*, não a original.

### 2026-10-03 — O que deveria entrar no pacote de replicação mínimo arquivado no Zenodo

Pergunta respondida: **repositório git completo (sem os bags brutos) é a
recomendação certa — não é preciso nada mais seletivo, mas falta um ajuste
concreto antes de criar a Release.**

Raciocínio: a integração GitHub→Zenodo (confirmada em fonte primária em
2026-10-02, ver achado acima) arquiva exatamente o conteúdo do repositório
git na tag da Release — não o working tree local, não os diretórios
gitignored. Hoje, o que está commitado e entraria automaticamente é:
código completo (`fleet_ws/src`, `backend/`, `frontend/`), `CITATION.cff`,
`LICENSE` (MIT), `README.md`, `orquestracion.md`, `conhecimento/*.md`,
`implementacao.md`, `fleet_ws/docs/REPLICATION.md` e
`EXPERIMENT_PROTOCOL.md`, e os resultados já processados das campanhas
recentes (`fleet_ws/runs/gt01_curta|gt01_longa|gt01_loop/*` — manifests,
exports JSON com proveniência git, logs; `fleet_ws/runs/fleet_pilot_tb*_v*/
analysis/*` e `fleet_ws/runs/dissertacao_teste1_*/analysis/*` — summary.json,
CSVs de trajetória, PNG do overlay; `fleet_ws/agent_runs/*.json`). Ficam de
fora, corretamente: `build/`, `install/`, `log/` (artefatos de build, não
dados de pesquisa), `collections/` (bags MCAP brutos, ~36MB, regeneráveis
relançando o protocolo documentado em `REPLICATION.md`), e — **ponto a
corrigir antes da Release** — `fleet_ws/routes/*` (ver achado acima).

**Roteiro concreto recomendado pro autor** (nenhum passo exige mudar
código, só decisões de versionamento + ações na UI do GitHub/Zenodo, que só
o autor logado pode fazer):

1. Decidir se quer versionar os arquivos de rota (resolve a lacuna do
   achado acima). Caminho de menor esforço: `git add -f` nos 8 arquivos
   específicos listados no achado acima (não remover o `routes/` do
   `.gitignore` por inteiro, que continuaria bloqueando rotas futuras de
   teste/scratch — só liberar os que correspondem a campanhas já
   publicadas/commitadas). Alternativa: mover esses 8 arquivos pra um
   diretório novo não coberto pelo gitignore (ex.
   `fleet_ws/routes_archive/`) e referenciar os dois diretórios na
   documentação. Decisão e execução ficam com o autor.
2. Confirmar que o commit/tag escolhido pra Release é o estado desejado
   (sugestão: depois do merge de `mission-coordinate-large-scale` pra
   `main`, ou a branch que o autor decidir ser a "oficial" — a Zenodo
   arquiva o que estiver no tag, independente de branch default).
3. No GitHub: criar uma **Release** nova (não só uma tag) — "Releases" →
   "Draft a new release", escolher/criar a tag (ex. `v1.0.0` ou
   `dissertacao-cap08-cap09`), preencher título e notas descrevendo o que
   essa versão representa (ex. "código + campanha de ground truth
   odom/pose/GT + pilotos da camada de agentes de IA, Capítulos 8-9").
4. Login em Zenodo com "Log in with GitHub", autorizar o app, ir à página
   de configurações do GitHub dentro do Zenodo, ligar o toggle do repo
   `fleet-ui` ANTES de publicar a Release (ou publicar de novo depois de
   ligar o toggle — o arquivamento automático só acontece em Releases
   criadas com o toggle já ligado, conforme o processo já confirmado em
   2026-10-02).
5. Depois de publicado, o Zenodo gera 2 DOIs: um específico da versão
   (a Release) e um "guarda-chuva" (concept DOI) que sempre aponta pra
   versão mais recente — citar o DOI "guarda-chuva" na dissertação é mais
   seguro (continua válido se o autor criar uma v1.1 depois).
6. Opcional, não obrigatório: se depois quiser incluir também os bags
   brutos específicos usados nas campanhas `gt01_*`/pilotos (não a íntegra
   de `collections/`, só os relevantes), usar "New version" na UI do
   Zenodo pra fazer upload manual deles no mesmo registro (ver achado
   acima — não confirmado em fonte primária direta, confirmar na UI antes
   de depender disso). Não é necessário pro pacote mínimo — 36MB de bags
   são regeneráveis seguindo `REPLICATION.md`.
7. Adicionar o DOI resultante ao `CITATION.cff` (campo `doi:` ou
   `identifiers:`) e citar na dissertação.

**Ação sugerida:** passos 1 (versionar as rotas) e 3-7 (criar a Release/
Zenodo) ficam como itens concretos em `implementacao.md`, "Pendente" — o
passo 1 é novo nesta rodada, os passos 3-7 só detalham o item que já
existia desde 2026-10-02, que seguia vago ("criar a Release e conectar o
Zenodo") e agora tem o roteiro exato.
