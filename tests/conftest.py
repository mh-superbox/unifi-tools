import logging
import tempfile
from pathlib import Path

import pytest

from unifi_tools.config import Config
from unifi_tools.config import LOGGER_NAME


@pytest.fixture(autouse=True, scope="session")
def logger():
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger(LOGGER_NAME).handlers.clear()
    logging.info("Initialize logging")


class ConfigLoader:
    def __init__(self):
        self.temp_name: Path = Path(tempfile.NamedTemporaryFile().name)

    def write_config(self, content: str):
        with open(self.temp_name, "w") as f:
            f.write(content)

    def get_config(self) -> Config:
        return Config(config_file_path=self.temp_name)

    def cleanup(self):
        self.temp_name.unlink()


@pytest.fixture()
def config_loader(request) -> ConfigLoader:
    c = ConfigLoader()
    c.write_config(request.param)

    logging.info("Create configuration: %s", c.get_config())

    return c
