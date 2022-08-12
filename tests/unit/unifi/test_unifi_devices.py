import json
from typing import List
from typing import Optional

import responses
from _pytest.logging import LogCaptureFixture
from responses import matchers

from unifi_tools.config import Config
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unit.unifi.test_unifi_api import TestUniFiApi
from unit.unifi.test_unifi_api_data import devices_json_response
from unit.unifi.test_unifi_api_data import devices_not_adopted_json_response
from unit.unifi.test_unifi_api_data import port_overrides_payload
from unit.unifi.test_unifi_api_data import response_header


class TestHappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    def test_device_info(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture, config: Config):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)

        mocked_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_response)
        device_info: Optional[dict] = unifi_devices.get_device_info(device_id="MOCKED_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert isinstance(device_info, dict)
        assert "MOCKED_ID" == device_info["_id"]

    @responses.activate
    def test_device_port_info(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture, config: Config):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)

        mocked_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_json_response),
            match=[
                matchers.header_matcher(response_header),
            ],
        )

        responses.add(mocked_response)
        device_port_info: Optional[List[dict]] = unifi_devices.get_device_port_info(device_id="MOCKED_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert isinstance(device_port_info, list)
        assert device_port_info == json.loads(port_overrides_payload)["port_overrides"]


class TestUnhappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    def test_device_info_not_adopted(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture, config: Config):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)

        mocked_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_not_adopted_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_response)
        device_info: Optional[dict] = unifi_devices.get_device_info(device_id="MOCKED_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert device_info is None
