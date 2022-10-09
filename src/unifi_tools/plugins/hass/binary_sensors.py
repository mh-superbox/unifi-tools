import asyncio
import json
from asyncio import Task
from typing import Any
from typing import List
from typing import Set
from typing import Tuple

from unifi_tools.config import Config
from unifi_tools.config import logger
from unifi_tools.features import FeatureConst
from unifi_tools.features import FeatureMap
from unifi_tools.features import FeaturePoEState
from unifi_tools.logging import LOG_MQTT_PUBLISH
from unifi_tools.plugins.hass.discover import HassBaseDiscovery
from unifi_tools.unifi import UniFiDevices


class HassBinarySensorsDiscovery(HassBaseDiscovery):
    publish_feature_types: List[str] = [FeatureConst.PORT]

    def __init__(self, unifi_devices: UniFiDevices, mqtt_client):
        self.config: Config = unifi_devices.config
        self.unifi_devices: UniFiDevices = unifi_devices
        self.mqtt_client = mqtt_client
        self.features: FeatureMap = unifi_devices.features

        super().__init__(config=unifi_devices.config)

    def _get_discovery(self, feature) -> Tuple[str, dict]:
        topic: str = f"{self.config.homeassistant.discovery_prefix}/binary_sensor/{feature.topic}/config"
        poe_on_states: str = "'" + FeaturePoEState.POE + "', '" + FeaturePoEState.POE24V + "'"

        message: dict = {
            "name": f"{feature.friendly_name}",
            "unique_id": f"{self.config.device_info.name.lower()}-{feature.unique_id}",
            "object_id": f"{self.config.device_info.name.lower()}-{feature.unique_id}",
            "json_attributes_topic": f"{feature.topic}/get",
            "state_topic": f"{feature.topic}/get",
            "value_template": "{% if value_json.poe_mode in [" + poe_on_states + "] %}on{% else %}off{% endif %}",
            "payload_on": "on",
            "payload_off": "off",
            "qos": 2,
            "device": {
                "name": feature.unifi_device.info["name"],
                "identifiers": feature.unifi_device.id,
                "model": feature.unifi_device.info["model"],
                "sw_version": feature.unifi_device.info["version"],
                "manufacturer": self.config.device_info.manufacturer,
            },
        }

        return topic, message

    async def publish(self):
        for feature in self.features.by_feature_type(self.publish_feature_types):
            # TODO Refactor when multiple feature types exists!
            if feature.poe_mode:
                topic, message = self._get_discovery(feature)
                json_data: str = json.dumps(message)
                await self.mqtt_client.publish(topic, json_data, qos=2, retain=True)
                logger.debug(LOG_MQTT_PUBLISH, topic, json_data)


class HassBinarySensorsMqttPlugin:
    """Provide Home Assistant MQTT commands for binary sensors."""

    def __init__(self, unifi_devices: UniFiDevices, mqtt_client):
        self._hass = HassBinarySensorsDiscovery(unifi_devices, mqtt_client)

    async def init_tasks(self) -> Set[Task]:
        tasks: Set[Task] = set()

        task: Task[Any] = asyncio.create_task(self._hass.publish())
        tasks.add(task)

        return tasks
