import time

from beacontools import BeaconScanner, EstimoteFilter


def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

scanner = BeaconScanner(callback,
    device_filter=EstimoteFilter(identifier="1efe427eb6f4bc2f")
)
scanner.start()
time.sleep(10)
scanner.stop()
