#!/usr/bin/env python3

"""
Usage:
    vip.py [--interface=<iface>] [--vip=<ip>] <hook> <role> <scope>

Examples:
    vip.py --interface=eth1 --vip=10.0.0.10 \
        on_role_change master myclustername

Options:
    --interface=<iface>     Network interface to use [default: eth0].
    --vip=<ip>              Virtual IP address to manage [default: 10.38.1.50].
    <hook>                  Possible values: on_reload, on_restart,
                            on_role_change, on_start, on_stop.
    <role>                  Current node role in cluster. Possible values: master, replica.
    <scope>                 Cluster name.
"""

import sys
import logging
from docopt import docopt
from pyroute2 import IPRoute
from pyroute2 import NetlinkError
from scapy.sendrecv import sendp
from scapy.layers.l2 import ARP, Ether

# Default interface and VIP address. These can be overridden via CLI options.
DEFAULT_INTERFACE = 'eth0'
DEFAULT_VIP_ADDRESS = '10.38.1.50'

hooks_list = ['on_role_change', 'on_start', 'on_restart', 'on_stop', 'on_reload']

# Get logger
logger = logging.getLogger('vip')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(name)s: %(asctime)s %(levelname)s: %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)


def ip_addr_manipulation(action, vip_address, interface):
    ip = IPRoute()
    index = ip.link_lookup(ifname=interface)
    if not index:
        logger.error("Network interface {} not found".format(interface))
        ip.close()
        return
    try:
        ip.addr(action, index=index[0], address=vip_address, mask=24)
        if action == 'add':
            logger.info(
                "An ip address {} added to the network interface {}.".format(
                    vip_address, interface))
            sendp(
                Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(psrc=vip_address),
                iface=interface,
                loop=1,
                inter=0,
                count=3,
            )
        else:
            logger.info(
                "An ip address {} removed from the network interface {}.".format(
                    vip_address, interface))
    except NetlinkError as e:
        if action == 'add':
            logger.info(
                "Unable to add an ip address {} to the network interface {}. Already added!".format(
                    vip_address, interface))
        else:
            logger.info(
                "Unable to remove an ip address {} from the network interface {}."
                " Already removed!".format(vip_address, interface)
            )
        logger.info("Netlink error: {}".format(e))
    finally:
        ip.close()


def main():
    args = docopt(__doc__)
    logger.info(
        "hook='{}', role='{}', scope='{}'".format(
            args['<hook>'], args['<role>'], args['<scope>']))

    interface = args['--interface'] or DEFAULT_INTERFACE
    vip_address = args['--vip'] or DEFAULT_VIP_ADDRESS

    if args['<hook>'] in hooks_list and args['<role>'] == 'master' and args['<scope>']:
        ip_addr_manipulation('add', vip_address, interface)

    if args['<hook>'] in hooks_list and args['<role>'] == 'replica' and args['<scope>']:
        ip_addr_manipulation('delete', vip_address, interface)


if __name__ == '__main__':
    main()
