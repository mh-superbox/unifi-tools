import json
from typing import Iterator
from typing import Optional

import pytest
import responses
from _pytest.logging import LogCaptureFixture
from responses import matchers

from conftest_data import CONFIG_CONTENT
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeaturePort
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unifi_tools.unifi import UniFiPort
from unittests.test_unifi_api import TestUniFiApi
from unittests.test_unifi_api_data import devices_json_response
from unittests.test_unifi_api_data import devices_not_adopted_json_response
from unittests.test_unifi_api_data import response_header
from unittests.test_unifi_devices_data import feature_map_repr


class TestHappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    @pytest.fixture(autouse=True)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def setup(self, config_loader, unifi_api: UniFiAPI):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mock_response)

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_device_info(self, config_loader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)
        device_info: Optional[dict] = unifi_devices.get_device_info(device_id="MOCKED_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert isinstance(device_info, dict)
        assert "MOCKED_ID" == device_info["_id"]

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_scan(self, config_loader, unifi_api: UniFiAPI):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)

        assert 0 == len(unifi_devices.unifi_device_map)
        unifi_devices.scan()
        assert 1 == len(unifi_devices.unifi_device_map)

        device = unifi_devices.unifi_device_map["MOCKED_ID"]
        port = device["ports"][1]

        assert isinstance(port, UniFiPort)
        assert "MOCKED SWITCH" == device["name"]
        assert "MOCKED MODEL" == device["model"]
        assert "MOCKED 6.2.14.13855" == device["version"]
        assert 4 == len(device.keys())

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_read_devices(self, config_loader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)

        assert 0 == len(unifi_devices.features)
        unifi_devices.read_devices()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] Reading adopted devices." in logs
        assert 1 == len(logs)

        features = unifi_devices.features.by_feature_type(["port"])

        feature = next(features)
        ports = unifi_devices.features[FeatureConst.PORT]

        assert feature_map_repr == str(unifi_devices.features)
        assert isinstance(features, Iterator)
        assert isinstance(ports, list)
        assert isinstance(feature, FeaturePort)
        assert 26 == len(ports)
        assert "MOCKED Port 1" == str(feature)
        assert {"poe_mode": "on"} == feature.value


class TestUnhappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_device_info_not_adopted(self, config_loader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_not_adopted_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mock_response)
        unifi_devices = UniFiDevices(unifi_api=unifi_api)
        device_info: dict = unifi_devices.get_device_info(device_id="MOCKED_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert 0 == len(device_info)
