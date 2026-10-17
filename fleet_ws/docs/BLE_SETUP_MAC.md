# Bluetooth (BLE) no macOS — checklist pra rodar `check_ble_setup.py` / `ble_rssi_publisher.py`

**Atenção**: baseado em pesquisa (documentação oficial do `bleak` e
troubleshooting do projeto), **não testado ao vivo** — não há máquina Mac
disponível nesta sessão. Trate como ponto de partida, não garantia.

## 1. Instalar

```bash
pip install bleak
```

No macOS, `bleak` usa o **CoreBluetooth** nativo — não precisa de nenhuma
lib de sistema extra (diferente do Linux, que depende do BlueZ).

## 2. A pegadinha real: permissão de Bluetooth por app

O macOS trata acesso a Bluetooth como dado sensível de privacidade (TCC —
Transparency, Consent and Control), igual câmera/microfone. Sem autorizar,
o processo Python **morre com SIGABRT** em vez de dar um erro Python normal
— é fácil confundir com um bug.

- Rode o scan uma vez (`python3 fleet_ws/scripts/check_ble_setup.py`).
- Se travar/morrer sem mensagem Python clara, abra **Ajustes do Sistema →
  Privacidade e Segurança → Bluetooth** e confirme se o **Terminal** (ou
  o app que roda o Python — iTerm, VS Code, etc.) está na lista, com a
  caixinha marcada.
- Se não aparecer na lista ainda, rode o scan de novo — o macOS costuma
  adicionar o app à lista na primeira tentativa de acesso (só sem marcar);
  depois é só marcar manualmente.

Fonte: documentação oficial do bleak, seção de troubleshooting
(bleak.readthedocs.io/en/latest/troubleshooting.html) — o problema é descrito
como "da configuração do app que roda Python", não um bug do bleak em si.

## 3. Versão do macOS: uma ressalva específica

macOS 12.0 a 12.2 tinha um bug conhecido: scan sem `service_uuids` explícito
não via nenhum dispositivo (corrigido no 12.3). `check_ble_setup.py` faz um
scan genérico (sem `service_uuids`) — se estiver numa dessas versões exatas
(pouco provável hoje, mas Macs de laboratório às vezes ficam presos numa
versão antiga), pode dar falso negativo mesmo com adaptador funcionando.

## 4. Rode o diagnóstico

```bash
python3 fleet_ws/scripts/check_ble_setup.py
```

Mesmo script do Linux/Windows — é cross-platform, não precisa de nenhuma
adaptação pro Mac.

## 5. Rodando o nó de verdade

ROS2 nativo no macOS é possível mas incomum em produção (sem o suporte de
pacote binário oficial que Linux tem). Se o resto do Fleet UI (ROS2/Gazebo)
rodar em Linux ou via Docker, a mesma lógica do documento do Windows se
aplica: o scanner BLE pode rodar nativo no Mac (CoreBluetooth funciona bem
localmente) e mandar o RSSI pro backend via HTTP, em vez de tentar rodar
rclpy direto no Mac — mas isso também não foi testado nesta sessão.
