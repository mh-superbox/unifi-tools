import itertools
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from typing import Final
from typing import List
from typing import Optional

from unifi_tools.config import Config
from unifi_tools.helpers import DataStorage


class UniFiFeatureConst:
    PORT: Final[str] = "port"
    POE_MODE: Final[str] = "poe_mode"
    PORT_IDX: Final[str] = "port_idx"
    POE_MODES: Final[tuple] = ("pasv24", "auto", "off")


class UniFiDeviceFeature(ABC):
    name: str = "Feature"

    def __init__(self, config: Config, unifi_devices, device_info: dict, short_name: str):
        self.config: Config = config
        self.unifi_devices = unifi_devices
        self.device_info: dict = device_info
        self.short_name: str = short_name

    def __repr__(self) -> str:
        return self.friendly_name

    @property
    @abstractmethod
    def feature_name(self) -> str:
        return ""

    @property
    @abstractmethod
    def friendly_name(self) -> str:
        return ""

    @property
    @abstractmethod
    def topic(self) -> str:
        return ""


class UniFiSwitchPort(UniFiDeviceFeature):
    name: str = "Port"

    def __init__(self, config: Config, unifi_devices, short_name: str, device_info: dict, port_idx: int):
        super().__init__(config=config, unifi_devices=unifi_devices, device_info=device_info, short_name=short_name)
        self.port_idx: int = port_idx

    @property
    def feature_name(self) -> str:
        return UniFiFeatureConst.PORT

    @property
    def friendly_name(self) -> str:
        return f"{self.name} #{self.port_idx}"

    @property
    def topic(self) -> str:
        topic: str = (
            f"""{self.config.device_name.lower()}/{self.device_info["_id"]}/{self.feature_name}/{self.port_idx}"""
        )

        return topic

    @staticmethod
    def _set_port_poe(port_info: dict, updated_port_info: dict):
        if (
            port_info.get(UniFiFeatureConst.POE_MODE)
            and updated_port_info.get(UniFiFeatureConst.POE_MODE) in UniFiFeatureConst.POE_MODES
            and port_info[UniFiFeatureConst.POE_MODE] != updated_port_info.get(UniFiFeatureConst.POE_MODE)
        ):
            port_info[UniFiFeatureConst.POE_MODE] = updated_port_info.get(UniFiFeatureConst.POE_MODE)

    async def set_port(self, updated_port_info: dict):
        port_overrides: Optional[List[dict]] = self.unifi_devices.get_device_port_info(self.device_info["_id"])

        if port_overrides:
            update_devices: bool = False

            for port_info in port_overrides:
                if port_info[UniFiFeatureConst.PORT_IDX] == self.port_idx:
                    self._set_port_poe(port_info, updated_port_info)
                    update_devices = True

            if update_devices:
                self.unifi_devices.update_device_port_info(
                    device_id=self.device_info["_id"], port_overrides={"port_overrides": port_overrides}
                )


class FeatureMap(DataStorage):
    def register(self, feature: UniFiDeviceFeature):
        if not self.data.get(feature.short_name):
            self.data[feature.short_name] = []

        self.data[feature.short_name].append(feature)

    def by_feature_type(self, feature_type: List[str]) -> Iterator:
        return itertools.chain.from_iterable(filter(None, map(self.data.get, feature_type)))
