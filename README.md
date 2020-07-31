
Create ~/.aws-vpn.cfg that looks like this:
```
[tokyo]
region=ap-northeast-1
endpoint-id=cvpn-endpoint-xxxxxxxxxxx
subnet-id=subnet-xxxxxxxxxxx
internet-access=on
```
If your endpoint is set up for accessing the VPC only, set `internet-access` to `off`.

To bring up the endpoint, execute:
`python3 -m aws_vpn_helper.bring tokyo up`
It usually takes a few minutes to complete the association process.
After that connect to the VPN using your usual VPN client.
When you are done, execute:
`python3 -m aws_vpn_helper.bring tokyo down`
