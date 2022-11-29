from typing import Final

CONFIG_CONTENT: Final[
    str
] = """device_info:
  name: MOCKED_UNIFI
mqtt:
  host: localhost
  port: 1883
  connection:
    keepalive: 15
    retry_limit: 30
    reconnect_interval: 10
homeassistant:
  enabled: true
  discovery_prefix: homeassistant
unifi_controller:
  url: localhost
  port: 8443
  username: username
  password: password
features:
  MOCKED_DEVICE_ID:
    object_id: MOCKED_ID
    ports:
      - port_idx: 3
        poe_mode: pasv24
logging:
  level: debug
"""
