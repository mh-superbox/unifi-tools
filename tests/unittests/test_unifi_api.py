import json

import pytest
import requests
import responses
from _pytest.logging import LogCaptureFixture
from requests import Response
from responses import matchers
from responses.registries import OrderedRegistry

from conftest import ConfigLoader
from conftest_data import CONFIG_CONTENT
from unifi_tools.config import Config
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiAPIResult
from unittests.test_unifi_api_data import DEVICES_JSON_RESPONSE
from unittests.test_unifi_api_data import PORT_OVERRIDES_PAYLOAD
from unittests.test_unifi_api_data import RESPONSE_HEADER


class TestUniFiApi:
    @pytest.fixture()
    def unifi_api(self, config_loader) -> UniFiAPI:
        config: Config = config_loader.get_config()

        config.unifi_controller.url = "unifi.local"
        config.unifi_controller.port = 443

        api = UniFiAPI(config=config)

        return api


class TestHappyPathUniFiApi(TestUniFiApi):
    @pytest.mark.parametrize(
        "url, port, expected",
        [
            ("unifi.local", 8443, "https://unifi.local:8443"),
            ("unifi.local", 443, "https://unifi.local"),
        ],
    )
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_controller_url(self, config_loader: ConfigLoader, url: str, port: int, expected: str):
        config: Config = config_loader.get_config()

        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)
        assert expected == unifi_api.controller_url

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_login(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_response)
        result, response = unifi_api.login()
        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/login" in logs
        assert "[API] Successfully logged in." in logs
        assert "[API] CSRF Token: None" in logs
        assert 3 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mock_response.call_count

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_logout(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGOUT_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[
                matchers.header_matcher(
                    {
                        "x-csrf-token": "",
                    },
                )
            ],
        )

        responses.add(mock_response)
        result, response = unifi_api.logout()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/logout" in logs
        assert "[API] Successfully logged out." in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mock_response.call_count

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_list_all_devices(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_response)
        result, response = unifi_api.list_all_devices()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mock_response.call_count

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_update_device(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.put(
            url=f"{unifi_api.controller_url}{UniFiAPI.REST_DEVICE_ENDPOINT}/MOCKED_DEVICE_ID",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[
                matchers.header_matcher(RESPONSE_HEADER),
                matchers.json_params_matcher(json.loads(PORT_OVERRIDES_PAYLOAD)),
            ],
        )

        responses.add(mock_response)
        result, response = unifi_api.update_device(
            device_id="MOCKED_DEVICE_ID", port_overrides=json.loads(PORT_OVERRIDES_PAYLOAD)
        )

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/rest/device/MOCKED_DEVICE_ID" in logs
        assert "[API] [update_device] MOCKED_DEVICE_ID" in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert result.data is not None
        assert requests.codes.ok == response.status_code
        assert 1 == mock_response.call_count

    @responses.activate(registry=OrderedRegistry)
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_reconnect(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_list_all_devices_failed_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json={
                "meta": {
                    "rc": "error",
                    "msg": "api.err.LoginRequired",
                },
                "data": [],
            },
            match=[matchers.header_matcher(RESPONSE_HEADER)],
            status=requests.codes.unauthorized,
        )

        mock_login_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        mock_list_all_devices_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(DEVICES_JSON_RESPONSE),
            match=[matchers.header_matcher(RESPONSE_HEADER)],
        )

        responses.add(mock_list_all_devices_failed_response)
        responses.add(mock_login_response)
        responses.add(mock_list_all_devices_response)

        result, response = unifi_api.list_all_devices()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [error] api.err.LoginRequired https://unifi.local/api/s/default/stat/device" in logs
        assert "[API] [ok] https://unifi.local/api/login" in logs
        assert "[API] Successfully logged in." in logs
        assert "[API] CSRF Token: None" in logs
        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 6 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mock_list_all_devices_failed_response.call_count
        assert 1 == mock_login_response.call_count
        assert 1 == mock_list_all_devices_response.call_count


class TestUnhappyPathUniFiApi(TestUniFiApi):
    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_exception_http_error(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            match=[matchers.header_matcher(RESPONSE_HEADER)],
            status=requests.codes.bad_gateway,
        )

        responses.add(mock_response)

        with pytest.raises(SystemExit) as error:
            unifi_api.login()
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] 502 Server Error: Bad Gateway for url: https://unifi.local/api/login" in logs
        assert 1 == len(logs)

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_exception_connection_error(
        self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture
    ):
        mock_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            body=requests.ConnectionError("MOCKED CONNECTION ERROR"),
        )

        responses.add(mock_response)

        with pytest.raises(SystemExit) as error:
            unifi_api.login()
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] MOCKED CONNECTION ERROR" in logs
        assert 1 == len(logs)

    @responses.activate
    @pytest.mark.parametrize("config_loader", [CONFIG_CONTENT], indirect=True)
    def test_json_decode_error(self, config_loader: ConfigLoader, unifi_api: UniFiAPI, caplog: LogCaptureFixture):
        mock_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            match=[matchers.header_matcher(RESPONSE_HEADER)],
            body="INVALID_JSON",
        )

        responses.add(mock_response)

        with pytest.raises(SystemExit) as error:
            unifi_api.login()
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] JSON decode error. API not available! Shutdown UniFi Tools." in logs
        assert 1 == len(logs)
