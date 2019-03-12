""" Testing complex packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import copy
import pytest #pylint: disable=unused-import
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
        fields.Packet(u'be', default=SubPacketBE()),
        fields.Packet(u'le', default=SubPacketLE()),
    ]

# Helper functions
def gen_params():
    """ Generate packet initializer values """
    return {
        u'be': SubPacketBE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead),
        u'le': SubPacketLE(int64=0x7eaddeaddeaddead, uint64=0xdeaddeaddeaddead)
    }

def pack_params(params):
    """ Pack sub-packet parameters independently """
    packed =  struct.pack(u'>qQ',
                          params[u'be'][u'int64'],
                          params[u'be'][u'uint64'])
    packed += struct.pack(u'<qQ',
                          params[u'le'][u'int64'],
                          params[u'le'][u'uint64'])
    return packed

### TESTS ###
# Initializing tests
def test_packet_init():
    """ Test initializing field values """
    params = gen_params()
    packet = Packet(**params)

    for key, value in packet.iteritems():
        assert params[key] == value

def test_packet_from_raw():
    """ Test from_raw() initializing field values """
    params = gen_params()
    packed = pack_params(params)
    packet = Packet.from_raw(packed)

    for key, value in packet.iteritems():
        assert params[key] == value
