"""Monitoring class for scanning using HCI (Linux, FreeBSD)"""
from enum import IntEnum
import struct

from construct import Struct, Byte, Bytes, GreedyRange, ConstructError

from .backend import open_dev, send_req, send_cmd
from .const import (EVT_LE_ADVERTISING_REPORT, LE_META_EVENT,
                    MS_FRACTION_DIVIDER, OCF_LE_SET_SCAN_ENABLE,
                    OCF_LE_SET_SCAN_PARAMETERS, OGF_LE_CTL,
                    OCF_LE_SET_EXT_SCAN_PARAMETERS, OCF_LE_SET_EXT_SCAN_ENABLE,
                    EVT_LE_EXT_ADVERTISING_REPORT, OGF_INFO_PARAM,
                    OCF_READ_LOCAL_VERSION, EVT_CMD_COMPLETE, ScanType, BluetoothAddressType,
                    ScanFilter)
from .monitor_base import MonitorBase
from .utils import (bin_to_int, bt_addr_to_string, to_int)


class HCIVersion(IntEnum):
    """HCI version enumeration

    https://www.bluetooth.com/specifications/assigned-numbers/host-controller-interface/
    """
    BT_CORE_SPEC_1_0 = 0
    BT_CODE_SPEC_1_1 = 1
    BT_CODE_SPEC_1_2 = 2
    BT_CORE_SPEC_2_0 = 3
    BT_CORE_SPEC_2_1 = 4
    BT_CORE_SPEC_3_0 = 5
    BT_CORE_SPEC_4_0 = 6
    BT_CORE_SPEC_4_1 = 7
    BT_CORE_SPEC_4_2 = 8
    BT_CORE_SPEC_5_0 = 9
    BT_CORE_SPEC_5_1 = 10
    BT_CORE_SPEC_5_2 = 11


class MonitorHci(MonitorBase):
    """Continously scan for BLE advertisements."""

    def __init__(self, callback, bt_device_id, device_filter, packet_filter, scan_parameters):
        super().__init__(callback, device_filter, packet_filter)

        # number of the bt device (hciX)
        self.bt_device_id = bt_device_id
        # bluetooth socket
        self.socket = None
        # hci version
        self.hci_version = HCIVersion.BT_CORE_SPEC_1_0
        # parameters to pass to bt device
        self.scan_parameters = scan_parameters

    def run(self):
        """Continously scan for BLE advertisements."""
        self.socket = open_dev(self.bt_device_id)

        self.hci_version = self.get_hci_version()
        self.set_scan_parameters(**self.scan_parameters)
        self.toggle_scan(True)

        while self.keep_going:
            pkt = self.socket.recv(255)
            event = to_int(pkt[1])
            subevent = to_int(pkt[3])
            if event == LE_META_EVENT and subevent in [EVT_LE_ADVERTISING_REPORT, EVT_LE_EXT_ADVERTISING_REPORT]:
                # we have an BLE advertisement
                payload = pkt[14:-1] if self.hci_version < HCIVersion.BT_CORE_SPEC_5_0 else pkt[29:]
                bt_addr = bt_addr_to_string(pkt[7:13])
                rssi = bin_to_int(pkt[-1] if self.hci_version < HCIVersion.BT_CORE_SPEC_5_0 else pkt[18])
                self.process_packet(payload, bt_addr, rssi)

        self.socket.close()

    def get_hci_version(self):
        """Gets the HCI version"""
        local_version = Struct(
            "status" / Byte,
            "hci_version" / Byte,
            "hci_revision" / Bytes(2),
            "lmp_version" / Byte,
            "manufacturer_name" / Bytes(2),
            "lmp_subversion" / Bytes(2),
        )

        try:
            resp = send_req(self.socket, OGF_INFO_PARAM, OCF_READ_LOCAL_VERSION,
                                         EVT_CMD_COMPLETE, local_version.sizeof(), bytes(), 0)
            return HCIVersion(GreedyRange(local_version).parse(resp)[0]["hci_version"])
        except (ConstructError, NotImplementedError):
            return HCIVersion.BT_CORE_SPEC_1_0

    def set_scan_parameters(self, scan_type=ScanType.ACTIVE, interval_ms=10, window_ms=10,
                            address_type=BluetoothAddressType.RANDOM, filter_type=ScanFilter.ALL):
        """"Sets the le scan parameters

        For extended set scan parameters command additional parameter scanning PHYs has to be provided.
        The parameter indicates the PHY(s) on which the advertising packets should be received on the
        primary advertising physical channel. For further information have a look on BT Core 5.1 Specification,
        page 1439 ( LE Set Extended Scan Parameters command).

        Args:
            scan_type: ScanType.(PASSIVE|ACTIVE)
            interval: ms (as float) between scans (valid range 2.5ms - 10240ms or 40.95s for extended version)
                ..note:: when interval and window are equal, the scan
                    runs continuos
            window: ms (as float) scan duration (valid range 2.5ms - 10240ms or 40.95s for extended version)
            address_type: Bluetooth address type BluetoothAddressType.(PUBLIC|RANDOM)
                * PUBLIC = use device MAC address
                * RANDOM = generate a random MAC address and use that
            filter: ScanFilter.(ALL|WHITELIST_ONLY) only ALL is supported, which will
                return all fetched bluetooth packets (WHITELIST_ONLY is not supported,
                because OCF_LE_ADD_DEVICE_TO_WHITE_LIST command is not implemented)

        Raises:
            ValueError: A value had an unexpected format or was not in range
        """
        max_interval = (0x4000 if self.hci_version < HCIVersion.BT_CORE_SPEC_5_0 else 0xFFFF)
        interval_fractions = interval_ms / MS_FRACTION_DIVIDER
        if interval_fractions < 0x0004 or interval_fractions > max_interval:
            raise ValueError(
                "Invalid interval given {}, must be in range of 2.5ms to {}ms!".format(
                    interval_fractions, max_interval * MS_FRACTION_DIVIDER))
        window_fractions = window_ms / MS_FRACTION_DIVIDER
        if window_fractions < 0x0004 or window_fractions > max_interval:
            raise ValueError(
                "Invalid window given {}, must be in range of 2.5ms to {}ms!".format(
                    window_fractions, max_interval * MS_FRACTION_DIVIDER))

        interval_fractions, window_fractions = int(interval_fractions), int(window_fractions)

        if self.hci_version < HCIVersion.BT_CORE_SPEC_5_0:
            command_field = OCF_LE_SET_SCAN_PARAMETERS
            scan_parameter_pkg = struct.pack(
                "<BHHBB",
                scan_type,
                interval_fractions,
                window_fractions,
                address_type,
                filter_type)
        else:
            command_field = OCF_LE_SET_EXT_SCAN_PARAMETERS
            scan_parameter_pkg = struct.pack(
                "<BBBBHH",
                address_type,
                filter_type,
                1,  # scan advertisements on the LE 1M PHY
                scan_type,
                interval_fractions,
                window_fractions)

        send_cmd(self.socket, OGF_LE_CTL, command_field, scan_parameter_pkg)

    def toggle_scan(self, enable):
        """Enables or disables BLE scanning

        For extended set scan enable command additional parameters duration and period have
        to be provided. When both are zero, the controller shall continue scanning until
        scanning is disabled. For non-zero values have a look on BT Core 5.1 Specification,
        page 1442 (LE Set Extended Scan Enable command).

        Args:
            enable: boolean value to enable (True) or disable (False) scanner"""
        filter_duplicates=False
        if self.hci_version < HCIVersion.BT_CORE_SPEC_5_0:
            command_field = OCF_LE_SET_SCAN_ENABLE
            command = struct.pack("BB", enable, filter_duplicates)
        else:
            command_field = OCF_LE_SET_EXT_SCAN_ENABLE
            command = struct.pack("<BBHH", enable, filter_duplicates,
                                  0,  # duration
                                  0   # period
                                  )
        send_cmd(self.socket, OGF_LE_CTL, command_field, command)
