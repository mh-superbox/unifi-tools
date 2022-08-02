import asyncio
from asyncio import Task
from contextlib import AsyncExitStack
from typing import Any
from typing import AsyncIterable
from typing import Set

from unifi_tools.config import LOG_MQTT_PUBLISH
from unifi_tools.config import LOG_MQTT_SUBSCRIBE
from unifi_tools.config import LOG_MQTT_SUBSCRIBE_TOPIC
from unifi_tools.config import logger


class UniFiSwitchMqttPlugin:
    """Provide unifi switch as MQTT commands."""

    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    async def init_tasks(self, stack: AsyncExitStack) -> Set[Task]:
        tasks: Set[Task] = set()

        topic: str = f"test/set"

        manager = self._mqtt_client.filtered_messages(topic)
        messages = await stack.enter_async_context(manager)

        subscribe_task: Task[Any] = asyncio.create_task(self._subscribe(topic, messages))
        tasks.add(subscribe_task)

        await self._mqtt_client.subscribe(topic)
        logger.debug(LOG_MQTT_SUBSCRIBE_TOPIC, topic)

        task = asyncio.create_task(self._publish())
        tasks.add(task)

        return tasks

    @staticmethod
    async def _subscribe(topic: str, messages: AsyncIterable):
        async for message in messages:
            value: str = message.payload.decode()

            print(value)

            logger.info(LOG_MQTT_SUBSCRIBE, topic, value)

    async def _publish(self):
        while True:
            topic: str = f"test/get"
            await self._mqtt_client.publish(topic, "publish test", qos=1, retain=True)
            logger.info(LOG_MQTT_PUBLISH, topic, "publish test")

            await asyncio.sleep(10)
