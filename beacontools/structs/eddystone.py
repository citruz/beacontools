"""All low level structures used for parsing eddystone packets."""
from construct import Struct, Byte, Switch, Const, OneOf, Int8sl, Array, \
                      Int16ul, Int16ub, Int32ub, GreedyString, GreedyRange

from ..const import EDDYSTONE_UUID, EDDYSTONE_URL_SCHEMES, EDDYSTONE_TLM_UNENCRYPTED, \
                    EDDYSTONE_TLM_ENCRYPTED, EDDYSTONE_UID_FRAME, EDDYSTONE_URL_FRAME, \
                    EDDYSTONE_TLM_FRAME, EDDYSTONE_EID_FRAME, FLAGS_DATA_TYPE, \
                    SERVICE_DATA_TYPE, SERVICE_UUIDS_DATA_TYPE

# pylint: disable=invalid-name

EddystoneUIDFrame = Struct(
    "tx_power" / Int8sl,
    "namespace" / Array(10, Byte),
    "instance" / Array(6, Byte),
    "rfu" / Const(b"\x00\x00")
)

EddystoneURLFrame = Struct(
    "tx_power" / Int8sl,
    "url_scheme" / OneOf(Byte, list(EDDYSTONE_URL_SCHEMES)),
    "url" / GreedyString(encoding="ascii")
)

UnencryptedTLMFrame = Struct(
    "voltage" / Int16ub,
    "temperature" / Int16ul,
    "advertising_count" / Int32ub,
    "seconds_since_boot" / Int32ub,
)

EncryptedTLMFrame = Struct(
    "encrypted_data" / Array(12, Byte),
    "salt" / Int16ul,
    "mic" / Int16ul
)

EddystoneTLMFrame = Struct(
    "tlm_version" / Byte,
    "data" / Switch(lambda ctx: ctx.tlm_version,
                    {
                        EDDYSTONE_TLM_UNENCRYPTED: UnencryptedTLMFrame,
                        EDDYSTONE_TLM_ENCRYPTED: EncryptedTLMFrame,
                    }
                   )
)

EddystoneEIDFrame = Struct(
    "tx_power" / Int8sl,
    "eid" / Array(8, Byte)
)

ServiceData = Struct(
    "eddystone_identifier" / Const(EDDYSTONE_UUID),
    "frame_type" / Byte,
    "frame" / Switch(lambda ctx: ctx.frame_type,
                     {
                         EDDYSTONE_UID_FRAME: EddystoneUIDFrame,
                         EDDYSTONE_URL_FRAME: EddystoneURLFrame,
                         EDDYSTONE_TLM_FRAME: EddystoneTLMFrame,
                         EDDYSTONE_EID_FRAME: EddystoneEIDFrame,
                     }
                    )
)

LTV = Struct(
    "length" / Byte,
    "type" / Byte,
    "value" / Switch(lambda ctx: ctx.type,
                     {
                         FLAGS_DATA_TYPE: Const(b"\x06") or Const(b"\x1a"),
                         SERVICE_UUIDS_DATA_TYPE: Const(EDDYSTONE_UUID),
                         SERVICE_DATA_TYPE: ServiceData
                     }
                    ),
)

EddystoneFrame = GreedyRange(LTV)
