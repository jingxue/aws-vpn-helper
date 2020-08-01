#!/usr/bin/env python3

import argparse
from .helper import EndPointManager


def main():
    parser = argparse.ArgumentParser(description='Prints AWS Client VPN EndPoint Status')
    parser.add_argument('config_section', help='A section name from ~/.aws-vpn.cfg')
    parser.add_argument('--profile', help='The AWS profile')
    parser.add_argument('-a', '--all', dest='all', action='store_true', help='Print all columns')
    _args = parser.parse_args()
    EndPointManager(_args).stat()


if __name__ == '__main__':
    main()
