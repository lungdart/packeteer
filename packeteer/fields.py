""" Field classes - Classes used to define a packets components """
#pylint: disable=C0326
import struct

class BaseField(object):
    """
    Field Base class
    Do not derive from this class, but use the pre-existing type classes instead
    """
    def __init__(self, name, _type, count, default):
        assert _type in 'xcbB?hHiIqQfds_'
        assert isinstance(count, basestring) or count > 0

        # Save parameters
        self.name     = name
        self.type     = _type
        self._count   = count
        self._default = default

        # Derive additional values
        self._value   = None
        self._parent  = None

    @property
    def value(self):
        """ Read only value to force set and rest commands """
        return self._value

    @property
    def count(self):
        """ Read only value to force lookup when dynamic """
        # Dynamic sizing. Lookup the value in the parent packet's appropriate
        #  field
        if isinstance(self._count, basestring):
            if self._parent is not None:
                return int(self._parent[self._count])
            return 0

        # Static Sizing
        return int(self._count)

    def register(self, parent):
        """ Register to a parent packet class, allows for dynamic counts """
        self._parent = parent
        self.reset()

    def reset(self):
        """ Reset the internal value to the default """
        # Update an associated dynamic count field if needed
        if isinstance(self._count, basestring):
            self._parent[self._count] = len(self._default)
        self._value = self._default

    def set(self, value):
        """ Set the internal value """
        # Update an associated dynamic count field if needed
        if isinstance(self._count, basestring):
            self._parent[self._count] = len(value)
        self._value = value

    def pack(self, big_endian=True):
        """ Pack the field value into a raw byte string """
        # Capture variables now in case they're dynamic
        count = self.count
        value = self._value

        # Repeating cases use multiple values
        fmt = '>' if big_endian else '<'
        if count > 1:
            fmt += str(count) + self.type
            return struct.pack(fmt, *value)

        # Non-repeating cases use a single value directly
        fmt += self.type
        return struct.pack(fmt, value)

    def unpack(self, raw, big_endian=True):
        """ Unpack a given value into this fields value store """
        # Capture variables now in case they're dynamic
        count = self.count

        # Repeating cases store multiple values
        fmt = '>' if big_endian else '<'
        if count > 1:
            fmt += str(count) + self.type
            self._value = list(struct.unpack(fmt, raw))

        # Non-repeating cases store a single value directly
        else:
            fmt += self.type
            self._value = struct.unpack(fmt, raw)[0]

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
        elif self.type == '_':
            return self._value.size()
        else:
            raise RuntimeError("Invalid field type {}".format(self.type))

class Padding(BaseField):
    """ Padding Field Type (1 Byte) """
    def __init__(self, count=1):
        super(Padding, self).__init__('padding', 'x', count, None)

    def pack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Padding shouldn't pack """
        return b''

    def unpack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Padding shouldn't unpack """
        return

class Char(BaseField):
    """ Character Field Type (1 Byte) """
    def __init__(self, name, count=1, default='\x00'):
        super(Char, self).__init__(name, 'c', count, default)

class Bool(BaseField):
    """ Boolean Field Type (1 Byte) """
    def __init__(self, name, count=1, default=False):
        super(Bool, self).__init__(name, '?', count, default)

class Int8(BaseField):
    """ Signed Integer Type (1 Byte) """
    def __init__(self, name, count=1, default=0):
        super(Int8, self).__init__(name, 'b', count, default)

class UInt8(BaseField):
    """ Unsigned Integer Type (1 Byte) """
    def __init__(self, name, count=1, default=0):
        super(UInt8, self).__init__(name, 'B', count, default)

class Int16(BaseField):
    """ Signed Integer Type (2 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(Int16, self).__init__(name, 'h', count, default)

class UInt16(BaseField):
    """ Unsigned Integer Type (2 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(UInt16, self).__init__(name, 'H', count, default)

class Int32(BaseField):
    """ Signed Integer Type (4 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(Int32, self).__init__(name, 'i', count, default)

class UInt32(BaseField):
    """ Unsigned Integer Type (4 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(UInt32, self).__init__(name, 'I', count, default)

class Int64(BaseField):
    """ Signed Integer Type (8 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(Int64, self).__init__(name, 'q', count, default)

class UInt64(BaseField):
    """ Unsigned Integer Type (8 Bytes) """
    def __init__(self, name, count=1, default=0):
        super(UInt64, self).__init__(name, 'Q', count, default)

class Float(BaseField):
    """ Float Type (4 Bytes) """
    def __init__(self, name, count=1, default=0.0):
        super(Float, self).__init__(name, 'f', count, default)

class Double(BaseField):
    """ Double Type (8 Bytes) """
    def __init__(self, name, count=1, default=0.0):
        super(Double, self).__init__(name, 'd', count, default)

class String(BaseField):
    """ String Type (Variable Size) """
    def __init__(self, name, size, default=''):
        super(String, self).__init__(name, 's', size, default)

    def pack(self, big_endian=True):
        """ Pack the string into the correct size and endianness """
        # Capture variables now in case they're dynamic
        count = self.count
        value = self._value

        # Strings always use a size value, and only store one string
        fmt = ('>' if big_endian else '<') + str(count) + self.type
        return struct.pack(fmt, value)

    def unpack(self, raw, big_endian=True):
        """ Unpack raw bytes into the strings value """
        # Capture variables now in case they're dynamic
        count = self.count

        # Strings always use a size value, and only store one string
        fmt = ('>' if big_endian else '<') + str(count) + 's'
        unpacked = struct.unpack(fmt, raw)[0]

        # Strip trailing null bytes for convienence
        self._value = unpacked.rstrip('\x00')

class Raw(String):
    """ Raw Data Type (Variable Size) """
    pass

class Packet(BaseField):
    """ Sub-packet (Variable size) """
    def __init__(self, name, default, count=1):
        super(Packet, self).__init__(name, '_', count, default)

    def pack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Hack the packet pack itself """
        return self._value.pack()

    def unpack(self, raw, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Have the packet unpack the raw data """
        self._value.unpack(raw)
