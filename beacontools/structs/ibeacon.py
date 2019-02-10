"""All low level structures used for parsing ibeacon packets."""
from construct import Struct, Byte, Const, Int8sl, Array, Int16ub
from ..const import IBEACON_PROXIMITY_TYPE

# pylint: disable=invalid-name

IBeaconMSD = Struct(
    "beacon_type" / Const(IBEACON_PROXIMITY_TYPE),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "tx_power" / Int8sl,
)
