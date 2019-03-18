""" Testing list field packet classes """
#pylint: disable=C0326,W0621,C1801
from __future__ import unicode_literals
import struct
import pytest #pylint: disable=unused-import
from packeteer import packets, fields

# Packet classes
class VariablePacket(packets.BigEndian):
    """ Variable sized list packet (Big Endian) """
    fields = [
        fields.List('list', fields.UInt8())
    ]

class StaticPacket(packets.BigEndian):
    """ Statically sized list packet (Big Endian) """
    fields = [
        fields.List('list', fields.UInt8(), size=10)
    ]

class DynamicPacket(packets.BigEndian):
    """ Dynamically sized list packet (Big Endian) """
    fields = [
        fields.UInt16('count'),
        fields.List('list', fields.UInt8(), size='count'),
    ]

class RawPacket(packets.BigEndian):
    """ Dynamically sized list of raw data packet (Big Endian) """
    fields = [
        fields.UInt16('count'),
        fields.List('list', fields.Raw(size=256), size='count'),
    ]

class SubpacketPacket(packets.BigEndian):
    """ Dynamically sized list of sub-packets (Big Endian) """
    class SubPacket(packets.BigEndian):
        """ Sub-packet (Big Endian) """
        fields = [
            fields.UInt8('value1'),
            fields.UInt8('value2')
        ]
    fields = [
        fields.UInt16('count'),
        fields.List('list', fields.Packet(default=SubPacket()), size='count'),
    ]

### TESTS ###
#@pytest.mark.skip()
def test_variable_list():
    """ Test unsized (variable) list of simple type fields """
    data = [1, 2, 3]
    packet = VariablePacket(list=data)
    raw    = packet.pack()

    assert packet['list'] == data
    assert packet.pack()  == raw

    packet['list'] = 4
    assert packet['list'] == [4]

#@pytest.mark.skip()
def test_static_list():
    """ Test statically sized list of simple type fields """
    data = [1, 2, 3]
    full_data = data + [0, 0, 0, 0, 0, 0, 0]
    packet1 = StaticPacket(list=data)
    raw1    = packet1.pack()
    packet2 = StaticPacket.from_raw(raw1)
    raw2    = struct.pack('>BBBBBBBBBB', *full_data)
    packet3 = StaticPacket()
    packet3.unpack(raw2)

    assert packet1['list'] == full_data
    assert packet2['list'] == full_data
    assert packet3['list'] == full_data
    assert raw1            == raw2

    packet1['list'] = 4
    assert packet1['list'] == [4, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#@pytest.mark.skip()
def test_dynamic_list():
    """ Test dynamically sized list of simple type fields """
    data = [1, 2, 3]
    count = len(data)
    packet1 = DynamicPacket(list=data)
    assert packet1['count'] == count
    assert packet1['list']  == data

    raw1    = packet1.pack()
    packet2 = DynamicPacket.from_raw(raw1)
    assert packet2['count'] == count
    assert packet2['list']  == data

    raw2    = struct.pack('>HBBB', count, *data)
    packet3 = DynamicPacket()
    packet3.unpack(raw2)
    assert raw1 == raw2
    assert packet3['count'] == count
    assert packet3['list']  == data

    packet4 = DynamicPacket()
    assert packet4['count'] == 0
    assert packet4['list']  == []

    packet4['list'] = 4
    assert packet4['count'] == 1
    assert packet4['list']  == [4]

#@pytest.mark.skip()
def test_raw_list():
    """ Test list of raw data fields """
    data = [b'foo', b'bar', b'Hello World']
    expected = []
    for datum in data:
        remainder = 256 - len(datum)
        padding = b''.join(b'\x00' for _ in range(remainder))
        expected.append(datum + padding)
    count = len(data)
    packet1 = RawPacket(list=data)
    assert packet1['count'] == count
    assert packet1['list']  == expected

    raw1    = packet1.pack()
    packet2 = RawPacket.from_raw(raw1)
    assert packet2['count'] == count
    assert packet2['list']  == expected

    fmt     = '>H' + ''.join(['256s' for _ in data])
    raw2    = struct.pack(fmt, count, *data)
    packet3 = RawPacket()
    packet3.unpack(raw2)
    assert raw1 == raw2
    assert packet3['count'] == count
    assert packet3['list']  == expected

    packet4 = RawPacket()
    assert packet4['count'] == 0
    assert packet4['list']  == []

    packet4['list'] = b'FooBar'
    expected = [b'FooBar' + b''.join(b'\x00' for _ in range(250))]
    assert packet4['count'] == 1
    assert packet4['list']  == expected

#@pytest.mark.skip()
def test_packet_list():
    """ Test list of subpacket fields """
    count = 5
    data = []
    for idx in range(count):
        packet = SubpacketPacket.SubPacket(value1=(2*idx)+0, value2=(2*idx)+1)
        data.append(packet)
    packet1 = SubpacketPacket(list=data)
    assert packet1['count'] == count
    assert packet1['list']  == data

    raw1    = packet1.pack()
    packet2 = SubpacketPacket.from_raw(raw1)
    assert packet2['count'] == count
    assert packet2['list']  == data

    raw2    = struct.pack('>HBBBBBBBBBB', count, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    packet3 = SubpacketPacket()
    packet3.unpack(raw2)
    assert raw1 == raw2
    assert packet3['count'] == count
    assert packet3['list']  == data

    packet4 = SubpacketPacket()
    assert packet4['count'] == 0
    assert packet4['list']  == []

    subpacket = SubpacketPacket.SubPacket(value1=42, value2=99)
    packet4['list'] = subpacket
    assert packet4['count'] == 1
    assert packet4['list']  == [subpacket]
