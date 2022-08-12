import logging

import pytest

from unifi_tools.config import Config
from unifi_tools.config import LoggingConfig


@pytest.fixture()
def config() -> Config:
    config = Config()

    config.logging = LoggingConfig(level="debug")
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return config
