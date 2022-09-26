import logging
from pathlib import Path

import pytest
from pytest_asyncio.plugin import SubRequest

from unifi_tools.config import Config
from unifi_tools.config import LOGGER_NAME


@pytest.fixture(autouse=True, scope="session")
def logger():
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger(LOGGER_NAME).handlers.clear()
    logging.info("Initialize logging")


class ConfigLoader:
    def __init__(self, temp: Path):
        self.temp: Path = temp
        self.temp_config_file_path: Path = self.temp / "settings.yml"

        self.systemd_path = self.temp / "systemd/system"
        self.systemd_path.mkdir(parents=True)

    def write_config(self, content: str):
        with open(self.temp_config_file_path, "w") as f:
            f.write(content)

    def get_config(self) -> Config:
        return Config(
            config_file_path=self.temp_config_file_path,
            systemd_path=self.systemd_path,
        )


@pytest.fixture()
def config_loader(request: SubRequest, tmp_path: Path) -> ConfigLoader:
    c: ConfigLoader = ConfigLoader(temp=tmp_path)
    c.write_config(request.param)

    logging.info("Create configuration: %s", c.get_config())

    return c
