# Packeteer: The packet serializer
![Travis (.com)](https://img.shields.io/travis/com/lungdart/packeteer.svg)
![Coveralls github](https://img.shields.io/coveralls/github/lungdart/packeteer.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/packeteer.svg)
![GitHub](https://img.shields.io/github/license/lungdart/packeteer.svg)

**Packeteer** is a light-weight packet serializer capable of translating between raw bytes and custom packet objects; Objects which are easier to understand, display, and work with

```python
import socket
from packeteer import packets, fields

HOST = '127.0.0.1'
PORT = '1234'

class Request(packets.BigEndian):
    """ Request packet """
    fields = [
        fields.UInt8('type'),
        fields.UInt8('size'),
        fields.Raw('data', size='size')
    ]

class Response(packets.BigEndian):
    """ Response packet """
    fields = [
        fields.Bool('success'),
        fields.Uint32('transfered'),
    ]

if __name__ == '__main__':
    data = b'Hello World'
    request = RequestPacket(type=0, data=data)
    response = ResponsePacket()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect()
        s.sendall(request)
        raw = s.recv(response.size())
        response.unpack(raw)

    print(repr(response))

# <Packet: Response packet>
#   success: True
#   transfered: 11
```


## Installation
**Packeteer** is available on PyPi, and can be installed with pip directly
```sh
$ pip install packeteer
```

## Requirements
### Operating systems
**Packeteer** has no OS dependencies, and should be compatible wherever python can run; However, it is only verified for Ubuntu 18.04. If you discover any issues in other environments, please open a new issue or submit a pull request.

### Python
**Packeteer** was developed and tested against python 2.7, 3.5, 3.6, and 3.7.

### Dependencies
**Packeteer** depends on the following packages:
* future
* six

For development and testing, these optional dependencies are also required:
* pytest
* pytest-cov
* tox

## Documentation
### Defining packets
Defining packets is as simple as deriving a new class from either *packets.BigEndian* or *packets.LittleEndian* (Depending on the byte ordering of your packet structure)

```python
import copy
from packeteer import packets, fields

class MyPacketBE(packets.BigEndian):
    name = 'Custom (Big Endian)'
    fields = [
        fields.Bool('OK'),
        fields.Int32('value', default=42)
    ]

class MyPacketLE(packets.LittleEndian):
    """ Custom (Little Endian) """
    fields = copy.deepcopy(MyPacketBE.fields)
```

Take notice that the packet definition is built using the *fields* variable, and the built-in field types; Field types and there options are explained in the fields section of the documentation.

The packet name is an optional value that can be set directly, otherwise it will be coppied from the classes doc-string. If no name is found, the name will be given a default value. The name is only used for human readibility when using repr()

### Working with packets
#### Creating new instances
When packet objects are constructed without any parameters, their default values are stored in each field
```python
from packeteer import packets, fields

class MyPacket(packets.BigEndian):
    """ Custom (Big Endian) """
    fields = [
        fields.Bool('OK'),
        fields.Int32('value', default=42)
    ]

packet = MyPacket()
print(repr(packet))
# <Packet: Custom (Big Endian)>
#   OK: False
#   value: 42
```

Packets can also be constructed with non-default values by using the field names to set values
```python
packet = MyPacket(OK=True)
print(repr(packet))
# <Packet: Custom (Big Endian)>
#   OK: True
#   value: 42

packet2 = MyPacket(value=100)
print(repr(packet2))
# <Packet: Custom (Big Endian)>
#   OK: False
#   value: 100
```

#### Working with packet values
Field values can be accessed like a list (By index) or like a dictionary (By key)
```python
packet = MyPacket()
print(packet[0], packet[1])
# False 42

print(packet['OK'], packet['value'])
# False 42
```

Values can also be set in the same fashion
```python
packet = MyPacket()
packet[0] = True
packet[1] = 100

print(packet['OK'], packet['value'])
# True 100
```

#### Packing/Unpacking
The entire purpose of this library is to work with bytes, so it should come to no surprise that packet instances can be serialized into their raw bytes and back.

```python
packet = MyPacket()

raw = b'\x01\x00\x00\x00\xFF'
packet.unpack(raw)
print(repr(packet))
# <Packet: Custom (Big Endian)>
#   OK: True
#   value: 255

raw2 = packet.pack()
print(raw == raw2)
# True
```

Packet instances can be constructed directly from bytes as well using the from_raw() call
```python
packet = MyPacket.from_raw(b'\x01\x00\x00\x00\xFF')
print(repr(packet))
# <Packet: Custom (Big Endian)>
#   OK: True
#   value: 255
```

### Fields
The different components of the packet are referred to as fields, which are a collection of the associated value, meta data, and supporting functions.

Packeteer comes with the following field types:
* *fields.Padding*: (1 Byte) N/A
* *fields.Bool*: (1 Byte) Boolean
* *fields.Char*: (1 Byte) Character
* *fields.Int8*: (1 Byte) Signed Integer
* *fields.UInt8*: (1 Byte) Unsigned Integer
* *fields.Int16*: (2 Byte) Signed Integer
* *fields.UInt16*: (2 Byte) Unsigned Integer
* *fields.Int32*: (4 Byte) Signed Integer
* *fields.UInt32*: (4 Byte) Unsigned Integer
* *fields.Int64*: (8 Byte) Signed Integer
* *fields.UInt64*: (8 Byte) Unsigned Integer
* *fields.Float*: (4 Byte) Float value
* *fields.Double* (8 Byte) Float value
* *fields.Raw*: (n Byte) Raw byte data as a single value
* *fields.String*: (n Bytes) Unicode String as a single value

The majority of the types are self explanatory and work identically to the others, but some like padding, string, and raw behave differently and are looked at further in the following sections

#### Padding
*fields.Padding* is a special field type that is 1 byte wide per character.

Padding bytes are nameless and not associated with any value; They can't be accessed, but they are counted when packing and unpacking.
```python
from packeteer import packets, fields

class PaddedPacket(packets.BigEndian):
    """ Padded """
    fields = [
        fields.Padding(),
        fields.UInt8('value'),
        fields.Padding(default=b'\xff')
    ]

packet = PaddedPacket(value=170)
print(repr(packet))
# <Packet: Padded>
#   value: 170

print(packet[0])
# 170

print(packet[1])
# IndexError

raw = packet.pack()
print(repr(raw))
# '\x00\xAA\xFF'

packet.unpack(b'\x00\x7f\xff')
print(repr(packet))
# <Packet: Padded>
#   value: 127
```

#### Raw data and strings
*fields.Raw* is a raw byte store of a given size (The size argument is required). If the data is too large for the field, it will be truncated to fit. Likewise if it is too short, it will be padded with null bytes.

*fields.String* is an extension of *fields.Raw* that stores it's internal value as a unicode string with the encoding of your choosing (Defaults to utf8). The internal value has any trailing null byte padding removed until it is serialized.

```python
from packeteer import packets, fields

class DataPacket(packets.BigEndian):
    """ Data Packet """
    fields = [
        fields.Raw('raw', size=12),
        fields.String('string', size=12, encoding='utf8')
    ]

packet = DataPacket(raw=b'Hello World', string='Hello World')
print(repr(packet))
# <Packet: Raw Packet>
#   raw: b'Hello World\x00'
#   string: u'Hellow World'
```


#### List fields
There are often times when you need to have a variable list of values in a packet (Think about a repeating set of values depending on a given count value). *fields.List* takes care of this. *fields.List* requires an additional argument of the field the list contains, with the rest of the arguments given as keywords that the underlying field type requires.

```python
from packeteer import packets, fields

class ListPacket(packets.BigEndian):
    """ List Packet """
    fields = [
        fields.UInt8('count')
        fields.List('messages', fields.String, size=128),
    ]

messages = ['foo', 'bar', 'Hello World']
packet = ListPacket(count=len(messages), messages=messages)
print(repr(packet))
# <Packet: List Packet>
#   count: 3
#   messages: [u'foo', u'bar', u'Hello World']
```
