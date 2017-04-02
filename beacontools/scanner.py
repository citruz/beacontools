import threading
import struct
import logging

import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C
EVT_LE_ADVERTISING_REPORT = 0x02

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class BeaconScanner():
    """Scan for Beacon advertisements."""

    def __init__(self, bt_device_id=0, device_filter=None, packet_filter=None):
        """Initialize scanner."""
        self._mon = Monitor(bt_device_id, device_filter, packet_filter)

    @property
    def bt_device_id(self):
        return self._mon.bt_device_id

    @property
    def device_filter(self):
        return self._mon.device_filter

    @device_filter.setter
    def device_filter(self, value):
        # TODO check wether it is a list and all are beacons
        self._mon.device_filter = value

    @property
    def packet_filter(self):
        return self._mon.packet_filter

    @packet_filter.setter
    def packet_filter(self, value):
        # TODO check wether it is a list and all are packet types
        self._mon.packet_filter = value

    def start(self):
        self._mon.start()

    def stop(self):
        self._mon.terminate()

class Monitor(threading.Thread):
    """Continously scan for BLE advertisements."""

    def __init__(self, bt_device_id, device_filter, packet_filter):
        """Construct interface object."""
        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = True

        # number of the bt device (hciX)
        self.bt_device_id = bt_device_id
        # list of beacons to monitor
        self.device_filter = device_filter
        # list of packet types to monitor
        self.packet_filter = packet_filter
        # bluetooth socket
        self.socket = None

    def run(self):
        """Continously scan for BLE advertisements."""
        self.socket = bluez.hci_open_dev(self.bt_device_id)
        self.toggle_scan(True)

        try:
            filtr = bluez.hci_filter_new()
            bluez.hci_filter_all_events(filtr)
            bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
            self.socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filtr)

            _LOGGER.debug("Scanner started")

            while self.keep_going:

                pkt = self.socket.recv(255)
                event = pkt[1]
                subevent = pkt[3]
                if event == LE_META_EVENT and subevent == EVT_LE_ADVERTISING_REPORT:
                    # we have an BLE advertisement
                    self.process_packet(pkt)
        except:
            _LOGGER.error("Exception while scanning for beacons", exc_info=True)
            raise
        finally:
            _LOGGER.debug("Stopped scanner")
            self.toggle_scan(False)

    def toggle_scan(self, enable):
        """Enable and disable BLE scanning."""
        if enable:
            command = "\x01\x00"
        else:
            command = "\x00\x00"
        bluez.hci_send_cmd(self.socket, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, command)

    def process_packet(self, pkt):
        """Process an BLE advertisement packet.
        First, we look for the unique ID which identifies Eddystone beacons.
        All other packets will be ignored. We then filter for UID and TLM
        frames. See https://github.com/google/eddystone/ for reference.
        If we find an UID frame the namespace and instance identifier are
        extracted and compared againt the user-supplied values.
        If there is a match, the bluetooth address associated to the
        advertisement will be saved. This is necessary to identify the TLM
        frames sent by this beacon as they do not contain the namespace and
        instance identifier.
        If we encounter an TLM frame, we check if the bluetooth address
        belongs to the beacon monitored. If yes, we can finally extract the
        temperature.
        """
        bt_addr = pkt[7:13]

        # strip bluetooth address and start parsing "length-type-value"
        # structure
        pkt = pkt[14:]
        for type_, data in self.parse_structure(pkt):
            # type 0x16: service data, 0xaa 0xfe: eddystone UUID
            if type_ == 0x16 and data[:2] == b"\xaa\xfe":
                # found eddystone beacon
                if data[2] == 0x00:
                    # UID frame
                    # need to extract namespace and instance
                    # and compare them against target value
                    namespace = data[4:14]
                    instance = data[14:20]

                    device = self.match_device(namespace, instance, bt_addr)
                    if device is not None:
                        # found bt address of monitored beacon
                        _LOGGER.debug("Found beacon at new address: %s",
                                      binascii.hexlify(bt_addr))
                        device.bt_addr = bt_addr

                elif data[2] == 0x20:
                    device = self.match_device_by_addr(bt_addr)
                    if device is not None:
                        # TLM frame from target beacon
                        temp = struct.unpack("<H", data[6:8])[0]
                        _LOGGER.debug("Received temperature for %s: %d",
                                      device.name, temp)
                        device.temperature = temp

    def match_device(self, namespace, instance, bt_addr):
        """Find beacon in device list.
        Interates device list for beacon with supplied namespace
        and instance id. Returns object only if bluetooth address is
        different.
        """
        for dev in self.devices:
            if dev.namespace == namespace and dev.instance == instance \
                    and (dev.bt_addr is None or dev.bt_addr != bt_addr):
                return dev

        return None

    def match_device_by_addr(self, bt_addr):
        """Find beacon in device list.
        Searches device list for beacon with the supplied bluetooth
        address.
        """
        for dev in self.devices:
            if dev.bt_addr == bt_addr:
                return dev
        return None

    @staticmethod
    def parse_structure(data):
        """Generator to parse the eddystone packet structure.
        | length | type |     data       |
        | 1 byte |1 byte| length-1 bytes |
        """
        while data:
            try:
                length, type_ = struct.unpack("BB", data[:2])
                value = data[2:1+length]
            except struct.error:
                break

            yield type_, value
            data = data[1+length:]

    def terminate(self):
        """Signal runner to stop and join thread."""
        self.keep_going = False
        self.join()
