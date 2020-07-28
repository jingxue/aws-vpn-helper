import os
import configparser
import argparse
import boto3


def read_config(section: str):
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.environ['HOME'], '.aws-vpn.cfg'))
    return cfg[section]


def bring_up(args):
    config = read_config(args.config_section)
    profile = args.profile
    if not profile:
        profile = config.get('profile', None)
    region = config.get('region', None)
    client = boto3.session.Session(region_name=region, profile_name=profile).client('ec2')
    resp = client.describe_client_vpn_target_networks(
        ClientVpnEndpointId=config['endpoint-id'],
        Filters=[{
            'Name': 'target-network-id',
            'Values': [config['subnet-id']]
        }])
    print(resp['ClientVpnTargetNetworks'])


def bring_down(args):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AWS Client VPN EndPoint Manager')
    parser.add_argument('config_section', help='A section name from ~/.aws-vpn.cfg')
    parser.add_argument('action', choices=['up', 'down'], help='The action to take on the endpoint')
    parser.add_argument('--profile', help='The AWS profile')

    _args = parser.parse_args()
    if _args.action == 'up':
        bring_up(_args)
    elif _args.action == 'down':
        bring_down(_args)