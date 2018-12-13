"""Constants."""
from enum import IntEnum


# for scanner
class ScannerMode(IntEnum):
    """Used to determine which packets should be parsed by the scanner."""
    MODE_NONE = 0
    MODE_IBEACON = 1
    MODE_EDDYSTONE = 2
    MODE_ESTIMOTE = 4
    MODE_ALL = MODE_IBEACON | MODE_EDDYSTONE | MODE_ESTIMOTE


# hci le scan parameters
class ScanType(IntEnum):
    """Determines which type of scan should be executed."""
    PASSIVE = 0x00
    ACTIVE = 0x01


class ScanFilter(IntEnum):
    """Determines if only white-listed MAC addresses will be filtered or not"""
    ALL = 0x00
    WHITELIST_ONLY = 0x01


class BluetoothAddressType(IntEnum):
    """Determines the scanner MAC-address"""
    PUBLIC = 0x00  # with device MAC-address
    RANDOM = 0x01  # with a random MAC-address


# used for window and interval (i.e. 0x10 * 0.625 = 10ms, 10ms / 0.625 = 0x10)
MS_FRACTION_DIVIDER = 0.625

LE_META_EVENT = 0x3e
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
EVT_LE_ADVERTISING_REPORT = 0x02

# for eddystone
FLAGS_DATA_TYPE = 0x01
SERVICE_UUIDS_DATA_TYPE = 0x03
SERVICE_DATA_TYPE = 0x16

EDDYSTONE_UUID = b"\xaa\xfe"

EDDYSTONE_UID_FRAME = 0x00
EDDYSTONE_URL_FRAME = 0x10
EDDYSTONE_TLM_FRAME = 0x20
EDDYSTONE_EID_FRAME = 0x30
EDDYSTONE_RESERVED_FRAME = 0x20
EDDYSTONE_TLM_UNENCRYPTED = 0x00
EDDYSTONE_TLM_ENCRYPTED = 0x01

EDDYSTONE_URL_SCHEMES = {
    0x00: "http://www.",
    0x01: "https://www.",
    0x02: "http://",
    0x03: "https://",
}

EDDYSTONE_TLD_ENCODINGS = {
    0x00: ".com/",
    0x01: ".org/",
    0x02: ".edu/",
    0x03: ".net/",
    0x04: ".info/",
    0x05: ".biz/",
    0x06: ".gov/",
    0x07: ".com",
    0x08: ".org",
    0x09: ".edu",
    0x0a: ".net",
    0x0b: ".info",
    0x0c: ".biz",
    0x0d: ".gov",
}

# for iBeacons
IBEACON_COMPANY_ID = b"\x4c\x00"
IBEACON_PROXIMITY_TYPE = b"\x02\x15"
CYPRESS_BEACON_DEFAULT_UUID = "00050001-0000-1000-8000-00805f9b0131"

# for Estimote
ESTIMOTE_UUID = b"\x9a\xfe"

ESTIMOTE_TELEMETRY_FRAME = 0x2
ESTIMOTE_TELEMETRY_SUBFRAME_A = 0
ESTIMOTE_TELEMETRY_SUBFRAME_B = 1
