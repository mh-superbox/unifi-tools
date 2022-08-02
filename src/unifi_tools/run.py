#!/usr/bin/env python3
import argparse
import asyncio
import sys
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from typing import Optional
from typing import Set

from asyncio_mqtt import Client
from asyncio_mqtt import MqttError

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.plugins.unifi.switch import UniFiSwitchMqttPlugin
from unifi_tools.version import __version__


class UniFiAPI:
    def __init__(self, controller: str):
        self.controller_url: str = f"https://{controller}"

    def login(self):
        pass


class UniFiTools:
    def __init__(self, config: Config, controller: str):
        self.config: Config = config
        self.controller_url: str = f"https://{controller}"

        self._mqtt_client_id: str = f"{config.device_name.lower()}-{uuid.uuid4()}"
        logger.info("[MQTT] Client ID: %s", self._mqtt_client_id)

        self._retry_reconnect: int = 0

    async def _init_tasks(self):
        async with AsyncExitStack() as stack:
            tasks: Set[Task] = set()
            stack.push_async_callback(self._cancel_tasks, tasks)

            mqtt_client: Client = Client(
                self.config.mqtt.host,
                self.config.mqtt.port,
                client_id=self._mqtt_client_id,
                keepalive=self.config.mqtt.keepalive,
            )

            await stack.enter_async_context(mqtt_client)
            self._retry_reconnect = 0

            logger.info("[MQTT] Connected to broker at '%s:%s'", self.config.mqtt.host, self.config.mqtt.port)

            unifi_switch = UniFiSwitchMqttPlugin(mqtt_client)
            unifi_switch_tasks = await unifi_switch.init_tasks(stack)
            tasks.update(unifi_switch_tasks)

            await asyncio.gather(*tasks)

    async def _cancel_tasks(self, tasks):
        for task in tasks:
            if task.done():
                continue

            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass

    async def run(self):
        reconnect_interval: int = self.config.mqtt.reconnect_interval
        retry_limit: Optional[int] = self.config.mqtt.retry_limit

        while True:
            try:
                logger.info("[MQTT] Connecting to broker ...")
                await self._init_tasks()
            except MqttError as error:
                logger.error(
                    "[MQTT] Error '%s'. Connecting attempt #%s. Reconnecting in %s seconds.",
                    error,
                    self._retry_reconnect + 1,
                    reconnect_interval,
                )
            finally:
                if retry_limit and self._retry_reconnect > retry_limit:
                    sys.exit(1)

                self._retry_reconnect += 1

                await asyncio.sleep(reconnect_interval)

    @classmethod
    def install(cls, assume_yes: bool):
        pass


def main():
    parser = argparse.ArgumentParser(description="Control UniFi port")
    parser.add_argument("-i", "--install", action="store_true", help="install unifi tools")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    try:
        if args.install:
            UniFiTools.install(assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()
            ut = UniFiTools(config=Config(), controller="unifi.superbox.home")

            try:
                loop.run_until_complete(ut.run())
            except asyncio.CancelledError:
                pass
            finally:
                logger.info("Successfully shutdown the UniFi Tools service.")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
