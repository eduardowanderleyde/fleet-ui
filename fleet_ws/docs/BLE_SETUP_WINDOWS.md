# Bluetooth (BLE) no Windows — caminho recomendado

**Atenção**: este documento é baseado em pesquisa (documentação oficial do
`bleak`) e no código já existente deste repositório (`docker-compose.windows.yml`,
`README.md`), **não em teste ao vivo** — não há máquina Windows disponível
nesta sessão. Trate os passos abaixo como ponto de partida, não garantia.

## O problema que isso evita

O Fleet UI completo (ROS2 + Gazebo + ponte web) já roda no Windows via Docker
Desktop (ver `docker-compose.windows.yml`, modo headless). Docker Desktop no
Windows usa WSL2 por baixo — passar um adaptador Bluetooth **físico** do
Windows pro WSL2 é conhecido por ser instável (ferramenta `usbipd-win`, não
pensada pra Bluetooth especificamente). **Não recomendo esse caminho.**

## O caminho recomendado: scanner BLE roda fora do Docker

`bleak` roda nativamente no Windows via WinRT (confirmado na documentação
oficial: bleak.readthedocs.io/en/stable/backends/windows.html) — **sem
precisar de Docker, WSL2 nem nenhuma camada extra**. A ideia:

1. O Fleet UI (backend + ROS2 + Gazebo) continua rodando dentro do Docker,
   exatamente como já está documentado no `README.md`, expondo a API em
   `localhost:8000` (já mapeado em `docker-compose.windows.yml`).
2. O scanner BLE roda como um **processo Python Windows nativo separado**,
   fora do container, direto no host — onde o adaptador Bluetooth do
   notebook/PC já funciona sem configuração extra.
3. Esse processo nativo manda cada leitura de RSSI pra dentro do container
   via HTTP, no mesmo `localhost:8000` que já está mapeado — **não existe
   hoje** um endpoint pronto pra isso no backend; seria preciso adicionar um
   `POST /api/ble_rssi` simples em `backend/main.py` que repassa o valor pro
   tópico ROS2 (o backend já roda dentro do container, com rclpy disponível).

```powershell
# no PowerShell do Windows, fora do Docker
pip install bleak requests
python ble_rssi_bridge_windows.py --target-address AA:BB:CC:DD:EE:FF
```

Esse `ble_rssi_bridge_windows.py` ainda não existe neste repositório — é o
próximo passo, só depois de confirmar numa máquina Windows real que o scan
nativo funciona (rodar `fleet_ws/scripts/check_ble_setup.py` direto no
Windows, fora do Docker, é o primeiro teste: ele já é cross-platform, não
precisa de nenhuma adaptação).

## Por que não official

Sem máquina Windows pra testar, não criei o endpoint novo no backend nem o
script de ponte — seria código não verificado apresentado como pronto, o que
é pior que não ter nada. O que está pronto e é seguro de rodar: o diagnóstico
`check_ble_setup.py` (mesmo arquivo do Linux, funciona em qualquer SO que o
bleak suporte).
