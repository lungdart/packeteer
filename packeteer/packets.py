""" Packet base class and common derivatives """
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

        # Register fields and create lookup tables
        self._fnames = {}
        self._fidx = {}
        parse_idx = 0
        for idx, field in enumerate(self.fields):
            field.register(self)
            if not isinstance(field, fields.Padding):
                self._fnames[field.name] = idx
                self._fidx[parse_idx] = idx
                parse_idx += 1

        # Set field values to what's given or their defaults
        self.clear()
        for name, value in kwargs.iteritems():
            idx = self._fnames[name]
            field = self.fields[idx]
            field.set(value)

    @classmethod
    def from_raw(cls, packed):
        """ Initialize a new packet from the raw bytes """
        instance = cls()
        instance.unpack(packed)
        return instance

    def __str__(self):
        return self.pack()

    def __repr__(self):
        msg = "<Packet: {}>\n".format(self.name)
        for field in self.fields:
            if not isinstance(field, fields.Padding):
                msg += "  {}: {}\n".format(field.name, field.value)
        msg = msg[:-1]
        return msg

    def __getitem__(self, key):
        # Get field by index
        if isinstance(key, int):
            try:
                idx = self._fidx[key]
            except KeyError:
                print "!!!", key, self._fidx
                raise IndexError(key)
        # Get field by name
        elif isinstance(key, basestring):
            idx = self._fnames[key]
        # Other accessors not supported
        else:
            raise KeyError(key)
        # Return value
        field = self.fields[idx]
        return field.value

    def __setitem__(self, key, value):
        # Get field by index
        if isinstance(key, int):
            try:
                idx = self._fidx[key]
            except KeyError:
                raise IndexError(key)
        # Get field by name
        elif isinstance(key, basestring):
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
        for byte, idx in enumerate(raw):
            line = ""
            if (idx % 16) == 0:
                line = "{:04x}".format(idx)
            elif (idx % 8) == 0:
                line += " "
            line += " {:02x}".format(byte)
            print line

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
