from enum import IntEnum
import struct
import struct
import objc
from CoreBluetooth import CBCentralManager, NSObject, CBManagerStatePoweredOn, CBPeripheral,\
        CBAdvertisementDataServiceDataKey, CBUUID, CBAdvertisementDataManufacturerDataKey
from Foundation import NSDictionary, NSNumber

from libdispatch import dispatch_queue_create, DISPATCH_QUEUE_SERIAL

from .const import SERVICE_DATA_TYPE, EXPOSURE_NOTIFICATION_UUID, MANUFACTURER_SPECIFIC_DATA_TYPE, COMPLETE_SERVICE_UUIDS_DATA_TYPE

import time

#from .backend import CentralManagerDelegate
from .monitor_base import MonitorBase
from .utils import (bin_to_int, bt_addr_to_string, to_int)

CBCentralManagerDelegate = objc.protocolNamed("CBCentralManagerDelegate")


class CentralManagerDelegate(NSObject, protocols=[CBCentralManagerDelegate]):
    def centralManagerDidUpdateState_(self, _manager):
        """Not interesting for now"""
        pass

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
            self, _manager: CBCentralManager, peripheral: CBPeripheral, adv_data: NSDictionary, rssi: NSNumber):
        """Callback that is being invoked by CoreBluetooth."""
        if not adv_data:
            return
        #print(adv_data)
        # we reconstruct the binary representation of the BLE packet to pass it to our parser
        packet = b""
        def append_to_packet(packet, data):
            return packet + struct.pack("B", len(data)) + data

        service_data = adv_data.objectForKey_(CBAdvertisementDataServiceDataKey)
        if service_data:
            for service_uuid, data in service_data.items():
                complete_uuids_data = struct.pack("BBB",
                                                  COMPLETE_SERVICE_UUIDS_DATA_TYPE,
                                                  service_uuid.data()[1],
                                                  service_uuid.data()[0])
                packet = append_to_packet(packet, complete_uuids_data)

                service_data = struct.pack("BBB",
                                           SERVICE_DATA_TYPE,
                                           service_uuid.data()[1],
                                           service_uuid.data()[0]) + data.bytes()
                packet = append_to_packet(packet, service_data)
                print(packet)

        manufacturer_data = adv_data.objectForKey_(CBAdvertisementDataManufacturerDataKey)
        if manufacturer_data:
            manufacturer_specific_data = struct.pack("B", MANUFACTURER_SPECIFIC_DATA_TYPE) + manufacturer_data
            packet = append_to_packet(packet, manufacturer_specific_data)

        if packet:
            self.process_packet(packet, peripheral.identifier().UUIDString(), rssi.intValue())


class MonitorMacOS(MonitorBase):
    """Continously scan for BLE advertisements."""

    def __init__(self, callback, device_filter, packet_filter, scan_parameters):
        super().__init__(callback, device_filter, packet_filter)
        # parameters to pass to bt device
        self.scan_parameters = scan_parameters
        self.manager = None

    def run(self):
        """Continously scan for BLE advertisements."""
        delegate = CentralManagerDelegate.alloc().init()
        delegate.process_packet = self.process_packet

        self.manager:CBCentralManager = CBCentralManager.alloc().initWithDelegate_queue_(delegate, dispatch_queue_create(b"scanner_queue", None))
        while self.manager.state() != CBManagerStatePoweredOn:
            print(f"state: {self.manager.state()}")
            time.sleep(1)

        self.toggle_scan(True)

        # this loop is required so that the thread does not die
        while self.keep_going:
            time.sleep(0.5)

    def toggle_scan(self, enable):
        if enable:
            self.manager.scanForPeripheralsWithServices_options_(None, None)
        else:
            self.manager.stopScan()
