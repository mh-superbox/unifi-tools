import asyncio
import json
import logging
from abc import ABC
from abc import abstractmethod
from asyncio import Task
from contextlib import AsyncExitStack
from typing import Any
from typing import AsyncContextManager
from typing import AsyncIterable
from typing import List
from typing import Set

from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap
from unifi_tools.log import LOG_MQTT_INVALID_SUBSCRIBE
from unifi_tools.log import LOG_MQTT_PUBLISH
from unifi_tools.log import LOG_MQTT_SUBSCRIBE
from unifi_tools.log import LOG_MQTT_SUBSCRIBE_TOPIC
from unifi_tools.log import LOG_NAME

logger = logging.getLogger(LOG_NAME)


class BaseFeaturesMqttPlugin(ABC):
    subscribe_feature_types: List[str] = []
    publish_feature_types: List[str] = []

    def __init__(self, unifi_devices, mqtt_client):
        self.unifi_devices = unifi_devices
        self.mqtt_client = mqtt_client
        self.features: FeatureMap = unifi_devices.features

    async def init_tasks(self, stack: AsyncExitStack, tasks: Set[Task]):
        """Initialize MQTT tasks for subscribe and publish MQTT topics.

        Parameters
        ----------
        stack: AsyncExitStack
        tasks: set
            A set of all MQTT tasks.
        """
        for feature in self.features.by_feature_types(self.subscribe_feature_types):
            topic: str = f"{feature.topic}/set"

            manager: AsyncContextManager = self.mqtt_client.filtered_messages(topic)
            messages: AsyncIterable = await stack.enter_async_context(manager)

            subscribe_task: Task[Any] = asyncio.create_task(self._subscribe(feature, topic, messages))
            tasks.add(subscribe_task)

            await self.mqtt_client.subscribe(topic)
            logger.debug(LOG_MQTT_SUBSCRIBE_TOPIC, topic)

        task = asyncio.create_task(self._publish())
        tasks.add(task)

    @abstractmethod
    async def _subscribe(self, feature, topic: str, messages: AsyncIterable):
        pass

    @abstractmethod
    async def _publish(self):
        pass


class FeaturesMqttPlugin(BaseFeaturesMqttPlugin):
    """Provide features control as MQTT commands."""

    PUBLISH_RUNNING: bool = True

    subscribe_feature_types: List[str] = [FeatureConst.PORT]
    publish_feature_types: List[str] = [FeatureConst.PORT]

    async def _subscribe(self, feature, topic: str, messages: AsyncIterable):
        async for message in messages:
            data: dict = {}

            value: str = message.payload.decode()

            try:
                data = json.loads(value)
            except ValueError:
                logger.error(LOG_MQTT_INVALID_SUBSCRIBE, topic, value)

            if data:
                feature.set_state(data)
                logger.info(LOG_MQTT_SUBSCRIBE, topic, value)

    async def _publish(self):
        while self.PUBLISH_RUNNING:
            self.unifi_devices.scan()

            for feature in self.features.by_feature_types(self.publish_feature_types):
                if feature.changed:
                    topic: str = f"{feature.topic}/get"
                    await self.mqtt_client.publish(topic, feature.payload, qos=1, retain=True)
                    logger.info(LOG_MQTT_PUBLISH, topic, feature.payload)

            await asyncio.sleep(25e-3)
