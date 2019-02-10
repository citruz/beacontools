import time

from beacontools import BeaconScanner, CJMonitorFilter


def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))


# scan for all CJ Monitor advertisements
scanner = BeaconScanner(callback, device_filter=CJMonitorFilter())
scanner.start()
time.sleep(5)
scanner.stop()
