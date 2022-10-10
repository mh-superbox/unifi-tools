from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Tuple

from unifi_tools.config import Config
from unifi_tools.config import FeatureConfig


class HassBaseDiscovery(ABC):
    def __init__(self, config: Config):
        self.config: Config = config

    def _get_object_id(self, feature) -> Optional[str]:
        """Get the object ID from the config. Used for ``Entity ID`` in Home Assistant."""
        object_id: Optional[str] = None
        features_config: Optional[FeatureConfig] = self.config.features.get(feature.device_id)

        if features_config:
            object_id = features_config.id

        return object_id

    @abstractmethod
    def _get_discovery(self, feature) -> Tuple[str, dict]:
        pass

    @abstractmethod
    async def publish(self):
        pass
