# vip-patroni

`vip.py` is a small utility script intended to be used as a Patroni callback. It
assigns or removes a virtual IP address (VIP) on the host running PostgreSQL
when Patroni triggers certain events (for example, a role change during
failover).

## Overview

The script relies on `pyroute2` to manipulate network interfaces and `scapy` to
broadcast ARP packets after the VIP changes. Command line parsing is handled by
`docopt`.

When executed, `vip.py` expects a Patroni hook name, the current node role
(`master` or `replica`) and the cluster scope. Optional arguments allow you to
specify the network interface and VIP without editing the script.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Python 3.8 or newer is recommended.
2. **Run with appropriate privileges**
   Adding or removing IP addresses requires administrative permissions. Test the
   script with sudo:
   ```bash
   sudo python vip.py on_start master mycluster
   ```
   Use `--interface` and `--vip` options to override defaults:
   ```bash
   sudo python vip.py --interface=eth1 --vip=10.0.0.10 on_start master mycluster
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
sudo python vip.py --interface=eth1 --vip=10.0.0.10 on_role_change replica mycluster
```
Check the logs or `ip addr show` to verify that the VIP is added or removed.

## Linting and Tests
Flake8 and pytest can be run locally to check the code style and run the unit
tests. The network operations are mocked so no special privileges are required:
```bash
pip install -r requirements.txt
flake8 vip.py tests

pytest
```

## Troubleshooting
- Ensure the selected network interface exists on your system and that the host
  has permission to modify it.
- ARP broadcast may require additional capabilities; run as root if you see
  permission errors.

## Further Learning
- [pyroute2 documentation](https://github.com/svinota/pyroute2)
- [scapy documentation](https://scapy.readthedocs.io)
- [docopt documentation](https://docopt.org)

## License
This project is licensed under the [MIT License](LICENSE).

