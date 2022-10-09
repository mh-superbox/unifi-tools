import asyncio
import json
from json import JSONDecodeError
from typing import Dict
from typing import Final
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import requests
import sys
from requests import Response

from superbox_utils.asyncio import cancel_tasks
from superbox_utils.dict.data_dict import DataDict
from unifi_tools.config import Config
from unifi_tools.config import LogPrefix
from unifi_tools.config import logger
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap
from unifi_tools.features import FeaturePort


class UniFiPort(NamedTuple):
    idx: int
    name: str
    poe_mode: Optional[str]


class UniFiDeviceMap(DataDict):
    def initialise(self, device_infos: List[dict]):
        for device_info in device_infos:
            if device_info.get("adopted") is True:
                device_id: str = device_info.pop("_id")
                ports: Dict[str, UniFiPort] = {}

                for port in device_info.get("port_overrides", []):
                    ports[port[FeatureConst.PORT_IDX]] = UniFiPort(
                        idx=port[FeatureConst.PORT_IDX],
                        name=port.get(FeatureConst.PORT_NAME),
                        poe_mode=port.get(FeatureConst.POE_MODE),
                    )

                self.data[device_id] = {
                    "ports": ports,
                    "name": device_info["name"],
                    "model": device_info["model"],
                    "version": device_info["version"],
                }


class UniFiAPIResult(NamedTuple):
    meta: dict
    data: list


class UniFiAPI:
    LOGIN_ENDPOINT: Final[str] = "/api/login"
    LOGOUT_ENDPOINT: Final[str] = "/api/logout"
    STATE_DEVICE_ENDPOINT: Final[str] = "/api/s/default/stat/device"
    REST_DEVICE_ENDPOINT: Final[str] = "/api/s/default/rest/device"

    @property
    def controller_url(self):
        _controller_url: str = f"https://{self.config.unifi_controller.url}"

        if self.config.unifi_controller.port != 443:
            _controller_url += f":{self.config.unifi_controller.port}"

        return _controller_url

    def __init__(self, config: Config):
        self.config: Config = config
        self.rc: int = 0

        self._session = requests.Session()
        self._session.hooks["response"].append(self._reconnect)

        self._logged_in: bool = False
        self._login: Optional[Response] = None

        self._headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }

    def login(self) -> Tuple[Optional[UniFiAPIResult], Optional[Response]]:
        result, response = self._request_url(
            method="post",
            url=f"{self.controller_url}{self.LOGIN_ENDPOINT}",
            headers=self._headers,
            json={
                "username": self.config.unifi_controller.username,
                "password": self.config.unifi_controller.password,
            },
        )

        self._login = response

        if result and result.meta.get("rc") == "ok" and response:
            logger.info("%s Successfully logged in.", LogPrefix.API)
            logger.debug("%s CSRF Token: %s", LogPrefix.API, response.cookies.get("csrf_token"))
            self._logged_in = True

        return result, response

    def logout(self) -> Tuple[Optional[UniFiAPIResult], Optional[Response]]:
        csrf_token: str = ""

        if self._login:
            csrf_token = self._login.cookies.get("csrf_token", "")

        result, response = self._request_url(
            method="post",
            url=f"{self.controller_url}{self.LOGOUT_ENDPOINT}",
            headers={
                "x-csrf-token": csrf_token,
            },
        )

        logger.info("%s Successfully logged out.", LogPrefix.API)
        self._logged_in = False

        return result, response

    def list_all_devices(self, log: bool = True) -> Tuple[Optional[UniFiAPIResult], Optional[Response]]:
        result, response = self._request_url(
            method="get",
            url=f"{self.controller_url}{ self.STATE_DEVICE_ENDPOINT}",
            headers=self._headers,
            log=log,
        )

        if result and result.data and log is True:
            logger.debug("%s [list_all_devices] %s", LogPrefix.API, result.data)

        return result, response

    def update_device(
        self, device_id: str, port_overrides: Dict[str, list]
    ) -> Tuple[Optional[UniFiAPIResult], Optional[Response]]:
        result, response = self._request_url(
            method="put",
            url=f"{self.controller_url}{self.REST_DEVICE_ENDPOINT}/{device_id}",
            headers=self._headers,
            json=port_overrides,
        )

        logger.debug("%s [update_device] %s", LogPrefix.API, device_id)

        return result, response

    def _request_url(
        self, url, method: str, headers: dict, json: Optional[dict] = None, log: bool = True
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

            response.raise_for_status()
        except requests.ConnectionError as e:
            logger.debug("%s %s", LogPrefix.API, e)
            self._exit(1)
        except requests.HTTPError as e:
            logger.error("%s %s", LogPrefix.API, e)
            self._exit(1)
        finally:
            if response:
                result = self._get_json(response)

                if result:
                    meta_info: str = f"""[{result.meta.get('rc')}]{f" {result.meta['msg']}" if result.meta.get('msg') else ""} {response.url}"""

                    if log is True:
                        logger.debug("%s %s", LogPrefix.API, meta_info)

        return result, response

    def _get_json(self, response: Response) -> Optional[UniFiAPIResult]:
        result: Optional[UniFiAPIResult] = None

        try:
            data = json.loads(response.text)
            result = UniFiAPIResult(meta=data.get("meta", {}), data=data.get("data", []))
        except JSONDecodeError:
            logger.error("%s JSON decode error. API not available! Shutdown UniFi Tools.", LogPrefix.API)
            self._exit(1)

        return result

    def _reconnect(self, response: Response, *args, **kwargs):
        if response.status_code == requests.codes.unauthorized:
            data: dict = json.loads(response.text)
            meta: dict = data.get("meta", {})

            logger.debug(
                "[API] %s", f"""[{meta.get('rc')}]{f" {meta['msg']}" if meta.get('msg') else ""} {response.url}"""
            )

            self._logged_in = False
            self.login()

            return self._session.send(response.request, verify=False)

    def _exit(self, rc):
        self.rc = rc

        if asyncio.get_event_loop().is_running():
            cancel_tasks()
        else:
            sys.exit(rc)


class UniFiDevice(NamedTuple):
    id: str
    info: dict


class UniFiDevices:
    def __init__(self, unifi_api: UniFiAPI):
        self.unifi_api: UniFiAPI = unifi_api
        self.unifi_device_map = UniFiDeviceMap()
        self.features = FeatureMap()
        self.config: Config = unifi_api.config

    def get_device_info(self, device_id: str) -> dict:
        result, response = self.unifi_api.list_all_devices()
        device_info: dict = {}

        if result:
            adopted_devices_list: List[dict] = [
                device for device in result.data if device.get("adopted") and device.get("_id") == device_id
            ]

            if adopted_devices_list:
                device_info = adopted_devices_list[0]

        return device_info

    def scan(self):
        result, response = self.unifi_api.list_all_devices(log=False)

        if result:
            self.unifi_device_map.initialise(result.data)

    def read_devices(self):
        logger.info("%s Reading adopted devices.", LogPrefix.API)
        self.scan()

        if self.unifi_device_map is None:
            logger.debug("%s Can't read adopted devices!", LogPrefix.API)
        else:
            for device_id, device_info in self.unifi_device_map.items():
                if device_info["ports"]:
                    unifi_switch: UniFiSwitch = UniFiSwitch(
                        unifi_devices=self,
                        unifi_device=UniFiDevice(id=device_id, info=device_info),
                    )

                    unifi_switch.parse_features()


class UniFiSwitch:
    def __init__(self, unifi_devices: UniFiDevices, unifi_device: UniFiDevice):
        self.config: Config = unifi_devices.config
        self.features: FeatureMap = unifi_devices.features
        self.unifi_devices: UniFiDevices = unifi_devices
        self.unifi_device: UniFiDevice = unifi_device

    def _parse_feature_port(self, port_info: UniFiPort):
        self.features.register(
            FeaturePort(
                unifi_devices=self.unifi_devices,
                unifi_device=self.unifi_device,
                port_info=port_info,
            )
        )

    def parse_features(self):
        for port_info in self.unifi_device.info["ports"].values():
            self._parse_feature_port(port_info=port_info)
