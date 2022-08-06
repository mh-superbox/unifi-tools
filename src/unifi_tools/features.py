import itertools
import json
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from typing import Final
from typing import List
from typing import Optional

from unifi_tools.config import Config
from unifi_tools.helpers import DataStorage


class FeaturePoEState:
    ON: str = "on"
    OFF: str = "off"
    POE: str = "auto"
    POE24V: str = "pasv24"


class FeatureConst:
    PORT: Final[str] = "port"
    POE: Final[str] = "PoE"
    POE_MODE: Final[str] = "poe_mode"
    PORT_IDX: Final[str] = "port_idx"
    POE_MODES: Final[tuple] = (
        FeaturePoEState.ON,
        FeaturePoEState.OFF,
        FeaturePoEState.POE,
        FeaturePoEState.POE24V,
    )


class Feature(ABC):
    name: str = "Feature"

    def __init__(self, config: Config, unifi_devices, unifi_device, short_name: str):
        self.config: Config = config
        self.unifi_devices = unifi_devices
        self.unifi_device = unifi_device
        self.short_name: str = short_name

        self._value: dict = {}

    def __repr__(self) -> str:
        return self.friendly_name

    @property
    @abstractmethod
    def value(self) -> dict:
        return {}

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
    def unique_id(self) -> str:
        return ""

    @property
    @abstractmethod
    def topic(self) -> str:
        return ""

    @property
    def state(self) -> str:
        return json.dumps(self.value)

    @property
    def changed(self) -> bool:
        changed: bool = self.value != self._value

        if changed:
            self._value = self.value

        return changed


class FeaturePort(Feature):
    name: str = "Port"

    def __init__(self, config: Config, unifi_devices, unifi_device, short_name: str, port_idx: int):
        super().__init__(
            config=config,
            unifi_devices=unifi_devices,
            unifi_device=unifi_device,
            short_name=short_name,
        )
        self.port_idx: int = port_idx

    @property
    def poe_mode(self) -> str:
        device_info = self.unifi_devices.cached_devices.get(self.unifi_device.id)
        port = device_info["ports"][self.port_idx]
        return self._get_real_poe_mode(poe_mode=port.poe_mode)

    @property
    def value(self) -> dict:
        _value: dict = {}

        if self.poe_mode:
            _value[FeatureConst.POE_MODE] = self.poe_mode

        return _value

    @property
    def feature_name(self) -> str:
        return FeatureConst.PORT

    @property
    def friendly_name(self) -> str:
        return f"{self.name} #{self.port_idx:02d} {FeatureConst.POE}"

    @property
    def unique_id(self) -> str:
        return f"{self.unifi_device.id}-{self.feature_name}-{self.port_idx}"

    @property
    def topic(self) -> str:
        return f"{self.config.device_name.lower()}/{self.unique_id}"

    def _get_real_poe_mode(self, poe_mode: str) -> str:
        # When state is "on" then check settings if PoE for this port is "auto" or "pasv24".
        if poe_mode == FeaturePoEState.ON:
            feature = self.config.get_feature(device_id=self.unifi_device.id)
            poe_mode = FeaturePoEState.POE

            for port in feature.get("ports", []):
                if port.get(FeatureConst.PORT_IDX) == self.port_idx:
                    poe_mode = port.get(FeatureConst.POE_MODE, FeaturePoEState.POE)
                    break

        return poe_mode

    def _set_port_poe(self, port_info: dict, poe_mode: str) -> bool:
        poe_mode = self._get_real_poe_mode(poe_mode=poe_mode)

        # Only update port if PoE mode is allowed and has changed!
        if (
            port_info.get(FeatureConst.POE_MODE)
            and poe_mode in FeatureConst.POE_MODES
            and port_info[FeatureConst.POE_MODE] != poe_mode
        ):
            port_info[FeatureConst.POE_MODE] = poe_mode
            return True

        return False

    async def set_state(self, value: dict):
        if FeatureConst.POE_MODE in value.keys():
            port_overrides: Optional[List[dict]] = self.unifi_devices.get_device_port_info(self.unifi_device.id)

            if port_overrides:
                update_devices: bool = False

                for port in port_overrides:
                    if port[FeatureConst.PORT_IDX] == self.port_idx:
                        update_devices = self._set_port_poe(port, value[FeatureConst.POE_MODE])
                        break

                if update_devices:
                    self.unifi_devices.update_device_port_info(
                        device_id=self.unifi_device.id, port_overrides={"port_overrides": port_overrides}
                    )


class FeatureMap(DataStorage):
    def register(self, feature: Feature):
        if not self.data.get(feature.short_name):
            self.data[feature.short_name] = []

        self.data[feature.short_name].append(feature)

    def by_feature_type(self, feature_type: List[str]) -> Iterator:
        return itertools.chain.from_iterable(filter(None, map(self.data.get, feature_type)))
