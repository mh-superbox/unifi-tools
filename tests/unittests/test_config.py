import pytest

from conftest import ConfigLoader
from unifi_tools.config import ConfigException
from unittests.test_config_data import CONFIG_INVALID_DEVICE_NAME
from unittests.test_config_data import CONFIG_INVALID_FEATURE_PROPERTY
from unittests.test_config_data import CONFIG_INVALID_FEATURE_TYPE
from unittests.test_config_data import CONFIG_INVALID_HOMEASSISTANT_DISCOVERY_PREFIX
from unittests.test_config_data import CONFIG_INVALID_LOG_LEVEL


class TestUnhappyPathConfig:
    @pytest.mark.parametrize(
        "config_loader, expected_log",
        [
            (
                CONFIG_INVALID_DEVICE_NAME,
                "Invalid value 'Invalid Device Name' in 'name'. The following characters are prohibited: a-z 0-9 -_",
            ),
            (
                CONFIG_INVALID_HOMEASSISTANT_DISCOVERY_PREFIX,
                "[HOMEASSISTANT] Invalid value 'invalid discovery name' in 'discovery_prefix'. The following characters are prohibited: a-z 0-9 -_",
            ),
            (
                CONFIG_INVALID_FEATURE_TYPE,
                "Expected features to be <class 'dict'>, got 'INVALID'",
            ),
            (
                CONFIG_INVALID_FEATURE_PROPERTY,
                "Invalid feature property: {'invalid_property': 'INVALID'}",
            ),
            (
                CONFIG_INVALID_LOG_LEVEL,
                "Invalid log level 'invalid'. The following log levels are allowed: error warning info debug.",
            ),
        ],
        indirect=["config_loader"],
    )
    def test_validation(self, config_loader: ConfigLoader, expected_log: str):
        with pytest.raises(ConfigException) as error:
            config_loader.get_config()

        assert expected_log == str(error.value)
