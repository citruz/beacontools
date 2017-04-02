from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter

def callback(bt_addr, packet, additional_info):
    print("<%s> %s %s" % (bt_addr, packet, additional_info))

scanner = BeaconScanner(callback, 
    device_filter=EddystoneFilter(namespace="12345678901234678901"),
    packet_filter=EddystoneTLMFrame
)
scanner.start()
