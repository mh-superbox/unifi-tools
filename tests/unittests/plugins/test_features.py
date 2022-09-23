import asyncio
import json
from asyncio import Task
from contextlib import AsyncExitStack
from typing import NamedTuple
from typing import Set
from unittest.mock import AsyncMock
from unittest.mock import PropertyMock

import pytest
import responses
from _pytest.logging import LogCaptureFixture
from asyncio_mqtt import Client
from responses import matchers
from responses.registries import OrderedRegistry

from conftest_data import CONFIG_CONTENT
from unifi_tools.plugins.features import FeaturesMqttPlugin
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unittests.plugins.test_features_data import devices_json_response_1
from unittests.plugins.test_features_data import devices_json_response_2
from unittests.plugins.test_features_data import port_overrides_payload
from unittests.test_unifi_api import TestUniFiApi
from unittests.test_unifi_api_data import RESPONSE_HEADER


class MockMQTTMessage(NamedTuple):
    payload: bytes


class MockMQTTMessages:
    def __init__(self, message):
        self.message = message

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.message:
            return MockMQTTMessage(self.message.pop())

        raise StopAsyncIteration


class TestHappyPathFeaturesMqttPlugin(TestUniFiApi):
    @responses.activate(registry=OrderedRegistry)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_init_tasks(self, config_loader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        async def run():
            mock_list_all_devices_response_1 = responses.get(
                url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
                json=json.loads(devices_json_response_2),
                match=[matchers.header_matcher(RESPONSE_HEADER)],
            )

            mock_list_all_devices_response_2 = responses.get(
                url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
                json=json.loads(devices_json_response_1),
                match=[matchers.header_matcher(RESPONSE_HEADER)],
            )

            mock_update_device_response = responses.put(
                url=f"{unifi_api.controller_url}{UniFiAPI.REST_DEVICE_ENDPOINT}/MOCKED_ID",
                json=json.loads(devices_json_response_2),
                match=[
                    matchers.header_matcher(RESPONSE_HEADER),
                    matchers.json_params_matcher(json.loads(port_overrides_payload)),
                ],
            )

            responses.add(mock_list_all_devices_response_1)
            responses.add(mock_list_all_devices_response_2)
            responses.add(mock_update_device_response)

            unifi_devices = UniFiDevices(unifi_api=unifi_api)
            unifi_devices.read_devices()

            mock_mqtt_messages = AsyncMock()
            mock_mqtt_messages.__aenter__.return_value = MockMQTTMessages([b"""{"poe_mode": "on"}"""])

            mock_mqtt_client = AsyncMock(spec=Client)
            mock_mqtt_client.filtered_messages.return_value = mock_mqtt_messages

            FeaturesMqttPlugin.PUBLISH_RUNNING = PropertyMock(side_effect=[True, False])
            features = FeaturesMqttPlugin(unifi_devices=unifi_devices, mqtt_client=mock_mqtt_client)

            async with AsyncExitStack() as stack:
                tasks: Set[Task] = set()

                await stack.enter_async_context(mock_mqtt_client)

                features_tasks = await features.init_tasks(stack)
                tasks.update(features_tasks)

                await asyncio.gather(*tasks)

                for task in tasks:
                    assert True is task.done()

            logs: list = [record.getMessage() for record in caplog.records]

            assert "[API] Reading adopted devices." in logs

            assert "[MQTT] Subscribe topic mocked_unifi/MOCKED_ID-port-1/set" in logs
            assert "[MQTT] Subscribe topic mocked_unifi/MOCKED_ID-port-2/set" in logs
            assert "[MQTT] Subscribe topic mocked_unifi/MOCKED_ID-port-3/set" in logs

            assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
            assert "[API] [ok] https://unifi.local/api/s/default/rest/device/MOCKED_ID" in logs
            assert "[API] [update_device] MOCKED_ID" in logs

            assert '[MQTT] [mocked_unifi/MOCKED_ID-port-1/set] Subscribe message: {"poe_mode": "on"}' in logs
            assert '[MQTT] [mocked_unifi/MOCKED_ID-port-1/get] Publishing message: {"poe_mode": "auto"}' in logs
            assert '[MQTT] [mocked_unifi/MOCKED_ID-port-2/get] Publishing message: {"poe_mode": "off"}' in logs
            assert '[MQTT] [mocked_unifi/MOCKED_ID-port-3/get] Publishing message: {"poe_mode": "off"}' in logs

            assert 12 == len(logs)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run())
