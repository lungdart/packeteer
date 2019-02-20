""" Field classes - Classes used to define a packets components """
#pylint: disable=C0326
from __future__ import unicode_literals
import struct
from builtins import bytes #pylint: disable=redefined-builtin
import six

class BaseField(object):
    """
    Field Base class
    Do not derive from this class, but use the pre-existing type classes instead
    """
    def __init__(self, name, _type, count, default):
        assert _type in 'xcbB?hHiIqQfds_'
        assert isinstance(count, six.string_types) or (
            isinstance(count, six.integer_types) and count > 0)

        # Save parameters
        self.name     = name
        self.type     = _type
        self._count   = count
        self._default = default

        # Derive additional values
        self._value   = None
        self._parent  = None

    def _listify(self, value):
        """ Transforms a single value into a list of values for multi count """
        # Get a single item list
        if isinstance(value, (tuple, list)):
            listy_value = list(value)
        else:
            listy_value = [value]

        # Correct list size, filling in default values when needed
        remainder = self.count - len(listy_value)
        listy_value += [self._default for _ in range(remainder)]
        listy_value = listy_value[:self.count]
        return listy_value

    @property
    def value(self):
        """ Read only value to force set and rest commands """
        return self._value

    @property
    def count(self):
        """ Read only value to force lookup when dynamic """
        # Dynamic sizing. Lookup the value in the parent packet's appropriate
        #  field
        if isinstance(self._count, six.string_types):
            if self._parent is not None:
                return int(self._parent[self._count])
            return 0

        # Static Sizing
        return int(self._count)

    def register(self, parent):
        """ Register to a parent packet class, allows for dynamic counts """
        self._parent = parent

    def reset(self):
        """ Reset the internal value to the default """
        self.set(self._default)

    def set(self, value):
        """ Set the internal value """
        # Update an associated dynamic count field if needed
        external_count = isinstance(self._count, six.string_types)
        if external_count:
            try:
                self._parent[self._count] = len(value)
            except TypeError:
                self._parent[self._count] = 1

        # Turn the value into a list for external and multi counts
        multi_count = self.count > 1
        if external_count or multi_count:
            value = self._listify(value)

        # Set value, rollback if invalid
        old_value = self._value
        self._value = value
        try:
            self.pack()
        except struct.error:
            self._value = old_value
            raise

    def pack(self, big_endian=True):
        """ Pack the field value into a raw byte string """
        # Repeating cases use multiple values
        fmt = '>' if big_endian else '<'
        if self.count > 1:
            fmt += str(self.count) + self.type
            return struct.pack(fmt, *self._value)

        # Non-repeating cases use a single value directly
        fmt += self.type
        return struct.pack(fmt, self._value)

    def unpack(self, raw, big_endian=True):
        """ Unpack a given value into this fields value store """
        # Repeating cases store multiple values
        fmt = '>' if big_endian else '<'
        if self.count > 1:
            fmt += str(self.count) + self.type
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
        """ Padding always packs to 0x00 """
        return b''.join([b'\x00' for _ in range(self.count)])

    def unpack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Padding shouldn't unpack """
        return

class Char(BaseField):
    """ Character Field Type (1 Byte) """
    def __init__(self, name, count=1, default=b'\x00'):
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

class Raw(BaseField):
    """ Raw Data Type (Variable Size) """
    def __init__(self, name, size, default=b''):
        super(Raw, self).__init__(name, 's', size, default)

    def _listify(self, value):
        """ Legacy function to ensure raw data is always sized """
        # Expand/Truncate value to the exact size using null byte padding
        listy_value = bytes(value)
        remainder = self.count - len(value)
        listy_value += b''.join([b'\x00' for _ in range(remainder)])
        listy_value = listy_value[:self.count]
        return listy_value

    def pack(self, big_endian=True):
        """ Raw data always uses a size value, and packs with null-bytes """
        fmt = ('>' if big_endian else '<') + str(self.count) + 's'
        return struct.pack(fmt, self._value)

    def unpack(self, raw, big_endian=True):
        """ Raw data always uses a size value and packs with null bytes """
        fmt = ('>' if big_endian else '<') + str(self.count) + 's'
        self._value = struct.unpack(fmt, raw)[0]

class String(Raw):
    """ String Type (Variable Size) """
    def __init__(self, name, size, default=u'', encoding='utf8'):
        super(String, self).__init__(name, size, default)
        self.encoding = encoding

    def _listify(self, value):
        """ Legacy function to ensure unicode strings are always sized """
        return value[:self.count]

    def set(self, value):
        """ Set the strings value """
        super(String, self).set(value)

    def pack(self, big_endian=True):
        """ Pack internal unicode value into a raw byte string """
        fmt = ('>' if big_endian else '<') + str(self.count) + 's'
        raw_value = bytes(self._value, encoding=self.encoding)
        return struct.pack(fmt, raw_value)

    def unpack(self, raw, big_endian=True):
        """ Unpack a raw byte string into a unicode value """
        fmt = ('>' if big_endian else '<') + str(self.count) + 's'
        raw_value = struct.unpack(fmt, raw)[0]
        stripped = raw_value.rstrip(b'\x00')
        self._value = six.text_type(stripped.decode(self.encoding))

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
