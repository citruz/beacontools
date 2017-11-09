import time
from beacontools import BeaconScanner, IBeaconFilter, CYPRESS_BEACON_DEFAULT_UUID

def callback(bt_addr, rssi, packet, additional_info):
    print("<%s, %d> Major:%s %.1fdegC %.1f %%RH" % (
        bt_addr, rssi, packet.major, packet.cypress_temperature, packet.cypress_humidity))

# scan for all iBeacon advertisements from beacons with the specified uuid
scanner = BeaconScanner(callback,
                        device_filter=IBeaconFilter(uuid=CYPRESS_BEACON_DEFAULT_UUID))
scanner.start()
# Cypress beacons by default transmit every 5 minutes
time.sleep(6*60)
scanner.stop()
