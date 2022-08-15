import json

import pytest
import responses
from responses import matchers

from unifi_tools.features import FeaturePoEState
from unifi_tools.features import FeaturePort
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevice
from unifi_tools.unifi import UniFiDevices
from unit.unifi.test_unifi_api import TestUniFiApi
from unit.unifi.test_unifi_api_data import devices_json_response
from unit.unifi.test_unifi_api_data import response_header
from unit.unifi.test_unifi_api_data import updated_port_overrides_payload
from unit.unifi.test_unifi_api_data import updated_port_overrides_with_custom_feature_settings_payload


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
                    "unique_id": "MOCKED_ID-port-1",
                    "topic": "mocked_unifi/MOCKED_ID-port-1",
                    "state": '{"poe_mode": "on"}',
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
                    "unique_id": "MOCKED_ID-port-26",
                    "topic": "mocked_unifi/MOCKED_ID-port-26",
                    "state": "{}",
                    "changed": False,
                },
            ),
        ],
    )
    def test_feature_port_properties(self, unifi_api: UniFiAPI, port_idx: int, expected: dict):
        unifi_devices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.scan()

        device = unifi_devices.unifi_device_map["MOCKED_ID"]

        feature = FeaturePort(
            unifi_devices=unifi_devices,
            unifi_device=UniFiDevice(id="MOCKED_ID", info=device),
            port_info=device["ports"][port_idx],
        )

        assert expected["poe_mode"] == feature.poe_mode
        assert expected["value"] == feature.value
        assert expected["feature_name"] == feature.feature_name
        assert expected["friendly_name"] == feature.friendly_name
        assert expected["unique_id"] == feature.unique_id
        assert expected["topic"] == feature.topic
        assert expected["state"] == feature.state
        assert expected["changed"] is feature.changed

    @responses.activate
    @pytest.mark.parametrize(
        "port_idx, poe_mode, payload, expected",
        [
            (1, FeaturePoEState.POE24V, updated_port_overrides_payload, False),
            (2, FeaturePoEState.ON, updated_port_overrides_payload, True),
            (3, FeaturePoEState.ON, updated_port_overrides_with_custom_feature_settings_payload, False),
        ],
    )
    def test_feature_set_state(self, unifi_api: UniFiAPI, port_idx: int, poe_mode: str, payload: str, expected: bool):
        mocked_response = responses.put(
            url=f"{unifi_api.controller_url}{UniFiAPI.REST_DEVICE_ENDPOINT}/MOCKED_ID",
            json=json.loads(devices_json_response),
            match=[
                matchers.header_matcher(response_header),
                matchers.json_params_matcher(json.loads(payload)),
            ],
        )

        responses.add(mocked_response)

        unifi_devices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.scan()

        device = unifi_devices.unifi_device_map["MOCKED_ID"]

        feature = FeaturePort(
            unifi_devices=unifi_devices,
            unifi_device=UniFiDevice(id="MOCKED_ID", info=device),
            port_info=device["ports"][port_idx],
        )

        update_devices: bool = feature.set_state(value={"poe_mode": poe_mode})

        assert expected is update_devices
