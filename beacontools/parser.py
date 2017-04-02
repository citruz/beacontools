from construct import ConstructError
import traceback
from .structs import EddystoneFrame
from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, EddystoneEncryptedTLMFrame, \
                          EddystoneTLMFrame
from .const import TLM_UNENCRYPTED, TLM_ENCRYPTED, SERVICE_DATA_TYPE, UID_FRAME, TLM_FRAME, URL_FRAME

def parse_packet(packet):
    try:
        frame = EddystoneFrame.parse(packet)
        for tlv in frame:
            if tlv['type'] == SERVICE_DATA_TYPE:
                data = tlv['value']
                if data['frame_type'] == UID_FRAME:
                    return EddystoneUIDFrame(data['frame'])

                elif data['frame_type'] == TLM_FRAME:
                    if data['frame']['tlm_version'] == TLM_ENCRYPTED:
                        return EddystoneEncryptedTLMFrame(data['frame']['data'])
                    elif data['frame']['tlm_version'] == TLM_UNENCRYPTED:
                        return EddystoneTLMFrame(data['frame']['data'])

                elif data['frame_type'] == URL_FRAME:
                    return EddystoneURLFrame(data['frame'])


    except ConstructError:
        traceback.print_exc()
        return None

    return None