#!/usr/bin/env python3

"""
Usage:
    vip.py <hook> <role> <scope>

Examples:
    vip.py on_role_change master myclustername

Options:
    <hook>                  Possible values: on_reload, on_restart, on_role_change, on_start, on_stop.
    <role>                  Current node role in cluster. Possible values: master, replica.
    <scope>                 Сluster name.
"""

import sys
import logging
from docopt import docopt
from pyroute2 import IPRoute
from pyroute2 import NetlinkError
from scapy.sendrecv import sendp
from scapy.layers.l2 import ARP, Ether

# Set up an interface and a virtual ip address configuration.
# You can set your own ip address and network interface name here.
vm_interface = 'eth0'
vm_vip_address = '10.38.1.50'

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

def ip_addr_manipulation(action, vip_address):
    ip = IPRoute()
    # Get interface name. link_lookup returns a list
    index = ip.link_lookup(ifname=vm_interface)
    if not index:
        logger.info(
            "Interface {} not found. Skipping ip address manipulation.".format(
                vm_interface))
        ip.close()
        return
    try:
        # Assign or remove IP address (vm_vip_address) to/from network interface (vm_interface)
        ip.addr(action, index[0], vip_address, mask=24)
        if action == 'add':
            logger.info(
                "An ip address {} added to the network interface {}.".format(
                    vip_address, vm_interface))
            # If assigned, send arp ping to everyone at Level2
            sendp(
                Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(psrc=vm_vip_address),
                iface=vm_interface,
                loop=1,
                inter=0,
                count=3,
            )
        else:
            logger.info(
                "An ip address {} removed from the network interface {}.".format(vip_address, vm_interface))
    except NetlinkError as e:
        if action == 'add':
            logger.info(
                "Unable to add an ip address {} to the network interface {}. Already added!".format(
                    vip_address, vm_interface))
        else:
            logger.info(
                "Unable to remove an ip address {} from the network interface {}. Already removed!".format(
                    vip_address, vm_interface))
        logger.info("Netlink error: {}".format(e))
    ip.close()

def main():

    args = docopt(__doc__, options_first=True)
    logger.info("hook='{}', role='{}', scope='{}'".format(
        args['<hook>'], args['<role>'], args['<scope>']))

    if args['<hook>'] in hooks_list and args['<role>'] == 'master' and args['<scope>']:
        ip_addr_manipulation('add', vm_vip_address)

    if args['<hook>'] in hooks_list and args['<role>'] == 'replica' and args['<scope>']:
        ip_addr_manipulation('delete', vm_vip_address)

if __name__ == '__main__':
    main()
