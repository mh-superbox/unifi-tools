#!/usr/bin/env python3
import argparse
import asyncio
import sys
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from time import sleep
from typing import Dict
from typing import Optional
from typing import Set

import requests
from asyncio_mqtt import Client
from asyncio_mqtt import MqttError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.plugins.unifi.switch import UniFiSwitchMqttPlugin
from unifi_tools.version import __version__

disable_warnings(InsecureRequestWarning)


class UniFiAPI:
    def __init__(self, config: Config):
        self.config: Config = config
        self._session = requests.Session()
        self._logged_in: bool = False

        self._headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }

        self._retry_reconnect: int = 0

    @staticmethod
    def return_json(response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug("[API] %s", e)
            logger.error("[API] Login failed with return code %s", response.status_code)
            sys.exit(1)

        return response.json()

    def login(self):
        response = self._session.post(
            f"https://{self.config.unifi_controller.url}/api/login",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
            verify=False,
        )

        data = self.return_json(response)

        cookies = response.cookies
        logger.debug("[API] Success. Cookies received:")
        [logger.debug("[API] %s ==> %s", c.name, c.value) for c in cookies]

        self._logged_in = True

    def run(self):
        reconnect_interval: int = self.config.unifi_controller.reconnect_interval
        retry_limit: Optional[int] = self.config.unifi_controller.retry_limit

        while self._logged_in is False:
            try:
                logger.info("[API] Login to %s", f"https://{self.config.unifi_controller.url}/api/login")
                self.login()
            except requests.exceptions.RequestException as error:
                logger.debug("[API] Error '%s'", error)
                logger.error(
                    "[API] Connecting attempt #%s. Reconnecting in %s seconds.",
                    self._retry_reconnect + 1,
                    reconnect_interval,
                )
            finally:
                if retry_limit and self._retry_reconnect > retry_limit:
                    sys.exit(1)

                self._retry_reconnect += 1

                sleep(reconnect_interval)


class UniFiTools:
    def __init__(self, config: Config):
        self.config: Config = config

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
    parser = argparse.ArgumentParser(description="Control UniFi devices with MQTT commands")
    parser.add_argument("-i", "--install", action="store_true", help="install unifi tools")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    try:
        if args.install:
            UniFiTools.install(assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()
            UniFiAPI(config=Config()).run()

            ut = UniFiTools(config=Config())

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
