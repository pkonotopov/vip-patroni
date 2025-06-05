import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import vip

class DummyIP:
    def __init__(self):
        self.addr_calls = []
        self.closed = False

    def link_lookup(self, ifname=None):
        return [1] if ifname == 'eth0' else []

    def addr(self, action, index, address, mask=24):
        self.addr_calls.append((action, index, address, mask))

    def close(self):
        self.closed = True

@mock.patch('vip.IPRoute', return_value=DummyIP())
@mock.patch('vip.sendp')
def test_add_ip(mock_sendp, mock_iproute):
    vip.ip_addr_manipulation('add', '10.0.0.10', 'eth0')
    ip = mock_iproute.return_value
    assert ip.addr_calls == [('add', 1, '10.0.0.10', 24)]
    mock_sendp.assert_called_once()
    assert ip.closed

@mock.patch('vip.IPRoute', return_value=DummyIP())
@mock.patch('vip.sendp')
def test_delete_ip(mock_sendp, mock_iproute):
    vip.ip_addr_manipulation('delete', '10.0.0.10', 'eth0')
    ip = mock_iproute.return_value
    assert ip.addr_calls == [('delete', 1, '10.0.0.10', 24)]
    mock_sendp.assert_not_called()
    assert ip.closed

@mock.patch('vip.IPRoute', return_value=DummyIP())
@mock.patch('vip.sendp')
def test_interface_missing(mock_sendp, mock_iproute, capsys):
    vip.ip_addr_manipulation('add', '10.0.0.10', 'wrong0')
    ip = mock_iproute.return_value
    assert ip.addr_calls == []
    mock_sendp.assert_not_called()
    assert ip.closed
