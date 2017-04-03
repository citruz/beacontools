import time
from beacontools import BeaconScanner, IBeaconFilter

def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

# scan for all iBeacon advertisements from beacons with the specified uuid 
scanner = BeaconScanner(callback, 
    device_filter=IBeaconFilter(uuid="e5b9e3a6-27e2-4c36-a257-7698da5fc140")
)
scanner.start()
time.sleep(5)
scanner.stop()