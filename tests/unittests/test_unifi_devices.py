import json
from typing import Iterator
from typing import Optional

import pytest
import responses
from _pytest.logging import LogCaptureFixture  # pylint: disable=import-private-name
from responses import matchers

from conftest_data import CONFIG_CONTENT
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeaturePort
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unifi_tools.unifi import UniFiPort
from unittests.test_unifi_api import TestUniFiApi
from unittests.test_unifi_api_data import DEVICES_JSON_RESPONSE
from unittests.test_unifi_api_data import DEVICES_NOT_ADOPTED_JSON_RESPONSE
from unittests.test_unifi_api_data import RESPONSE_HEADER
from unittests.test_unifi_devices_data import FEATURE_MAP_REPR


class TestHappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    @pytest.fixture(autouse=True)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def setup(self, unifi_api: UniFiAPI):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_response)

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_device_info(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
        device_info: Optional[dict] = unifi_devices.get_device_info(device_id="MOCKED_DEVICE_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert len(logs) == 2

        assert isinstance(device_info, dict)
        assert device_info["_id"] == "MOCKED_DEVICE_ID"

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_scan(self, unifi_api: UniFiAPI):
        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)

        assert not unifi_devices.unifi_device_map.data
        unifi_devices.scan()
        assert len(unifi_devices.unifi_device_map.data) == 1

        device = unifi_devices.unifi_device_map.data["MOCKED_DEVICE_ID"]
        port = device["ports"][1]

        assert isinstance(port, UniFiPort)
        assert device["name"] == "MOCKED SWITCH"
        assert device["model"] == "MOCKED MODEL"
        assert device["version"] == "MOCKED 6.2.14.13855"
        assert len(device.keys()) == 4

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_read_devices(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)

        assert not unifi_devices.features.data
        unifi_devices.read_devices()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] Reading adopted devices." in logs
        assert len(logs) == 1

        features = unifi_devices.features.by_feature_types(["port"])

        feature = next(features)
        ports = unifi_devices.features.data[FeatureConst.PORT]

        assert str(unifi_devices.features.data) == FEATURE_MAP_REPR
        assert isinstance(features, Iterator)
        assert isinstance(ports, list)
        assert isinstance(feature, FeaturePort)
        assert len(ports) == 26
        assert str(feature) == "MOCKED Port 1"
        assert feature.value == {"poe_mode": "on"}


class TestUnhappyPathUniFiDevices(TestUniFiApi):
    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_device_info_not_adopted(self, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(DEVICES_NOT_ADOPTED_JSON_RESPONSE),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_response)
        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
        device_info: dict = unifi_devices.get_device_info(device_id="MOCKED_DEVICE_ID")

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert len(logs) == 2

        assert not device_info
