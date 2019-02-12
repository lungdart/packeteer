### IMPORTS ###
import struct

### CLASSES ###
class Field(object):
    """
    Field Base class
    Do not derive from this class, but use the pre-existing type classes instead
    """

    def __init__(self, name, _type, count, default):
        self.name   = name
        self.type   = _type
        self.count  = count
        self.value  = default
        self.format = str(self.count) + self.type

        assert self.type in 'xcbB?hHiIqQfds'

    def pack(self, big_endian=True):
        """ Pack the field value into a raw byte string """
        fmt = '>' if big_endian else '<'
        fmt += self.format
        return struct.pack(fmt, self.value)

    def unpack(self, value, big_endian=True):
        """ Unpack a given value into this fields value store """
        fmt = '>' if big_endian else '<'
        fmt += self.format
        self.value = struct.unpack(fmt, value)

    def size(self):
        """ Fetch the size of this field """
        if self.type in 'xcbB?s':
            return self.count
        elif self.type in 'hH':
            return 2 * self.count
        elif self.type in 'iIf':
            return 4 * self.count
        elif self.type in 'qQd':
            return 8 * self.count

class Padding(Field):
    """ Padding Field Type (1 Byte) """
    def __init__(self, name, count=1):
        super(Padding, self).__init__(name, 'x', count, None)

class Char(Field):
    """ Character Field Type (1 Byte) """
    def __init__(self, name, count=1, default=None):
        super(Char, self).__init__(name, 'c', count, default)

class Bool(Field):
    """ Boolean Field Type (1 Byte) """
    def __init__(self, name, count=1, default=None):
        super(Bool, self).__init__(name, '?', count, default)

class Int8(Field):
    """ Signed Integer Type (1 Byte) """
    def __init__(self, name, count=1, default=None):
        super(Int8, self).__init__(name, 'b', count, default)

class UInt8(Field):
    """ Unsigned Integer Type (1 Byte) """
    def __init__(self, name, count=1, default=None):
        super(UInt8, self).__init__(name, 'B', count, default)

class Int16(Field):
    """ Signed Integer Type (2 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(Int16, self).__init__(name, 'h', count, default)

class UInt16(Field):
    """ Unsigned Integer Type (2 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(UInt16, self).__init__(name, 'H', count, default)

class Int32(Field):
    """ Signed Integer Type (4 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(Int32, self).__init__(name, 'i', count, default)

class UInt32(Field):
    """ Unsigned Integer Type (4 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(UInt32, self).__init__(name, 'I', count, default)

class Int64(Field):
    """ Signed Integer Type (8 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(Int64, self).__init__(name, 'q', count, default)

class UInt64(Field):
    """ Unsigned Integer Type (8 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(UInt64, self).__init__(name, 'Q', count, default)

class Float(Field):
    """ Float Type (4 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(Float, self).__init__(name, 'f', count, default)

class Double(Field):
    """ Double Type (8 Bytes) """
    def __init__(self, name, count=1, default=None):
        super(Double, self).__init__(name, 'd', count, default)

class String(Field):
    """ String Type (Variable Size) """
    def __init__(self, name, size, default=None):
        super(String, self).__init__(name, 's', size, default)
