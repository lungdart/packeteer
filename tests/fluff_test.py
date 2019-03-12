""" Testing simple packet class creation and usage """
#pylint: disable=C0326,W0621
from __future__ import unicode_literals
import re
from itertools import chain
import six
import pytest #pylint: disable=unused-import
from packeteer import packets, fields

# Custom packet classes
class PacketNoName(packets.BigEndian): #pylint: disable=missing-docstring
    fields = [fields.UInt32(str(x)) for x in range(16)]
class PacketSetName(packets.BigEndian): #pylint: disable=missing-docstring
    name = 'SETNAME'
    fields = [fields.UInt32(str(x)) for x in range(16)]
class PacketDocName(packets.BigEndian):
    """ DOCNAME """
    fields = [fields.UInt32(str(x)) for x in range(16)]
class PacketIter(packets.BigEndian):
    """ ITER """
    fields = list(
        chain.from_iterable(
            (fields.UInt32(str(x)), fields.Padding()) for x in range(16)
        )
    )


### TESTS ###
def test_name():
    """ Test if packets name is derived correctly """
    no_name = PacketNoName()
    set_name = PacketSetName()
    doc_name = PacketDocName()

    assert no_name.name == 'Unknown Packet'
    assert set_name.name == 'SETNAME'
    assert doc_name.name == 'DOCNAME'

def test_bytes():
    """ Test if packets are correctly converted to byte objects """
    packet = PacketNoName()
    expected = b''.join([b'\x00' for _ in range(16 * 4)])
    assert bytes(packet) == expected

def test_str():
    """ Test if packets correctly convert to strings """
    packet = PacketNoName()
    result = str(packet)
    raw = ''.join(['\x00' for _ in range(packet.size())])

    assert isinstance(result, six.string_types)
    assert result == raw

def test_repr():
    """ Test if packet representation is formatted correctly """
    no_name = PacketNoName()
    set_name = PacketSetName()
    doc_name = PacketDocName()

    pattern = r'<Packet: (.+)>[\n  (.+): (.+)]*'
    assert re.match(pattern, repr(no_name)) is not None
    assert re.match(pattern, repr(set_name)) is not None
    assert re.match(pattern, repr(doc_name)) is not None

def test_hex_dump():
    """ Test dumping a packet as a hex dump """
    # Empty dump
    packet = PacketNoName()
    expected_dump = """0000 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
0010 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
0020 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
0030 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00"""
    assert packet.hex_dump() == expected_dump

    # Set dump
    for idx in range(16):
        packet[idx] = 0x42
    expected_dump = """0000 00 00 00 42 00 00 00 42  00 00 00 42 00 00 00 42
0010 00 00 00 42 00 00 00 42  00 00 00 42 00 00 00 42
0020 00 00 00 42 00 00 00 42  00 00 00 42 00 00 00 42
0030 00 00 00 42 00 00 00 42  00 00 00 42 00 00 00 42"""
    assert packet.hex_dump() == expected_dump

def test_dict():
    """ Tests fetching a packet as a dictionary """
    packet = PacketNoName()
    packet_dict = packet.dict()

    assert isinstance(packet_dict, dict)
    for key in packet.keys():
        assert key in packet_dict
        assert packet[key] == packet_dict[key]

def test_iter():
    """ Test fetching a packet value iterator """
    packet = PacketIter()
    for val in packet:
        assert val == 0

def test_equal():
    """ Test for packet equality """
    packet1 = PacketNoName()
    packet2 = PacketNoName()
    assert packet1 == packet2

    packet1['0'] = 42
    packet2['0'] = 42
    assert packet1 == packet2

def test_unequal():
    """ Test for packet inequality """
    packet1      = PacketNoName()
    packet1['0'] = 42
    packet2      = PacketNoName()
    assert packet1 != packet2

def test_iterkeys():
    """ Test iterating over keys """
    packet = PacketIter()
    idx = 0
    for key in packet.iterkeys():
        assert key == str(idx)
        idx += 1

def test_itervalues():
    """ Test iterating over values """
    packet = PacketIter()
    for value in packet.itervalues():
        assert value == 0

def test_iteritems():
    """ Test iterating over keys value pairs """
    packet = PacketIter()
    idx = 0
    for key, value in packet.iteritems():
        assert key == str(idx)
        assert value == 0
        idx += 1
