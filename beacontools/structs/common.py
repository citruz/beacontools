"""Definiton of the length-type-value structure used by all beacon types."""
from construct import Struct, Byte, Switch, OneOf, Array, Bytes, GreedyRange

from .eddystone import EddystoneUIDFrame, EddystoneURLFrame, EddystoneTLMFrame, EddystoneEIDFrame
from .estimote import EstimoteTelemetryFrame, EstimoteNearableFrame
from ..const import SERVICE_DATA_TYPE, MANUFACTURER_SPECIFIC_DATA_TYPE, EDDYSTONE_UUID, \
                    ESTIMOTE_UUID, EDDYSTONE_UID_FRAME, EDDYSTONE_URL_FRAME, EDDYSTONE_TLM_FRAME, \
                    EDDYSTONE_EID_FRAME, ESTIMOTE_TELEMETRY_FRAME, ESTIMOTE_MANUFACTURER_BYTES

# pylint: disable=invalid-name

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

ManufacturerSpecificData = Struct(
    "company_identifier" / Bytes(2),
    "data" / Switch(lambda ctx: ctx.company_identifier, {
        ESTIMOTE_MANUFACTURER_BYTES: EstimoteNearableFrame
    })
)

LTV = Struct(
    "length" / Byte,
    "type" / Byte,
    "value" / Switch(lambda ctx: ctx.type, {
        SERVICE_DATA_TYPE: ServiceData,
        MANUFACTURER_SPECIFIC_DATA_TYPE: ManufacturerSpecificData,
    }, default=Array(lambda ctx: ctx.length - 1, Byte)),
)

LTVFrame = GreedyRange(LTV)
