import json
from typing import Type
import pytest
import responses
from responses import matchers

from unifi_tools.features import Feature
from unifi_tools.features import FeaturePort
from unifi_tools.features import FeaturePort
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevice
from unifi_tools.unifi import UniFiDevices
from unit.unifi.test_unifi_api import TestUniFiApi
from unit.unifi.test_unifi_api_data import devices_json_response
from unit.unifi.test_unifi_api_data import response_header


class TestHappyPathFeatures(TestUniFiApi):
    @responses.activate
    @pytest.fixture(autouse=True)
    def setup(self, unifi_api: UniFiAPI):
        mocked_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_response)

    @responses.activate
    def test_feature_port_properties(self, unifi_api: UniFiAPI):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.scan()

        device = unifi_devices.unifi_device_map["MOCKED_ID"]

        feature = FeaturePort(
            unifi_devices=unifi_devices,
            unifi_device=UniFiDevice(id="MOCKED_ID", info=device),
            port_info=device["ports"][1],
        )

        assert {"poe_mode": "on"} == feature.value
        assert "port" == feature.feature_name
        assert "MOCKED Port 1" == feature.friendly_name
        assert "MOCKED_ID-port-1" == feature.unique_id
        assert "mocked_unifi/MOCKED_ID-port-1" == feature.topic
        assert '{"poe_mode": "on"}' == feature.state
        assert True is feature.changed

        # feature.set_state(value={"poe_mode": "off"})
        print(feature.changed)
