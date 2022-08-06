import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap
from unifi_tools.features import FeaturePort


class UniFiAPI:
    def __init__(self, config: Config):
        self.config: Config = config
        self._session = requests.Session()
        self._logged_in: bool = False

        self._headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }

    @property
    def controller_url(self):
        _controller_url: str = f"https://{self.config.unifi_controller.url}"

        if self.config.unifi_controller.port != 443:
            _controller_url += f":{self.config.unifi_controller.port}"

        return _controller_url

    @staticmethod
    def return_json(response, log: bool = True) -> Optional[Tuple[list, dict]]:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug("[API] %s", e)
            logger.error("[API] Request failed with return code %s", response.status_code)

        try:
            data: dict = response.json()
            meta: dict = data.get("meta", {})

            if log is True:
                logger.debug(
                    "[API] [%s]%s %s", meta.get("rc"), f""" {meta["msg"]}""" if meta.get("msg") else "", response.url
                )

            return data.get("data", []), meta
        except requests.exceptions.JSONDecodeError:
            return None

    def login(self):
        response = self._session.post(
            f"{self.controller_url}/api/login",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
            verify=False,
        )

        result: Optional[Tuple[dict, dict]] = self.return_json(response)

        if result is None:
            sys.exit(1)

        if result[1].get("rc") == "ok":
            cookies = response.cookies
            logger.info("[API] Successfully logged in.")
            logger.debug("[API] Cookies received:")
            [logger.debug("[API] %s ==> %s", c.name, c.value) for c in cookies]
            self._logged_in = True
        else:
            logger.info("[API] Can't connect to API. Maybe wrong username or password?")
            sys.exit(1)

    def logout(self):
        response = self._session.post(
            f"{self.controller_url}/api/logout",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
            verify=False,
        )

        self.return_json(response)
        logger.info("[API] Successfully logged out")
        self._logged_in = False

    def list_all_devices(self, log: bool = True) -> Optional[List[dict]]:
        response = self._session.get(
            f"{self.controller_url}/api/s/default/stat/device",
            headers=self._headers,
            verify=False,
        )

        result: Optional[Tuple[list, dict]] = self.return_json(response, log=log)

        if result is None:
            return None

        self._reconnect(meta=result[1], func_name="list_all_devices")
        devices_data: List[dict] = result[0]

        if devices_data and log is True:
            logger.debug("[API] [list_all_devices] %s", devices_data)

        return devices_data

    def update_device(self, device_id: str, port_overrides: List[dict]) -> bool:
        response = self._session.put(
            f"{self.controller_url}/api/s/default/rest/device/{device_id}",
            headers=self._headers,
            verify=False,
            data=json.dumps(port_overrides),
        )

        result: Optional[Tuple[list, dict]] = self.return_json(response)

        if result is None:
            return False

        self._reconnect(meta=result[1], func_name="update_device")
        logger.debug("[API] [update_device] %s", device_id)

        return True

    def _reconnect(self, meta: dict, func_name: str):
        if meta.get("rc") == "error" and meta.get("msg") == "api.err.LoginRequired":
            self._logged_in = False

            self.login()
            getattr(self, func_name)()


class UniFiSwitch:
    def __init__(self, config: Config, unifi_devices, device_info: dict):
        self.config: Config = config
        self.unifi_devices: UniFiDevices = unifi_devices
        self.features: FeatureMap = unifi_devices.features
        self.device_info: dict = device_info

    def _parse_feature_port(self, port_info: dict):
        self.features.register(
            FeaturePort(
                config=self.config,
                unifi_devices=self.unifi_devices,
                short_name=FeatureConst.PORT,
                device_info=self.device_info,
                port_idx=port_info["port_idx"],
            )
        )

    def parse_features(self):
        for port_info in self.device_info.get("port_overrides"):
            self._parse_feature_port(port_info)


class UniFiDevices:
    def __init__(self, config: Config, unifi_api: UniFiAPI):
        self.config: Config = config
        self.unifi_api: UniFiAPI = unifi_api
        self.features = FeatureMap()
        self.cached_devices: List[dict] = []

    def get_device_info(self, device_id: str, log: bool = True) -> Optional[dict]:
        list_all_devices: Optional[List[dict]] = self.unifi_api.list_all_devices(log=log)

        if list_all_devices is None:
            logger.debug("[API] Can't read device info!")
        else:
            adopted_devices_list: List[dict] = [
                device for device in list_all_devices if device.get("adopted") and device.get("_id") == device_id
            ]

            if adopted_devices_list:
                return adopted_devices_list[0]

        return None

    def get_device_port_info(self, device_id: str, log: bool = True) -> Optional[List[dict]]:
        device_info: Optional[dict] = self.get_device_info(device_id=device_id, log=log)

        if device_info:
            return device_info.get("port_overrides")

        return None

    def update_device_port_info(self, device_id: str, port_overrides: List[dict]):
        self.unifi_api.update_device(device_id=device_id, port_overrides=port_overrides)

    def scan(self):
        self.cached_devices = self.unifi_api.list_all_devices(log=False)

    def read_devices(self):
        logger.info("[API] Reading adopted devices.")
        self.scan()

        if self.cached_devices is None:
            logger.debug("[API] Can't read adopted devices!")
        else:
            adopted_devices_list: List[dict] = [device for device in self.cached_devices if device.get("adopted")]

            for device_info in adopted_devices_list:
                if device_info.get("port_overrides"):
                    unifi_switch: UniFiSwitch = UniFiSwitch(
                        config=self.config, unifi_devices=self, device_info=device_info
                    )

                    unifi_switch.parse_features()
