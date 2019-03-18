""" Field classes - Classes used to define a packets components """
#pylint: disable=C0326
from __future__ import unicode_literals
import struct
import copy
from builtins import bytes #pylint: disable=redefined-builtin
import six

class Field(object):
    """
    Field Base class
    Do not derive from this class, but use the pre-existing type classes instead
    """
    def __init__(self, name=None, _type=None, default=None):
        if _type is not None:
            assert _type in 'xcbB?hHiIqQfds'

        # Save parameters
        self.name     = name
        self.type     = _type
        self._default = default
        self._parent  = None
        self._value   = None
        self.reset()

    @property
    def value(self):
        """ Read only value to force set and rest commands """
        return self._value

    def _register(self, parent):
        """ Register the parent packet as owning this field """
        self._parent = parent

    def reset(self):
        """ Reset the internal value to the default """
        self.set(self._default)

    def set(self, value):
        """ Set the internal value """
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
        if self.type is None:
            raise RuntimeError("Invalid field type {}".format(self.type))
        fmt = ('>' if big_endian else '<') + self.type
        return struct.pack(fmt, self._value)

    def unpack(self, raw, big_endian=True):
        """ Unpack a given value into this fields value store """
        if self.type is None:
            raise RuntimeError("Invalid field type {}".format(self.type))
        fmt = ('>' if big_endian else '<') + self.type
        part = raw[:self.size()]
        self._value = struct.unpack(fmt, part)[0]

    def size(self):
        """ Fetch the size of this field """
        if self.type in 'xcbB?s':
            return 1
        if self.type in 'hH':
            return 2
        if self.type in 'iIf':
            return 4
        if self.type in 'qQd':
            return 8
        raise RuntimeError("Invalid field type {}".format(self.type))

class SizedField(Field):
    """ Variable sized field """
    def __init__(self, size=None, **kwargs):
        self._size = size
        super(SizedField, self).__init__(**kwargs)

    def size(self):
        """ Fetch the size of the field """
        if self._size is None:
            return len(self._value)
        if isinstance(self._size, six.string_types) and self._parent is not None:
            return int(self._parent[self._size])
        if isinstance(self._size, six.string_types) and self._parent is None:
            return 0
        return self._size

    def _size_val(self, value): #pylint: disable=no-self-use
        """ Override this to handle value sizing when set """
        return value

    def set(self, value):
        """ Set the internal value """
        # Size the value correctly, and assure any dynamic sizing references
        # are updated
        sized_value = self._size_val(value)
        if isinstance(self._size, six.string_types) and self._parent is not None:
            self._parent[self._size] = len(sized_value)
        # Set the value normally
        super(SizedField, self).set(sized_value)

# Standard type fields
class Char(Field):
    """ Character Field Type (1 Byte) """
    def __init__(self, name=None, default=b'\x00', **kwargs):
        super(Char, self).__init__(name=name, _type='c', default=default, **kwargs)

class Bool(Field):
    """ Boolean Field Type (1 Byte) """
    def __init__(self, name=None, default=False, **kwargs):
        super(Bool, self).__init__(name=name, _type='?', default=default, **kwargs)

class Int8(Field):
    """ Signed Integer Type (1 Byte) """
    def __init__(self, name=None, default=0, **kwargs):
        super(Int8, self).__init__(name=name, _type='b', default=default, **kwargs)

class UInt8(Field):
    """ Unsigned Integer Type (1 Byte) """
    def __init__(self, name=None, default=0, **kwargs):
        super(UInt8, self).__init__(name=name, _type='B', default=default, **kwargs)

class Int16(Field):
    """ Signed Integer Type (2 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(Int16, self).__init__(name=name, _type='h', default=default, **kwargs)

class UInt16(Field):
    """ Unsigned Integer Type (2 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(UInt16, self).__init__(name=name, _type='H', default=default, **kwargs)

class Int32(Field):
    """ Signed Integer Type (4 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(Int32, self).__init__(name=name, _type='i', default=default, **kwargs)

class UInt32(Field):
    """ Unsigned Integer Type (4 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(UInt32, self).__init__(name=name, _type='I', default=default, **kwargs)

class Int64(Field):
    """ Signed Integer Type (8 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(Int64, self).__init__(name=name, _type='q', default=default, **kwargs)

class UInt64(Field):
    """ Unsigned Integer Type (8 Bytes) """
    def __init__(self, name=None, default=0, **kwargs):
        super(UInt64, self).__init__(name=name, _type='Q', default=default, **kwargs)

class Float(Field):
    """ Float Type (4 Bytes) """
    def __init__(self, name=None, default=0.0, **kwargs):
        super(Float, self).__init__(name=name, _type='f', default=default, **kwargs)

class Double(Field):
    """ Double Type (8 Bytes) """
    def __init__(self, name=None, default=0.0, **kwargs):
        super(Double, self).__init__(name=name, _type='d', default=default, **kwargs)

# Specialty fields
class Padding(Field):
    """ Padding Field Type (1 Byte) """
    def __init__(self, default=b'\x00', **kwargs):
        super(Padding, self).__init__(_type='x', default=default, **kwargs)

    def pack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Padding always packs to 0x00 """
        return self._default

    def unpack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Padding shouldn't unpack """
        return

class Packet(Field):
    """ Sub-packet (Variable size) """
    def __init__(self, name=None, default=None):
        super(Packet, self).__init__(name=name, default=default)

    def size(self):
        """ Use the size of the underlying packet(s) """
        return self._value.size()

    def pack(self, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Have the packet(s) pack itself """
        if self._value is not None:
            return self._value.pack()
        return b''

    def unpack(self, raw, *args, **kwargs): #pylint: disable=arguments-differ, unused-argument
        """ Have the packet unpack the raw data """
        self._value.unpack(raw)

class Raw(SizedField):
    """ Raw Data Type (Variable Size) """
    def __init__(self, name=None, default=b'', **kwargs):
        super(Raw, self).__init__(name=name, _type='s', default=default, **kwargs)

    def _size_val(self, value):
        """ Modify value to the exact size, padding with null bytes when needed """
        # Only size the value to fit with static sizing
        if isinstance(self._size, six.integer_types):
            size = self.size()
            remainder = size - len(value)
            for _ in range(remainder):
                value += b'\x00'
            value = value[:size]
        return value

    def pack(self, big_endian=True):
        """ Raw data always uses a size value, and packs with null-bytes """
        fmt = ('>' if big_endian else '<') + str(self.size()) + 's'
        return struct.pack(fmt, self._value)

    def unpack(self, raw, big_endian=True):
        """ Raw data always uses a size value and packs with null bytes """
        size = self.size()
        fmt = ('>' if big_endian else '<') + str(size) + 's'
        part = raw[:size]
        self._value = struct.unpack(fmt, part)[0]

class String(SizedField):
    """ String Type (Variable Size) """
    def __init__(self, name=None, default=u'', encoding='utf8', **kwargs):
        self.encoding = encoding
        super(String, self).__init__(name=name, default=default, **kwargs)

    def _size_val(self, value):
        """ Modify value to the fit within the size """
        # Only size the value if a static size is given
        if isinstance(self._size, six.integer_types):
            return value[:self.size()]
        return value

    def pack(self, big_endian=True):
        """ Pack internal unicode value into a raw byte string """
        fmt = ('>' if big_endian else '<') + str(self.size()) + 's'
        raw_value = bytes(self._value, encoding=self.encoding)
        return struct.pack(fmt, raw_value)

    def unpack(self, raw, big_endian=True):
        """ Unpack a raw byte string into a unicode value """
        size = self.size()
        fmt = ('>' if big_endian else '<') + str(size) + 's'
        part = raw[:size]
        raw_value = struct.unpack(fmt, part)[0]
        stripped = raw_value.rstrip(b'\x00')
        self._value = six.text_type(stripped.decode(self.encoding))

class List(SizedField):
    """ List of fields (Variable size) """
    def __init__(self, name=None, field=None, **kwargs):
        self._field = field
        super(List, self).__init__(name=name, **kwargs)

    def _create_field(self, value=None):
        """ Create a new field instance with the optional value """
        field = copy.deepcopy(self._field)
        if value:
            field.set(value)
        field._register(self._parent) #pylint: disable=protected-access
        return field

    def _size_val(self, value):
        """ Transform value(s) into a list of appropriate fields """
        # Ensure the value is a list of fields with their internal values set
        if isinstance(value, (list, tuple)):
            fields = [self._create_field(x) for x in value]
        elif value:
            fields = [self._create_field(value)]
        else:
            fields = []

        # Only modify the size of the list if the the field has a static size
        if isinstance(self._size, six.integer_types):
            remainder = self._size - len(fields)
            for _ in range(remainder):
                field = self._create_field()
                fields.append(field)
            fields = fields[:self._size]

        return fields

    @property
    def value(self):
        """ Read only value to force set and rest commands """
        raw_values = []
        for field in self._value:
            raw_values.append(field.value)
        return raw_values

    def size(self):
        """ Size of the field is the sum of the all nested fields """
        # In order to facilitate the edge case of a dynamically sized field
        #  whose size has been updated, but the underlying list hasn't changed
        #  size yet, we generate a copy of the fields list at the expected size
        #  and use that to calculate the total size instead. The new fields
        #  aren't saved because it feels wrong to have size be a non const safe
        #  operation.
        if self._value is None:
            fields = []
        else:
            fields = self._value

        if self._size is None:
            count = len(fields)
        elif isinstance(self._size, six.string_types) and self._parent is not None:
            count = self._parent[self._size]
        elif isinstance(self._size, six.string_types) and self._parent is None:
            count = 0
        else:
            count = self._size

        remainder = count - len(fields)
        for _ in range(remainder):
            field = self._create_field()
            fields.append(field)
        fields = fields[:count]

        result = 0
        for field in fields:
            result += field.size()
        return result

    def pack(self, big_endian=True):
        """ Pack the list of sub-fields into bytes """
        data = b''
        if isinstance(self._value, (list, tuple)):
            for field in self._value:
                data += field.pack()
        return data

    def unpack(self, raw, big_endian=True):
        """ Unpack the raw data into the sub-fields """
        # Unpacking requires knowing the underlying size of the data before hand
        if self._size is None:
            raise RuntimeError("Can't unpack raw data into a field of variable size")

        if isinstance(self._size, six.string_types) and self._parent is not None:
            size = self._parent[self._size]
        elif isinstance(self._size, six.string_types) and self._parent is None:
            size = 0
        else:
            size = self._size

        start = 0
        self._value = []
        for _ in range(size):
            part = raw[start:]
            field = self._create_field()
            field.unpack(part)
            self._value.append(field)
            start += field.size()
