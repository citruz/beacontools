"""All low level structures used for parsing control-j Monitor packets."""
from construct import Struct, BitStruct, Flag, BitsInteger, Const, Int8ul, Int16ul, Switch, Array, Byte, Bytes, \
    GreedyString

# pylint: disable=invalid-name

CJMonitorAdvertisingPacket = Struct(
    Const(b"\x02\x01"),  # Length 0x02 Type: 0x01 (Advertising Flags)
    "advertising_flags" / BitStruct(
        "reserved" / BitsInteger(3),
        "le_br_edr_support_host" / Flag,
        "le_br_edr_support_controller" / Flag,
        "br_edr_not_supported" / Flag,
        "le_general_discoverable_mode" / Flag,
        "le_limited_discoverable_mode" / Flag,
    ),

    Const(b"\x05\x02\x1A\x18\x00\x18"),  # 16 bit uuids
    "msd_length" / Int8ul,
    Const(b"\xff"),
    "company_id" / Int16ul,
    "beacon_type" / Int16ul,
    "temperature" / Int16ul,
    "humidity" / Int8ul,
    "light" / Int8ul,
    "namelen"/ Int8ul,
    Const(b"\x09"),
    "name" / Array(lambda ctx: ctx.namelen - 1, Byte)
)
