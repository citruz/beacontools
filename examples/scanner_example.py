from beacontools import BeaconScanner, EddystoneUIDFrame, EddystoneTLMFrame, EddystoneFilter

def callback(bt_addr, packet, additional_info):
    print("<%s> %s %s" % (bt_addr, packet, additional_info))

eddyfilter = EddystoneFilter(namespace="12345678901234678901")
scanner = BeaconScanner(callback, device_filter=None, packet_filter=EddystoneTLMFrame)
scanner.start()
