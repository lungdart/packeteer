""" Testing simple packet class creation and usage """
#pylint: disable=C0326,W0621
from __future__ import unicode_literals
import struct
import copy
import pytest #pylint: disable=unused-import
from tests.values import good_values, set_values #pylint: disable=unused-import
from packeteer import packets, fields

# Expected values and formats
KEYS_PACKET   = [u'char', u'bool',
                 u'int8', u'int16', u'int32', u'int64',
                 u'uint8', u'uint16', u'uint32', u'uint64',
                 u'raw']
FMT_PACKET    = '{e}xxxxxc?xbhiqxBHIQx256s'
FMT_PACKET_BE = FMT_PACKET.format(e='>')
FMT_PACKET_LE = FMT_PACKET.format(e='<')
SIZE_PACKET   = 296

# Custom packet classes
class PacketBE(packets.BigEndian):
    """ Simple Packet (Big Endian) """
    fields = [
        fields.Padding(count=5),
        fields.Char('char'),
        fields.Bool('bool'),
        fields.Padding(),
        fields.Int8('int8'),
        fields.Int16('int16'),
        fields.Int32('int32'),
        fields.Int64('int64'),
        fields.Padding(),
        fields.UInt8('uint8'),
        fields.UInt16('uint16'),
        fields.UInt32('uint32'),
        fields.UInt64('uint64'),
        fields.Padding(),
        fields.Raw('raw', size=256),
    ]
class PacketLE(packets.LittleEndian):
    """ Simple Packet (Little Endian) """
    fields = copy.deepcopy(PacketBE.fields)

# Helper functions
def extract_values(values):
    """ Extracts ordered values for packet generation from the given dict """
    packet = PacketBE()
    ordered_values = [values[x] for x in packet.keys()]
    return tuple(ordered_values)

def check_packet(packet, value_lookup):
    """ Checks all the fetching functions of the packet to ensure they're correct """
    # packet.keys()
    keys = packet.keys()
    assert KEYS_PACKET == keys

    # packet.values()
    values = packet.values()
    expected_values = extract_values(value_lookup)
    for idx, value in enumerate(values):
        assert expected_values[idx] == value

    # packet.items()
    expected_items = [(keys[i], values[i]) for i in range(len(keys))]
    assert expected_items == packet.items()

    # packet.size()
    assert SIZE_PACKET == packet.size()

    # packet.iterkeys()
    idx = 0
    for key in packet.iterkeys():
        assert key == KEYS_PACKET[idx]
        idx += 1

    # packet.itervalues()
    idx = 0
    for value in packet.itervalues():
        assert value == values[idx]
        idx += 1

    # packet.iteritems()
    idx = 0
    for key, value in packet.iteritems():
        assert KEYS_PACKET[idx] == key
        assert expected_values[idx] == value
        idx += 1


### TESTS ###
# Helper tests
def test_simple_struct(good_values): #pylint: disable=redefined-outer-name
    """ Test the helper functions """
    values = extract_values(good_values)
    packed_be = struct.pack(FMT_PACKET_BE, *values)
    unpacked_be = struct.unpack(FMT_PACKET_BE, packed_be)
    repacked_be = struct.pack(FMT_PACKET_BE, *unpacked_be)

    packed_le = struct.pack(FMT_PACKET_LE, *values)
    unpacked_le = struct.unpack(FMT_PACKET_LE, packed_le)
    repacked_le = struct.pack(FMT_PACKET_LE, *unpacked_le)

    assert packed_be == repacked_be
    assert packed_le == repacked_le

# Initializing tests
def test_init(good_values):
    """ Test initializing field values """
    packet_be = PacketBE(**good_values)
    packet_le = PacketLE(**good_values)

    check_packet(packet_be, good_values)
    check_packet(packet_le, good_values)

def test_from_raw(good_values):
    """ Test from_raw() initializing PacketBE field values """
    values = extract_values(good_values)

    packed_be = struct.pack(FMT_PACKET_BE, *values)
    packet_be = PacketBE.from_raw(packed_be)
    packed_le = struct.pack(FMT_PACKET_LE, *values)
    packet_le = PacketLE.from_raw(packed_le)

    check_packet(packet_be, good_values)
    check_packet(packet_le, good_values)

# Modifying tests
def test_get_set(set_values):
    """ Test getting and setting of packet values """
    packet = PacketBE()
    for key in packet.keys():
        packet[key] = set_values[key]

    for key in packet.keys():
        assert packet[key] == set_values[key]

def test_clear(set_values):
    """ Test clearing all packet field values"""
    values = extract_values(set_values)
    packet = PacketBE(**set_values)
    packet.clear()

    for idx, key in enumerate(packet.keys()):
        assert key != values[idx]
