""" String values for use in tests """
#pylint: disable=C0326
from __future__ import unicode_literals
import random
from builtins import bytes #pylint: disable=redefined-builtin
import pytest

LONG_BYTES  = b''.join([bytes([x]) for x in range(0, 255)])

def extend(value, length):
    """ Extends a string value to an exact size """
    remainder = length - len(value)
    value += b''.join([b'\x00' for _ in range(remainder)])
    value = value[:length]
    return value

@pytest.fixture
def good_values():
    """ Generate a list of good values """
    choice = random.choice([b'Hello World!', b'', b'a', b'ab', LONG_BYTES])
    return {
        'raw'   : extend(choice, 256),
        'string': choice
    }

@pytest.fixture
def set_values():
    """ Generate a list of non default values """
    return {
        'raw'   : extend(b'Hello World', 256),
        'string': b'Hello World'
    }

@pytest.fixture
def good_data():
    """ Generate random length data """
    size = random.randint(1, 128)
    data = b''.join([bytes([x]) for x in range(1, size+1)])
    return data
