from construct import GreedyRange, Struct, Byte, Array, Switch, Const, OneOf, Range, Int16ul, Int32ul, GreedyString

from ..const import *

EddystoneUIDFrame = Struct(
    "tx_power" / Byte,
    "namespace" / Byte[10],
    "instance" / Byte[6],
    "rfu" / Const(b"\x00\x00")
)

EddystoneURLFrame = Struct(
    "tx_power" / Byte,
    "url_scheme" / OneOf(Byte, list(URL_SCHEMES)),
    "url" / GreedyString(encoding="ascii")
)

UnencryptedTLMFrame = Struct(
    "voltage" / Int16ul,
    "temperature" / Int16ul,
    "advertising_count" / Int32ul,
    "seconds_since_boot" / Int32ul,
)

EncryptedTLMFrame = Struct(
    "encrypted_data" / Byte[12],
    "salt" / Int16ul,
    "mic" / Int16ul
)

EddystoneTLMFrame = Struct(
    "tlm_version" / Byte,
    "data" / Switch(lambda ctx: ctx.tlm_version,
        {
            TLM_UNENCRYPTED: UnencryptedTLMFrame,
            TLM_ENCRYPTED: EncryptedTLMFrame,
        }
    )
)


ServiceData = Struct(
    "eddystone_identifier" / Const(EDDYSTONE_UUID),
    "frame_type" / Byte,
    "frame" / Switch(lambda ctx: ctx.frame_type,
        {
            UID_FRAME: EddystoneUIDFrame,
            URL_FRAME: EddystoneURLFrame,
            TLM_FRAME: EddystoneTLMFrame,
        }
    )

)

LTV = Struct(
    "length" / Byte,
    "type" / Byte,
    "value" / Switch(lambda ctx: ctx.type,
        {
            FLAGS_DATA_TYPE: Const(b"\x06"),
            SERVICE_UUIDS_DATA_TYPE: Const(EDDYSTONE_UUID),
            SERVICE_DATA_TYPE: ServiceData
        }
    ),
)

EddystoneFrame = LTV[:]

