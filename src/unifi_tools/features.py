import json
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from typing import Final
from typing import List

import itertools

from superbox_utils.dict.data_dict import DataDict
from unifi_tools.config import Config


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
    PORT_NAME: Final[str] = "name"
    POE_MODES: Final[tuple] = (
        FeaturePoEState.ON,
        FeaturePoEState.OFF,
        FeaturePoEState.POE,
        FeaturePoEState.POE24V,
    )


class Feature(ABC):
    name: str = "Feature"

    def __init__(self, unifi_devices, unifi_device):
        self.config: Config = unifi_devices.config
        self.unifi_devices = unifi_devices
        self.unifi_device = unifi_device
        self.unifi_api = unifi_devices.unifi_api

        self._value: dict = {}

    def __repr__(self) -> str:
        return self.friendly_name

    @property
    @abstractmethod
    def value(self) -> dict:
        pass

    @property
    @abstractmethod
    def feature_name(self) -> str:
        pass

    @property
    @abstractmethod
    def friendly_name(self) -> str:
        pass

    @property
    @abstractmethod
    def unique_id(self) -> str:
        pass

    @property
    @abstractmethod
    def topic(self) -> str:
        pass

    @property
    @abstractmethod
    def json_attributes(self) -> str:
        pass

    # @property
    # def state(self) -> str:
    #     return json.dumps(self.value)

    @property
    def changed(self) -> bool:
        changed: bool = self.value != self._value

        if changed:
            self._value = self.value

        return changed


class FeaturePort(Feature):
    name: str = "Port"

    def __init__(self, unifi_devices, unifi_device, port_info):
        super().__init__(
            unifi_devices=unifi_devices,
            unifi_device=unifi_device,
        )
        self.port_info = port_info

    @property
    def real_poe_mode(self) -> str:
        device_info = self.unifi_devices.unifi_device_map.get(self.unifi_device.id)
        port = device_info["ports"][self.port_info.idx]

        return port.poe_mode

    @property
    def poe_mode(self) -> str:
        poe_mode: str = self.real_poe_mode

        if poe_mode in [FeaturePoEState.POE24V, FeaturePoEState.POE]:
            poe_mode = FeaturePoEState.ON

        return poe_mode

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
        if self.port_info.name:
            return self.port_info.name

        return f"{self.name} #{self.port_info.idx:02d}"

    @property
    def unique_id(self) -> str:
        return f"{self.unifi_device.id}-{self.feature_name.lower()}-{self.port_info.idx}"

    @property
    def topic(self) -> str:
        return f"{self.config.device_info.name.lower()}/{self.unique_id}"

    @property
    def json_attributes(self) -> str:
        _json_attributes: dict = {}

        if self.real_poe_mode:
            _json_attributes["poe_mode"] = self.real_poe_mode

        return json.dumps(_json_attributes)

    def _get_real_poe_mode(self, poe_mode: str) -> str:
        # When state is "on" then check settings if PoE for this port is "auto" or "pasv24".
        if poe_mode == FeaturePoEState.ON:
            feature = self.config.get_feature(device_id=self.unifi_device.id)
            poe_mode = FeaturePoEState.POE

            for port in feature.get("ports", []):
                if port.get(FeatureConst.PORT_IDX) == self.port_info.idx:
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

    def set_state(self, value: dict) -> bool:
        update_devices: bool = False

        if FeatureConst.POE_MODE in value.keys():
            device_info = self.unifi_devices.get_device_info(device_id=self.unifi_device.id)
            port_overrides: list = device_info.get("port_overrides", [])

            for port in port_overrides:
                if port[FeatureConst.PORT_IDX] == self.port_info.idx:
                    update_devices = self._set_port_poe(port, value[FeatureConst.POE_MODE])
                    break

            if update_devices:
                self.unifi_api.update_device(
                    device_id=self.unifi_device.id, port_overrides={"port_overrides": port_overrides}
                )

        return update_devices


class FeatureMap(DataDict):
    def register(self, feature: Feature):
        if not self.get(feature.feature_name):
            self[feature.feature_name] = []

        self[feature.feature_name].append(feature)

    def by_feature_type(self, feature_type: List[str]) -> Iterator:
        return itertools.chain.from_iterable(filter(None, map(self.data.get, feature_type)))
