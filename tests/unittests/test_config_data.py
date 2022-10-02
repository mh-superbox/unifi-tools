from typing import Final

CONFIG_INVALID_DEVICE_NAME: Final[
    str
] = """device_name: Invalid Device Name
logging:
  level: debug
"""

CONFIG_INVALID_HOMEASSISTANT_DISCOVERY_PREFIX: Final[
    str
] = """device_name: MOCKED_UNIFI
homeassistant:
  enabled: true
  discovery_prefix: INVALID DISCOVERY NAME
logging:
  level: debug
"""

CONFIG_INVALID_TYPE: Final[
    str
] = """device_name: MOCKED_DEVICE
features: INVALID
logging:
  level: debug
"""

CONFIG_INVALID_LOG_LEVEL: Final[
    str
] = """device_name: MOCKED_UNIPI
logging:
  level: invalid"""
