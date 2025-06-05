# vip-patroni

`vip.py` is a small utility script intended to be used as a Patroni callback. It
assigns or removes a virtual IP address (VIP) on the host running PostgreSQL
when Patroni triggers certain events (for example, a role change during
failover).

## Overview

The script relies on `pyroute2` to manipulate network interfaces and `scapy` to
broadcast ARP packets after the VIP changes. Command line parsing is handled by
`docopt`.

When executed, `vip.py` expects three arguments: the Patroni hook name,
the current node role (`master` or `replica`), and the cluster scope. On master
events it adds the configured VIP, and on replica events it removes it.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Adjust the interface and VIP**
   Edit the variables `vm_interface` and `vm_vip_address` at the top of
   `vip.py` to match your network environment.
3. **Run with appropriate privileges**
   Adding or removing IP addresses requires administrative permissions. Test the
   script with sudo:
   ```bash
   sudo python vip.py on_start master mycluster
   ```

## Integrating with Patroni

Configure Patroni callbacks in your `postgres.yml` (or equivalent) file:
```yaml
callbacks:
  on_role_change: /path/to/vip.py on_role_change
  on_start: /path/to/vip.py on_start
  on_stop: /path/to/vip.py on_stop
```
The path should point to the location of `vip.py` on each node.

## Example Usage
Simulate a role change by calling the script manually:
```bash
sudo python vip.py on_role_change master mycluster
sudo python vip.py on_role_change replica mycluster
```
Check the logs or `ip addr show` to verify that the VIP is added or removed.

## Troubleshooting
- Ensure the selected network interface exists on your system and that the host
  has permission to modify it.
- ARP broadcast may require additional capabilities; run as root if you see
  permission errors.

## Further Learning
- [pyroute2 documentation](https://github.com/svinota/pyroute2)
- [scapy documentation](https://scapy.readthedocs.io)
- [docopt documentation](https://docopt.org)

