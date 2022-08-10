import pytest
import responses
from requests import Response
from responses import matchers

from unifi_tools.config import Config
from unifi_tools.unifi import UniFiAPI
from unifi_tools.unifi import UniFiAPIResult


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
    def test_login(self, caplog, config: Config, url: str, port: int):
        config.unifi_controller.url = url
        config.unifi_controller.port = port

        unifi_api = UniFiAPI(config=config)

        mocked_response = responses.post(
            url=f"{unifi_api.controller_url}{UniFiAPI.LOGIN_ENDPOINT}",
            json={
                "meta": {"rc": "ok"},
                "data": [],
            },
            match=[
                matchers.header_matcher(
                    {
                        "Accept": "application/json",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                )
            ],
        )

        responses.add(mocked_response)
        result, response = unifi_api.login()
        logs: list = [record.getMessage() for record in caplog.records]

        assert "[API] [ok] https://unifi.local/api/login" in logs
        assert "[API] Successfully logged in." in logs
        assert "[API] CSRF Token: None" in logs

        assert isinstance(result, UniFiAPIResult)
        assert isinstance(response, Response)

        assert "ok" == result.meta["rc"]
        assert 200 == response.status_code
        assert 1 == mocked_response.call_count
