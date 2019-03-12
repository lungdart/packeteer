""" Testing raw field packet classes """
#pylint: disable=C0326,W0621
import struct
import pytest #pylint: disable=unused-import
from tests.values.string import good_data #pylint: disable=unused-import
from packeteer import packets, fields


# Packet classes
class VariablePacket(packets.BigEndian):
    """ Variably sized raw data packet (Big Endian) """
    fields = [
        fields.Raw('raw'),
    ]

class StaticPacket(packets.BigEndian):
    """ Statically sizes raw data packet (Big Endian) """
    fields = [
        fields.Raw('raw', size=256),
    ]

class DynamicPacket(packets.BigEndian):
    """ Dynamically sized raw data packet(Big Endian) """
    fields = [
        fields.UInt16('count'),
        fields.Raw('raw', size='count'),
    ]

### TESTS ###
def test_variable_raw(good_data):
    """ Test unsized (variable) raw fields """
    packet = VariablePacket(raw=good_data)
    raw    = packet.pack()

    assert packet['raw'].rstrip(b'\x00') == good_data
    assert packet.pack() == raw

def test_static_raw(good_data):
    """ Test statically sized raw fields """
    packet1 = StaticPacket(raw=good_data)
    raw1    = packet1.pack()
    packet2 = StaticPacket.from_raw(raw1)
    raw2    = struct.pack(u'>256s', good_data)
    packet3 = StaticPacket()
    packet3.unpack(raw2)

    assert packet1['raw'].rstrip(b'\x00') == good_data
    assert packet2['raw'].rstrip(b'\x00') == good_data
    assert packet3['raw'].rstrip(b'\x00') == good_data
    assert raw1 == raw2

def test_dynamic_raw(good_data):
    """ Test dynamically sized raw fields """
    count = len(good_data)
    packet1 = DynamicPacket(raw=good_data)
    raw1    = packet1.pack()
    packet2 = DynamicPacket.from_raw(raw1)
    raw2    = struct.pack('>H{}s'.format(count), count, good_data)
    packet3 = DynamicPacket()
    packet3.unpack(raw2)

    assert packet1['count'] == len(good_data)
    assert packet2['count'] == len(good_data)
    assert packet3['count'] == len(good_data)
    assert packet1['raw'].rstrip(b'\x00') == good_data
    assert packet2['raw'].rstrip(b'\x00') == good_data
    assert packet3['raw'].rstrip(b'\x00') == good_data
    assert raw1 == raw2
