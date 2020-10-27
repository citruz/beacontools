"""Constants."""
from enum import IntEnum


# for scanner
class ScannerMode(IntEnum):
    """Used to determine which packets should be parsed by the scanner."""
    MODE_NONE = 0
    MODE_IBEACON = 1
    MODE_EDDYSTONE = 2
    MODE_ESTIMOTE = 4
    MODE_CJMONITOR = 8
    MODE_EXPOSURE_NOTIFICATION = 16
    MODE_ALL = MODE_IBEACON | MODE_EDDYSTONE | MODE_ESTIMOTE | MODE_CJMONITOR  | MODE_EXPOSURE_NOTIFICATION


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
OCF_LE_SET_EXT_SCAN_PARAMETERS = 0x0041
OCF_LE_SET_EXT_SCAN_ENABLE = 0x0042
EVT_LE_EXT_ADVERTISING_REPORT = 0x0D
OGF_INFO_PARAM = 0x04
OCF_READ_LOCAL_VERSION = 0x01
EVT_CMD_COMPLETE = 0x0E

# for Generic Access Profile parsing
FLAGS_DATA_TYPE = 0x01
SERVICE_UUIDS_DATA_TYPE = 0x03
MORE_SERVICE_UUIDS_DATA_TYPE = 0x02
COMPLETE_SERVICE_UUIDS_DATA_TYPE = 0x03
COMPLETE_LOCALE_NAME_DATA_TYPE = 0x09
SERVICE_DATA_TYPE = 0x16
MANUFACTURER_SPECIFIC_DATA_TYPE = 0xFF

# for eddystone
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
IBEACON_MANUFACTURER_ID = b"\x4c\x00"
IBEACON_PROXIMITY_TYPE = b"\x02\x15"
CYPRESS_BEACON_DEFAULT_UUID = "00050001-0000-1000-8000-00805f9b0131"

# for Estimote
ESTIMOTE_UUID = b"\x9a\xfe"
ESTIMOTE_MANUFACTURER_ID = b"\x5d\x01"
ESTIMOTE_NEARABLE_FRAME = b"\x01"
ESTIMOTE_NEARABLE_BATTERY_SERVICE_UUID = b"\x0f\x18"

ESTIMOTE_TELEMETRY_FRAME = 0x2
ESTIMOTE_TELEMETRY_SUBFRAME_A = 0
ESTIMOTE_TELEMETRY_SUBFRAME_B = 1

# for Control-J Monitor
CJ_SERVICE_UUID = b"\x1A\x18\x00\x18"
CJ_MANUFACTURER_ID = b"\x72\x04"
CJ_TEMPHUM_TYPE = 0x10fe

# for COVID-19 Exposure Notifications
# see https://blog.google/documents/70/Exposure_Notification_-_Bluetooth_Specification_v1.2.2.pdf
EXPOSURE_NOTIFICATION_UUID = b"\x6f\xfd"
