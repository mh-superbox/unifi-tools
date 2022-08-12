import json

import pytest
import requests
import responses
from _pytest.logging import LogCaptureFixture
from requests import Response
from responses import matchers
from responses.registries import OrderedRegistry

from unifi_tools.config import Config
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiAPIResult
from unit.test_unifi_api_data import happy_path_devices_json_response
from unit.test_unifi_api_data import happy_path_port_overrides_payload
from unit.test_unifi_api_data import response_header


class TestHappyPathUniFiApi:
    @pytest.mark.parametrize(
        "url, port, expected",
        [
            ("unifi.local", 8443, "https://unifi.local:8443"),
            ("unifi.local", 443, "https://unifi.local"),
        ],
    )
    def test_controller_url(self, config: Config, url: str, port: int, expected: str):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)
        assert expected == unifi_api.controller_url

    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_login(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_response)
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
        assert 1 == mocked_response.call_count

    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_logout(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.post(
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

        responses.add(mocked_response)
        result, response = unifi_api.logout()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/logout" in logs
        assert "[API] Successfully logged out." in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mocked_response.call_count

    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_list_all_devices(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(happy_path_devices_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_response)
        result, response = unifi_api.list_all_devices()

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/stat/device" in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert requests.codes.ok == response.status_code
        assert 1 == mocked_response.call_count

    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_update_device(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.put(
            url=f"{unifi_api.controller_url}{UniFiAPI.REST_DEVICE_ENDPOINT}/MOCKED_ID",
            json=json.loads(happy_path_devices_json_response),
            match=[
                matchers.header_matcher(response_header),
                matchers.json_params_matcher(json.loads(happy_path_port_overrides_payload)),
            ],
        )

        responses.add(mocked_response)
        result, response = unifi_api.update_device(
            device_id="MOCKED_ID", port_overrides=json.loads(happy_path_port_overrides_payload)
        )

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/s/default/rest/device/MOCKED_ID" in logs
        assert "[API] [update_device] MOCKED_ID" in logs
        assert 2 == len(logs)

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert result.data is not None
        assert requests.codes.ok == response.status_code
        assert 1 == mocked_response.call_count

    @responses.activate(registry=OrderedRegistry)
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_reconnect(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_list_all_devices_failed_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json={
                "meta": {
                    "rc": "error",
                    "msg": "api.err.LoginRequired",
                },
                "data": [],
            },
            match=[matchers.header_matcher(response_header)],
            status=requests.codes.unauthorized,
        )

        mocked_login_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[matchers.header_matcher(response_header)],
        )

        mocked_list_all_devices_response = responses.get(
            url=f"{unifi_api.controller_url}{UniFiAPI.STATE_DEVICE_ENDPOINT}",
            json=json.loads(happy_path_devices_json_response),
            match=[matchers.header_matcher(response_header)],
        )

        responses.add(mocked_list_all_devices_failed_response)
        responses.add(mocked_login_response)
        responses.add(mocked_list_all_devices_response)

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
        assert 1 == mocked_list_all_devices_failed_response.call_count
        assert 1 == mocked_login_response.call_count
        assert 1 == mocked_list_all_devices_response.call_count


class TestUnhappyPathUniFiApi:
    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_exception_http_error(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            match=[matchers.header_matcher(response_header)],
            status=requests.codes.bad_gateway,
        )

        responses.add(mocked_response)

        with pytest.raises(SystemExit) as error:
            unifi_api.login()
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] 502 Server Error: Bad Gateway for url: https://unifi.local/api/login" in logs
        assert 1 == len(logs)

    @responses.activate
    @pytest.mark.parametrize("url, port", [("unifi.local", 443)])
    def test_json_decode_error(self, caplog: LogCaptureFixture, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            match=[matchers.header_matcher(response_header)],
            body="INVALID_JSON",
        )

        responses.add(mocked_response)

        with pytest.raises(SystemExit) as error:
            unifi_api.login()
            assert 1 == error.value

        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] JSON decode error. API not available! Shutdown UniFi Tools." in logs
        assert 1 == len(logs)
