""" Test for failure cases """
#pylint: disable=C0326,W0621
from __future__ import unicode_literals
import pytest #pylint: disable=unused-import
from packeteer import packets, fields

# Custom packet classes
class Packet(packets.BigEndian): #pylint: disable=missing-docstring
    fields = [
        fields.UInt8('uint8'),
        fields.Padding(),
        fields.String('string', size=16),
    ]

def test_bad_get_key():
    """ Test fetching a bad key """
    packet = Packet(uint8=42, string='Hello World')
    with pytest.raises(KeyError):
        value = packet['fake_key']
    with pytest.raises(IndexError):
        value = packet[100]
    with pytest.raises(TypeError):
        value = packet[None]

def test_bad_set_key():
    """ Test setting a value from a bad key """
    packet = Packet()
    with pytest.raises(KeyError):
        packet['fake_key'] = 42
    with pytest.raises(IndexError):
        value = packet[100] = 42
    with pytest.raises(TypeError):
        value = packet[None] = 42

def test_bad_set_value():
    """ Test setting an impossible value """
    packet = Packet()
    with pytest.raises(TypeError):
        packet['uint8'] = 65535
    with pytest.raises(TypeError):
        packet['uint8'] = 'foo'
    with pytest.raises(TypeError):
        packet['uint8'] = b'bar'
    with pytest.raises(TypeError):
        packet['uint8'] = Packet()
    with pytest.raises(TypeError):
        packet['uint8'] = [42, 100]

def test_bad_equal():
    """ Test comparing packet equality to bad values """
    packet = Packet()
    #pylint: disable=unneeded-not,superfluous-parens
    assert not (packet == 42)
    #pylint: enable=unneeded-not

def test_bad_unequal():
    """ Test comparing packet inequality to bad values """
    packet = Packet()
    assert packet != 42
