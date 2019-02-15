""" Tools for making value choices in tests """
#pylint: disable=C0326
import random
import pytest

# Minimum values
MIN_CHAR  = '\x00'
MIN_INT8  = -2**7
MIN_INT16 = -2**15
MIN_INT32 = -2**31
MIN_INT64 = -2**63

# Maximum values
MAX_CHAR   = '\xff'
MAX_INT8   = (2**7) - 1
MAX_INT16  = (2**15) -1
MAX_INT32  = (2**31) - 1
MAX_INT64  = (2**63) - 1
MAX_UINT8  = (2**8) - 1
MAX_UINT16 = (2**16) - 1
MAX_UINT32 = (2**32) - 1
MAX_UINT64 = (2**64) - 1

@pytest.fixture
def good_values():
    """ Generate a list of good values """
    long_string = ''.join([chr(x) for x in range(1, 256)])
    return {
        "char"   : random.choice(['c', MIN_CHAR, MAX_CHAR]),
        "bool"   : random.choice([True, False]),
        "int8"   : random.choice([42, 0, MIN_INT8, MAX_INT8]),
        "int16"  : random.choice([42, 0, MIN_INT16, MAX_INT16]),
        "int32"  : random.choice([42, MIN_INT32, MAX_INT32]),
        "int64"  : random.choice([42, 0, MIN_INT64, MAX_INT64]),
        "uint8"  : random.choice([42, 0, MAX_UINT8]),
        "uint16" : random.choice([42, 0, MAX_UINT16]),
        "uint32" : random.choice([42, 0, MAX_UINT32]),
        "uint64" : random.choice([42, 0, MAX_UINT64]),
        "string" : random.choice(["Hello World!", "", "a", "ab", long_string])
    }

@pytest.fixture
def set_values():
    """ Generate a list of non default values """
    return {
        "char"   : 'c',
        "bool"   : True,
        "int8"   : 42,
        "int16"  : 42,
        "int32"  : 42,
        "int64"  : 42,
        "uint8"  : 42,
        "uint16" : 42,
        "uint32" : 42,
        "uint64" : 42,
        "string" : "Hello World"
    }

@pytest.fixture
def good_data():
    """ Generate random length data """
    size = random.randint(1, 128)
    data = b''.join([chr(x) for x in range(1, size+1)])
    return data
