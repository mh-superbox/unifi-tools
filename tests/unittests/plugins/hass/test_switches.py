import asyncio
import json
from asyncio import Task
from contextlib import AsyncExitStack
from typing import Set
from unittest.mock import AsyncMock

import pytest
import responses
from _pytest.logging import LogCaptureFixture
from asyncio_mqtt import Client
from responses import matchers
from responses.registries import OrderedRegistry

from conftest import ConfigLoader
from conftest_data import CONFIG_CONTENT
from unifi_tools.features import Feature
from unifi_tools.plugins.hass.switches import HassSwitchesDiscovery
from unifi_tools.plugins.hass.switches import HassSwitchesMqttPlugin
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiDevices
from unittests.plugins.test_features_data import devices_json_response_2
from unittests.test_unifi_api import TestUniFiApi
from unittests.test_unifi_api_data import RESPONSE_HEADER


class TestHappyPathHassSwitchesMqttPlugin(TestUniFiApi):
    @responses.activate(registry=OrderedRegistry)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_init_tasks(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        async def run():
            mock_list_all_devices_response_1 = responses.get(
                url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
                json=json.loads(devices_json_response_2),
                match=[matchers.header_matcher(RESPONSE_HEADER)],
            )

            responses.add(mock_list_all_devices_response_1)

            unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
            unifi_devices.read_devices()

            mock_mqtt_client: AsyncMock = AsyncMock(spec=Client)
            plugin: HassSwitchesMqttPlugin = HassSwitchesMqttPlugin(
                unifi_devices=unifi_devices, mqtt_client=mock_mqtt_client
            )

            async with AsyncExitStack() as stack:
                tasks: Set[Task] = set()

                await stack.enter_async_context(mock_mqtt_client)

                plugin_tasks = await plugin.init_tasks()
                tasks.update(plugin_tasks)

                await asyncio.gather(*tasks)

                for task in tasks:
                    assert True is task.done()

            logs: list = [record.getMessage() for record in caplog.records]

            assert "[API] Reading adopted devices." in logs

            assert (
                '[MQTT] [homeassistant/switch/mocked_unifi/MOCKED_DEVICE_ID-port-1/config] Publishing message: {"name": "MOCKED Port 1", "unique_id": "mocked_unifi-MOCKED_DEVICE_ID-port-1", "command_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-1/set", "state_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-1/get", "value_template": "{% if value_json.poe_mode in [\'auto\', \'pasv24\'] %}on{% else %}off{% endif %}", "state_on": "on", "state_off": "off", "payload_on": "{\\"poe_mode\\": \\"on\\"}", "payload_off": "{\\"poe_mode\\": \\"off\\"}", "qos": 2, "device": {"name": "MOCKED SWITCH", "identifiers": "MOCKED_DEVICE_ID", "model": "MOCKED MODEL", "sw_version": "MOCKED 6.2.14.13855", "manufacturer": "Ubiquiti Inc."}, "object_id": "MOCKED_ID"}'
                in logs
            )
            assert (
                '[MQTT] [homeassistant/switch/mocked_unifi/MOCKED_DEVICE_ID-port-2/config] Publishing message: {"name": "MOCKED Port 2", "unique_id": "mocked_unifi-MOCKED_DEVICE_ID-port-2", "command_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-2/set", "state_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-2/get", "value_template": "{% if value_json.poe_mode in [\'auto\', \'pasv24\'] %}on{% else %}off{% endif %}", "state_on": "on", "state_off": "off", "payload_on": "{\\"poe_mode\\": \\"on\\"}", "payload_off": "{\\"poe_mode\\": \\"off\\"}", "qos": 2, "device": {"name": "MOCKED SWITCH", "identifiers": "MOCKED_DEVICE_ID", "model": "MOCKED MODEL", "sw_version": "MOCKED 6.2.14.13855", "manufacturer": "Ubiquiti Inc."}, "object_id": "MOCKED_ID"}'
                in logs
            )
            assert (
                '[MQTT] [homeassistant/switch/mocked_unifi/MOCKED_DEVICE_ID-port-3/config] Publishing message: {"name": "MOCKED Port 3", "unique_id": "mocked_unifi-MOCKED_DEVICE_ID-port-3", "command_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-3/set", "state_topic": "mocked_unifi/MOCKED_DEVICE_ID-port-3/get", "value_template": "{% if value_json.poe_mode in [\'auto\', \'pasv24\'] %}on{% else %}off{% endif %}", "state_on": "on", "state_off": "off", "payload_on": "{\\"poe_mode\\": \\"on\\"}", "payload_off": "{\\"poe_mode\\": \\"off\\"}", "qos": 2, "device": {"name": "MOCKED SWITCH", "identifiers": "MOCKED_DEVICE_ID", "model": "MOCKED MODEL", "sw_version": "MOCKED 6.2.14.13855", "manufacturer": "Ubiquiti Inc."}, "object_id": "MOCKED_ID"}'
                in logs
            )

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run())

    @responses.activate(registry=OrderedRegistry)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_discovery_message(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_list_all_devices_response_1 = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(devices_json_response_2),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_list_all_devices_response_1)

        unifi_devices: UniFiDevices = UniFiDevices(unifi_api=unifi_api)
        unifi_devices.read_devices()

        mock_mqtt_client: AsyncMock = AsyncMock(spec=Client)
        plugin: HassSwitchesMqttPlugin = HassSwitchesMqttPlugin(
            unifi_devices=unifi_devices, mqtt_client=mock_mqtt_client
        )

        feature: Feature = next(plugin._hass.features.by_feature_type(HassSwitchesDiscovery.publish_feature_types))
        topic, message = plugin._hass._get_discovery(feature)

        assert "MOCKED Port 1" == message["name"]
        assert "mocked_unifi-MOCKED_DEVICE_ID-port-1" == message["unique_id"]
        assert "MOCKED_ID" == message["object_id"]
        assert "mocked_unifi/MOCKED_DEVICE_ID-port-1/set" == message["command_topic"]
        assert "mocked_unifi/MOCKED_DEVICE_ID-port-1/get" == message["state_topic"]
        assert (
            "{% if value_json.poe_mode in ['auto', 'pasv24'] %}on{% else %}off{% endif %}" == message["value_template"]
        )
        assert "on" == message["state_on"]
        assert "off" == message["state_off"]
        assert '{"poe_mode": "on"}' == message["payload_on"]
        assert '{"poe_mode": "off"}' == message["payload_off"]
        assert 2 == message["qos"]
        assert "MOCKED SWITCH" == message["device"]["name"]
        assert "MOCKED_DEVICE_ID" == message["device"]["identifiers"]
        assert "MOCKED MODEL" == message["device"]["model"]
        assert "MOCKED 6.2.14.13855" == message["device"]["sw_version"]
        assert "Ubiquiti Inc." == message["device"]["manufacturer"]

        assert "homeassistant/switch/mocked_unifi/MOCKED_DEVICE_ID-port-1/config" == topic
