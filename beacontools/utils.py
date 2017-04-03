"""Utilities for byte conversion."""
from binascii import hexlify
import array
import struct


def data_to_hexstring(data):
    """Convert an array of binary data to the hex representation as a string."""
    return hexlify(data_to_binstring(data)).decode('ascii')

def data_to_uuid(data):
    """Convert an array of binary data to the iBeacon uuid format."""
    string = data_to_hexstring(data)
    return string[0:8]+'-'+string[8:12]+'-'+string[12:16]+'-'+string[16:20]+'-'+string[20:32]

def data_to_binstring(data):
    """Convert an array of binary data to a binary string."""
    return array.array('B', data).tostring()

def bt_addr_to_string(addr):
    """Convert a binary string to the hex representation."""
    addr_str = array.array('B', addr)
    addr_str.reverse()
    hex_str = hexlify(addr_str.tostring()).decode('ascii')
    # insert ":" seperator between the bytes
    return ':'.join(a+b for a, b in zip(hex_str[::2], hex_str[1::2]))

def is_one_of(obj, types):
    """Return true iff obj is an instance of one of the types."""
    for type_ in types:
        if isinstance(obj, type_):
            return True
    return False

def is_packet_type(cls):
    """Check if class is one the packet types."""
    from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, \
                              EddystoneEncryptedTLMFrame, EddystoneTLMFrame, IBeaconAdvertisement
    return (cls in [EddystoneURLFrame, EddystoneUIDFrame, EddystoneEncryptedTLMFrame, \
                    EddystoneTLMFrame, IBeaconAdvertisement])

def to_int(string):
    """Convert a one element byte string to int for python 2 support."""
    if isinstance(string, str):
        return ord(string[0])
    else:
        return string

def bin_to_int(string):
    """Convert a one element byte string to signed int for python 2 support."""
    if isinstance(string, str):
        return struct.unpack("b", string)[0]
    else:
        return struct.unpack("b", bytes([string]))[0]
