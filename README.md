[![license-url](https://img.shields.io/npm/l/make-coverage-badge.svg)](https://opensource.org/licenses/MIT)
![coverage-badge](https://raw.githubusercontent.com/mh-superbox/unifi-tools/main/coverage.svg)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)

# UniFi Tools

Control UniFi devices with MQTT commands. Optionally you can enable the Home Assistant MQTT discovery for binary sensors, switches.

**Supported features:**

* Turn on/off PoE for UniFi switch ports (Switch in Home Assistant)
* Get the PoE modes from UniFi switch ports (Binary sensor in Home Assistant)

## Installation

**Requirements:**

* Python 3.8

### From GIT

```shell
$ sudo -i
$ cd /opt
$ git clone https://github.com/mh-superbox/unifi-tools.git
$ pip install -e /opt/unifi-tools
$ unifi-tools --install
```

### From PyPi

```shell
$ sudo -i
$ pip install unifi-tools
$ unifi-tools --install
```

## Arguments

| Argument    | Description                                                           |
|-------------|-----------------------------------------------------------------------|
| `--install` | install unifi tools                                                   |
| `--yes`     | automatic yes to install prompts                                      |
| `-v`        | verbose mode: multiple -v options increase the verbosity (maximum: 4) |

## Configuration

You can set the settings in the `/etc/unifi/settings.yaml`.


### Device

| Key           | Value                                                                          |
|---------------|--------------------------------------------------------------------------------|
| `device_name` | The device name for the subscribe and publish topics. Default is the hostname. |

```yaml
# settings.yaml
device_info:
  mame: UniFi
```

### MQTT

| Key                  | Value                                                                                                                                                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `host`               | The hostname or IP address of the remote broker: Default is `localhost`.                                                                                                                                                |
| `port`               | The network port of the server host to connect to. Defaults is `1883`.                                                                                                                                                  |
| `keepalive`          | Maximum period in seconds allowed between communications with the broker. If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker. Default tis `15`. |
| `retry_limit`        | Number of attempts to connect to the MQTT broker. Default to `30` (Disable with `False`).                                                                                                                               |
| `reconnect_interval` | Time between connection attempts. Default is `10`.                                                                                                                                                                      |

```yaml
# settings.yaml
mqtt:
  host: localhost
  port: 1883
  connection:
    keepalive: 15
    retry_limit: 30
    reconnect_interval: 10
```

### Home Assistant

| Key                | Value                                                           |
|--------------------|-----------------------------------------------------------------|
| `enabled`          | Enable Home Assistant MQTT Discovery. Default is `true`.        |
| `discovery_prefix` | The prefix for the discovery topic. Default is `homeassistant`. |

```yaml
# settings.yaml
homeassistant:
  enabled: true
  discovery_prefix: homeassistant
```

### UniFi Controller


| Key        | Value                                                                            |
|------------|----------------------------------------------------------------------------------|
| `url`      | URL to the UniFi controller                                                      |
| `port`     | The network port of the unifi controller host to connect to. Defaults is `8443`. |
| `username` | Username for the unifi controller user.                                          |
| `password` | Password for the unifi controller user.                                          |

```yaml
# settings.yaml
unifi_controller:
  url: localhost
  port: 8443
  username: username
  password: password
```


### Features

In features section you can define the PoE mode for a port from a UniFi switch.
The UniFi switch is defined with its unique ID.

| Key        | Value                        |
|------------|------------------------------|
| `port_idx` | Port number                  |
| `poe_mode` | PoE mode (`pasv24`or `auto`) |

```yaml
# settings.yaml
features:
  6070cd81a61f7408a770607c:
    ports:
      - port_idx: 1
        poe_mode: pasv24
```


### Logging

| Key     | Value                                                                  |
|---------|------------------------------------------------------------------------|
| `level` | Set level to `debug`, `info`, `warning` or `error`. Default is `info`. |

```yaml
# settings.yaml
logging:
  level: info
```

## Usage

Available MQTT topics:

### Features

| Topic                                                 | Description                                                                                                                    |
|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `[device_name]/UNIQUE-UNIFI-SWITCH-ID-port-[1-x]/get` | Get a JSON string with port settings from this topic.                                                                          |
| `[device_name]/UNIQUE-UNIFI-SWITCH-ID-port-[1-x]/set` | Send a string with the value `{"poe_mode": "on"}` or `{"poe_mode": "off"}` to this topic. This enable or disable the PoE mode. |

## TODO

* Support to change UniFi switch port profile.
