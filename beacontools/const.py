"""Constants."""

# for eddystone
FLAGS_DATA_TYPE = 0x01
SERVICE_UUIDS_DATA_TYPE = 0x03
SERVICE_DATA_TYPE = 0x16

EDDYSTONE_UUID = b"\xaa\xfe"

EDDYSTONE_UID_FRAME = 0x00
EDDYSTONE_URL_FRAME = 0x10
EDDYSTONE_TLM_FRAME = 0x20
EDDYSTONE_EID_FRAME = 0x20
EDDYSTONE_RESERVED_FRAME = 0x20
EDDYSTONE_TLM_UNENCRYPTED = 0x00
EDDYSTONE_TLM_ENCRYPTED = 0x01

EDDYSTONE_URL_SCHEMES = {
    0x00: "http://www.",
    0x01: "https://www.",
    0x02: "http://",
    0x03: "https://",
}

EDDYSTONE_TLD_ENCODINGS = {
    0x00: ".com/",
    0x01: ".org/",
    0x02: ".edu/",
    0x03: ".net/",
    0x04: ".info/",
    0x05: ".biz/",
    0x06: ".gov/",
    0x07: ".com",
    0x08: ".org",
    0x09: ".edu",
    0x0a: ".net",
    0x0b: ".info",
    0x0c: ".biz",
    0x0d: ".gov",
}
