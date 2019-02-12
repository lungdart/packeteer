class Packet(object):
    """
    Packet Base class
    Do not derive from this base class, use BigEndian and LittleEndian instead
    """
    big_endian = None
    name = "Unknown Packet"
    fields = []

    def __init__(self, **kwargs):
        self.clear()

        for name, value in kwargs:
            for field in self.fields:
                if name == field.name:
                    field = value

    def __str__(self):
        raw = self.pack()
        msg = b''.join(['\\x{:02x}'.format(x) for x in raw])
        print msg

    def __repr__(self):
        msg = "### {} ###".format(self.name)
        for field in self.fields:
            msg += "{}: {}".format(field.name, field.value)
        print msg

    def __getitem__(self, key):
        # Access by index, auto raises
        if isinstance(key, int):
            return self.fields[key]
        # Access by field name
        elif isinstance(key, basestring):
            for field in self.fields:
                if field.name == key:
                    return field
        # This point is only reached in bad requests, or bad field names
        raise KeyError(key)

    def __setitem__(self, key, value):
        # Access by index, auto raises
        if isinstance(key, int):
            self.fields[key] = value
            return
        # Access by field name
        elif isinstance(key, basestring):
            for field in self.fields:
                if field.name == key:
                    field = value
                    return
        # This point is only reached in bad requests, or bad field names
        raise KeyError(key)

    def __iter__(self):
        return self.fields.__iter__()

    def pack(self):
        """ Fetch the packed raw byte string of the packet """
        raw = b''
        for field in self.fields:
            raw += field.pack(big_endial=self.big_endian)
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
            field.clear()

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
        result = []
        for field in self.fields:
            result.append(field.name)
        return result

    def values(self):
        """ Fetch a list of the field values """
        result = []
        for field in self.fields:
            result.append(field.value)
        return result

    def items(self):
        """ Fetch a list of field name value pairs """
        result = []
        for field in self.fields:
            pair = (field.name, field.value)
            result.append(pair)
        return result

    def iterkeys(self):
        """ Fetch a field name iterator """
        for field in self.fields:
            yield field.name

    def itervalues(self):
        """ Fetch a field value iterator """
        for field in self.fields:
            yield field.value

    def iteritems(self):
        """ Fetch a field name, value pair iterator """
        for field in self.fields:
            yield (field.name, field.value)

    def dict(self):
        """ Fetch the packet as an ordered dictionary """
        result = {}
        for field in self.fields:
            result[field.name] = field.value
        return result

class BigEndian(Packet):
    """ Big Endian Packet Class """
    big_endian = True

class LittleEndian(Packet):
    """ Little Endian Packet Class """
    big_endian = False
