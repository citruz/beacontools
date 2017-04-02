"""Classes responsible for Beacon scanning."""
import threading
import logging

import bluetooth._bluetooth as bluez

from .parser import parse_packet
from .utils import bt_addr_to_string
from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, \
                          EddystoneEncryptedTLMFrame, EddystoneTLMFrame
from .device_filters import BtAddrFilter, DeviceFilter
from .utils import is_packet_type, is_one_of

LE_META_EVENT = 0x3e
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C
EVT_LE_ADVERTISING_REPORT = 0x02

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# pylint: disable=no-member

class BeaconScanner(object):
    """Scan for Beacon advertisements."""

    def __init__(self, callback, bt_device_id=0, device_filter=None, packet_filter=None):
        """Initialize scanner."""
        # check if device filters are valid
        if device_filter is not None:
            if not isinstance(device_filter, list):
                device_filter = [device_filter]
            for filtr in device_filter:
                if not isinstance(filtr, DeviceFilter):
                    raise ValueError("Device filters must be instances of DeviceFilter")

        # check if packet filters are valid
        if packet_filter is not None:
            if not isinstance(packet_filter, list):
                packet_filter = [packet_filter]
            for filtr in packet_filter:
                if not is_packet_type(filtr):
                    raise ValueError("Packet filters must be one of the packet types")

        self._mon = Monitor(callback, bt_device_id, device_filter, packet_filter)

    def start(self):
        """Start beacon scanning."""
        self._mon.start()

    def stop(self):
        """Stop beacon scanning."""
        self._mon.terminate()

class Monitor(threading.Thread):
    """Continously scan for BLE advertisements."""

    def __init__(self, callback, bt_device_id, device_filter, packet_filter):
        """Construct interface object."""
        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = True
        self.callback = callback

        # number of the bt device (hciX)
        self.bt_device_id = bt_device_id
        # list of beacons to monitor
        self.device_filter = device_filter
        # list of packet types to monitor
        self.packet_filter = packet_filter
        # bluetooth socket
        self.socket = None
        # keep track of Eddystone Beacon <-> bt addr mapping
        self.eddystone_mappings = []

    def run(self):
        """Continously scan for BLE advertisements."""
        self.socket = bluez.hci_open_dev(self.bt_device_id)

        filtr = bluez.hci_filter_new()
        bluez.hci_filter_all_events(filtr)
        bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
        self.socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filtr)

        self.toggle_scan(True)

        while self.keep_going:
            pkt = self.socket.recv(255)
            event = pkt[1]
            subevent = pkt[3]
            if event == LE_META_EVENT and subevent == EVT_LE_ADVERTISING_REPORT:
                # we have an BLE advertisement
                self.process_packet(pkt)

    def toggle_scan(self, enable):
        """Enable and disable BLE scanning."""
        if enable:
            command = "\x01\x00"
        else:
            command = "\x00\x00"
        bluez.hci_send_cmd(self.socket, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, command)

    def process_packet(self, pkt):
        """Parse the packet and call callback if one of the filters matches."""
        # check if this is an eddystone packet before parsing
        # this reduces the CPU load significantly
        if pkt[19:21] != b"\xaa\xfe":
            return

        bt_addr = bt_addr_to_string(pkt[7:13])
        # strip bluetooth address and parse packet
        packet = parse_packet(pkt[14:])

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
            self.callback(bt_addr, packet, properties)

        elif self.device_filter is None:
            # filter by packet type
            if is_one_of(packet, self.packet_filter):
                self.callback(bt_addr, packet, properties)
        else:
            # filter by device and packet type
            if self.packet_filter and not is_one_of(packet, self.packet_filter):
                # return if packet filter does not match
                return

            # iterate over filters and call .matches() on each
            for filtr in self.device_filter:
                if isinstance(filtr, BtAddrFilter):
                    if filtr.matches({'bt_addr':bt_addr}):
                        self.callback(bt_addr, packet, properties)
                        return

                elif filtr.matches(properties):
                    self.callback(bt_addr, packet, properties)
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
        if is_one_of(packet, [EddystoneTLMFrame, EddystoneURLFrame, EddystoneEncryptedTLMFrame]):
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
