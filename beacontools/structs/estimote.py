from construct import Struct, Byte, Switch, Const, OneOf, Int8sl, Array, Int8ul, \
                      Int16ul, Int16ub, Int32ub, GreedyString, GreedyRange, Probe, \
                      IfThenElse

from ..const import ESTIMOTE_TELEMETRY_SUBFRAME_A, ESTIMOTE_TELEMETRY_SUBFRAME_B

# pylint: disable=invalid-name

EstimoteTelemetrySubFrameA = Struct(
    Probe(),

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