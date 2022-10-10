from typing import Final

CONFIG_INVALID_DEVICE_NAME: Final[
    str
] = """device_info:
  name: Invalid Device Name
logging:
  level: debug
"""

CONFIG_INVALID_HOMEASSISTANT_DISCOVERY_PREFIX: Final[
    str
] = """device_info:
  name: MOCKED_UNIFI
homeassistant:
  enabled: true
  discovery_prefix: INVALID DISCOVERY NAME
logging:
  level: debug
"""

CONFIG_INVALID_FEATURE_TYPE: Final[
    str
] = """device_info:
  name: MOCKED_DEVICE
features: INVALID
logging:
  level: debug
"""

CONFIG_INVALID_FEATURE_PROPERTY: Final[
    str
] = """device_info:
  name: MOCKED_DEVICE
features:
  MOCKED_DEVICE_ID:
    invalid_property: INVALID
logging:
  level: debug
"""

CONFIG_INVALID_LOG_LEVEL: Final[
    str
] = """device_info:
  name: MOCKED_UNIPI
logging:
  level: invalid"""
