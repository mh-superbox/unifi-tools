#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description="Control UniFi port")
    parser.add_argument("controller", help="hostname or IP address of UniFi Controller")
    parser.add_argument("username", help="username with admin rights on UniFi Controller")
    parser.add_argument("password", help="corresponding password for admin user")
    parser.add_argument("mac", help="MAC address (with or without colons) of switch")
    parser.add_argument("ports", help="port numbers to acquire new state (list separated by comma, e.g., '5,6,7'")
    parser.add_argument("state", help="desired state of PoE ports, e.g., 'auto' or 'off'")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
