import asyncio
import json
from abc import ABC
from abc import abstractmethod
from asyncio import Task
from contextlib import AsyncExitStack
from typing import Any
from typing import AsyncIterable
from typing import List
from typing import Set

from unifi_tools.config import LOG_MQTT_INVALIDE_SUBSCRIBE
from unifi_tools.config import LOG_MQTT_PUBLISH
from unifi_tools.config import LOG_MQTT_SUBSCRIBE
from unifi_tools.config import LOG_MQTT_SUBSCRIBE_TOPIC
from unifi_tools.config import logger
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap


class BaseFeaturesMqttPlugin(ABC):
    subscribe_feature_types: List[str] = []
    publish_feature_types: List[str] = []

    def __init__(self, unifi_devices, mqtt_client):
        self.unifi_devices = unifi_devices
        self.mqtt_client = mqtt_client
        self.features: FeatureMap = unifi_devices.features
        self.cached_devices: List[dict] = unifi_devices.cached_devices

    async def init_tasks(self, stack: AsyncExitStack) -> Set[Task]:
        tasks: Set[Task] = set()

        for feature in self.features.by_feature_type(self.subscribe_feature_types):
            topic: str = f"{feature.topic}/set"

            manager = self.mqtt_client.filtered_messages(topic)
            messages = await stack.enter_async_context(manager)

            subscribe_task: Task[Any] = asyncio.create_task(self._subscribe(feature, topic, messages))
            tasks.add(subscribe_task)

            await self.mqtt_client.subscribe(topic)
            logger.debug(LOG_MQTT_SUBSCRIBE_TOPIC, topic)

        task = asyncio.create_task(self._publish())
        tasks.add(task)

        return tasks

    @staticmethod
    @abstractmethod
    async def _subscribe(feature, topic: str, messages: AsyncIterable):
        pass

    @abstractmethod
    async def _publish(self):
        pass


class FeaturesMqttPlugin(BaseFeaturesMqttPlugin):
    """Provide features control as MQTT commands."""

    subscribe_feature_types: List[str] = [FeatureConst.PORT]
    publish_feature_types: List[str] = [FeatureConst.PORT]

    def __init__(self, unifi_devices, mqtt_client):
        super().__init__(unifi_devices, mqtt_client)

    @staticmethod
    async def _subscribe(feature, topic: str, messages: AsyncIterable):
        async for message in messages:
            data: dict = {}
            value: str = message.payload.decode()

            try:
                data = json.loads(value)
            except ValueError:
                logger.error(LOG_MQTT_INVALIDE_SUBSCRIBE, topic, value)

            if data:
                await feature.set_state(data)
                logger.info(LOG_MQTT_SUBSCRIBE, topic, value)

    async def _publish(self):
        while True:
            self.unifi_devices.scan()

            features = self.features.by_feature_type(self.publish_feature_types)

            for feature in features:
                if feature.changed:
                    topic: str = f"{feature.topic}/get"
                    await self.mqtt_client.publish(topic, feature.state, qos=1, retain=True)
                    logger.info(LOG_MQTT_PUBLISH, topic, feature.state)

            await asyncio.sleep(25e-3)
