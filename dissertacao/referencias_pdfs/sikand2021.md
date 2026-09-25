# sikand2021

**Título:** Robofleet: Open Source Communication and Management for Fleets of Autonomous Robots

**Autores:** Kavan Singh Sikand, Logan Zartman, Sadegh Rabiee, Joydeep Biswas

**Ano:** 2021

**Venue:** 2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pp. 406–412

**DOI:** [10.1109/IROS51168.2021.9635830](https://doi.org/10.1109/IROS51168.2021.9635830)
(preprint: arXiv:2103.06993)

**Página oficial:** https://ieeexplore.ieee.org/document/9635830

## Abstract

Long-term deployment of a fleet of mobile robots requires reliable and secure two-way
communication channels between individual robots and remote human operators for supervision
and tasking. Existing open-source solutions to this problem degrade in performance in
challenging real-world situations such as intermittent and low-bandwidth connectivity, do not
provide security control options, and can be computationally expensive on hardware-constrained
mobile robot platforms. In this paper, we present Robofleet, a lightweight open-source system
which provides inter-robot communication, remote monitoring, and remote tasking for a fleet of
ROS-enabled service-mobile robots that is designed with the practical goals of resilience to
network variance and security control in mind.

Robofleet supports multi-user, multi-robot communication via a central server. This architecture
deduplicates network traffic between robots, significantly reducing overall network load when
compared with native ROS communication. This server also functions as a single entrypoint into
the system, enabling security control and user authentication. Individual robots run the
lightweight Robofleet client, which is responsible for exchanging messages with the Robofleet
server. It automatically adapts to adverse network conditions through backpressure monitoring
as well as topic-level priority control, ensuring that safety-critical messages are successfully
transmitted. Finally, the system includes a web-based visualization tool that can be run on any
internet-connected, browser-enabled device to monitor and control the fleet.

We compare Robofleet to existing methods of robotic communication, and demonstrate that it
provides superior resilience to network variance while maintaining performance that exceeds
that of widely-used systems.

## Status

**PDF disponível.** Baixado do preprint arXiv (versão de acesso aberto legítima):
https://arxiv.org/abs/2103.06993 — arquivo salvo como `sikand2021.pdf` nesta pasta.
