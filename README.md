# Unifi Tools

Control UniFi devices with MQTT commands. Optionally you can enable the Home Assistant MQTT discovery for binary sensors, switches.

**Supported features:**

* Turn on/off PoE for UniFi switch ports (Switch in Home Assistant)
* Get the PoE states from UniFi switch ports (Binary sensor in Home Assistant)

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

| Argument    | Description                      |
|-------------|----------------------------------|
| `--install` | install unifi tools              |
| `--yes`     | automatic yes to install prompts |

## Configuration

You can set the settings in the `/etc/unifi/settings.yaml`.


### Device

| Key           | Value                                                                          |
|---------------|--------------------------------------------------------------------------------|
| `device_name` | The device name for the subscribe and publish topics. Default is the hostname. |

```yaml
# control.yaml
device_name: UniFi
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
# control.yaml
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
# control.yaml
homeassistant:
  enabled: true
  discovery_prefix: homeassistant
```

### UniFi Controller

WIP

### Features

WIP

### Logging

| Key     | Value                                                                  |
|---------|------------------------------------------------------------------------|
| `level` | Set level to `debug`, `info`, `warning` or `error`. Default is `info`. |

```yaml
# control.yaml
logging:
  level: info
```

## Usage

Available MQTT topics:

## TODO

* Support for to change UniFi switch port profile
