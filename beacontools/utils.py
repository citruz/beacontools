"""Utilities for byte conversion."""
from binascii import hexlify
import array


def data_to_hexstring(data):
    """Convert an array of binary data to the hex representation as a string."""
    return hexlify(array.array('B', data).tostring()).decode('ascii')

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
                              EddystoneEncryptedTLMFrame, EddystoneTLMFrame
    return (cls in [EddystoneURLFrame, EddystoneUIDFrame, EddystoneEncryptedTLMFrame, \
                    EddystoneTLMFrame])
