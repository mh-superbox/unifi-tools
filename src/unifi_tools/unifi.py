import asyncio
import json
import sys
from json import JSONDecodeError
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import requests
from requests import ConnectionError
from requests import HTTPError
from requests import Response

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap
from unifi_tools.features import FeaturePort
from unifi_tools.helpers import DataStorage
from unifi_tools.helpers import cancel_tasks


class UniFiPort(NamedTuple):
    idx: int
    poe_mode: Optional[str]


class UniFiCachedDeviceMap(DataStorage):
    def initialise(self, device_infos: List[dict]):
        for device_info in device_infos:
            if device_info.get("adopted") is False:
                continue

            device_id: str = device_info.pop("_id")
            ports: Dict[str, UniFiPort] = {}

            for port in device_info.get("port_overrides", []):
                ports[port[FeatureConst.PORT_IDX]] = UniFiPort(
                    idx=port[FeatureConst.PORT_IDX],
                    poe_mode=port.get(FeatureConst.POE_MODE),
                )

            self.data[device_id] = {
                "ports": ports,
            }


class UniFiAPIResult(NamedTuple):
    meta: dict
    data: list


class UniFiAPI:
    def __init__(self, config: Config):
        self.config: Config = config
        self.rc: int = 0
        self._session = requests.Session()
        self._logged_in: bool = False
        self._login: Optional[Response] = None

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

    def _exit(self, rc):
        self.rc = rc

        if asyncio.get_event_loop().is_running():
            cancel_tasks()
        else:
            sys.exit(rc)

    def _get_json(self, response, log: bool = True) -> Optional[UniFiAPIResult]:
        try:
            data: dict = json.loads(response.text)
            meta: dict = data.get("meta", {})

            meta_info: str = f"""[{meta.get("rc")}]{f" {meta['msg']}" if meta.get("msg") else ""} {response.url}"""

            if meta.get("rc") == "error" and response.status_code != 401:
                raise HTTPError(meta_info, response=response)
            elif log is True:
                logger.debug("[API] %s", meta_info)

            return UniFiAPIResult(meta=meta, data=data.get("data", []))
        except JSONDecodeError:
            logger.error("[API] JSON decode error. API not available! Shutdown UniFi Tools.")
            self._exit(1)

        return None

    def _request(
        self,
        url,
        method: str,
        headers: dict,
        json: Optional[dict] = None,
        log: bool = True,
    ) -> Tuple[Optional[UniFiAPIResult], Optional[Response]]:
        result: Optional[UniFiAPIResult] = None
        response: Optional[Response] = None

        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                verify=False,
            )

            if 500 <= response.status_code < 600:
                raise HTTPError(
                    f"{response.status_code} Server Error: {response.reason} for url: {url}", response=response
                )

            result = self._get_json(response, log=log)
        except ConnectionError as e:
            logger.debug("[API] %s", e)
            # self._exit(1)
        except HTTPError as e:
            logger.error("[API] %s", e)
            self._exit(1)

        return result, response

    def login(self):
        result, response = self._request(
            method="post",
            url=f"{self.controller_url}/api/login",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
        )

        self._login = response

        if result and result.meta.get("rc") == "ok":
            logger.info("[API] Successfully logged in.")
            logger.debug("[API] CSRF Token: %s", response.cookies.get("csrf_token"))
            self._logged_in = True

    def logout(self):
        self._request(
            method="post",
            url=f"{self.controller_url}/api/logout",
            headers={
                "x-csrf-token": self._login.cookies.get("csrf_token"),
            },
        )

        logger.info("[API] Successfully logged out")
        self._logged_in = False

    def list_all_devices(self, log: bool = True) -> List[dict]:
        result, response = self._request(
            method="get",
            url=f"{self.controller_url}/api/s/default/stat/device",
            headers=self._headers,
            log=log,
        )

        if result is None:
            return []

        self._reconnect(response=response, func_name="list_all_devices")
        devices_data: List[dict] = result.data

        if devices_data and log is True:
            logger.debug("[API] [list_all_devices] %s", devices_data)

        return devices_data

    def update_device(self, device_id: str, port_overrides: Dict[str, list]):
        result, response = self._request(
            method="put",
            url=f"{self.controller_url}/api/s/default/rest/device/{device_id}",
            headers=self._headers,
            json=port_overrides,
        )

        if result is None:
            return False

        self._reconnect(response=response, func_name="update_device")
        logger.debug("[API] [update_device] %s", device_id)

    def _reconnect(self, response: Optional[Response], func_name: str):
        if response and response.status_code == 401:
            self._logged_in = False
            self.login()

            getattr(self, func_name)()


class UniFiDevice(NamedTuple):
    id: str
    info: dict


class UniFiDevices:
    def __init__(self, config: Config, unifi_api: UniFiAPI):
        self.config: Config = config
        self.unifi_api: UniFiAPI = unifi_api
        self.features = FeatureMap()
        self.cached_devices = UniFiCachedDeviceMap()

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

    def update_device_port_info(self, device_id: str, port_overrides: Dict[str, list]):
        self.unifi_api.update_device(device_id=device_id, port_overrides=port_overrides)

    def scan(self):
        self.cached_devices.initialise(self.unifi_api.list_all_devices(log=False))

    def read_devices(self):
        logger.info("[API] Reading adopted devices.")
        self.scan()

        if self.cached_devices is None:
            logger.debug("[API] Can't read adopted devices!")
        else:
            for device_id, device_info in self.cached_devices.items():
                if device_info["ports"]:
                    unifi_switch: UniFiSwitch = UniFiSwitch(
                        config=self.config,
                        features=self.features,
                        unifi_devices=self,
                        unifi_device=UniFiDevice(id=device_id, info=device_info),
                    )

                    unifi_switch.parse_features()


class UniFiSwitch:
    def __init__(self, config: Config, features: FeatureMap, unifi_devices: UniFiDevices, unifi_device: UniFiDevice):
        self.config: Config = config
        self.features: FeatureMap = features
        self.unifi_devices: UniFiDevices = unifi_devices
        self.unifi_device: UniFiDevice = unifi_device

    def _parse_feature_port(self, port_idx: int):
        self.features.register(
            FeaturePort(
                config=self.config,
                unifi_devices=self.unifi_devices,
                short_name=FeatureConst.PORT,
                unifi_device=self.unifi_device,
                port_idx=port_idx,
            )
        )

    def parse_features(self):
        for port_idx in self.unifi_device.info["ports"].keys():
            self._parse_feature_port(port_idx)
