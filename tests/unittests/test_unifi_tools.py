import builtins
import subprocess
from argparse import Namespace
from typing import List

import pytest as pytest
from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture
from pytest_mock.plugin import MockerFixture

from conftest_data import CONFIG_CONTENT
from unifi_tools.run import UniFiTools
from unifi_tools.run import parse_args
from unittests.test_unifi_tools_data import UNIFI_TOOLS_INSTALLER_WITHOUT_ENABLE_SYSTEMD_OUTPUT
from unittests.test_unifi_tools_data import UNIFI_TOOLS_INSTALLER_WITHOUT_OVERWRITE_CONFIG_OUTPUT
from unittests.test_unifi_tools_data import UNIFI_TOOLS_INSTALLER_WITH_ENABLE_SYSTEMD_OUTPUT


class TestHappyPathUniFiTools:
    def test_parse_args(self):
        parser = parse_args(["-c", "/tmp/settings.yml", "-i", "-y"])

        assert "/tmp/settings.yml" == parser.config
        assert True is parser.install
        assert True is parser.yes
        assert isinstance(parser, Namespace)

    @pytest.mark.parametrize(
        "side_effect, expected",
        [
            (["Y", "Y"], UNIFI_TOOLS_INSTALLER_WITH_ENABLE_SYSTEMD_OUTPUT),
            (["Y", "N"], UNIFI_TOOLS_INSTALLER_WITHOUT_ENABLE_SYSTEMD_OUTPUT),
            (["N", "N"], UNIFI_TOOLS_INSTALLER_WITHOUT_OVERWRITE_CONFIG_OUTPUT),
        ],
    )
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_installer(
        self,
        config_loader,
        mocker: MockerFixture,
        caplog: LogCaptureFixture,
        capsys: CaptureFixture,
        side_effect: List[str],
        expected: str,
    ):
        config = config_loader.get_config()

        mock_input = mocker.patch.object(builtins, "input")
        mock_input.side_effect = side_effect

        mock_subprocess = mocker.patch.object(subprocess, "check_output")
        mock_subprocess.return_value = "MOCKED STATUS"

        UniFiTools.install(config=config, assume_yes=False)

        logs: list = [record.getMessage() for record in caplog.records]

        if mock_subprocess.called:
            assert "MOCKED STATUS" in logs

        try:
            assert expected % config_loader.temp_config_path == capsys.readouterr().out
        except TypeError:
            assert expected == capsys.readouterr().out

        config_loader.cleanup()
