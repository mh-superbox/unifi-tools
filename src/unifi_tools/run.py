#!/usr/bin/env python3
import argparse
import asyncio
import json
import signal
import sys
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from time import sleep
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import requests
from asyncio_mqtt import Client
from asyncio_mqtt import MqttError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.features import FeatureMap
from unifi_tools.features import UniFiFeatureConst
from unifi_tools.features import UniFiSwitchPort
from unifi_tools.plugins.features import UniFiSwitchFeaturesMqttPlugin
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
    def return_json(response) -> dict:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug("[API] %s", e)
            logger.error("[API] Request failed with return code %s", response.status_code)
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

        self.return_json(response)

        cookies = response.cookies
        logger.debug("[API] Successfully logged in. Cookies received:")
        [logger.debug("[API] %s ==> %s", c.name, c.value) for c in cookies]

        self._logged_in = True

    def logout(self):
        response = self._session.post(
            f"https://{self.config.unifi_controller.url}/api/logout",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
            verify=False,
        )

        self.return_json(response)

        logger.debug("[API] Successfully logged out")

        self._logged_in = False

    def list_all_devices(self) -> list:
        response = self._session.get(
            f"https://{self.config.unifi_controller.url}/api/s/default/stat/device",
            headers=self._headers,
            verify=False,
        )

        data = self.return_json(response)
        logger.debug("[API] List all devices")

        return data.get("data", [])

    def update_device(self, device_id: str, port_overrides: List[dict]):
        response = self._session.put(
            f"https://{self.config.unifi_controller.url}/api/s/default/rest/device/{device_id}",
            headers=self._headers,
            verify=False,
            data=json.dumps(port_overrides),
        )

        self.return_json(response)
        logger.debug("[API] Updated device %s", device_id)

    def connect(self):
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


class UniFiSwitch:
    def __init__(self, config: Config, unifi_devices, device_info: dict):
        self.config: Config = config
        self.unifi_devices: UniFiDevices = unifi_devices
        self.features: FeatureMap = unifi_devices.features
        self.device_info: dict = device_info

    def _parse_feature_port(self, port):
        self.features.register(
            UniFiSwitchPort(
                config=self.config,
                unifi_devices=self.unifi_devices,
                short_name=UniFiFeatureConst.PORT,
                device_info=self.device_info,
                port_idx=port["port_idx"],
            )
        )

    def parse_features(self):
        for port in self.device_info.get("port_overrides"):
            self._parse_feature_port(port)


class UniFiDevices:
    def __init__(self, config: Config, unifi_api: UniFiAPI):
        self.config: Config = config
        self.unifi_api: UniFiAPI = unifi_api
        self.features = FeatureMap()

    def get_device_info(self, device_id: str) -> Optional[dict]:
        adopted_devices_list: List[dict] = [
            device
            for device in self.unifi_api.list_all_devices()
            if device.get("adopted") and device.get("_id") == device_id
        ]

        if adopted_devices_list:
            return adopted_devices_list[0]

        return None

    def get_device_port_info(self, device_id: str) -> Optional[List[dict]]:
        device_info: Optional[dict] = self.get_device_info(device_id=device_id)

        if device_info:
            return device_info.get("port_overrides")

        return None

    def update_device_port_info(self, device_id: str, port_overrides: List[dict]):
        self.unifi_api.update_device(device_id=device_id, port_overrides=port_overrides)

    def read_devices(self):
        logger.info("[API] Reading adopted devices")
        adopted_devices_list: List[dict] = [
            device for device in self.unifi_api.list_all_devices() if device.get("adopted")
        ]

        for device_info in adopted_devices_list:
            if device_info.get("port_overrides"):
                unifi_switch: UniFiSwitch = UniFiSwitch(config=self.config, unifi_devices=self, device_info=device_info)
                unifi_switch.parse_features()


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

            features = UniFiSwitchFeaturesMqttPlugin(features=self.unifi_devices.features, mqtt_client=mqtt_client)
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
    parser.add_argument("-i", "--install", action="store_true", help="install unifi tools")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    try:
        if args.install:
            UniFiTools.install(assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()

            unifi_api = UniFiAPI(config=Config())
            unifi_api.connect()

            unifi_devices = UniFiDevices(config=Config(), unifi_api=unifi_api)
            unifi_tools = UniFiTools(config=Config(), unifi_devices=unifi_devices)

            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, unifi_tools.cancel_tasks)

            try:
                loop.run_until_complete(unifi_tools.run())
            except asyncio.CancelledError:
                pass
            finally:
                unifi_api.logout()
                logger.info("Successfully shutdown the UniFi Tools service.")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
