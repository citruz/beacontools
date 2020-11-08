"""Base class for the Monitoring component"""
import threading

from ahocorapy.keywordtree import KeywordTree

from .const import (CJ_MANUFACTURER_ID, EDDYSTONE_UUID,
                    ESTIMOTE_MANUFACTURER_ID, ESTIMOTE_UUID,
                    EXPOSURE_NOTIFICATION_UUID,
                    IBEACON_MANUFACTURER_ID, IBEACON_PROXIMITY_TYPE,
                    MANUFACTURER_SPECIFIC_DATA_TYPE, ScannerMode)
from .device_filters import BtAddrFilter
from .packet_types import (EddystoneEIDFrame, EddystoneEncryptedTLMFrame,
                           EddystoneTLMFrame, EddystoneUIDFrame,
                           EddystoneURLFrame)
from .parser import parse_packet
from .utils import get_mode, is_one_of

class MonitorBase(threading.Thread):
    """Continously scan for BLE advertisements."""

    def __init__(self, callback, device_filter, packet_filter):
        """Construct interface object."""

        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = True
        self.callback = callback

        # list of beacons to monitor
        self.device_filter = device_filter
        self.mode = get_mode(device_filter)
        # list of packet types to monitor
        self.packet_filter = packet_filter
        # keep track of Eddystone Beacon <-> bt addr mapping
        self.eddystone_mappings = []

        # construct an aho-corasick search tree for efficient prefiltering
        service_uuid_prefix = b"\x03\x03"
        self.kwtree = KeywordTree()
        if self.mode & ScannerMode.MODE_IBEACON:
            self.kwtree.add(bytes([MANUFACTURER_SPECIFIC_DATA_TYPE]) + IBEACON_MANUFACTURER_ID + IBEACON_PROXIMITY_TYPE)
        if self.mode & ScannerMode.MODE_EDDYSTONE:
            self.kwtree.add(service_uuid_prefix + EDDYSTONE_UUID)
        if self.mode & ScannerMode.MODE_ESTIMOTE:
            self.kwtree.add(service_uuid_prefix + ESTIMOTE_UUID)
            self.kwtree.add(bytes([MANUFACTURER_SPECIFIC_DATA_TYPE]) + ESTIMOTE_MANUFACTURER_ID)
        if self.mode & ScannerMode.MODE_CJMONITOR:
            self.kwtree.add(bytes([MANUFACTURER_SPECIFIC_DATA_TYPE]) + CJ_MANUFACTURER_ID)
        if self.mode & ScannerMode.MODE_EXPOSURE_NOTIFICATION:
            self.kwtree.add(service_uuid_prefix + EXPOSURE_NOTIFICATION_UUID)
        self.kwtree.finalize()

    def process_packet(self, payload: bytes, bt_addr: str, rssi: int):
        """Parse the packet and call callback if one of the filters matches."""

        # check if this could be a valid packet before parsing
        # this reduces the CPU load significantly
        if not self.kwtree.search(payload):
            return

        # strip bluetooth address and parse packet
        packet = parse_packet(payload)

        # return if packet was not an beacon advertisement
        if not packet:
            return

        # we need to remeber which eddystone beacon has which bt address
        # because the TLM and URL frames do not contain the namespace and instance
        self.save_bt_addr(packet, bt_addr)
        # properties holds the identifying information for a beacon
        # e.g. instance and namespace for eddystone; uuid, major, minor for iBeacon
        properties = self.get_properties(packet, bt_addr)

        if self.device_filter is None and self.packet_filter is None:
            # no filters selected
            self.callback(bt_addr, rssi, packet, properties)

        elif self.device_filter is None:
            # filter by packet type
            if is_one_of(packet, self.packet_filter):
                self.callback(bt_addr, rssi, packet, properties)
        else:
            # filter by device and packet type
            if self.packet_filter and not is_one_of(packet, self.packet_filter):
                # return if packet filter does not match
                return

            # iterate over filters and call .matches() on each
            for filtr in self.device_filter:
                if isinstance(filtr, BtAddrFilter):
                    if filtr.matches({'bt_addr':bt_addr}):
                        self.callback(bt_addr, rssi, packet, properties)
                        return

                elif filtr.matches(properties):
                    self.callback(bt_addr, rssi, packet, properties)
                    return

    def save_bt_addr(self, packet, bt_addr):
        """Add to the list of mappings."""
        if isinstance(packet, EddystoneUIDFrame):
            # remove out old mapping
            new_mappings = [m for m in self.eddystone_mappings if m[0] != bt_addr]
            new_mappings.append((bt_addr, packet.properties))
            self.eddystone_mappings = new_mappings

    def get_properties(self, packet, bt_addr):
        """Get properties of beacon depending on type."""
        if is_one_of(packet, [EddystoneTLMFrame, EddystoneURLFrame, \
                              EddystoneEncryptedTLMFrame, EddystoneEIDFrame]):
            # here we retrieve the namespace and instance which corresponds to the
            # eddystone beacon with this bt address
            return self.properties_from_mapping(bt_addr)
        else:
            return packet.properties

    def properties_from_mapping(self, bt_addr):
        """Retrieve properties (namespace, instance) for the specified bt address."""
        for addr, properties in self.eddystone_mappings:
            if addr == bt_addr:
                return properties
        return None

    def terminate(self):
        """Signal runner to stop and join thread."""
        self.toggle_scan(False)
        self.keep_going = False
        self.join()

    def toggle_scan(self, _enable):
        """Start or stop the scan"""
        raise NotImplementedError("This must be implemented by the OS specific monitor")
