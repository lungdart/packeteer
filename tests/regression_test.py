""" Regression testing """
#pylint: disable=C0326
import struct
import pytest
from packeteer import packets, fields

"""
TEST 1
Ticket #: n/a
Description: Packets with nested lists of dynamically sized packets do not get
             created correctly with from_raw(), due to the inner most size not
             being set until the out lists are populated first, but the outer
             list sizes actually depend on the inner list sizes.
"""
class Packet1(packets.LittleEndian):
    """ Test 1 - Dynamic list of sub-packets """
    class Sub1(packets.LittleEndian):
        """ Test 1 - SubPacket 1 """
        class Sub2(packets.LittleEndian):
            """ Test 1 - SubPacket 2 """
            fields = [
                fields.UInt32('entry1'),
                fields.UInt32('entry2'),
            ]
        fields = [
            fields.UInt8('size2'),
            fields.List('data2', fields.Packet(default=Sub2()), size='size2')
        ]
    fields = [
        fields.UInt8('size1'),
        fields.List('data1', fields.Packet(default=Sub1()), size='size1')
    ]

def test_1():
    """ Run regression test 1 """
    raw    = struct.pack('<BBIIIIIIBIIIIBII',
                         3, 3, 0, 100, 1, 101, 2, 102, 2, 3, 103, 4, 104, 1, 5, 105)
    packet = Packet1.from_raw(raw)

    # Parent packet has 3 sub packets
    assert packet['size1']      == 3
    assert len(packet['data1']) == 3

    # Sub packet 0, has 3 sub-sub packets
    assert packet['data1'][0]['size2']      == 3
    assert len(packet['data1'][0]['data2']) == 3

    assert packet['data1'][0]['data2'][0]['entry1']   == 0
    assert packet['data1'][0]['data2'][0]['entry2']   == 100
    assert packet['data1'][0]['data2'][1]['entry1']   == 1
    assert packet['data1'][0]['data2'][1]['entry2']   == 101
    assert packet['data1'][0]['data2'][2]['entry1']   == 2
    assert packet['data1'][0]['data2'][2]['entry2']   == 102

    # Sub packet 1 has 2 sub-sub packets
    assert packet['data1'][1]['size2']      == 2
    assert len(packet['data1'][1]['data2']) == 2

    assert packet['data1'][1]['data2'][0]['entry1']   == 3
    assert packet['data1'][1]['data2'][0]['entry2']   == 103
    assert packet['data1'][1]['data2'][1]['entry1']   == 4
    assert packet['data1'][1]['data2'][1]['entry2']   == 104

    # Sub packet 3 has 1 sub sub packet
    assert packet['data1'][2]['size2']      == 1
    assert len(packet['data1'][2]['data2']) == 1

    assert packet['data1'][2]['data2'][0]['entry1']   == 5
    assert packet['data1'][2]['data2'][0]['entry2']   == 105
