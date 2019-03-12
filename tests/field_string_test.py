""" Testing string field packet classes """
#pylint: disable=C0326,W0621
from __future__ import unicode_literals
import struct
import pytest #pylint: disable=unused-import
import six
from tests.values.string import good_data #pylint: disable=unused-import
from packeteer import packets, fields


# Packet classes
class VariablePacket(packets.BigEndian):
    """ Variably sized string packet (Big Endian) """
    fields = [
        fields.String('string'),
    ]

class StaticPacket(packets.BigEndian):
    """ Statically sizes string packet (Big Endian) """
    fields = [
        fields.String('string', size=256),
    ]

class DynamicPacket(packets.BigEndian):
    """ Dynamically sizes string packet (Big Endian) """
    fields = [
        fields.UInt16('count'),
        fields.String('string', size='count'),
    ]

### TESTS ###
def test_variable_string(good_data):
    """ Test unsized (variable) string fields """
    string = six.text_type(good_data, encoding='utf8')
    packet = VariablePacket(string=string)
    raw    = packet.pack()

    assert packet['string'] == string
    assert packet.pack()    == raw

def test_static_string(good_data):
    """ Test statically sized string fields """
    string = six.text_type(good_data, encoding='utf8')
    packet1 = StaticPacket(string=string)
    raw1    = packet1.pack()
    packet2 = StaticPacket.from_raw(raw1)
    raw2    = struct.pack('>256s', good_data)
    packet3 = StaticPacket()
    packet3.unpack(raw2)

    assert packet1['string'] == string
    assert packet2['string'] == string
    assert packet3['string'] == string
    assert raw1              == raw2

def test_dynamic_string(good_data):
    """ Test dynamically sized string fields """
    string = six.text_type(good_data, encoding='utf8')
    count = len(good_data)
    packet1 = DynamicPacket(string=string)
    raw1    = packet1.pack()
    packet2 = DynamicPacket.from_raw(raw1)
    raw2    = struct.pack('>H{}s'.format(count), count, good_data)
    packet3 = DynamicPacket()
    packet3.unpack(raw2)

    assert packet1['count']  == len(string)
    assert packet2['count']  == len(string)
    assert packet3['count']  == len(string)
    assert packet1['string'] == string
    assert packet2['string'] == string
    assert packet3['string'] == string
    assert raw1 == raw2
