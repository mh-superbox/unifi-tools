import dataclasses
import logging
import re
import socket
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any
from typing import Final
from typing import Match
from typing import NamedTuple
from typing import Optional

import yaml

from unifi_tools.logging import LOG_LEVEL
from unifi_tools.logging import LOG_NAME
from unifi_tools.logging import init_logger
from unifi_tools.logging import stream_handler

logger: logging.Logger = init_logger(name=LOG_NAME, level="info", handlers=[stream_handler])


class LogPrefix:
    API: Final[str] = "[API]"
    CONFIG: Final[str] = "[CONFIG]"
    MQTT: Final[str] = "[MQTT]"


class RegexValidation(NamedTuple):
    regex: str
    error: str


class Validation:
    ALLOWED_CHARACTERS: RegexValidation = RegexValidation(
        regex=r"^[a-z\d_-]*$", error="The following characters are prohibited: a-z 0-9 -_"
    )


class ConfigException(Exception):
    pass


@dataclass
class ConfigBase:
    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                item = getattr(self, key)

                if is_dataclass(item):
                    item.update(value)
                else:
                    setattr(self, key, value)

        self.validate()

    def update_from_yaml_file(self, config_path: Path):
        _config: dict = {}

        if config_path.exists():
            try:
                _config = yaml.load(config_path.read_text(), Loader=yaml.FullLoader)
            except yaml.MarkedYAMLError as e:
                raise ConfigException(f"{LogPrefix.CONFIG} Can't read YAML file!\n{str(e.problem_mark)}")

        self.update(_config)

    def validate(self):
        for f in dataclasses.fields(self):
            value: Any = getattr(self, f.name)

            if is_dataclass(value):
                value.validate()
            else:
                if method := getattr(self, f"_validate_{f.name}", None):
                    setattr(self, f.name, method(getattr(self, f.name), f=f))

                if not isinstance(value, f.type) and not is_dataclass(value):
                    raise ConfigException(f"{LogPrefix.CONFIG} Expected {f.name} to be {f.type}, got {repr(value)}")


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

    def _validate_discovery_prefix(self, value: str, f: dataclasses.Field):
        value = value.lower()
        result: Optional[Match[str]] = re.search(Validation.ALLOWED_CHARACTERS.regex, value)

        if result is None:
            raise ConfigException(
                f"{LogPrefix.CONFIG} [{self.__class__.__name__.replace('Config', '').upper()}] Invalid value '{value}' in '{f.name}'. {Validation.ALLOWED_CHARACTERS.error}"
            )

        return value


@dataclass
class UniFiControllerConfig(ConfigBase):
    url: str = field(default="localhost")
    port: int = field(default=8443)
    username: str = field(default="username")
    password: str = field(default="password")


@dataclass
class LoggingConfig(ConfigBase):
    level: str = field(default="info")

    def update_level(self):
        logger.setLevel(LOG_LEVEL[self.level])

    def _validate_level(self, value: str, f: dataclasses.Field):
        value = value.lower()

        if value not in LOG_LEVEL.keys():
            raise ConfigException(
                f"{LogPrefix.CONFIG} Invalid log level '{self.level}'. The following log levels are allowed: {' '.join(LOG_LEVEL.keys())}."
            )

        return value


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
        self.update_from_yaml_file(config_path=self.config_file_path)
        self.logging.update_level()

    @staticmethod
    def _validate_device_name(value: str, f: dataclasses.Field):
        value = value.lower()
        result: Optional[Match[str]] = re.search(Validation.ALLOWED_CHARACTERS.regex, value)

        if result is None:
            raise ConfigException(
                f"{LogPrefix.CONFIG} Invalid value '{value}' in '{f.name}'. {Validation.ALLOWED_CHARACTERS.error}"
            )

        return value

    def get_feature(self, device_id: str) -> dict:
        return self.features.get(device_id, {})
