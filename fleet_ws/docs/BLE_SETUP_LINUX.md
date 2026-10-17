# Bluetooth (BLE) no Linux — checklist pra rodar `ble_rssi_publisher.py`

Testado de ponta a ponta nesta sessão numa máquina Linux (Ubuntu) **sem**
adaptador Bluetooth físico — confirma que o caminho de erro funciona, não
que o scan funciona (isso só com hardware real).

## 1. Pré-requisitos

```bash
# dentro do venv do backend (ou outro venv do projeto)
pip install bleak
```

`bleak` no Linux usa o **BlueZ** via D-Bus (biblioteca `dbus-fast`, instalada
junto). Não precisa de `bluepy`, `pybluez` nem nada mais além disso.

## 2. Confirme que o serviço Bluetooth do sistema está de pé

```bash
systemctl status bluetooth
# se não estiver ativo:
sudo systemctl start bluetooth
```

## 3. Confirme que o seu usuário tem permissão de scan

Em algumas distros, escanear BLE sem root exige estar no grupo `bluetooth`:

```bash
groups $USER | grep bluetooth || sudo usermod -aG bluetooth $USER
# depois de rodar isso, é preciso deslogar/logar de novo (ou reiniciar)
```

## 4. Rode o diagnóstico

```bash
python3 fleet_ws/scripts/check_ble_setup.py
```

Saída esperada com hardware funcionando: lista pelo menos 1 dispositivo BLE
próximo (qualquer um — celular, fone, etc.) em até 3 segundos. Se falhar,
o script já imprime a causa mais provável (sem adaptador, D-Bus fora do ar,
permissão).

## 5. Docker: um detalhe que não é óbvio

Se o Fleet UI estiver rodando dentro de um container Docker (ver
`docker-compose.yml`, modo Linux usa `network_mode: host`), o adaptador
Bluetooth do host **não aparece automaticamente** dentro do container — BLE
via D-Bus precisa que o socket do D-Bus do sistema (`/var/run/dbus`) e o
grupo `bluetooth` estejam acessíveis de dentro do container. Isso não foi
testado nesta sessão (sem adaptador físico pra confirmar); se o nó rodar na
mesma máquina física sem Docker (fora do container, direto no host), esse
problema não existe.

## 6. Rodando o nó de verdade

```bash
ros2 run fleet_orchestrator ble_rssi_publisher \
  --ros-args -p target_address:="AA:BB:CC:DD:EE:FF" -p scan_interval_s:=1.0
```

Troque `target_address` pelo endereço MAC real do dispositivo fixo do
experimento (não o celular que o robô carrega — é o outro lado da conexão).
