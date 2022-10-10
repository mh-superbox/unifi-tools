import json

import pytest
import responses
from responses import matchers

from conftest import ConfigLoader
from conftest_data import CONFIG_CONTENT
from unifi_tools.features import FeaturePoEState
from unifi_tools.features import FeaturePort
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevice
from unifi_tools.unifi import UniFiDevices
from unittests.test_unifi_api import TestUniFiApi
from unittests.test_unifi_api_data import DEVICES_JSON_RESPONSE
from unittests.test_unifi_api_data import RESPONSE_HEADER
from unittests.test_unifi_api_data import UPDATED_PORT_OVERRIDES_PAYLOAD
from unittests.test_unifi_api_data import UPDATED_PORT_OVERRIDES_WITH_CUSTOM_FEATURE_SETTINGS_PAYLOAD


class TestHappyPathFeatures(TestUniFiApi):
    @responses.activate
    @pytest.fixture(autouse=True)
    def setup(self, unifi_api: UniFiAPI):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_response)

    @responses.activate
    @pytest.mark.parametrize(
        "port_idx, expected",
        [
            (
                1,
                {
                    "poe_mode": "on",
                    "value": {"poe_mode": "on"},
                    "feature_name": "port",
                    "friendly_name": "MOCKED Port 1",
                    "unique_id": "MOCKED_DEVICE_ID-port-1",
                    "topic": "mocked_unifi/MOCKED_DEVICE_ID-port-1",
                    "state": '{"poe_mode": "on"}',
                    "json_attributes": '{"poe_mode": "pasv24"}',
                    "changed": True,
                },
            ),
            (
                26,
                {
                    "poe_mode": None,
                    "value": {},
                    "feature_name": "port",
                    "friendly_name": "Port #26",
                    "unique_id": "MOCKED_DEVICE_ID-port-26",
                    "topic": "mocked_unifi/MOCKED_DEVICE_ID-port-26",
                    "state": "{}",
                    "json_attributes": "{}",
                    "changed": False,
                },
            ),
        ],
    )
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_feature_port_properties(
        self, config_loader: ConfigLoader, unifi_api: UniFiAPI, port_idx: int, expected: dict
    ):
        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.scan()

        device = unifi_devices.unifi_device_map["MOCKED_DEVICE_ID"]

        feature = FeaturePort(
            unifi_devices=unifi_devices,
            unifi_device=UniFiDevice(id="MOCKED_DEVICE_ID", info=device),
            port_info=device["ports"][port_idx],
        )

        assert expected["poe_mode"] == feature.poe_mode
        assert expected["value"] == feature.value
        assert expected["feature_name"] == feature.feature_name
        assert expected["friendly_name"] == feature.friendly_name
        assert expected["unique_id"] == feature.unique_id
        assert expected["topic"] == feature.topic
        assert expected["json_attributes"] == feature.json_attributes
        assert expected["changed"] is feature.changed

    @responses.activate
    @pytest.mark.parametrize(
        "port_idx, poe_mode, payload, expected",
        [
            (1, FeaturePoEState.POE24V, UPDATED_PORT_OVERRIDES_PAYLOAD, False),
            (2, FeaturePoEState.ON, UPDATED_PORT_OVERRIDES_PAYLOAD, True),
            (3, FeaturePoEState.ON, UPDATED_PORT_OVERRIDES_WITH_CUSTOM_FEATURE_SETTINGS_PAYLOAD, False),
        ],
    )
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_feature_set_state(
        self,
        config_loader: ConfigLoader,
        unifi_api: UniFiAPI,
        port_idx: int,
        poe_mode: str,
        payload: str,
        expected: bool,
    ):
        mock_response = responses.put(
            url=f"{unifi_api.controller_url}{UniFiAPI.REST_DEVICE_ENDPOINT}/MOCKED_DEVICE_ID",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[
                matchers.header_matcher(RESPONSE_HEADER),
                matchers.json_params_matcher(json.loads(payload)),
            ],
        )

        responses.add(mock_response)

        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.scan()

        device = unifi_devices.unifi_device_map["MOCKED_DEVICE_ID"]

        feature = FeaturePort(
            unifi_devices=unifi_devices,
            unifi_device=UniFiDevice(id="MOCKED_DEVICE_ID", info=device),
            port_info=device["ports"][port_idx],
        )

        update_devices: bool = feature.set_state(value={"poe_mode": poe_mode})

        assert expected is update_devices
