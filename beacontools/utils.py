"""Utilities for byte conversion."""
from binascii import hexlify
import array

def data_to_hexstring(data):
    """Convert an array of binary data to the hex representation as a string."""
    return hexlify(array.array('B', data).tostring()).decode('ascii')

def data_to_binstring(data):
    """Convert an array of binary data to a binary string."""
    return array.array('B', data).tostring()
