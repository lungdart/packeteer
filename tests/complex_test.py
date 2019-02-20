""" Testing complex packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import copy
import pytest #pylint: disable=unused-import
from tests.values import good_data #pylint: disable=unused-import
from packeteer import packets, fields


# Packet classes
class SubPacketBE(packets.BigEndian):
    """ Sub-packet (Big Endian) """
    fields = [
        fields.Int64(u'int64'),
        fields.UInt64(u'uint64')
    ]
class SubPacketLE(packets.LittleEndian):
    """ Sub-packet (Little Endian) """
    fields = copy.deepcopy(SubPacketBE.fields)
class Packet(packets.BigEndian):
    """ Complex Packet (Big Endian) """
    fields = [
        fields.Padding(),
        fields.Packet(u'be', default=SubPacketBE()),
        fields.UInt8(u'multi', count=2),
        fields.Packet(u'le', default=SubPacketLE()),
        fields.UInt16(u'size'),
        fields.Raw(u'data', size=u'size')
    ]


# Helper functions
def gen_params(good_data):
    """ Generate complex packet initializer values """
    return {
        u'be': SubPacketBE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        u'multi': [0xde, 0xad],
        u'le': SubPacketLE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        u'size': len(good_data),
        u'data': good_data
    }

def pack_params(params, big_endian=True):
    """ Pack complex packet parameters independently """
    endian = u'>' if big_endian else u'<'
    packed = struct.pack(u'{}x'.format(endian))
    packed += struct.pack(u'>qQ',
                          params[u'be'][u'int64'], params[u'be'][u'uint64'])
    packed += struct.pack(u'{}2B'.format(endian),
                          params[u'multi'][0], params[u'multi'][1])
    packed += struct.pack(u'<qQ',
                          params[u'le'][u'int64'], params[u'le'][u'uint64'])
    packed += struct.pack(u'{}H{}s'.format(endian, params[u'size']),
                          params[u'size'], params[u'data'])

    return packed

### TESTS ###
# Initializing tests
def test_complex_init(good_data):
    """ Test initializing PacketBE field values """
    params = gen_params(good_data)
    packet = Packet(**params)

    for key, value in packet.iteritems():
        assert params[key] == value

def test_complex_from_raw(good_data):
    """ Test from_raw() initializing PacketBE field values """
    params = gen_params(good_data)
    packed = pack_params(params, big_endian=True)
    packet = Packet.from_raw(packed)

    for key, value in packet.iteritems():
        assert params[key] == value
