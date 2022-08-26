devices_json_response_1: str = """{
    "meta": {
        "rc": "ok"
    },
    "data": [
        {
            "_id": "MOCKED_ID",
            "adopted": true,
            "anomalies": -1,
            "anon_id": "ef1c5fdb-7f24-4806-88d9-76db276a9b01",
            "architecture": "armv7l",
            "board_rev": 8,
            "cfgversion": "9b584e5b55742366",
            "config_network": {
                "type": "dhcp"
            },
            "connected_at": 1659811098,
            "dot1x_portctrl_enabled": false,
            "ethernet_table": [
                {
                    "mac": "b4:fb:e4:b6:6f:12",
                    "num_port": 26,
                    "name": "eth0"
                },
                {
                    "mac": "b4:fb:e4:b6:6f:13",
                    "name": "srv0"
                }
            ],
            "flowctrl_enabled": false,
            "fw_caps": -1488265691,
            "gateway_mac": "00:0d:b9:52:45:50",
            "has_fan": true,
            "has_temperature": true,
            "hash_id": "68d976db276a9b01",
            "hw_caps": 0,
            "inform_ip": "10.10.0.5",
            "inform_url": "http://10.10.0.5:8080/inform",
            "internet": true,
            "ip": "10.10.0.2",
            "jumboframe_enabled": false,
            "kernel_version": "3.6.5",
            "led_override": "on",
            "led_override_color": "#0000FF",
            "led_override_color_brightness": 100,
            "license_state": "registered",
            "mac": "b4:fb:e4:b6:6f:12",
            "manufacturer_id": 2,
            "mgmt_network_id": "6070c964a61f7408a7706056",
            "model": "MOCKED MODEL",
            "model_in_eol": false,
            "model_in_lts": false,
            "model_incompatible": false,
            "name": "MOCKED SWITCH",
            "port_overrides": [
                {
                    "name": "MOCKED Port 1",
                    "port_idx": 1,
                    "poe_mode": "off",
                    "portconf_id": "60c0bdca0da23303beb7f799",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                },
                {
                    "name": "MOCKED Port 2",
                    "port_idx": 2,
                    "poe_mode": "off",
                    "portconf_id": "6070c964a61f7408a770605c",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                },
                {
                    "name": "MOCKED Port 3",
                    "port_idx": 3,
                    "poe_mode": "off",
                    "portconf_id": "6070c964a61f7408a770605a",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                }
            ],
            "port_table": [],
            "power_source_ctrl_enabled": false,
            "provisioned_at": 1660056204,
            "required_version": "4.0.72",
            "satisfaction": 93,
            "serial": "MOCKED SN",
            "setup_id": "db2faf9c-bfc9-4a4d-94c7-42b1c7c8807a",
            "site_id": "MOCKED_SITE_ID",
            "snmp_contact": "",
            "snmp_location": "",
            "stp_priority": "32768",
            "stp_version": "rstp",
            "switch_caps": {
                "feature_caps": 33790,
                "max_mirror_sessions": 1,
                "max_aggregate_sessions": 13,
                "max_l3_intf": 0,
                "max_reserved_routes": 0,
                "max_static_routes": 0
            },
            "sys_error_caps": 0,
            "syslog_key": "b99aa2e7fc09fa7e4579fc4f188d343d44d2016feb8da5fab93ff0137c44ffbe",
            "two_phase_adopt": false,
            "type": "usw",
            "unsupported": false,
            "unsupported_reason": 0,
            "version": "MOCKED 6.2.14.13855",
            "x_aes_gcm": true,
            "x_authkey": "fa2cac41b3392b94ead02f7b19b7dd3c",
            "x_fingerprint": "36:ee:f1:e7:8a:35:74:57:62:20:38:6e:88:a9:ba:49:f7:49:6c:87",
            "x_ssh_hostkey_fingerprint": "ac:18:57:5a:c7:df:b3:91:32:62:65:b0:b5:0e:cf:dd",
            "device_id": "MOCKED_DEVICE_ID",
            "state": 1,
            "start_disconnected_millis": 1659811081133,
            "default": false,
            "discovered_via": "l2",
            "adopt_ip": "10.10.0.2",
            "adopt_url": "http://10.10.0.5:8080/inform",
            "last_seen": 1660156344,
            "min_inform_interval_seconds": 30,
            "upgradable": false,
            "adoptable_when_upgraded": false,
            "rollupgrade": false,
            "known_cfgversion": "9b584e5b55742366",
            "uptime": 9221294,
            "_uptime": 9221294,
            "locating": false,
            "start_connected_millis": 1659811098608,
            "prev_non_busy_state": 5,
            "next_interval": 30,
            "connect_request_ip": "10.10.0.2",
            "connect_request_port": "43193",
            "sys_stats": {
                "loadavg_1": "1.92",
                "loadavg_15": "1.90",
                "loadavg_5": "1.97",
                "mem_buffer": 0,
                "mem_total": 262381568,
                "mem_used": 101146624
            },
            "system-stats": {
                "cpu": "58.6",
                "mem": "38.5",
                "uptime": "9221292"
            },
            "ssh_session_table": [],
            "lldp_table": [],
            "displayable_version": "6.2.14",
            "connection_network_name": "100 Wired",
            "startup_timestamp": 1650935051,
            "is_access_point": false,
            "fan_level": 50,
            "general_temperature": 44,
            "overheating": false,
            "total_max_power": 222,
            "downlink_table": [],
            "uplink": {
                "full_duplex": true,
                "ip": "10.10.0.2",
                "mac": "b4:fb:e4:b6:6f:12",
                "name": "eth0",
                "netmask": "255.255.255.0",
                "num_port": 26,
                "rx_bytes": 197836717150,
                "rx_dropped": 32672,
                "rx_errors": 0,
                "rx_multicast": 0,
                "rx_packets": 191976683,
                "speed": 1000,
                "tx_bytes": 44168593129,
                "tx_dropped": 0,
                "tx_errors": 0,
                "tx_packets": 152092398,
                "up": true,
                "port_idx": 23,
                "media": "GE",
                "max_speed": 1000,
                "type": "wire",
                "tx_bytes-r": 108855,
                "rx_bytes-r": 111289,
                "uplink_source": "legacy"
            },
            "uplink_depth": 1,
            "dhcp_server_table": [],
            "stat": {
                "sw": {
                    "site_id": "6070c958a61f7408a7706045",
                    "o": "sw",
                    "oid": "b4:fb:e4:b6:6f:12",
                    "sw": "b4:fb:e4:b6:6f:12",
                    "time": 1659810900000,
                    "datetime": "2022-08-06T18:35:00Z",
                    "rx_packets": 5.32184491E8,
                    "rx_bytes": 3.65520364634E11,
                    "rx_errors": 2.0,
                    "rx_dropped": 90251.0,
                    "rx_crypts": 0.0,
                    "rx_frags": 0.0,
                    "tx_packets": 5.34546812E8,
                    "tx_bytes": 3.65787119179E11,
                    "tx_errors": 0.0,
                    "tx_dropped": 7986.0,
                    "tx_retries": 0.0,
                    "rx_multicast": 243312.0,
                    "rx_broadcast": 167629.0,
                    "tx_multicast": 2109596.0,
                    "tx_broadcast": 649372.0,
                    "bytes": 7.31307483813E11,
                    "duration": 3.4521E8,
                    "port_1-tx_packets": 252643.0,
                    "port_1-tx_bytes": 2.8950692E7,
                    "port_1-tx_multicast": 162609.0,
                    "port_2-rx_packets": 1091061.0,
                    "port_2-rx_bytes": 3.45292656E8,
                    "port_2-rx_dropped": 11380.0,
                    "port_2-tx_packets": 1712177.0,
                    "port_2-tx_bytes": 1.80328541E8,
                    "port_2-rx_multicast": 14208.0,
                    "port_2-tx_multicast": 248062.0,
                    "port_2-tx_broadcast": 20618.0,
                    "port_15-rx_packets": 1.8298847E8,
                    "port_15-rx_bytes": 3.1716781209E10,
                    "port_15-tx_packets": 1.71216353E8,
                    "port_15-tx_bytes": 2.37528449442E11,
                    "port_15-rx_multicast": 11952.0,
                    "port_15-tx_multicast": 116298.0,
                    "port_15-tx_broadcast": 9505.0,
                    "port_17-rx_packets": 5562600.0,
                    "port_17-rx_bytes": 3.922492626E9,
                    "port_17-rx_dropped": 17072.0,
                    "port_17-tx_packets": 3861188.0,
                    "port_17-tx_bytes": 5.81183863E8,
                    "port_17-rx_multicast": 25574.0,
                    "port_17-rx_broadcast": 97894.0,
                    "port_17-tx_multicast": 216275.0,
                    "port_18-rx_packets": 7.8471511E7,
                    "port_18-rx_bytes": 3.5752637412E10,
                    "port_18-rx_dropped": 17070.0,
                    "port_18-tx_packets": 7.9941617E7,
                    "port_18-tx_bytes": 3.6065099519E10,
                    "port_18-rx_multicast": 38475.0,
                    "port_18-tx_multicast": 229484.0,
                    "port_18-tx_broadcast": 20428.0,
                    "port_19-rx_packets": 1603528.0,
                    "port_19-rx_bytes": 1.83256589E8,
                    "port_19-tx_packets": 2344967.0,
                    "port_19-tx_bytes": 2.67304486E8,
                    "port_19-tx_multicast": 224649.0,
                    "port_19-tx_broadcast": 129688.0,
                    "port_21-rx_packets": 25332.0,
                    "port_21-rx_bytes": 2761733.0,
                    "port_21-tx_packets": 212727.0,
                    "port_21-tx_bytes": 4.7317433E7,
                    "port_21-rx_multicast": 4175.0,
                    "port_21-tx_multicast": 139580.0,
                    "port_21-tx_broadcast": 47413.0,
                    "port_23-rx_packets": 1.19441433E8,
                    "port_23-rx_bytes": 1.03013291414E11,
                    "port_23-rx_dropped": 11380.0,
                    "port_23-tx_packets": 1.08950803E8,
                    "port_23-tx_bytes": 3.7588998761E10,
                    "port_23-rx_multicast": 92316.0,
                    "port_23-tx_multicast": 282028.0,
                    "port_23-tx_broadcast": 131187.0,
                    "port_24-rx_packets": 1.35340937E8,
                    "port_24-rx_bytes": 1.89876174838E11,
                    "port_24-rx_dropped": 22760.0,
                    "port_24-tx_packets": 1.51593354E8,
                    "port_24-tx_bytes": 3.2680110024E10,
                    "port_24-rx_multicast": 37290.0,
                    "port_24-tx_multicast": 277156.0,
                    "port_24-tx_broadcast": 137882.0,
                    "port_1-rx_packets": 49345.0,
                    "port_1-rx_bytes": 7050393.0,
                    "port_1-rx_multicast": 573.0,
                    "port_17-tx_broadcast": 31794.0,
                    "port_24-rx_broadcast": 12451.0,
                    "port_15-rx_broadcast": 1300.0,
                    "port_21-rx_broadcast": 465.0,
                    "port_21-rx_dropped": 3537.0,
                    "port_18-rx_broadcast": 217.0,
                    "port_19-rx_multicast": 127.0,
                    "port_18-tx_dropped": 7495.0,
                    "port_3-tx_packets": 964.0,
                    "port_3-tx_bytes": 206966.0,
                    "port_3-tx_multicast": 572.0,
                    "port_3-tx_broadcast": 44.0,
                    "port_3-rx_packets": 532.0,
                    "port_3-rx_bytes": 139572.0,
                    "port_3-rx_multicast": 97.0,
                    "port_3-rx_broadcast": 46.0,
                    "port_1-tx_broadcast": 46383.0,
                    "port_23-rx_broadcast": 45691.0,
                    "port_3-rx_dropped": 4.0,
                    "port_11-tx_packets": 1504042.0,
                    "port_11-tx_bytes": 1.829192668E9,
                    "port_11-tx_multicast": 123309.0,
                    "port_11-tx_broadcast": 23144.0,
                    "port_11-rx_packets": 1391483.0,
                    "port_11-rx_bytes": 1.61083574E8,
                    "port_11-rx_broadcast": 3700.0,
                    "port_11-rx_dropped": 3153.0,
                    "port_11-rx_multicast": 4125.0,
                    "port_15-rx_dropped": 26.0,
                    "port_1-rx_broadcast": 3055.0,
                    "port_1-rx_dropped": 12.0,
                    "port_16-tx_packets": 203280.0,
                    "port_16-tx_bytes": 2.9818516E7,
                    "port_16-tx_multicast": 37192.0,
                    "port_16-rx_packets": 158210.0,
                    "port_16-rx_bytes": 8.8962569E7,
                    "port_16-rx_multicast": 1567.0,
                    "port_16-rx_broadcast": 1689.0,
                    "port_16-tx_broadcast": 11702.0,
                    "port_2-rx_broadcast": 27.0,
                    "port_4-tx_packets": 1.266206E7,
                    "port_4-tx_bytes": 1.8949027308E10,
                    "port_4-tx_multicast": 26566.0,
                    "port_6-tx_packets": 90637.0,
                    "port_6-tx_bytes": 1.113096E7,
                    "port_6-tx_multicast": 25816.0,
                    "port_4-rx_packets": 5976115.0,
                    "port_4-rx_bytes": 4.40571279E8,
                    "port_4-rx_multicast": 5522.0,
                    "port_4-rx_broadcast": 1044.0,
                    "port_4-rx_dropped": 903.0,
                    "port_6-rx_packets": 83934.0,
                    "port_6-rx_bytes": 9868770.0,
                    "port_6-rx_multicast": 7311.0,
                    "port_4-tx_broadcast": 18979.0,
                    "port_6-rx_broadcast": 50.0,
                    "port_6-tx_broadcast": 20605.0,
                    "port_6-rx_dropped": 2930.0,
                    "port_16-rx_dropped": 24.0,
                    "port_4-rx_errors": 1.0,
                    "port_15-tx_dropped": 190.0,
                    "port_24-tx_dropped": 301.0,
                    "port_21-rx_errors": 1.0
                }
            },
            "tx_bytes": 197836717150,
            "rx_bytes": 44168593129,
            "bytes": 242005310279,
            "num_sta": 9,
            "user-num_sta": 9,
            "guest-num_sta": 0,
            "x_has_ssh_hostkey": true
        }
    ]
}"""

devices_json_response_2: str = """{
    "meta": {
        "rc": "ok"
    },
    "data": [
        {
            "_id": "MOCKED_ID",
            "adopted": true,
            "anomalies": -1,
            "anon_id": "ef1c5fdb-7f24-4806-88d9-76db276a9b01",
            "architecture": "armv7l",
            "board_rev": 8,
            "cfgversion": "9b584e5b55742366",
            "config_network": {
                "type": "dhcp"
            },
            "connected_at": 1659811098,
            "dot1x_portctrl_enabled": false,
            "ethernet_table": [
                {
                    "mac": "b4:fb:e4:b6:6f:12",
                    "num_port": 26,
                    "name": "eth0"
                },
                {
                    "mac": "b4:fb:e4:b6:6f:13",
                    "name": "srv0"
                }
            ],
            "flowctrl_enabled": false,
            "fw_caps": -1488265691,
            "gateway_mac": "00:0d:b9:52:45:50",
            "has_fan": true,
            "has_temperature": true,
            "hash_id": "68d976db276a9b01",
            "hw_caps": 0,
            "inform_ip": "10.10.0.5",
            "inform_url": "http://10.10.0.5:8080/inform",
            "internet": true,
            "ip": "10.10.0.2",
            "jumboframe_enabled": false,
            "kernel_version": "3.6.5",
            "led_override": "on",
            "led_override_color": "#0000FF",
            "led_override_color_brightness": 100,
            "license_state": "registered",
            "mac": "b4:fb:e4:b6:6f:12",
            "manufacturer_id": 2,
            "mgmt_network_id": "6070c964a61f7408a7706056",
            "model": "MOCKED MODEL",
            "model_in_eol": false,
            "model_in_lts": false,
            "model_incompatible": false,
            "name": "MOCKED SWITCH",
            "port_overrides": [
                {
                    "name": "MOCKED Port 1",
                    "port_idx": 1,
                    "poe_mode": "auto",
                    "portconf_id": "60c0bdca0da23303beb7f799",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                },
                {
                    "name": "MOCKED Port 2",
                    "port_idx": 2,
                    "poe_mode": "off",
                    "portconf_id": "6070c964a61f7408a770605c",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                },
                {
                    "name": "MOCKED Port 3",
                    "port_idx": 3,
                    "poe_mode": "off",
                    "portconf_id": "6070c964a61f7408a770605a",
                    "port_security_mac_address": [],
                    "stp_port_mode": true,
                    "autoneg": true,
                    "port_security_enabled": false
                }
            ],
            "port_table": [],
            "power_source_ctrl_enabled": false,
            "provisioned_at": 1660056204,
            "required_version": "4.0.72",
            "satisfaction": 93,
            "serial": "MOCKED SN",
            "setup_id": "db2faf9c-bfc9-4a4d-94c7-42b1c7c8807a",
            "site_id": "MOCKED_SITE_ID",
            "snmp_contact": "",
            "snmp_location": "",
            "stp_priority": "32768",
            "stp_version": "rstp",
            "switch_caps": {
                "feature_caps": 33790,
                "max_mirror_sessions": 1,
                "max_aggregate_sessions": 13,
                "max_l3_intf": 0,
                "max_reserved_routes": 0,
                "max_static_routes": 0
            },
            "sys_error_caps": 0,
            "syslog_key": "b99aa2e7fc09fa7e4579fc4f188d343d44d2016feb8da5fab93ff0137c44ffbe",
            "two_phase_adopt": false,
            "type": "usw",
            "unsupported": false,
            "unsupported_reason": 0,
            "version": "MOCKED 6.2.14.13855",
            "x_aes_gcm": true,
            "x_authkey": "fa2cac41b3392b94ead02f7b19b7dd3c",
            "x_fingerprint": "36:ee:f1:e7:8a:35:74:57:62:20:38:6e:88:a9:ba:49:f7:49:6c:87",
            "x_ssh_hostkey_fingerprint": "ac:18:57:5a:c7:df:b3:91:32:62:65:b0:b5:0e:cf:dd",
            "device_id": "MOCKED_DEVICE_ID",
            "state": 1,
            "start_disconnected_millis": 1659811081133,
            "default": false,
            "discovered_via": "l2",
            "adopt_ip": "10.10.0.2",
            "adopt_url": "http://10.10.0.5:8080/inform",
            "last_seen": 1660156344,
            "min_inform_interval_seconds": 30,
            "upgradable": false,
            "adoptable_when_upgraded": false,
            "rollupgrade": false,
            "known_cfgversion": "9b584e5b55742366",
            "uptime": 9221294,
            "_uptime": 9221294,
            "locating": false,
            "start_connected_millis": 1659811098608,
            "prev_non_busy_state": 5,
            "next_interval": 30,
            "connect_request_ip": "10.10.0.2",
            "connect_request_port": "43193",
            "sys_stats": {
                "loadavg_1": "1.92",
                "loadavg_15": "1.90",
                "loadavg_5": "1.97",
                "mem_buffer": 0,
                "mem_total": 262381568,
                "mem_used": 101146624
            },
            "system-stats": {
                "cpu": "58.6",
                "mem": "38.5",
                "uptime": "9221292"
            },
            "ssh_session_table": [],
            "lldp_table": [],
            "displayable_version": "6.2.14",
            "connection_network_name": "100 Wired",
            "startup_timestamp": 1650935051,
            "is_access_point": false,
            "fan_level": 50,
            "general_temperature": 44,
            "overheating": false,
            "total_max_power": 222,
            "downlink_table": [],
            "uplink": {
                "full_duplex": true,
                "ip": "10.10.0.2",
                "mac": "b4:fb:e4:b6:6f:12",
                "name": "eth0",
                "netmask": "255.255.255.0",
                "num_port": 26,
                "rx_bytes": 197836717150,
                "rx_dropped": 32672,
                "rx_errors": 0,
                "rx_multicast": 0,
                "rx_packets": 191976683,
                "speed": 1000,
                "tx_bytes": 44168593129,
                "tx_dropped": 0,
                "tx_errors": 0,
                "tx_packets": 152092398,
                "up": true,
                "port_idx": 23,
                "media": "GE",
                "max_speed": 1000,
                "type": "wire",
                "tx_bytes-r": 108855,
                "rx_bytes-r": 111289,
                "uplink_source": "legacy"
            },
            "uplink_depth": 1,
            "dhcp_server_table": [],
            "stat": {
                "sw": {
                    "site_id": "6070c958a61f7408a7706045",
                    "o": "sw",
                    "oid": "b4:fb:e4:b6:6f:12",
                    "sw": "b4:fb:e4:b6:6f:12",
                    "time": 1659810900000,
                    "datetime": "2022-08-06T18:35:00Z",
                    "rx_packets": 5.32184491E8,
                    "rx_bytes": 3.65520364634E11,
                    "rx_errors": 2.0,
                    "rx_dropped": 90251.0,
                    "rx_crypts": 0.0,
                    "rx_frags": 0.0,
                    "tx_packets": 5.34546812E8,
                    "tx_bytes": 3.65787119179E11,
                    "tx_errors": 0.0,
                    "tx_dropped": 7986.0,
                    "tx_retries": 0.0,
                    "rx_multicast": 243312.0,
                    "rx_broadcast": 167629.0,
                    "tx_multicast": 2109596.0,
                    "tx_broadcast": 649372.0,
                    "bytes": 7.31307483813E11,
                    "duration": 3.4521E8,
                    "port_1-tx_packets": 252643.0,
                    "port_1-tx_bytes": 2.8950692E7,
                    "port_1-tx_multicast": 162609.0,
                    "port_2-rx_packets": 1091061.0,
                    "port_2-rx_bytes": 3.45292656E8,
                    "port_2-rx_dropped": 11380.0,
                    "port_2-tx_packets": 1712177.0,
                    "port_2-tx_bytes": 1.80328541E8,
                    "port_2-rx_multicast": 14208.0,
                    "port_2-tx_multicast": 248062.0,
                    "port_2-tx_broadcast": 20618.0,
                    "port_15-rx_packets": 1.8298847E8,
                    "port_15-rx_bytes": 3.1716781209E10,
                    "port_15-tx_packets": 1.71216353E8,
                    "port_15-tx_bytes": 2.37528449442E11,
                    "port_15-rx_multicast": 11952.0,
                    "port_15-tx_multicast": 116298.0,
                    "port_15-tx_broadcast": 9505.0,
                    "port_17-rx_packets": 5562600.0,
                    "port_17-rx_bytes": 3.922492626E9,
                    "port_17-rx_dropped": 17072.0,
                    "port_17-tx_packets": 3861188.0,
                    "port_17-tx_bytes": 5.81183863E8,
                    "port_17-rx_multicast": 25574.0,
                    "port_17-rx_broadcast": 97894.0,
                    "port_17-tx_multicast": 216275.0,
                    "port_18-rx_packets": 7.8471511E7,
                    "port_18-rx_bytes": 3.5752637412E10,
                    "port_18-rx_dropped": 17070.0,
                    "port_18-tx_packets": 7.9941617E7,
                    "port_18-tx_bytes": 3.6065099519E10,
                    "port_18-rx_multicast": 38475.0,
                    "port_18-tx_multicast": 229484.0,
                    "port_18-tx_broadcast": 20428.0,
                    "port_19-rx_packets": 1603528.0,
                    "port_19-rx_bytes": 1.83256589E8,
                    "port_19-tx_packets": 2344967.0,
                    "port_19-tx_bytes": 2.67304486E8,
                    "port_19-tx_multicast": 224649.0,
                    "port_19-tx_broadcast": 129688.0,
                    "port_21-rx_packets": 25332.0,
                    "port_21-rx_bytes": 2761733.0,
                    "port_21-tx_packets": 212727.0,
                    "port_21-tx_bytes": 4.7317433E7,
                    "port_21-rx_multicast": 4175.0,
                    "port_21-tx_multicast": 139580.0,
                    "port_21-tx_broadcast": 47413.0,
                    "port_23-rx_packets": 1.19441433E8,
                    "port_23-rx_bytes": 1.03013291414E11,
                    "port_23-rx_dropped": 11380.0,
                    "port_23-tx_packets": 1.08950803E8,
                    "port_23-tx_bytes": 3.7588998761E10,
                    "port_23-rx_multicast": 92316.0,
                    "port_23-tx_multicast": 282028.0,
                    "port_23-tx_broadcast": 131187.0,
                    "port_24-rx_packets": 1.35340937E8,
                    "port_24-rx_bytes": 1.89876174838E11,
                    "port_24-rx_dropped": 22760.0,
                    "port_24-tx_packets": 1.51593354E8,
                    "port_24-tx_bytes": 3.2680110024E10,
                    "port_24-rx_multicast": 37290.0,
                    "port_24-tx_multicast": 277156.0,
                    "port_24-tx_broadcast": 137882.0,
                    "port_1-rx_packets": 49345.0,
                    "port_1-rx_bytes": 7050393.0,
                    "port_1-rx_multicast": 573.0,
                    "port_17-tx_broadcast": 31794.0,
                    "port_24-rx_broadcast": 12451.0,
                    "port_15-rx_broadcast": 1300.0,
                    "port_21-rx_broadcast": 465.0,
                    "port_21-rx_dropped": 3537.0,
                    "port_18-rx_broadcast": 217.0,
                    "port_19-rx_multicast": 127.0,
                    "port_18-tx_dropped": 7495.0,
                    "port_3-tx_packets": 964.0,
                    "port_3-tx_bytes": 206966.0,
                    "port_3-tx_multicast": 572.0,
                    "port_3-tx_broadcast": 44.0,
                    "port_3-rx_packets": 532.0,
                    "port_3-rx_bytes": 139572.0,
                    "port_3-rx_multicast": 97.0,
                    "port_3-rx_broadcast": 46.0,
                    "port_1-tx_broadcast": 46383.0,
                    "port_23-rx_broadcast": 45691.0,
                    "port_3-rx_dropped": 4.0,
                    "port_11-tx_packets": 1504042.0,
                    "port_11-tx_bytes": 1.829192668E9,
                    "port_11-tx_multicast": 123309.0,
                    "port_11-tx_broadcast": 23144.0,
                    "port_11-rx_packets": 1391483.0,
                    "port_11-rx_bytes": 1.61083574E8,
                    "port_11-rx_broadcast": 3700.0,
                    "port_11-rx_dropped": 3153.0,
                    "port_11-rx_multicast": 4125.0,
                    "port_15-rx_dropped": 26.0,
                    "port_1-rx_broadcast": 3055.0,
                    "port_1-rx_dropped": 12.0,
                    "port_16-tx_packets": 203280.0,
                    "port_16-tx_bytes": 2.9818516E7,
                    "port_16-tx_multicast": 37192.0,
                    "port_16-rx_packets": 158210.0,
                    "port_16-rx_bytes": 8.8962569E7,
                    "port_16-rx_multicast": 1567.0,
                    "port_16-rx_broadcast": 1689.0,
                    "port_16-tx_broadcast": 11702.0,
                    "port_2-rx_broadcast": 27.0,
                    "port_4-tx_packets": 1.266206E7,
                    "port_4-tx_bytes": 1.8949027308E10,
                    "port_4-tx_multicast": 26566.0,
                    "port_6-tx_packets": 90637.0,
                    "port_6-tx_bytes": 1.113096E7,
                    "port_6-tx_multicast": 25816.0,
                    "port_4-rx_packets": 5976115.0,
                    "port_4-rx_bytes": 4.40571279E8,
                    "port_4-rx_multicast": 5522.0,
                    "port_4-rx_broadcast": 1044.0,
                    "port_4-rx_dropped": 903.0,
                    "port_6-rx_packets": 83934.0,
                    "port_6-rx_bytes": 9868770.0,
                    "port_6-rx_multicast": 7311.0,
                    "port_4-tx_broadcast": 18979.0,
                    "port_6-rx_broadcast": 50.0,
                    "port_6-tx_broadcast": 20605.0,
                    "port_6-rx_dropped": 2930.0,
                    "port_16-rx_dropped": 24.0,
                    "port_4-rx_errors": 1.0,
                    "port_15-tx_dropped": 190.0,
                    "port_24-tx_dropped": 301.0,
                    "port_21-rx_errors": 1.0
                }
            },
            "tx_bytes": 197836717150,
            "rx_bytes": 44168593129,
            "bytes": 242005310279,
            "num_sta": 9,
            "user-num_sta": 9,
            "guest-num_sta": 0,
            "x_has_ssh_hostkey": true
        }
    ]
}"""

port_overrides_payload: str = """{
    "port_overrides": [
        {
            "name": "MOCKED Port 1",
            "port_idx": 1,
            "poe_mode": "auto",
            "portconf_id": "60c0bdca0da23303beb7f799",
            "port_security_mac_address": [],
            "stp_port_mode": true,
            "autoneg": true,
            "port_security_enabled": false
        },
        {
            "name": "MOCKED Port 2",
            "port_idx": 2,
            "poe_mode": "off",
            "portconf_id": "6070c964a61f7408a770605c",
            "port_security_mac_address": [],
            "stp_port_mode": true,
            "autoneg": true,
            "port_security_enabled": false
        },
        {
            "name": "MOCKED Port 3",
            "port_idx": 3,
            "poe_mode": "off",
            "portconf_id": "6070c964a61f7408a770605a",
            "port_security_mac_address": [],
            "stp_port_mode": true,
            "autoneg": true,
            "port_security_enabled": false
        }
    ]
}"""