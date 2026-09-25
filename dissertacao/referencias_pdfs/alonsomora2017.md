# alonsomora2017

**Título:** Multi-robot Formation Control and Object Transport in Dynamic Environments via Constrained Optimization

**Autores:** Javier Alonso-Mora, Stuart Baker, Daniela Rus

**Ano:** 2017

**Venue:** The International Journal of Robotics Research, vol. 36, n. 9, pp. 1000–1021 (SAGE)

**DOI:** [10.1177/0278364917719333](https://doi.org/10.1177/0278364917719333)

**Página oficial:** https://journals.sagepub.com/doi/10.1177/0278364917719333

**Cópia Open Access confirmada (repositório institucional):**
https://research.tudelft.nl/en/publications/multi-robot-formation-control-and-object-transport-in-dynamic-env
(TU Delft Research Portal, licença CC BY-NC, arquivo indexado como
`research.tudelft.nl/files/25370849/0278364917719333.pdf`)

## Abstract

We present a constrained optimization method for multi-robot formation control in dynamic
environments, where the robots adjust the parameters of the formation, such as size and
three-dimensional orientation, to avoid collisions with static and moving obstacles, and to make
progress towards their goal. We describe two variants of the algorithm, one for local motion
planning and one for global path planning. The local planner first computes a large
obstacle-free convex region in a neighborhood of the robots, embedded in position-time space.
Then, the parameters of the formation are optimized therein by solving a constrained
optimization, via sequential convex programming. The robots navigate towards the optimized
formation with individual controllers that account for their dynamics. The idea is extended to
global path planning by sampling convex regions in free position space and connecting them if a
transition in formation is possible - computed via the constrained optimization. The path of
lowest cost to the goal is then found via graph search. The method applies to ground and aerial
vehicles navigating in two- and three-dimensional environments among static and dynamic
obstacles, allows for reconfiguration, and is efficient and scalable with the number of robots.
In particular, we consider two applications, a team of aerial vehicles navigating in formation,
and a small team of mobile manipulators that collaboratively carry an object. The approach is
verified in experiments with a team of three mobile manipulators and in simulations with a team
of up to sixteen Micro Air Vehicles (quadrotors).

(Abstract obtido via API pública da Semantic Scholar, DOI 10.1177/0278364917719333.)

## Status

**PDF confirmado como Open Access, mas não baixado por bloqueio técnico.** O TU Delft Research
Portal (repositório institucional, um dos autores é da TU Delft) hospeda o PDF sob licença CC
BY-NC — a página confirma explicitamente essa disponibilidade. Porém, o servidor de arquivos do
portal está atrás de uma proteção anti-bot (Cloudflare "Just a moment..." challenge) que impediu
o download automatizado nesta sessão (duas tentativas, ambas retornaram uma página de desafio
HTML em vez do PDF). Recomendo ao autor baixar manualmente pelo link acima em um navegador
comum — é acesso aberto legítimo, só não pôde ser automatizado aqui.
