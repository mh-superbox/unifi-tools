#!/usr/bin/env python3
import argparse
import asyncio
import signal
import sys
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Optional
from typing import Set

from asyncio_mqtt import Client
from asyncio_mqtt import MqttError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.plugins.features import FeaturesMqttPlugin
from unifi_tools.unifi import UniFiDevices
from unifi_tools.version import __version__

disable_warnings(InsecureRequestWarning)


class UniFiTools:
    def __init__(self, config: Config, unifi_devices: UniFiDevices):
        self.config: Config = config
        self.unifi_devices: UniFiDevices = unifi_devices

        self._mqtt_client_id: str = f"{config.device_name.lower()}-{uuid.uuid4()}"
        logger.info("[MQTT] Client ID: %s", self._mqtt_client_id)

        self._retry_reconnect: int = 0

    async def _init_tasks(self):
        async with AsyncExitStack() as stack:
            tasks: Set[Task] = set()

            mqtt_client: Client = Client(
                self.config.mqtt.host,
                self.config.mqtt.port,
                client_id=self._mqtt_client_id,
                keepalive=self.config.mqtt.keepalive,
            )

            await stack.enter_async_context(mqtt_client)
            self._retry_reconnect = 0

            logger.info("[MQTT] Connected to broker at '%s:%s'", self.config.mqtt.host, self.config.mqtt.port)

            features = FeaturesMqttPlugin(unifi_devices=self.unifi_devices, mqtt_client=mqtt_client)
            features_tasks = await features.init_tasks(stack)
            tasks.update(features_tasks)

            # if self.config.homeassistant.enabled:
            #     hass_binary_sensors_plugin = HassBinarySensorsMqttPlugin(self, mqtt_client)
            #     hass_binary_sensors_tasks = await hass_binary_sensors_plugin.init_tasks()
            #     tasks.update(hass_binary_sensors_tasks)

            await asyncio.gather(*tasks)

    @staticmethod
    def cancel_tasks():
        for task in asyncio.all_tasks():
            if task.done():
                continue

            task.cancel()

    async def run(self):
        self.unifi_devices.read_devices()

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
    parser.add_argument("-c", "--config", help="path to configuration file")
    parser.add_argument("-i", "--install", action="store_true", help="install unifi tools")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    try:
        if args.install:
            UniFiTools.install(assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()

            config_overwrites: dict = {}

            if args.config:
                config_overwrites["config_file_path"] = Path(args.config)

            config = Config(**config_overwrites)

            unifi_api = UniFiAPI(config=config)
            unifi_api.login()

            unifi_devices = UniFiDevices(config=config, unifi_api=unifi_api)
            unifi_tools = UniFiTools(config=config, unifi_devices=unifi_devices)

            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, unifi_tools.cancel_tasks)

            try:
                loop.run_until_complete(unifi_tools.run())
            except asyncio.CancelledError:
                pass
            finally:
                loop.close()
                unifi_api.logout()
                logger.info("Successfully shutdown the UniFi Tools service.")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
