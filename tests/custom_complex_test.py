import struct
import copy
import pytest
from values import good_data
from packeter import packets, fields

FMT_PACKET = '{e}x>qQ{e}2B<qQ{e}H'

# Packet classes
class SubPacketBE(packets.BigEndian):
    """ Sub-packet (Big Endian) """
    fields = [
        fields.Int64('int64'),
        fields.UInt64('uint64')
    ]
class SubPacketLE(packets.LittleEndian):
    """ Sub-packet (Little Endian) """
    fields = copy.deepcopy(SubPacketBE.fields)

class PacketBE(packets.BigEndian):
    """ Complex Packet (Big Endian) """
    fields = [
        fields.Padding(),
        fields.Packet('be', default=SubPacketBE()),
        fields.UInt8('multi', count=2),
        fields.Packet('le', default=SubPacketLE()),
        fields.UInt16('size'),
        fields.Raw('data', size='size')
    ]
class PacketLE(packets.LittleEndian):
    """ Complex Packet (Little Endian) """
    fields = copy.deepcopy(PacketBE.fields)

# Helper functions
def gen_params(good_data):
    """ Generate complex packet initializer values """
    return {
        'be': SubPacketBE(int64=0x0eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        'multi': [0xde, 0xad],
        'le': SubPacketLE(int64=0x0eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        'size': len(good_data),
        'data': good_data
    }

def pack_params(params, big_endian=True):
    """ Pack complex packet parameters independently """
    e = '>' if big_endian else '<'
    packed = struct.pack('{}x'.format(e))
    packed += struct.pack(">qQ",
        params['be']['int64'], params['be']['uint64'])
    packed += struct.pack("{}2B".format(e),
        params['multi'][0], params['multi'][1])
    packed += struct.pack("<qQ",
        params['le']['int64'], params['le']['uint64'])
    packed += struct.pack("{}H{}s".format(e,
        params['size']), params['size'], params['data'])

    return packed

### TESTS ###
# Initializing tests
def test_init_be(good_data):
    """ Test initializing PacketBE field values """
    params = gen_params(good_data)
    packet = PacketBE(**params)

    for key, value in packet.iteritems():
        assert params[key] == value

def test_init_le(good_data):
    """ Test initializing PacketLE field values """
    params = gen_params(good_data)
    packet = PacketLE(**params)

    for key, value in packet.iteritems():
        assert params[key] == value

#@pytest.mark.skip(reason="Implementing...")
def test_from_packed_be(good_data):
    """ Test from_packed() initializing PacketBE field values """
    params = gen_params(good_data)
    packed = pack_params(params, big_endian=True)
    packet = PacketBE.from_packed(packed)

    for key, value in packet.iteritems():
        assert params[key] == value

# @pytest.mark.skip(reason="Implementing...")
# def test_from_packed_le(good_values):
#     """ Test from_packed() initializing SimplePacketLE field values """
#     values = extract_values(good_values)
#     packed = struct.pack(FMT_PACKET_LE, *values)
#     packet = PacketLE.from_packed(packed)

#     for key, value in packet.iteritems():
#         assert good_values[key] == value

# # Utility tests
# @pytest.mark.skip(reason="Implementing...")
# def test_keys():
#     """ Test fetching packet field names """
#     packet = PacketBE()
#     assert KEYS_PACKET == packet.keys()

# @pytest.mark.skip(reason="Implementing...")
# def test_values(set_values):
#     """ Test fetching packet field values """
#     values = extract_values(set_values)
#     packet = PacketBE(**set_values)

#     for idx, value in enumerate(packet.values()):
#         assert values[idx] == value

# @pytest.mark.skip(reason="Implementing...")
# def test_items(set_values):
#     """ Test fetching packet field key value pairs """
#     packet = PacketBE(**set_values)
#     keys = packet.keys()
#     vals = packet.values()
#     items = [(keys[i], vals[i]) for i in range(len(keys))]

#     assert items == packet.items()

# @pytest.mark.skip(reason="Implementing...")
# def test_size(set_values):
#     """ Test fetching the packet size """
#     packet = PacketBE()
#     size = packet.size()

#     assert SIZE_PACKET == size

# @pytest.mark.skip(reason="Implementing...")
# def test_get_set(set_values):
#     """ Test getting and setting of packet values """
#     packet = PacketBE()
#     for key in packet.keys():
#         packet[key] = set_values[key]

#     for key in packet.keys():
#         assert packet[key] == set_values[key]

# @pytest.mark.skip(reason="Implementing...")
# def test_iterkeys():
#     """ Test iterating over packet field names """
#     packet = PacketBE()
#     idx = 0
#     for key in packet.iterkeys():
#         assert key == KEYS_PACKET[idx]
#         idx += 1

# @pytest.mark.skip(reason="Implementing...")
# def test_itervalues(set_values):
#     """ Test iterating over packet field values """
#     values = extract_values(set_values)
#     packet = PacketBE(**set_values)

#     idx = 0
#     for value in packet.itervalues():
#         assert value == values[idx]
#         idx += 1

# @pytest.mark.skip(reason="Implementing...")
# def test_iteritems(set_values):
#     """ Test iterating over packet field name value pairs """
#     values = extract_values(set_values)
#     packet = PacketBE(**set_values)

#     idx = 0
#     for key, value in packet.iteritems():
#         assert key == KEYS_PACKET[idx]
#         assert value == values[idx]
#         idx += 1

# @pytest.mark.skip(reason="Implementing...")
# def test_clear(set_values):
#     """ Test clearing all packet field values"""
#     values = extract_values(set_values)
#     packet = PacketBE(**set_values)
#     packet.clear()

#     for idx, key in enumerate(packet.keys()):
#         assert key != values[idx]
