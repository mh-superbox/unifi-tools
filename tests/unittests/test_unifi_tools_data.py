from typing import Final

UNIFI_TOOLS_INSTALLER_WITH_ENABLE_SYSTEMD_OUTPUT: Final[
    str
] = """Copy config file to '%s'
Copy systemd service 'unifi-tools.service'
Enable systemd service 'unifi-tools.service'
"""


UNIFI_TOOLS_INSTALLER_WITHOUT_ENABLE_SYSTEMD_OUTPUT: Final[
    str
] = """Copy config file to '%s'
Copy systemd service 'unifi-tools.service'

You can enable the systemd service with the command:
systemctl enable --now unifi-tools
"""

UNIFI_TOOLS_INSTALLER_WITHOUT_OVERWRITE_CONFIG_OUTPUT: Final[
    str
] = """Copy systemd service 'unifi-tools.service'

You can enable the systemd service with the command:
systemctl enable --now unifi-tools
"""
