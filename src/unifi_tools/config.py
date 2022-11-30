import dataclasses
import logging
import re
import socket
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Final
from typing import List

from superbox_utils.config.exception import ConfigException
from superbox_utils.config.loader import ConfigLoaderMixin
from superbox_utils.config.loader import Validation
from superbox_utils.hass.config import HomeAssistantConfig
from superbox_utils.logging import init_logger
from superbox_utils.logging import stream_handler
from superbox_utils.logging.config import LoggingConfig
from superbox_utils.mqtt.config import MqttConfig

from unifi_tools.log import LOG_NAME

logger: logging.Logger = init_logger(name=LOG_NAME, level="info", handlers=[stream_handler])


class LogPrefix:
    API: Final[str] = "[API]"
    CONFIG: Final[str] = "[CONFIG]"
    DEVICEINFO: Final[str] = "[DEVICEINFO]"
    FEATURE: Final[str] = "[FEATURE]"
    MQTT: Final[str] = "[MQTT]"


@dataclass
class DeviceInfo(ConfigLoaderMixin):
    name: str = field(default=socket.gethostname())
    manufacturer: str = field(default="Ubiquiti Inc.")

    @staticmethod
    def _validate_name(value: str, _field: dataclasses.Field) -> str:
        if re.search(Validation.NAME.regex, value) is None:
            raise ConfigException(
                f"{LogPrefix.DEVICEINFO} Invalid value '{value}' in '{_field.name}'. {Validation.NAME.error}"
            )

        return value


@dataclass
class UniFiControllerConfig(ConfigLoaderMixin):
    url: str = field(default="localhost")
    port: int = field(default=8443)
    username: str = field(default="username")
    password: str = field(default="password")


@dataclass
class FeatureConfig(ConfigLoaderMixin):
    object_id: str = field(default_factory=str)
    ports: list = field(default_factory=list)

    @staticmethod
    def _validate_object_id(value: str, _field: dataclasses.Field) -> str:
        value = value.lower()

        if re.search(Validation.ID.regex, value) is None:
            raise ConfigException(
                f"{LogPrefix.FEATURE} Invalid value '{value}' in '{_field.name}'. {Validation.ID.error}"
            )

        return value


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

        self.init()

    def init(self):
        """Initialize configuration and start custom validation."""
        for device_id, feature_data in self.features.items():
            try:
                feature_config: FeatureConfig = FeatureConfig(**feature_data)
                feature_config.validate()
                self.features[device_id] = feature_config
            except TypeError as error:
                raise ConfigException(f"Invalid feature property: {feature_data}") from error

        self._validate_feature_object_ids()

    def _validate_feature_object_ids(self):
        object_ids: List[str] = []

        for feature in self.features.values():
            if feature.object_id in object_ids:
                raise ConfigException(f"{LogPrefix.FEATURE} Duplicate ID '{feature.object_id}' found in 'features'!")

            if feature.object_id:
                object_ids.append(feature.object_id)
