""" Testing complex packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import pytest #pylint: disable=unused-import
from tests.values.simple import good_values #pylint: disable=unused-import
from packeteer import packets, fields


# Packet classes
class Packet(packets.BigEndian):
    """ Padding Data Packet (Big Endian) """
    fields = [
        fields.Padding(),
        fields.UInt8('first'),
        fields.Padding(),
        fields.UInt8('second'),
        fields.Padding(default=b'\xa0')
    ]

def pack_params(value):
    """ Pack padding data parameters independently """
    packed =  struct.pack(u'>xBxBx', value, value)
    packed = packed[:-1] + b'\xa0'
    return packed

### TESTS ###
# Initializing tests
def test_padding_init(good_values):
    """ Test initializing field values """
    value = good_values['uint8']
    packet = Packet(first=value, second=value)
    assert packet.size()      == 5
    assert len(packet.keys()) == 2
    assert packet[0]          == value
    assert packet[1]          == value
    assert packet.pack()      == pack_params(value)

def test_padding_from_raw(good_values):
    """ Test from_raw() initializing field values """
    value = good_values['uint8']
    packed = pack_params(value)
    packet = Packet.from_raw(packed)
    assert packed == packet.pack()
