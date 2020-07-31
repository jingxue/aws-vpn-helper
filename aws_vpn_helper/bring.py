#!/usr/bin/env python3

import argparse
from .helper import EndPointManager


def main():
    parser = argparse.ArgumentParser(description='AWS Client VPN EndPoint Manager')
    parser.add_argument('config_section', help='A section name from ~/.aws-vpn.cfg')
    parser.add_argument('action', choices=['up', 'down'], help='The action to take on the endpoint')
    parser.add_argument('--profile', help='The AWS profile')
    _args = parser.parse_args()
    if _args.action == 'up':
        EndPointManager(_args).bring_up()
    elif _args.action == 'down':
        EndPointManager(_args).bring_down()


if __name__ == '__main__':
    main()
