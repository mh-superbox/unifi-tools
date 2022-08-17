import logging
import tempfile
from pathlib import Path
from typing import Final

import pytest

from unifi_tools.config import Config

CONFIG_CONTENT: Final[
    str
] = """device_name: MOCKED_UNIFI
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


@pytest.fixture()
def config() -> Config:
    tmp = tempfile.NamedTemporaryFile()

    with open(tmp.name, "w") as f:
        f.write(CONFIG_CONTENT)

    _config = Config(config_file_path=Path(tmp.name))
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return _config
