import itertools
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from typing import Final
from typing import List
from typing import Optional

from unifi_tools.config import Config
from unifi_tools.helpers import DataStorage


class UniFiFeaturePoEState:
    ON: str = "on"
    OFF: str = "off"
    POE: str = "auto"
    POE24V: str = "pasv24"


class UniFiFeatureConst:
    PORT: Final[str] = "port"
    POE_MODE: Final[str] = "poe_mode"
    PORT_IDX: Final[str] = "port_idx"
    POE_MODES: Final[tuple] = (
        UniFiFeaturePoEState.POE24V,
        UniFiFeaturePoEState.POE,
        UniFiFeaturePoEState.OFF,
        UniFiFeaturePoEState.ON,
    )


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

    def _set_port_poe(self, port_info: dict, updated_port_info: dict) -> bool:
        updated_poe_mode: Optional[str] = updated_port_info.get(UniFiFeatureConst.POE_MODE)

        # When state is "on" then check settings if PoE for this port is "auto" or "pasv24".
        if updated_poe_mode == UniFiFeaturePoEState.ON:
            feature = self.config.get_feature(device_id=self.device_info["_id"])
            updated_poe_mode = UniFiFeaturePoEState.POE

            for port in feature.get("ports", []):
                if port.get(UniFiFeatureConst.PORT_IDX) == self.port_idx:
                    updated_poe_mode = port.get(UniFiFeatureConst.POE_MODE, UniFiFeaturePoEState.POE)
                    break

        # Only update port if PoE mode is allowed and has changed!
        if (
            port_info.get(UniFiFeatureConst.POE_MODE)
            and updated_poe_mode in UniFiFeatureConst.POE_MODES
            and port_info[UniFiFeatureConst.POE_MODE] != updated_poe_mode
        ):
            port_info[UniFiFeatureConst.POE_MODE] = updated_poe_mode
            return True

        return False

    async def set_port(self, updated_port_info: dict) -> bool:
        port_overrides: Optional[List[dict]] = self.unifi_devices.get_device_port_info(self.device_info["_id"])

        if port_overrides:
            update_devices: bool = False

            for port_info in port_overrides:
                if port_info[UniFiFeatureConst.PORT_IDX] == self.port_idx:
                    update_devices = self._set_port_poe(port_info, updated_port_info)

            if update_devices:
                return self.unifi_devices.update_device_port_info(
                    device_id=self.device_info["_id"], port_overrides={"port_overrides": port_overrides}
                )

        return False


class FeatureMap(DataStorage):
    def register(self, feature: UniFiDeviceFeature):
        if not self.data.get(feature.short_name):
            self.data[feature.short_name] = []

        self.data[feature.short_name].append(feature)

    def by_feature_type(self, feature_type: List[str]) -> Iterator:
        return itertools.chain.from_iterable(filter(None, map(self.data.get, feature_type)))
