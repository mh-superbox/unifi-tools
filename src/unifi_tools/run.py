#!/usr/bin/env python3
import argparse
import asyncio
import shutil
import signal
import subprocess
import sys
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Final
from typing import Optional
from typing import Set

from asyncio_mqtt import Client
from asyncio_mqtt import MqttError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.helpers import cancel_tasks
from unifi_tools.plugins.features import FeaturesMqttPlugin
from unifi_tools.plugins.hass.binary_sensors import HassBinarySensorsMqttPlugin
from unifi_tools.plugins.hass.switches import HassSwitchesMqttPlugin
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unifi_tools.version import __version__

disable_warnings(InsecureRequestWarning)


class UniFiTools:
    SYSTEMD_SERVICE: Final[str] = "unifi-tools"

    def __init__(self, unifi_devices: UniFiDevices):
        self.unifi_devices: UniFiDevices = unifi_devices
        self.config: Config = unifi_devices.config

        self._mqtt_client_id: str = f"{self.config.device_name.lower()}-{uuid.uuid4()}"
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

            if self.config.homeassistant.enabled:
                hass_binary_sensors_plugin = HassBinarySensorsMqttPlugin(
                    unifi_devices=self.unifi_devices, mqtt_client=mqtt_client
                )
                hass_binary_sensors_tasks = await hass_binary_sensors_plugin.init_tasks()
                tasks.update(hass_binary_sensors_tasks)

                hass_switches_plugin = HassSwitchesMqttPlugin(unifi_devices=self.unifi_devices, mqtt_client=mqtt_client)
                hass_switches_tasks = await hass_switches_plugin.init_tasks()
                tasks.update(hass_switches_tasks)

            await asyncio.gather(*tasks)

    @classmethod
    def cancel_tasks(cls):
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
    def install(cls, config: Config, assume_yes: bool):
        src_config_path: Path = Path(__file__).parents[0] / "installer/etc/unifi"
        src_systemd_path: Path = (
            Path(__file__).parents[0] / f"installer/etc/systemd/system/{cls.SYSTEMD_SERVICE}.service"
        )
        dest_config_path: Path = config.config_file_path.parent

        dirs_exist_ok: bool = False
        copy_config_files: bool = True

        if dest_config_path.exists():
            overwrite_config: str = "y"

            if not assume_yes:
                overwrite_config = input("\nOverwrite existing config file? [Y/n]")

            if overwrite_config.lower() == "y":
                dirs_exist_ok = True
            else:
                copy_config_files = False

        if copy_config_files:
            print(f"Copy config file to '{dest_config_path}'")
            shutil.copytree(src_config_path, dest_config_path, dirs_exist_ok=dirs_exist_ok)

        print(f"Copy systemd service '{cls.SYSTEMD_SERVICE}.service'")
        shutil.copyfile(src_systemd_path, f"{config.systemd_path}/{cls.SYSTEMD_SERVICE}.service")

        enable_and_start_systemd: str = "y"

        if not assume_yes:
            enable_and_start_systemd = input("\nEnable and start systemd service? [Y/n]")

        if enable_and_start_systemd.lower() == "y":
            print(f"Enable systemd service '{cls.SYSTEMD_SERVICE}.service'")
            status = subprocess.check_output(f"systemctl enable --now {cls.SYSTEMD_SERVICE}", shell=True)

            if status:
                logger.info(status)
        else:
            print("\nYou can enable the systemd service with the command:")
            print(f"systemctl enable --now {cls.SYSTEMD_SERVICE}")


def parse_args(args):
    parser = argparse.ArgumentParser(description="Control UniFi devices with MQTT commands")
    parser.add_argument("-c", "--config", help="path to configuration file")
    parser.add_argument("-i", "--install", action="store_true", help="install unifi tools")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    try:
        config_overwrites: dict = {}

        if args.config:
            config_overwrites["config_file_path"] = Path(args.config)

        config = Config(**config_overwrites)

        if args.install:
            UniFiTools.install(config=config, assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()

            unifi_api = UniFiAPI(config=config)
            unifi_api.login()

            unifi_devices = UniFiDevices(unifi_api=unifi_api)
            unifi_tools = UniFiTools(unifi_devices=unifi_devices)

            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, cancel_tasks)

            try:
                loop.run_until_complete(unifi_tools.run())
            except asyncio.CancelledError:
                pass
            finally:
                if unifi_api.rc > 0:
                    sys.exit(unifi_api.rc)
                else:
                    unifi_api.logout()
                    logger.info("Successfully shutdown the UniFi Tools service.")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
