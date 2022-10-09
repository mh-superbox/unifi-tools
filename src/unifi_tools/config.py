import dataclasses
import logging
import re
import socket
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Final
from typing import Match
from typing import Optional

from superbox_utils.config.exception import ConfigException
from superbox_utils.config.loader import ConfigLoaderMixin
from superbox_utils.config.loader import Validation
from superbox_utils.hass.config import HomeAssistantConfig
from superbox_utils.logging import init_logger
from superbox_utils.logging import stream_handler
from superbox_utils.logging.config import LoggingConfig
from superbox_utils.mqtt.config import MqttConfig
from unifi_tools.logging import LOG_NAME

logger: logging.Logger = init_logger(name=LOG_NAME, level="info", handlers=[stream_handler])


class LogPrefix:
    API: Final[str] = "[API]"
    CONFIG: Final[str] = "[CONFIG]"
    MQTT: Final[str] = "[MQTT]"


@dataclass
class DeviceInfo(ConfigLoaderMixin):
    name: str = field(default=socket.gethostname())
    manufacturer: str = field(default="Ubiquiti Inc.")

    @staticmethod
    def _validate_name(value: str, f: dataclasses.Field) -> str:
        result: Optional[Match[str]] = re.search(Validation.ALLOWED_CHARACTERS.regex, value)

        if result is None:
            raise ConfigException(f"Invalid value '{value}' in '{f.name}'. {Validation.ALLOWED_CHARACTERS.error}")

        return value


@dataclass
class UniFiControllerConfig(ConfigLoaderMixin):
    url: str = field(default="localhost")
    port: int = field(default=8443)
    username: str = field(default="username")
    password: str = field(default="password")


@dataclass
class Config(ConfigLoaderMixin):
    device_info: DeviceInfo = field(default=DeviceInfo())
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    homeassistant: HomeAssistantConfig = field(default_factory=HomeAssistantConfig)
    unifi_controller: UniFiControllerConfig = field(default_factory=UniFiControllerConfig)
    features: dict = field(default_factory=dict)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    config_file_path: Path = field(default=Path("/etc/unifi/settings.yaml"))
    systemd_path: Path = field(default=Path("/etc/systemd/system"))

    def __post_init__(self):
        self.update_from_yaml_file(config_path=self.config_file_path)
        self.logging.update_level(name=LOG_NAME)

    def get_feature(self, device_id: str) -> dict:
        return self.features.get(device_id, {})
