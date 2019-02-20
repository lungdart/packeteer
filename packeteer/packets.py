""" Packet base class and common derivatives """
from __future__ import unicode_literals, print_function
import copy
import six
from packeteer import fields

class BasePacket(object):
    """
    Packet Base class
    Do not derive from this base class, use BigEndian and LittleEndian instead
    """
    big_endian = None
    fields = []

    def __init__(self, **kwargs):
        # Bootstrap the doc-string for the packet name for convenience
        if not hasattr(self, 'name') and self.__doc__:
            self.name = self.__doc__.strip()
        elif not hasattr(self, 'name'):
            self.name = 'Unknown Packet'

        # Prevent sharing field instances by creating unique copies
        self.fields = copy.deepcopy(self.fields)

        # Register fields and create lookup tables that ignore padding
        self._fnames = {}
        self._fidx = {}
        sparse_idx = 0
        for idx, field in enumerate(self.fields):
            field.register(self)
            if not isinstance(field, fields.Padding):
                self._fnames[field.name] = idx
                self._fidx[sparse_idx] = idx
                sparse_idx += 1

        # Set field values to what's given or their defaults
        self.clear()
        for name, value in six.iteritems(kwargs):
            idx = self._fnames[name]
            field = self.fields[idx]
            field.set(value)

    @classmethod
    def from_raw(cls, packed):
        """ Initialize a new packet from the raw bytes """
        instance = cls()
        instance.unpack(packed)
        return instance

    def __bytes__(self):
        return self.pack()

    def __str__(self):
        return str(self.pack().decode('utf8'))

    def __repr__(self):
        msg = "<Packet: {}>\n".format(self.name)
        for field in self.fields:
            if not isinstance(field, fields.Padding):
                msg += "  {}: {}\n".format(field.name, field.value)
        msg = msg[:-1]
        return msg

    def __getitem__(self, key):
        # Get field by index
        if isinstance(key, six.integer_types):
            try:
                idx = self._fidx[key]
            except KeyError:
                raise IndexError(key)
        # Get field by name
        elif isinstance(key, six.string_types):
            idx = self._fnames[key]
        # Other accessors not supported
        else:
            raise KeyError(key)
        # Return value
        field = self.fields[idx]
        return field.value

    def __setitem__(self, key, value):
        # Get field by index
        if isinstance(key, six.integer_types):
            try:
                idx = self._fidx[key]
            except KeyError:
                raise IndexError(key)
        # Get field by name
        elif isinstance(key, six.string_types):
            idx = self._fnames[key]
        # Other accessors not supported
        else:
            raise KeyError(key)
        # Set Value
        field = self.fields[idx]
        field.set(value)

    def __iter__(self):
        return self.fields.__iter__()

    def __eq__(self, rhs):
        if self.__class__ == rhs.__class__:
            equal = True
            for name, value in self.iteritems():
                equal &= value == rhs[name]
            return equal
        return NotImplemented

    def __ne__(self, rhs):
        equal = self.__eq__(rhs)
        if equal is not NotImplemented:
            return not equal
        return NotImplemented

    def pack(self):
        """ Fetch the packed raw byte string of the packet """
        raw = b''
        for field in self.fields:
            raw += field.pack(big_endian=self.big_endian)
        return raw

    def unpack(self, raw):
        """ Unpack a raw byte string into this packets fields """
        start = 0
        for field in self.fields:
            end = start + field.size()
            part = raw[start:end]
            field.unpack(part, big_endian=self.big_endian)
            start = end

    def clear(self):
        """ Clear all field values to their defaults """
        for field in self.fields:
            field.reset()

    def size(self):
        """ Calculate the packet size """
        result = 0
        for field in self.fields:
            result += field.size()
        return result

    def hex_dump(self):
        """ Print a human readable hex dump of the packet data """
        raw = self.pack()
        dump = ''
        for idx, byte in enumerate(bytearray(raw)):
            # Prepend the line with an address
            if (idx % 16) == 0:
                dump += "{:04x}".format(idx)
            # Visual pleasing space in the middle of 16 bytes
            elif (idx % 8) == 0:
                dump += ' '
            # Add bytes
            dump += " {:02x}".format(byte)
            # End with a new line if we're not finished
            if (idx % 16) == 15 and idx != len(raw)-1:
                dump += '\n'
        return dump

    def keys(self):
        """ Fetch a list of the field names """
        return [x.name for x in self.fields if not isinstance(x, fields.Padding)]

    def values(self):
        """ Fetch a list of the field values """
        return [x.value for x in self.fields if not isinstance(x, fields.Padding)]

    def items(self):
        """ Fetch a list of field name value pairs """
        return [(x.name, x.value) for x in self.fields if not isinstance(x, fields.Padding)]

    def iterkeys(self):
        """ Fetch a field name iterator """
        for field in self.fields:
            if isinstance(field, fields.Padding):
                continue
            yield field.name

    def itervalues(self):
        """ Fetch a field value iterator """
        for field in self.fields:
            if isinstance(field, fields.Padding):
                continue
            yield field.value

    def iteritems(self):
        """ Fetch a field name, value pair iterator """
        for field in self.fields:
            if isinstance(field, fields.Padding):
                continue
            yield (field.name, field.value)

    def dict(self):
        """ Fetch the packet as an ordered dictionary """
        return {name:value for name, value in self.items()}

class BigEndian(BasePacket):
    """ Big Endian Packet Class """
    big_endian = True

class LittleEndian(BasePacket):
    """ Little Endian Packet Class """
    big_endian = False
