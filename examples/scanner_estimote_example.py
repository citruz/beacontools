import time

from beacontools import BeaconScanner, EstimoteTelemetryFrameA, EstimoteTelemetryFrameB, EstimoteFilter

def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

# scan for all Estimote telemetry packets from a specific beacon
scanner = BeaconScanner(callback, 
    packet_filter=[EstimoteTelemetryFrameA, EstimoteTelemetryFrameB],
    # remove the following line to see packets from all beacons
    device_filter=EstimoteFilter(identifier="47a038d5eb032640")
)
scanner.start()
time.sleep(10)
scanner.stop()
