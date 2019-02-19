""" Testing simple packet class creation and usage """
#pylint: disable=C0326,W0621
import struct
import copy
import pytest #pylint: disable=unused-import
from tests.values import good_values, set_values #pylint: disable=unused-import
from packeteer import packets, fields

### First example
class RequestPacket(packets.BigEndian):
    """ Request packet """
    fields = [
        fields.UInt8('type'),
        fields.UInt32('size'),
        fields.Raw('data', size='size')
    ]

class ResponsePacket(packets.BigEndian):
    """ Response packet """
    fields = [
        fields.Bool('success'),
        fields.UInt32('transfered'),
    ]

def test_example():
    data = b'Hello World'
    request = RequestPacket(type=0, size=len(data), data=data)
    assert request.name == 'Request packet'
    assert request['type'] == 0
    assert request['size'] == 11
    assert request['data'] == b'Hello World'

    response = ResponsePacket()
    raw = b'\x01\x00\x00\x00\x0B'
    response.unpack(raw)
    assert response.name == 'Response packet'
    assert response['success']
    assert response['transfered'] == 11

### Defining Packets
class MyPacketBE(packets.BigEndian):
    name = 'Custom (Big Endian)'
    fields = [
        fields.Bool('OK'),
        fields.Int32('value', default=42)
    ]

class MyPacketLE(packets.LittleEndian):
    ''' Custom (Little Endian) '''
    fields = copy.deepcopy(MyPacketBE.fields)

def test_defining_packets():
    be_raw = b'\x01\x00\x00\x00\x2A'
    big_endian = MyPacketBE.from_raw(be_raw)
    assert big_endian.name == 'Custom (Big Endian)'
    assert big_endian['OK']
    assert big_endian['value'] == 42
    assert big_endian.pack() == be_raw

    le_raw = b'\x00\x2A\x00\x00\x00'
    little_endian = MyPacketLE.from_raw(le_raw)
    assert little_endian.name == 'Custom (Little Endian)'
    assert not little_endian['OK']
    assert little_endian['value'] == 42
    assert little_endian.pack() == le_raw

### Creating new instances
class MyPacket(packets.BigEndian):
    ''' Custom (Big Endian) '''
    fields = [
        fields.Bool('OK'),
        fields.Int32('value', default=42)
    ]

def test_creating_new_instances():
    packet = MyPacket()
    assert repr(packet) == """<Packet: Custom (Big Endian)>
  OK: False
  value: 42"""

    packet = MyPacket(OK=True)
    assert repr(packet) == """<Packet: Custom (Big Endian)>
  OK: True
  value: 42"""

    packet = MyPacket(value=100)
    assert repr(packet) == """<Packet: Custom (Big Endian)>
  OK: False
  value: 100"""

    packet = MyPacket()
    assert not packet[0]
    assert not packet['OK']
    assert packet[1] == 42
    assert packet['value'] == 42

    packet = MyPacket()
    packet[0] = True
    packet[1] = 100
    assert packet['OK']
    assert packet['value'] == 100

### Packing/Unpacking
def test_packing_unpacking():
    packet = MyPacket()
    raw = b'\x01\x00\x00\x00\xFF'
    packet.unpack(raw)
    assert repr(packet) == """<Packet: Custom (Big Endian)>
  OK: True
  value: 255"""

    raw2 = packet.pack()
    assert raw == raw2

    packet = MyPacket.from_raw(b'\x01\x00\x00\x00\xFF')
    assert repr(packet) == """<Packet: Custom (Big Endian)>
  OK: True
  value: 255"""

### Fields
def test_field_existence():
    assert hasattr(fields, 'Padding')
    assert hasattr(fields, 'Bool')
    assert hasattr(fields, 'Char')
    assert hasattr(fields, 'Int8')
    assert hasattr(fields, 'UInt8')
    assert hasattr(fields, 'Int16')
    assert hasattr(fields, 'UInt16')
    assert hasattr(fields, 'Int32')
    assert hasattr(fields, 'UInt32')
    assert hasattr(fields, 'Int64')
    assert hasattr(fields, 'UInt64')
    assert hasattr(fields, 'Float')
    assert hasattr(fields, 'Double')
    assert hasattr(fields, 'Raw')
    assert hasattr(fields, 'String')

### Padding
class PaddedPacket(packets.BigEndian):
    ''' Padded '''
    fields = [
        fields.Padding(count=4),
        fields.UInt8('value'),
        fields.Padding(count=2)
    ]

def test_padding():
    packet = PaddedPacket(value=255)
    assert repr(packet) == """<Packet: Padded>
  value: 255"""
    assert packet[0] == 255
    with pytest.raises(IndexError):
        packet[1]

    raw = packet.pack()
    assert raw == b'\x00\x00\x00\x00\xFF\x00\x00'

    packet.unpack(b'\x00\x00\x00\x00\x7F\x00\x00')
    assert repr(packet) == """<Packet: Padded>
  value: 127"""

### Strings and Raw data
class StringPacket(packets.BigEndian):
    ''' String vs Char'''
    fields = [
        fields.Char('chars', count=12),
        fields.String('string', size=12),
        fields.Raw('raw', size=12)
    ]

def test_strings_and_raw():
    msg = 'Hello World'
    chars = [x for x in msg]
    packet = StringPacket(string=msg, raw=msg, chars=chars)
    assert packet['chars'] == chars + ['\x00']
    assert packet['string'] == msg
    assert packet['raw'] == msg + '\x00'
    assert repr(packet) == """<Packet: String vs Char>
  chars: ['H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '\\x00']
  string: Hello World
  raw: Hello World\x00"""

### Multi-count fields
class CountPacket(packets.BigEndian):
    ''' Multi-count '''
    fields = [fields.Int32('value', count=4)]

def test_multi_count():
    packet = CountPacket(value=(42, 33, 1, 999))
    assert packet['value'] == [42, 33, 1, 999]

    packet['value'] = [0, 0, 0, 0]
    assert packet['value'] == [0, 0, 0, 0]

    packet['value'][2] = 42
    assert packet['value'] == [0, 0, 42, 0]

### Dynamic count fields
class ListPacket(packets.BigEndian):
    ''' Result List '''
    fields = [
        fields.UInt8('result_count'),
        fields.Bool('results', count='result_count')
    ]

class DataPacket(packets.BigEndian):
    ''' Variable Length Data '''
    fields = [
        fields.UInt8('data_size'),
        fields.Raw('data', size='data_size')
    ]

def test_dynamic_count():
    results = [True, False, True, False, False]
    packet = ListPacket(results=results)
    assert packet['result_count'] == len(results)
    assert packet['results'] == results

    results = [False, False]
    packet['results'] = results
    assert packet['result_count'] == len(results)
    assert packet['results'] == results

    data = b''.join([chr(x) for x in range(8)])
    packet = DataPacket(data=data)
    assert packet['data_size'] == len(data)
    assert packet['data'] == data
