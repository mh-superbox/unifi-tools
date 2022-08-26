from argparse import Namespace

from unifi_tools.run import parse_args


class TestHappyPathUniFiTools:
    def test_parse_args(self):
        parser = parse_args(["-c", "/tmp/settings.yml", "-i", "-y"])

        assert "/tmp/settings.yml" == parser.config
        assert True is parser.install
        assert True is parser.yes
        assert isinstance(parser, Namespace)
