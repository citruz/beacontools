"""All low level structures used for parsing Estimote packets."""
from construct import Struct, Byte, Switch, Int8sl, Array, Int8ul, Const, Int16ul

from ..const import ESTIMOTE_TELEMETRY_SUBFRAME_A, ESTIMOTE_TELEMETRY_SUBFRAME_B, \
                    ESTIMOTE_NEARABLE_FRAME

# pylint: disable=invalid-name

EstimoteTelemetrySubFrameA = Struct(
    "acceleration" / Array(3, Int8sl),
    "previous_motion" / Byte,
    "current_motion" / Byte,
    "combined_fields" / Array(5, Byte),
)

EstimoteTelemetrySubFrameB = Struct(
    "magnetic_field" / Array(3, Int8sl),
    "ambient_light" / Int8ul,
    "combined_fields" / Array(5, Byte),
    "battery_level" / Int8ul,
)

EstimoteTelemetryFrame = Struct(
    "identifier" / Array(8, Byte),
    "subframe_type" / Byte,
    "sub_frame" / Switch(lambda ctx: ctx.subframe_type, {
        ESTIMOTE_TELEMETRY_SUBFRAME_A: EstimoteTelemetrySubFrameA,
        ESTIMOTE_TELEMETRY_SUBFRAME_B: EstimoteTelemetrySubFrameB,
    })
)

EstimoteNearableFrame = Struct(
    Const(ESTIMOTE_NEARABLE_FRAME),
    "identifier" / Array(8, Byte),
    "hardware_version" / Int8ul,
    "firmware_version" / Int8ul,
    "temperature" / Int16ul,
    "is_moving" / Int8ul,
)
