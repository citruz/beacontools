"""Beacon advertisement parser."""
from construct import ConstructError

from .structs import EddystoneFrame, IBeaconAdvertisingPacket
from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, EddystoneEncryptedTLMFrame, \
                          EddystoneTLMFrame, EddystoneEIDFrame, IBeaconAdvertisement
from .const import EDDYSTONE_TLM_UNENCRYPTED, EDDYSTONE_TLM_ENCRYPTED, SERVICE_DATA_TYPE, \
                   EDDYSTONE_UID_FRAME, EDDYSTONE_TLM_FRAME, EDDYSTONE_URL_FRAME, \
                   EDDYSTONE_EID_FRAME


def parse_packet(packet):
    """Parse a beacon advertisement packet."""
    frame = parse_eddystone_packet(packet)
    if frame is None:
        frame = parse_ibeacon_packet(packet)
    return frame

# pylint: disable=too-many-return-statements
def parse_eddystone_packet(packet):
    """Parse an eddystone beacon advertisement packet."""
    try:
        frame = EddystoneFrame.parse(packet)
        for tlv in frame:
            if tlv['type'] == SERVICE_DATA_TYPE:
                data = tlv['value']
                if data['frame_type'] == EDDYSTONE_UID_FRAME:
                    return EddystoneUIDFrame(data['frame'])

                elif data['frame_type'] == EDDYSTONE_TLM_FRAME:
                    if data['frame']['tlm_version'] == EDDYSTONE_TLM_ENCRYPTED:
                        return EddystoneEncryptedTLMFrame(data['frame']['data'])
                    elif data['frame']['tlm_version'] == EDDYSTONE_TLM_UNENCRYPTED:
                        return EddystoneTLMFrame(data['frame']['data'])

                elif data['frame_type'] == EDDYSTONE_URL_FRAME:
                    return EddystoneURLFrame(data['frame'])

                elif data['frame_type'] == EDDYSTONE_EID_FRAME:
                    return EddystoneEIDFrame(data['frame'])

    except ConstructError:
        return None

    return None

def parse_ibeacon_packet(packet):
    """Parse an ibeacon beacon advertisement packet."""
    try:
        pkt = IBeaconAdvertisingPacket.parse(packet)
        return IBeaconAdvertisement(pkt)

    except ConstructError:
        return None
