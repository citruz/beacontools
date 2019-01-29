"""Utilities for byte conversion."""
from binascii import hexlify
from re import compile as compile_regex
import array
import struct

from .const import ScannerMode

# compiled regex to match lowercase MAC-addresses coming from
# bt_addr_to_string
RE_MAC_ADDR = compile_regex('(?:[0-9a-f]{2}:){5}(?:[0-9a-f]{2})')


def is_valid_mac(mac):
    """"Returns True if the given argument matches RE_MAC_ADDR, otherwise False"""
    return RE_MAC_ADDR.match(mac) is not None


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
                              EddystoneEncryptedTLMFrame, EddystoneTLMFrame, \
                              EddystoneEIDFrame, IBeaconAdvertisement, \
                              EstimoteTelemetryFrameA, EstimoteTelemetryFrameB
    return (cls in [EddystoneURLFrame, EddystoneUIDFrame, EddystoneEncryptedTLMFrame, \
                    EddystoneTLMFrame, EddystoneEIDFrame, IBeaconAdvertisement, \
                    EstimoteTelemetryFrameA, EstimoteTelemetryFrameB])


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


def get_mode(device_filter):
    """Determine which beacons the scanner should look for."""
    from .device_filters import IBeaconFilter, EddystoneFilter, BtAddrFilter, EstimoteFilter
    if device_filter is None or len(device_filter) == 0:
        return ScannerMode.MODE_ALL

    mode = ScannerMode.MODE_NONE
    for filtr in device_filter:
        if isinstance(filtr, IBeaconFilter):
            mode |= ScannerMode.MODE_IBEACON
        elif isinstance(filtr, EddystoneFilter):
            mode |= ScannerMode.MODE_EDDYSTONE
        elif isinstance(filtr, EstimoteFilter):
            mode |= ScannerMode.MODE_ESTIMOTE
        elif isinstance(filtr, BtAddrFilter):
            mode |= ScannerMode.MODE_ALL
            break

    return mode
