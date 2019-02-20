""" Testing packing and unpacking of all types """
from __future__ import unicode_literals
import pytest #pylint: disable=unused-import
from packeteer import packets, fields

@pytest.fixture
def values():
    """ Fixture for ready made values """
    return {
        'char'  : b'c',
        'bool'  : True,
        'int8'  : 42,
        'int16' : 42,
        'int32' : 42,
        'int64' : 42,
        'uint8' : 42,
        'uint16': 42,
        'uint32': 42,
        'uint64': 42,
        'float' : 2.5, # Some values can not be tested for equality due to float encoding
        'double': 2.5, # Some values can not be tested for equality due to float encoding
        'raw'   : b'REDRUM',
        'string': 'Redrum'
    }

class BigPacket(packets.BigEndian):
    """ Big Packet """
    fields = [
        fields.Char('char'),
        fields.Bool('bool'),
        fields.Int8('int8'),
        fields.Int16('int16'),
        fields.Int32('int32'),
        fields.Int64('int64'),
        fields.UInt8('uint8'),
        fields.UInt16('uint16'),
        fields.UInt32('uint32'),
        fields.UInt64('uint64'),
        fields.Float('float'),
        fields.Double('double'),
        fields.Raw('raw', size=16),
        fields.String('string', size=16)
    ]

def test_big_empty():
    """ Test packing and unpacking all fields with default values """
    packet1 = BigPacket()
    raw1 = packet1.pack()
    packet2 = packet1.from_raw(raw1)
    raw2 = packet2.pack()
    assert packet1 == packet2
    assert raw1 == raw2

def test_big_set(values):
    """ Test packing and unpacking all fields with set values """
    packet1 = BigPacket(**values)
    raw1 = packet1.pack()
    packet2 = packet1.from_raw(raw1)
    raw2 = packet2.pack()
    assert packet1 == packet2
    assert raw1 == raw2
