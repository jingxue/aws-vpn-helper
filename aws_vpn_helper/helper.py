import os
import time
import configparser
import argparse
import boto3


class EndPointManager:
    def __init__(self, args):
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(os.environ['HOME'], '.aws-vpn.cfg'))
        self.config = cfg[args.config_section]
        profile = args.profile
        if not profile:
            profile = self.config.get('profile', None)
        region = self.config.get('region', None)
        self._client = boto3.session.Session(region_name=region, profile_name=profile).client('ec2')
        self.__endpoint_id = self.config['endpoint-id']
        self.__subnet_id = self.config['subnet-id']

    def bring_up(self):
        existing = self._get_target_networks(self.__endpoint_id, self.__subnet_id)
        proceed = True
        if existing:
            if existing['Status']['Code'] == 'associated':
                print(f'Endpoint {self.__endpoint_id} is already associated with subnet {self.__subnet_id} and ready to use')
                proceed = False
            elif existing['Status']['Code'] == 'associating':
                print(f'Endpoint {existing["ClientVpnEndpointId"]} is in the process of being associated to'
                      + f' subnet {existing["TargetNetworkId"]}')
                proceed = False
            elif existing['Status']['Code'] == 'association-failed':
                print(f'Endpoint {self.__endpoint_id} failed to associate with subnet {self.__subnet_id} from a previous attempt.')
                proceed = False
        if not proceed:
            return

        resp = self._client.associate_client_vpn_target_network(
            ClientVpnEndpointId=self.__endpoint_id,
            SubnetId=self.__subnet_id)
        if self.config.getboolean('internet-access', False):
            print(f'Creating route for Internet access.')
            self._client.create_client_vpn_route(
                ClientVpnEndpointId=self.__endpoint_id,
                DestinationCidrBlock='0.0.0.0/0',
                TargetVpcSubnetId=self.__subnet_id,
                Description='Internet Access')
        print(f'Association {resp["AssociationId"]} is being established. This may take a few minutes.')
        self._show_progress()
        while proceed:
            time.sleep(10)
            existing = self._get_target_networks(self.__endpoint_id, self.__subnet_id)
            if existing:
                if existing['Status']['Code'] == 'associated':
                    print(f'\nEndpoint {self.__endpoint_id} has become associated with subnet {self.__subnet_id} and ready to use')
                    proceed = False
                elif existing['Status']['Code'] == 'associating':
                    self._show_progress()
                elif existing['Status']['Code'] == 'association-failed':
                    print(f'\nEndpoint {self.__endpoint_id} failed to associate with subnet {self.__subnet_id}.')
                    proceed = False
        print()

    def bring_down(self):
        existing = self._get_target_networks(self.__endpoint_id, self.__subnet_id)
        if not existing or existing['Status']['Code'] in ('association-failed', 'disassociated'):
            print(f'Endpoint {self.__endpoint_id} is not associated with subnet {self.__subnet_id}. No further actions are needed.')
            return

        self._client.disassociate_client_vpn_target_network(
            ClientVpnEndpointId=self.__endpoint_id,
            AssociationId=existing['AssociationId'])
        print(f'Disassociating {existing["AssociationId"]}. This may take a few minutes.')
        while existing and existing['Status']['Code'] != 'disassociated':
            self._show_progress()
            time.sleep(10)
            existing = self._get_target_networks(self.__endpoint_id, self.__subnet_id)
        print()

    def _get_target_networks(self, endpoint_id, subnet_id):
        resp = self._client.describe_client_vpn_target_networks(
            ClientVpnEndpointId=endpoint_id,
            Filters=[{
                'Name': 'target-network-id',
                'Values': [subnet_id]
            }])
        return resp['ClientVpnTargetNetworks'][0] if len(resp['ClientVpnTargetNetworks']) > 0 else None

    @staticmethod
    def _show_progress():
        print('.', end='', flush=True)

