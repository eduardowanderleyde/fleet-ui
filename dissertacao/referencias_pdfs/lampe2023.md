# lampe2023

**Título:** RobotKube: Orchestrating Large-Scale Cooperative Multi-Robot Systems with Kubernetes and ROS

**Autores:** Bastian Lampe, Lennart Reiher, Lukas Zanger, Timo Woopen, Raphael van Kempen, Lutz Eckstein

**Ano:** 2023

**Venue:** 2023 IEEE 26th International Conference on Intelligent Transportation Systems (ITSC), pp. 2719–2725

**DOI:** [10.1109/ITSC57777.2023.10422370](https://doi.org/10.1109/ITSC57777.2023.10422370)
(preprint: arXiv:2308.07053)

**Página oficial:** https://ieeexplore.ieee.org/document/10422370

## Abstract

Modern cyber-physical systems (CPS) such as Cooperative Intelligent Transport Systems (C-ITS)
are increasingly defined by the software which operates these systems. In practice,
microservice architectures can be employed, which may consist of containerized microservices
running in a cluster comprised of robots and supporting infrastructure. These microservices
need to be orchestrated dynamically according to ever changing requirements posed at the
system. Additionally, these systems are embedded in DevOps processes aiming at continually
updating and upgrading both the capabilities of CPS components and of the system as a whole.
In this paper, we present RobotKube, an approach to orchestrating containerized microservices
for large-scale cooperative multi-robot CPS based on Kubernetes. We describe how to automate
the orchestration of software across a CPS, and include the possibility to monitor and
selectively store relevant accruing data. In this context, we present two main components of
such a system: an event detector capable of, e.g., requesting the deployment of additional
applications, and an application manager capable of automatically configuring the required
changes in the Kubernetes cluster. By combining the widely adopted Kubernetes platform with
the Robot Operating System (ROS), we enable the use of standard tools and practices for
developing, deploying, scaling, and monitoring microservices in C-ITS. We demonstrate and
evaluate RobotKube in an exemplary and reproducible use case that we make publicly available
at https://github.com/ika-rwth-aachen/robotkube.

## Status

**PDF disponível.** Baixado do preprint arXiv (versão de acesso aberto legítima):
https://arxiv.org/abs/2308.07053 — arquivo salvo como `lampe2023.pdf` nesta pasta.
