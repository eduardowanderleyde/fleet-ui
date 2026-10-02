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

### 2026-10-02 — Ação aplicada: `CITATION.cff` criado

Item 3 (acima) sobre `CITATION.cff` foi feito: arquivo criado na raiz do
repositório (`CITATION.cff`, `cff-version: 1.2.0`), autor confirmado
diretamente com o autor do projeto (Eduardo Wanderley, consistente com o
`@eduardowanderleyde` do GitHub), licença MIT (já existente em
`LICENSE`), `repository-code` apontando pro GitHub. **Não tem DOI ainda**
— isso depende do item 2 (Zenodo), que segue pendente porque exige login
do próprio autor no Zenodo, não pode ser feito por um agente. Ver
`implementacao.md` ("Feito" e "Pendente").
