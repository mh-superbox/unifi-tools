import logging

import pytest

from unifi_tools.config import Config
from unifi_tools.config import LoggingConfig


@pytest.fixture()
def config() -> Config:
    config = Config()

    config.logging = LoggingConfig(level="debug")
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    config.device_name = "MOCKED_UNIFI"
    config.features = {
        "MOCKED_ID": {
            "ports": [
                {
                    "port_idx": 3,
                    "poe_mode": "pasv24",
                }
            ]
        }
    }

    return config
