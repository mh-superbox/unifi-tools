import itertools
import json
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from functools import cached_property
from typing import Dict
from typing import Final
from typing import List
from typing import Optional

from superbox_utils.text.text import slugify

from unifi_tools.config import Config
from unifi_tools.config import FeatureConfig


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

    @cached_property
    @abstractmethod
    def feature_name(self) -> str:
        """Abstract method for feature name."""
        pass  # pylint: disable=unnecessary-pass

    @cached_property
    @abstractmethod
    def friendly_name(self) -> str:
        """Abstract method for friendly name."""
        pass  # pylint: disable=unnecessary-pass

    @cached_property
    @abstractmethod
    def device_id(self) -> str:
        """Abstract method for device id."""
        pass  # pylint: disable=unnecessary-pass

    @cached_property
    @abstractmethod
    def unique_id(self) -> str:
        """Return unique id for Home Assistant."""
        pass  # pylint: disable=unnecessary-pass

    @cached_property
    @abstractmethod
    def topic(self) -> str:
        """Return Unique name for the MQTT topic."""
        pass  # pylint: disable=unnecessary-pass

    @property
    @abstractmethod
    def payload(self) -> str:
        """Abstract method for payload."""
        pass  # pylint: disable=unnecessary-pass

    @property
    @abstractmethod
    def value(self) -> dict:
        """Abstract method for value."""
        pass  # pylint: disable=unnecessary-pass

    @property
    def changed(self) -> bool:
        """Detect whether the status has changed."""
        changed: bool = False

        if self.value != self._value:
            changed = True
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
        """Get Real POE mode.

        Returns
        -------
        str
            "auto" or "pasv24" if POE is enabled else "off"
        """
        device_info = self.unifi_devices.unifi_device_map.data.get(self.unifi_device.id)
        port = device_info["ports"][self.port_info.idx]

        return port.poe_mode

    @property
    def poe_mode(self) -> str:
        """Get the POE mode.

        Returns
        -------
        str
            "on" if POE is enabled else "off"
        """
        if (poe_mode := self.real_poe_mode) in [FeaturePoEState.POE24V, FeaturePoEState.POE]:
            poe_mode = FeaturePoEState.ON

        return poe_mode

    @property
    def value(self) -> dict:
        """Return the feature state as dict."""
        _value: dict = {}

        if self.poe_mode:
            _value[FeatureConst.POE_MODE] = self.poe_mode

        return _value

    @cached_property
    def feature_name(self) -> str:
        """Return feature name."""
        return FeatureConst.PORT

    @cached_property
    def friendly_name(self) -> str:
        """Return friendly name for Home Assistant."""
        if self.port_info.name:
            return self.port_info.name

        return f"{self.name} #{self.port_info.idx:02d}"

    @cached_property
    def device_id(self) -> str:
        """Return device id."""
        _device_id: str = self.unifi_device.id

        if features_config := self.config.features.get(self.unifi_device.id):
            _device_id = features_config.object_id

        return _device_id.lower()

    @cached_property
    def unique_id(self) -> str:
        """Return unique id for Home Assistant."""
        return f"{slugify(self.config.device_info.name)}-{self.unifi_device.id.lower()}-{self.feature_name.lower()}-{self.port_info.idx}"

    @cached_property
    def object_id(self) -> str:
        """Return object id for Home Assistant."""
        return (
            f"{slugify(self.config.device_info.name)}-{self.device_id}-{self.feature_name.lower()}-{self.port_info.idx}"
        )

    @cached_property
    def topic(self) -> str:
        """Return Unique name for the MQTT topic."""
        return (
            f"{slugify(self.config.device_info.name)}/{self.device_id}-{self.feature_name.lower()}-{self.port_info.idx}"
        )

    @property
    def payload(self) -> str:
        """Return the POE mode as JSON dump."""
        _json_attributes: dict = {}

        if self.real_poe_mode:
            _json_attributes["poe_mode"] = self.real_poe_mode

        return json.dumps(_json_attributes)

    def _get_real_poe_mode(self, poe_mode: str) -> str:
        # When state is "on" then check settings if PoE for this port is "auto" or "pasv24".
        if poe_mode == FeaturePoEState.ON:
            features_config: Optional[FeatureConfig] = self.config.features.get(self.unifi_device.id)
            poe_mode = FeaturePoEState.POE

            if features_config:
                for port in features_config.ports:
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
        """Set unifi switch port state.

        Parameters
        ----------
        value: dict
            Port settings as dictionary.

        Returns
        -------
        bool
            True if port state updated.
        """
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


class FeatureMap:
    def __init__(self):
        self.data: Dict[str, List[Feature]] = {}

    def register(self, feature: Feature):
        """Add a feature to the data storage.

        Parameters
        ----------
        feature: Feature
        """
        if not self.data.get(feature.feature_name):
            self.data[feature.feature_name] = []

        self.data[feature.feature_name].append(feature)

    def by_feature_types(self, feature_types: List[str]) -> Iterator:
        """Filter features by feature type.

        Parameters
        ----------
        feature_types: list

        Returns
        -------
        Iterator
            A list of features filtered by feature type.
        """
        return itertools.chain.from_iterable(
            [item for item in (self.data.get(feature_type) for feature_type in feature_types) if item is not None]
        )
