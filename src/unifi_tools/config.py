import dataclasses
import logging
import re
import socket
import sys
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from pathlib import Path
from typing import Dict
from typing import Final
from typing import Match
from typing import Optional

import yaml

LOG_MQTT_PUBLISH: Final[str] = "[MQTT] [%s] Publishing message: %s"
LOG_MQTT_SUBSCRIBE: Final[str] = "[MQTT] [%s] Subscribe message: %s"
LOG_MQTT_INVALIDE_SUBSCRIBE: Final[str] = "[MQTT] [%s] Invalid subscribe message: %s"
LOG_MQTT_SUBSCRIBE_TOPIC: Final[str] = "[MQTT] Subscribe topic %s"
LOGGER_NAME: Final[str] = "unifi-tools"

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(logging.Formatter(fmt="%(levelname)8s | %(message)s"))

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(stdout_handler)


@dataclass
class ConfigBase:
    def __post_init__(self):
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)

            if not isinstance(value, f.type) and not is_dataclass(value):
                logger.error(
                    "[CONFIG] %s - Expected %s to be %s, got %s",
                    self.__class__.__name__,
                    f.name,
                    f.type,
                    repr(value),
                )

                sys.exit(1)

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                item = getattr(self, key)

                if is_dataclass(item):
                    item.update(value)
                else:
                    setattr(self, key, value)


@dataclass
class MqttConfig(ConfigBase):
    host: str = field(default="localhost")
    port: int = field(default=1883)
    keepalive: int = field(default=15)
    retry_limit: int = field(default=30)
    reconnect_interval: int = field(default=10)


@dataclass
class DeviceInfo(ConfigBase):
    manufacturer: str = field(default="Ubiquiti Inc.")


@dataclass
class HomeAssistantConfig(ConfigBase):
    enabled: bool = field(default=True)
    discovery_prefix: str = field(default="homeassistant")
    device: DeviceInfo = field(default_factory=DeviceInfo)


@dataclass
class UniFiControllerConfig(ConfigBase):
    url: str = field(default="localhost")
    port: int = field(default=8443)
    username: str = field(default="username")
    password: str = field(default="password")


@dataclass
class LoggingConfig(ConfigBase):
    level: str = field(default="info")


@dataclass
class Config(ConfigBase):
    device_name: str = field(default=socket.gethostname())
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    homeassistant: HomeAssistantConfig = field(default_factory=HomeAssistantConfig)
    unifi_controller: UniFiControllerConfig = field(default_factory=UniFiControllerConfig)
    features: dict = field(default_factory=dict)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    config_file_path: Path = field(default=Path("/etc/unifi/settings.yaml"))
    systemd_path: Path = field(default=Path("/etc/systemd/system"))

    def __post_init__(self):
        _config: dict = self.get_config(self.config_file_path)
        self.update(_config)

        super().__post_init__()

        if self.device_name:
            result: Optional[Match[str]] = re.search(r"^[\w\d_-]*$", self.device_name)

            if result is None:
                logger.error(
                    "[CONFIG] Invalid value '%s' in 'device_name'. "
                    "The following characters are prohibited: A-Z a-z 0-9 -_",
                    self.device_name,
                )
                sys.exit(1)

        self._change_logger_level()

    def get_feature(self, device_id: str) -> dict:
        return self.features.get(device_id, {})

    @staticmethod
    def get_config(config_path: Path) -> dict:
        _config: dict = {}

        if config_path.exists():
            _config = yaml.load(config_path.read_text(), Loader=yaml.FullLoader)

        return _config

    def _change_logger_level(self):
        level: Dict[str, int] = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }

        logger.setLevel(level[self.logging.level])
