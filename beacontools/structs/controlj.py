"""All low level structures used for parsing control-j Monitor packets."""
from construct import Struct, Int8ul, Int16ul, Switch

from ..const import CJ_TEMPHUM_TYPE

# pylint: disable=invalid-name

CJMonitorTempHum = Struct(
    "temperature" / Int16ul,
    "humidity" / Int8ul,
    "light" / Int8ul,
)

CJMonitorMSD = Struct(
    "beacon_type" / Int16ul,
    "data" / Switch(lambda ctx: ctx.beacon_type, {
        CJ_TEMPHUM_TYPE: CJMonitorTempHum,
    }),
)
