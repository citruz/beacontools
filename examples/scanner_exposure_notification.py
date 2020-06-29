import time

from beacontools import BeaconScanner, ExposureNotificationFrame

def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

# scan for all COVID-19 exposure notifications
scanner = BeaconScanner(callback, 
    packet_filter=[ExposureNotificationFrame]
)
scanner.start()
time.sleep(5)
scanner.stop()
