import tempfile
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from unifi_tools.config import Config
from unittests.test_config_data import config_invalid_device_name
from unittests.test_config_data import config_invalid_type


class TestUnhappyPathConfig:
    def test_invalid_device_name(self, caplog: LogCaptureFixture):
        tmp = tempfile.NamedTemporaryFile()

        with open(tmp.name, "w") as f:
            f.write(config_invalid_device_name)

        with pytest.raises(SystemExit) as error:
            Config(config_file_path=Path(tmp.name))
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert (
            "[CONFIG] Invalid value 'Invalid Device Name' in 'device_name'. The following characters are prohibited: A-Z a-z 0-9 -_"
            in logs
        )

    def test_invalid_type(self, caplog: LogCaptureFixture):
        tmp = tempfile.NamedTemporaryFile()

        with open(tmp.name, "w") as f:
            f.write(config_invalid_type)

        with pytest.raises(SystemExit) as error:
            Config(config_file_path=Path(tmp.name))
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[CONFIG] Config - Expected features to be <class 'dict'>, got 'INVALID'" in logs
