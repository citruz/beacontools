"""All low level structures used for parsing ibeacon packets."""
from construct import Struct, BitStruct, Flag, BitsInteger, Byte, Const, Int8sl, Array, Int16ub
from ..const import IBEACON_COMPANY_ID, IBEACON_PROXIMITY_TYPE

# pylint: disable=invalid-name

IBeaconAdvertisingPacket = Struct(
    Const(b"\x02\x01"),  # Length 0x02 Type: 0x01 (Advertising Flags)
    "advertising_flags" / BitStruct(
        "reserved" /  BitsInteger(3),
        "le_br_edr_support_host" /  Flag,
        "le_br_edr_support_controller" /  Flag,
        "br_edr_not_supported" /  Flag,
        "le_general_discoverable_mode" /  Flag,
        "le_limited_discoverable_mode" /  Flag,
    ),
    Const(b"\x1A\xFF"),  # Len 0x1A Type: 0xFF (Manufacturer specific)
    "company_id" / Const(IBEACON_COMPANY_ID),
    "beacon_type" / Const(IBEACON_PROXIMITY_TYPE),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "tx_power" / Int8sl,
)
