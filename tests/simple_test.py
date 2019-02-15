""" Testing simple packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import copy
import pytest #pylint: disable=unused-import
from tests.values import good_values, set_values #pylint: disable=unused-import
from packeter import packets, fields

# Expected values and formats
KEYS_PACKET   = ['char', 'bool', 'int8', 'int16', 'int32', 'int64', 'uint8',
                 'uint16', 'uint32', 'uint64', 'string']
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
        fields.String('string', size=256)
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


### TESTS ###
# Helper tests
def test_struct_be(good_values): #pylint: disable=redefined-outer-name
    """ Test the helper functions against the PacketBE structure """
    values = extract_values(good_values)
    packed = struct.pack(FMT_PACKET_BE, *values)
    unpacked = struct.unpack(FMT_PACKET_BE, packed)
    repacked = struct.pack(FMT_PACKET_BE, *unpacked)

    assert packed == repacked

def test_struct_le(good_values): #pylint: disable=redefined-outer-name
    """ Test the helper functions against the PacketLE structure """
    values = extract_values(good_values)
    packed = struct.pack(FMT_PACKET_LE, *values)
    unpacked = struct.unpack(FMT_PACKET_LE, packed)
    repacked = struct.pack(FMT_PACKET_LE, *unpacked)

    assert packed == repacked

# Initializing tests
def test_init_be(good_values):
    """ Test initializing PacketLE field values """
    packet = PacketLE(**good_values)

    for key, value in packet.iteritems():
        assert good_values[key] == value

def test_init_le(good_values):
    """ Test initializing PacketLE field values """
    packet = PacketLE(**good_values)

    for key, value in packet.iteritems():
        assert good_values[key] == value

def test_from_packed_be(good_values):
    """ Test from_packed() initializing PacketBE field values """
    values = extract_values(good_values)
    packed = struct.pack(FMT_PACKET_BE, *values)
    packet = PacketBE.from_packed(packed)

    for key, value in packet.iteritems():
        assert good_values[key] == value

def test_from_packed_le(good_values):
    """ Test from_packed() initializing PacketLE field values """
    values = extract_values(good_values)
    packed = struct.pack(FMT_PACKET_LE, *values)
    packet = PacketLE.from_packed(packed)

    for key, value in packet.iteritems():
        assert good_values[key] == value

# Utility tests
def test_keys():
    """ Test fetching packet field names """
    packet = PacketBE()
    assert KEYS_PACKET == packet.keys()

def test_values(set_values):
    """ Test fetching packet field values """
    values = extract_values(set_values)
    packet = PacketBE(**set_values)

    for idx, value in enumerate(packet.values()):
        assert values[idx] == value

def test_items(set_values):
    """ Test fetching packet field key value pairs """
    packet = PacketBE(**set_values)
    keys = packet.keys()
    vals = packet.values()
    items = [(keys[i], vals[i]) for i in range(len(keys))]

    assert items == packet.items()

def test_size():
    """ Test fetching the packet size """
    packet = PacketBE()
    size = packet.size()

    assert SIZE_PACKET == size

def test_get_set(set_values):
    """ Test getting and setting of packet values """
    packet = PacketBE()
    for key in packet.keys():
        packet[key] = set_values[key]

    for key in packet.keys():
        assert packet[key] == set_values[key]

def test_iterkeys():
    """ Test iterating over packet field names """
    packet = PacketBE()
    idx = 0
    for key in packet.iterkeys():
        assert key == KEYS_PACKET[idx]
        idx += 1

def test_itervalues(set_values):
    """ Test iterating over packet field values """
    values = extract_values(set_values)
    packet = PacketBE(**set_values)

    idx = 0
    for value in packet.itervalues():
        assert value == values[idx]
        idx += 1

def test_iteritems(set_values):
    """ Test iterating over packet field name value pairs """
    values = extract_values(set_values)
    packet = PacketBE(**set_values)

    idx = 0
    for key, value in packet.iteritems():
        assert key == KEYS_PACKET[idx]
        assert value == values[idx]
        idx += 1

def test_clear(set_values):
    """ Test clearing all packet field values"""
    values = extract_values(set_values)
    packet = PacketBE(**set_values)
    packet.clear()

    for idx, key in enumerate(packet.keys()):
        assert key != values[idx]
