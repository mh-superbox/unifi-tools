#!/usr/bin/env python3
import argparse
import asyncio
import shutil
import signal
import subprocess
import uuid
from asyncio import Task
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Final
from typing import Set

import sys
from asyncio_mqtt import Client
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from superbox_utils.argparse import init_argparse
from superbox_utils.asyncio import cancel_tasks
from superbox_utils.mqtt.connect import mqtt_connect
from unifi_tools.config import Config
from unifi_tools.config import ConfigException
from unifi_tools.config import logger
from unifi_tools.logging import LOG_NAME
from unifi_tools.plugins.features import FeaturesMqttPlugin
from unifi_tools.plugins.hass.binary_sensors import HassBinarySensorsMqttPlugin
from unifi_tools.plugins.hass.switches import HassSwitchesMqttPlugin
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unifi_tools.version import __version__

disable_warnings(InsecureRequestWarning)


class UniFiTools:
    NAME: Final[str] = "unifi-tools"

    def __init__(self, unifi_devices: UniFiDevices):
        self.unifi_devices: UniFiDevices = unifi_devices
        self.config: Config = unifi_devices.config

    async def _init_tasks(self, stack: AsyncExitStack, mqtt_client: Client):
        tasks: Set[Task] = set()

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

    async def run(self):
        self.unifi_devices.read_devices()

        await mqtt_connect(
            mqtt_config=self.config.mqtt,
            logger=logger,
            mqtt_client_id=f"{self.config.device_info.name.lower()}-{uuid.uuid4()}",
            callback=self._init_tasks,
        )

    @classmethod
    def install(cls, config: Config, assume_yes: bool):
        src_config_path: Path = Path(__file__).parents[0] / "installer/etc/unifi"
        src_systemd_path: Path = Path(__file__).parents[0] / f"installer/etc/systemd/system/{cls.NAME}.service"
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

        print(f"Copy systemd service '{cls.NAME}.service'")
        shutil.copyfile(src_systemd_path, f"{config.systemd_path}/{cls.NAME}.service")

        enable_and_start_systemd: str = "y"

        if not assume_yes:
            enable_and_start_systemd = input("\nEnable and start systemd service? [Y/n]")

        if enable_and_start_systemd.lower() == "y":
            print(f"Enable systemd service '{cls.NAME}.service'")
            status = subprocess.check_output(f"systemctl enable --now {cls.NAME}", shell=True)

            if status:
                logger.info(status)
        else:
            print("\nYou can enable the systemd service with the command:")
            print(f"systemctl enable --now {cls.NAME}")


def parse_args(args) -> argparse.Namespace:
    parser: argparse.ArgumentParser = init_argparse(description="Control UniFi devices with MQTT commands")
    parser.add_argument("-i", "--install", action="store_true", help=f"install {UniFiTools.NAME}")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args(args)


def main():
    args: argparse.Namespace = parse_args(sys.argv[1:])

    try:
        config = Config()
        config.logging.update_level(LOG_NAME, verbose=args.verbose)

        if args.install:
            UniFiTools.install(config=config, assume_yes=args.yes)
        else:
            loop = asyncio.new_event_loop()

            unifi_api = UniFiAPI(config=config)
            unifi_api.login()

            unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
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
    except ConfigException as e:
        logger.error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
