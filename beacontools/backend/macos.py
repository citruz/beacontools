import struct
import objc
from CoreBluetooth import CBCentralManager, NSObject, CBManagerStatePoweredOn, CBPeripheral,\
        CBAdvertisementDataServiceDataKey, CBUUID, CBAdvertisementDataManufacturerDataKey
from Foundation import NSDictionary, NSNumber

from libdispatch import dispatch_queue_create, DISPATCH_QUEUE_SERIAL

import time

from beacontools.const import SERVICE_DATA_TYPE,EXPOSURE_NOTIFICATION_UUID, MANUFACTURER_SPECIFIC_DATA_TYPE
from beacontools.parser import parse_packet

CBCentralManagerDelegate = objc.protocolNamed("CBCentralManagerDelegate")


class CentralManagerDelegate(NSObject, protocols=[CBCentralManagerDelegate]):
    def centralManagerDidUpdateState_(self, manager):
        print(f"centralManagerDidUpdateState: {manager.state()}")

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
            self, manager: CBCentralManager, peripheral: CBPeripheral, adv_data: NSDictionary, rssi: NSNumber):
        #print(f"centralManagerdidDiscoverPeripheral: {locals()}")
        if not adv_data:
            return
        print(adv_data)
        packet = b""
        service_data = adv_data.objectForKey_(CBAdvertisementDataServiceDataKey)
        if service_data:
            for service_uuid, data in service_data.items():
                print(service_uuid)
                service_packet = struct.pack("BBB", SERVICE_DATA_TYPE, service_uuid.data()[1], service_uuid.data()[0]) + data.bytes()
                packet += struct.pack("B", len(service_packet)) + service_packet
        
        manufacturer_data = adv_data.objectForKey_(CBAdvertisementDataManufacturerDataKey)
        if manufacturer_data:
            manufacturer_packet = struct.pack("B", MANUFACTURER_SPECIFIC_DATA_TYPE) + manufacturer_data
            packet += struct.pack("B", len(manufacturer_packet)) + manufacturer_packet
        print(packet)
        print(parse_packet(packet))


def main():
    delegate = CentralManagerDelegate.alloc().init()
    manager:CBCentralManager = CBCentralManager.alloc().initWithDelegate_queue_(delegate, dispatch_queue_create(b"scanner_queue", None))
    while manager.state() != CBManagerStatePoweredOn:
        print(f"state: {manager.state()}")
        time.sleep(1)
    manager.scanForPeripheralsWithServices_options_(None, None)
    while True:
        time.sleep(5)


if __name__ == '__main__':
    main()