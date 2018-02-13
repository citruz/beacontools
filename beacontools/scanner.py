"""Classes responsible for Beacon scanning."""
import threading
import logging
from importlib import import_module

from .parser import parse_packet
from .utils import bt_addr_to_string
from .packet_types import EddystoneUIDFrame, EddystoneURLFrame, \
                          EddystoneEncryptedTLMFrame, EddystoneTLMFrame, \
                          EddystoneEIDFrame
from .device_filters import BtAddrFilter, DeviceFilter
from .utils import is_packet_type, is_one_of, to_int, bin_to_int, get_mode
from .const import MODE_IBEACON, MODE_EDDYSTONE, LE_META_EVENT, OGF_LE_CTL, \
                   OCF_LE_SET_SCAN_ENABLE, EVT_LE_ADVERTISING_REPORT, MODE_BOTH


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
            if len(device_filter) > 0:
                for filtr in device_filter:
                    if not isinstance(filtr, DeviceFilter):
                        raise ValueError("Device filters must be instances of DeviceFilter")
            else:
                device_filter = None

        # check if packet filters are valid
        if packet_filter is not None:
            if not isinstance(packet_filter, list):
                packet_filter = [packet_filter]
            if len(packet_filter) > 0:
                for filtr in packet_filter:
                    if not is_packet_type(filtr):
                        raise ValueError("Packet filters must be one of the packet types")
            else:
                packet_filter = None

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
        # do import here so that the package can be used in parsing-only mode (no bluez required)
        self.bluez = import_module('bluetooth._bluetooth')

        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = True
        self.callback = callback

        # number of the bt device (hciX)
        self.bt_device_id = bt_device_id
        # list of beacons to monitor
        self.device_filter = device_filter
        self.mode = get_mode(device_filter)
        # list of packet types to monitor
        self.packet_filter = packet_filter
        # bluetooth socket
        self.socket = None
        # keep track of Eddystone Beacon <-> bt addr mapping
        self.eddystone_mappings = []

    def run(self):
        """Continously scan for BLE advertisements."""
        self.socket = self.bluez.hci_open_dev(self.bt_device_id)

        filtr = self.bluez.hci_filter_new()
        self.bluez.hci_filter_all_events(filtr)
        self.bluez.hci_filter_set_ptype(filtr, self.bluez.HCI_EVENT_PKT)
        self.socket.setsockopt(self.bluez.SOL_HCI, self.bluez.HCI_FILTER, filtr)

        self.toggle_scan(True)

        while self.keep_going:
            pkt = self.socket.recv(255)
            event = to_int(pkt[1])
            subevent = to_int(pkt[3])
            if event == LE_META_EVENT and subevent == EVT_LE_ADVERTISING_REPORT:
                # we have an BLE advertisement
                self.process_packet(pkt)

    def toggle_scan(self, enable):
        """Enable and disable BLE scanning."""
        if enable:
            command = "\x01\x00"
        else:
            command = "\x00\x00"
        self.bluez.hci_send_cmd(self.socket, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, command)

    def process_packet(self, pkt):
        """Parse the packet and call callback if one of the filters matches."""
        # check if this could be a valid packet before parsing
        # this reduces the CPU load significantly
        if (self.mode == MODE_BOTH and \
                (pkt[19:21] != b"\xaa\xfe") and (pkt[19:23] != b"\x4c\x00\x02\x15")) \
                or (self.mode == MODE_EDDYSTONE and (pkt[19:21] != b"\xaa\xfe")) \
                or (self.mode == MODE_IBEACON and (pkt[19:23] != b"\x4c\x00\x02\x15")):
            return

        bt_addr = bt_addr_to_string(pkt[7:13])
        rssi = bin_to_int(pkt[-1])
        # strip bluetooth address and parse packet
        packet = parse_packet(pkt[14:-1])

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
