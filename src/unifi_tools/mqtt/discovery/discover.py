from abc import ABC
from abc import abstractmethod
from typing import Tuple

from unifi_tools.config import Config


class HassBaseDiscovery(ABC):
    def __init__(self, config: Config):
        self.config: Config = config

    @abstractmethod
    def _get_discovery(self, feature) -> Tuple[str, dict]:
        pass

    @abstractmethod
    async def publish(self):
        pass
