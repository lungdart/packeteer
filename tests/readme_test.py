""" Testing simple packet class creation and usage """
#pylint: disable=C0326,W0621
from __future__ import unicode_literals
import copy
import six
import pytest #pylint: disable=unused-import
from tests.values.simple import good_values, set_values #pylint: disable=unused-import
from packeteer import packets, fields

### First example
class RequestPacket(packets.BigEndian):
    """ Request packet """
    fields = [
        fields.UInt8('type'),
        fields.UInt8('size'),
        fields.Raw('data', size='size')
    ]

class ResponsePacket(packets.BigEndian):
    """ Response packet """
    fields = [
        fields.Bool('success'),
        fields.UInt32('transfered'),
    ]

def test_example():
    """ Test the header example in the README """
    data = b'Hello World'
    request = RequestPacket(type=0, data=data)
    assert request.name == 'Request packet'
    assert request['type'] == 0
    assert request['size'] == len(data)
    assert request['data'] == data

    response = ResponsePacket()
    raw = b'\x01\x00\x00\x00\x0B'
    response.unpack(raw)
    assert response.name == 'Response packet'
    assert response['success']
    assert response['transfered'] == 11

### Defining Packets
class MyPacketBE(packets.BigEndian): #pylint: disable=missing-docstring
    name = 'Custom (Big Endian)'
    fields = [
        fields.Bool('OK'),
        fields.Int32('value', default=42)
    ]

class MyPacketLE(packets.LittleEndian):
    """ Custom (Little Endian) """
    fields = copy.deepcopy(MyPacketBE.fields)

def test_defining_packets():
    """ Test defining packet class section of the README """
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
    """ Test creating new instances section of the README """
    packet = MyPacket()
    assert not packet[0]
    assert packet[1] == 42

    packet = MyPacket(OK=True)
    assert packet[0]
    assert packet[1] == 42

    packet = MyPacket(value=100)
    assert not packet[0]
    assert packet[1] == 100

    packet = MyPacket()
    assert not packet['OK']
    assert packet['value'] == 42

    packet = MyPacket()
    packet[0] = True
    packet[1] = 100
    assert packet['OK']
    assert packet['value'] == 100

### Packing/Unpacking
def test_packing_unpacking():
    """ Test the packing and unpacking section of the README """
    packet = MyPacket()
    raw = b'\x01\x00\x00\x00\xFF'
    packet.unpack(raw)
    assert packet[0]
    assert packet[1] == 255

    raw2 = packet.pack()
    assert raw == raw2

    packet = MyPacket.from_raw(b'\x01\x00\x00\x00\xFF')
    assert packet['OK']
    assert packet['value'] == 255

### Fields
def test_field_existence():
    """ Test the field list in the README is accurate """
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
    """ Padded """
    fields = [
        fields.Padding(),
        fields.UInt8('value'),
        fields.Padding(default=b'\xff')
    ]

def test_padding():
    """ Test the padding section of the README """
    packet = PaddedPacket(value=170)
    assert packet[0] == 170
    with pytest.raises(IndexError):
        packet[1] #pylint: disable=pointless-statement

    raw = packet.pack()
    assert raw == b'\x00\xaa\xff'

    packet.unpack(b'\x00\x7F\xff')
    assert packet[0] == 127

### Strings and Raw data
class DataPacket(packets.BigEndian):
    """ Data Packet """
    fields = [
        fields.Raw('raw', size=12),
        fields.String('string', size=12, encoding='utf8')
    ]

def test_raw_and_strings():
    """ Test the strings and raw data section of the README """
    msg = b'Hello World'
    packet = DataPacket(raw=msg, string=six.text_type(msg, encoding='utf8'))
    assert packet['raw'] == msg + b'\x00'
    assert packet['string'] == six.text_type(msg, encoding='utf8')

### List fields
class ListPacket(packets.BigEndian):
    """ List Packet """
    fields = [
        fields.UInt8('count'),
        fields.List('messages', fields.String(size=128), size='count'),
    ]


def test_list():
    """ Test the list field section of the README """
    messages = ['foo', 'bar', 'Hello World']
    packet = ListPacket(messages=messages)
    assert packet['count'] == len(packet['messages'])
    assert packet['messages'][0] == messages[0]
    assert packet['messages'][1] == messages[1]
    assert packet['messages'][2] == messages[2]
