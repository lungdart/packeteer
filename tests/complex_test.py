""" Testing complex packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import copy
import pytest #pylint: disable=unused-import
from tests.values import good_data #pylint: disable=unused-import
from packeter import packets, fields


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
        'be': SubPacketBE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        'multi': [0xde, 0xad],
        'le': SubPacketLE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        'size': len(good_data),
        'data': good_data
    }

def pack_params(params, big_endian=True):
    """ Pack complex packet parameters independently """
    endian = '>' if big_endian else '<'
    packed = struct.pack('{}x'.format(endian))
    packed += struct.pack(">qQ",
                          params['be']['int64'], params['be']['uint64'])
    packed += struct.pack("{}2B".format(endian),
                          params['multi'][0], params['multi'][1])
    packed += struct.pack("<qQ",
                          params['le']['int64'], params['le']['uint64'])
    packed += struct.pack("{}H{}s".format(endian, params['size']),
                          params['size'], params['data'])

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

def test_from_packed_be(good_data):
    """ Test from_packed() initializing PacketBE field values """
    params = gen_params(good_data)
    packed = pack_params(params, big_endian=True)
    packet = PacketBE.from_packed(packed)

    for key, value in packet.iteritems():
        assert params[key] == value

def test_from_packed_le(good_data):
    """ Test from_packed() initializing PacketBE field values """
    params = gen_params(good_data)
    packed = pack_params(params, big_endian=False)
    packet = PacketLE.from_packed(packed)

    for key, value in packet.iteritems():
        assert params[key] == value
