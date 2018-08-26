"""All low level structures used for parsing eddystone packets."""
from construct import Struct, Byte, Switch, OneOf, Int8sl, Array, \
                      Int16ul, Int16ub, Int32ub, GreedyString, GreedyRange, \
                      Bytes

from ..const import EDDYSTONE_UUID, EDDYSTONE_URL_SCHEMES, EDDYSTONE_TLM_UNENCRYPTED, \
                    EDDYSTONE_TLM_ENCRYPTED, EDDYSTONE_UID_FRAME, EDDYSTONE_URL_FRAME, \
                    EDDYSTONE_TLM_FRAME, EDDYSTONE_EID_FRAME, FLAGS_DATA_TYPE, \
                    SERVICE_DATA_TYPE, SERVICE_UUIDS_DATA_TYPE, ESTIMOTE_UUID, \
                    ESTIMOTE_TELEMETRY_FRAME

from .estimote import EstimoteTelemetryFrame

# pylint: disable=invalid-name

EddystoneUIDFrame = Struct(
    "tx_power" / Int8sl,
    "namespace" / Array(10, Byte),
    "instance" / Array(6, Byte),
    "rfu" / Array(2, Byte)
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
    "data" / Switch(lambda ctx: ctx.tlm_version, {
        EDDYSTONE_TLM_UNENCRYPTED: UnencryptedTLMFrame,
        EDDYSTONE_TLM_ENCRYPTED: EncryptedTLMFrame,
    })
)

EddystoneEIDFrame = Struct(
    "tx_power" / Int8sl,
    "eid" / Array(8, Byte)
)

ServiceData = Struct(
    "service_identifier" / OneOf(Bytes(2), [EDDYSTONE_UUID, ESTIMOTE_UUID]),
    "frame_type" / Byte,
    "frame" / Switch(lambda ctx: ctx.service_identifier, {
        # eddystone frames
        EDDYSTONE_UUID: Switch(lambda ctx: ctx.frame_type, {
            EDDYSTONE_UID_FRAME: EddystoneUIDFrame,
            EDDYSTONE_URL_FRAME: EddystoneURLFrame,
            EDDYSTONE_TLM_FRAME: EddystoneTLMFrame,
            EDDYSTONE_EID_FRAME: EddystoneEIDFrame,
        }),
        # estimote frames
        ESTIMOTE_UUID: Switch(lambda ctx: ctx.frame_type & 0xF, {
            ESTIMOTE_TELEMETRY_FRAME: EstimoteTelemetryFrame,
        }),
    }),
)


LTV = Struct(
    "length" / Byte,
    "type" / Byte,
    "value" / Switch(lambda ctx: ctx.type, {
        FLAGS_DATA_TYPE: Array(lambda ctx: ctx.length -1, Byte),
        SERVICE_UUIDS_DATA_TYPE: OneOf(Bytes(2), [EDDYSTONE_UUID, ESTIMOTE_UUID]),
        SERVICE_DATA_TYPE: ServiceData
    }, default=Array(lambda ctx: ctx.length -1, Byte)),
)

LTVFrame = GreedyRange(LTV)
