import argparse
import asyncio
import shutil
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
from requests import __version__  # type: ignore
from superbox_utils.argparse import init_argparse
from superbox_utils.config.exception import ConfigException
from superbox_utils.core.exception import UnexpectedException
from superbox_utils.mqtt.connect import mqtt_connect
from superbox_utils.text.text import slugify
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from unifi_tools.config import Config
from unifi_tools.config import LogPrefix
from unifi_tools.config import logger
from unifi_tools.log import LOG_NAME
from unifi_tools.mqtt.discovery.binary_sensors import HassBinarySensorsMqttPlugin
from unifi_tools.mqtt.discovery.switches import HassSwitchesMqttPlugin
from unifi_tools.mqtt.features import FeaturesMqttPlugin
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices

disable_warnings(InsecureRequestWarning)


class UniFiTools:
    NAME: Final[str] = "unifi-tools"

    def __init__(self, unifi_devices: UniFiDevices):
        self.unifi_devices: UniFiDevices = unifi_devices
        self.config: Config = unifi_devices.config

    async def _init_tasks(self, stack: AsyncExitStack, mqtt_client: Client):
        tasks: Set[Task] = set()
        stack.push_async_callback(self._cancel_tasks, tasks)

        await FeaturesMqttPlugin(unifi_devices=self.unifi_devices, mqtt_client=mqtt_client).init_tasks(stack, tasks)

        if self.config.homeassistant.enabled:
            await HassBinarySensorsMqttPlugin(unifi_devices=self.unifi_devices, mqtt_client=mqtt_client).init_tasks(
                tasks
            )

            await HassSwitchesMqttPlugin(unifi_devices=self.unifi_devices, mqtt_client=mqtt_client).init_tasks(tasks)

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
        """Connect to UniFi API and read devices."""
        self.unifi_devices.read_devices()

        await mqtt_connect(
            mqtt_config=self.config.mqtt,
            logger=logger,
            mqtt_client_id=f"{slugify(self.config.device_info.name)}-{uuid.uuid4()}",
            callback=self._init_tasks,
        )

    @classmethod
    def install(cls, config: Config, assume_yes: bool):
        """Interactive installer for UniFi Tools.

        Parameters
        ----------
        config: Config
            Unipi Control configuration
        assume_yes: bool
            Non-interactive mode. Accept all prompts with ``yes``.
        """
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

            if status := subprocess.check_output(f"systemctl enable --now {cls.NAME}", shell=True):
                logger.info(status)
        else:
            print("\nYou can enable the systemd service with the command:")
            print(f"systemctl enable --now {cls.NAME}")


def parse_args(args) -> argparse.Namespace:
    """Initialize argument parser options.

    Parameters
    ----------
    args: list
        Arguments as list.

    Returns
    -------
    Argparse namespace
    """
    parser: argparse.ArgumentParser = init_argparse(description="Control UniFi devices with MQTT commands")
    parser.add_argument("-i", "--install", action="store_true", help=f"install {UniFiTools.NAME}")
    parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to install prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args(args)


def main():
    """Entrypoint for UniFi Tool script."""
    unifi_api: Optional[UniFiAPI] = None

    try:
        args: argparse.Namespace = parse_args(sys.argv[1:])

        config = Config()
        config.logging.update_level(LOG_NAME, verbose=args.verbose)

        if args.install:
            UniFiTools.install(config=config, assume_yes=args.yes)
        else:
            unifi_api: UniFiAPI = UniFiAPI(config=config)
            unifi_api.login()

            unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
            unifi_tools = UniFiTools(unifi_devices=unifi_devices)

            asyncio.run(unifi_tools.run())
    except ConfigException as error:
        logger.error("%s %s", LogPrefix.CONFIG, error)
        sys.exit(1)
    except UnexpectedException as error:
        logger.error(error)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        if unifi_api:
            if unifi_api.return_code > 0:
                sys.exit(unifi_api.return_code)
            else:
                unifi_api.logout()

            logger.info("Successfully shutdown the UniFi Tools service.")
