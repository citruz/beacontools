"""Beacon advertisement parser."""
from construct import ConstructError

from .structs import LTVFrame, IBeaconAdvertisingPacket
from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, EddystoneEncryptedTLMFrame, \
                          EddystoneTLMFrame, EddystoneEIDFrame, IBeaconAdvertisement, \
                          EstimoteTelemetryFrameA, EstimoteTelemetryFrameB
from .const import EDDYSTONE_TLM_UNENCRYPTED, EDDYSTONE_TLM_ENCRYPTED, SERVICE_DATA_TYPE, \
                   EDDYSTONE_UID_FRAME, EDDYSTONE_TLM_FRAME, EDDYSTONE_URL_FRAME, \
                   EDDYSTONE_EID_FRAME, EDDYSTONE_UUID, ESTIMOTE_UUID, ESTIMOTE_TELEMETRY_FRAME, \
                   ESTIMOTE_TELEMETRY_SUBFRAME_A, ESTIMOTE_TELEMETRY_SUBFRAME_B


def parse_packet(packet):
    """Parse a beacon advertisement packet."""
    frame = parse_ltv_packet(packet)
    if frame is None:
        frame = parse_ibeacon_packet(packet)
    return frame

def parse_ltv_packet(packet):
    """Parse a tag-length-value style beacon packet."""
    try:
        frame = LTVFrame.parse(packet)
        for ltv in frame:
            if ltv['type'] == SERVICE_DATA_TYPE:
                data = ltv['value']

                if data["service_identifier"] == EDDYSTONE_UUID:
                    return parse_eddystone_service_data(data)

                elif data["service_identifier"] == ESTIMOTE_UUID:
                    return parse_estimote_service_data(data)

    except ConstructError:
        return None

    return None

def parse_eddystone_service_data(data):
    """Parse Eddystone service data."""
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
    else:
        return None

def parse_estimote_service_data(data):
    """Parse Estimote service data."""
    if data['frame_type'] & 0xF == ESTIMOTE_TELEMETRY_FRAME:
        protocol_version = (data['frame_type'] & 0xF0) >> 4
        if data['frame']['subframe_type'] == ESTIMOTE_TELEMETRY_SUBFRAME_A:
            return EstimoteTelemetryFrameA(data['frame'], protocol_version)
        elif data['frame']['subframe_type'] == ESTIMOTE_TELEMETRY_SUBFRAME_B:
            return EstimoteTelemetryFrameB(data['frame'], protocol_version)
    return None

def parse_ibeacon_packet(packet):
    """Parse an ibeacon beacon advertisement packet."""
    try:
        pkt = IBeaconAdvertisingPacket.parse(packet)
        return IBeaconAdvertisement(pkt)

    except ConstructError:
        return None
