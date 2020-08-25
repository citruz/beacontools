"""All low level structures used for parsing eddystone packets."""
from construct import Struct, Byte, Switch, OneOf, Int8sl, Array, \
                      GreedyString, Int16ub, Int16ul, Int32ub

from ..const import EDDYSTONE_URL_SCHEMES, EDDYSTONE_TLM_UNENCRYPTED, EDDYSTONE_TLM_ENCRYPTED

# pylint: disable=invalid-name

EddystoneUIDFrame = Struct(
    "tx_power" / Int8sl,
    "namespace" / Array(10, Byte),
    "instance" / Array(6, Byte),
    # commented out because it is not used anyway and there seem to be beacons which
    # don't send it at all (see https://github.com/citruz/beacontools/issues/39)
    # "rfu" / Array(2, Byte)
)

EddystoneURLFrame = Struct(
    "tx_power" / Int8sl,
    "url_scheme" / OneOf(Byte, list(EDDYSTONE_URL_SCHEMES)),
    "url" / GreedyString(encoding="ascii")
)

UnencryptedTLMFrame = Struct(
    "voltage" / Int16ub,
    "temperature" / Int16ub,
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
