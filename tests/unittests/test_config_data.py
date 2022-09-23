from typing import Final

CONFIG_INVALID_DEVICE_NAME: Final[
    str
] = """device_name: Invalid Device Name
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
  MOCKED_ID:
    ports:
      - port_idx: 3
        poe_mode: pasv24
logging:
  level: debug
"""

CONFIG_INVALID_TYPE: Final[
    str
] = """device_name: MOCKED_DEVICE
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
features: INVALID
logging:
  level: debug
"""
