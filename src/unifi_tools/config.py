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
from typing import Match
from typing import Optional

import yaml

LOG_MQTT_PUBLISH: str = "[MQTT] [%s] Publishing message: %s"
LOG_MQTT_SUBSCRIBE: str = "[MQTT] [%s] Subscribe message: %s"
LOG_MQTT_INVALIDE_SUBSCRIBE: str = "[MQTT] [%s] Invalid subscribe message: %s"
LOG_MQTT_SUBSCRIBE_TOPIC: str = "[MQTT] Subscribe topic %s"

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(logging.Formatter(fmt="%(levelname)8s | %(message)s"))

logger = logging.getLogger("asyncio")
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
    host: str = field(default="unipi.home")  # TODO change to localhost
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
    device: DeviceInfo = field(default=DeviceInfo())


@dataclass
class UniFiControllerConfig(ConfigBase):
    url: str = field(default="unifi.superbox.one")  # TODO change
    username: str = field(default="hass")  # TODO change
    password: str = field(default="TQx6TXacuUu98ee4VqJH")  # TODO change
    retry_limit: int = field(default=30)
    reconnect_interval: int = field(default=10)


@dataclass
class LoggingConfig(ConfigBase):
    level: str = field(default="debug")  # TODO change to info


@dataclass
class Config(ConfigBase):
    device_name: str = field(default=socket.gethostname())
    mqtt: MqttConfig = field(default=MqttConfig())
    homeassistant: HomeAssistantConfig = field(default=HomeAssistantConfig())
    unifi_controller: UniFiControllerConfig = field(default=UniFiControllerConfig())
    logging: LoggingConfig = field(default=LoggingConfig())
    config_base_path: Path = field(default=Path("/etc"))

    def __post_init__(self):
        super().__post_init__()

        config_path: Path = self.config_base_path.joinpath("unifi-tools.yaml")
        _config: dict = self.get_config(config_path)

        self.update(_config)

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
