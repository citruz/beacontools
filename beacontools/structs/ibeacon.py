"""All low level structures used for parsing eddystone packets."""
from construct import Struct, Byte, Const, Int8sl, Array, Int16ub

from ..const import IBEACON_COMPANY_ID, IBEACON_PROXIMITY_TPYE

# pylint: disable=invalid-name

IBeaconAdvertisingPacket = Struct(
    "flags" / Const(b"\x02\x01\x06"),
    "length" / Const(b"\x1A"),
    "type" / Const(b"\xFF"),
    "company_id" / Const(IBEACON_COMPANY_ID),
    "beacon_type" / Const(IBEACON_PROXIMITY_TPYE),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "tx_power" / Int8sl,
)
