# -*- coding: utf-8 -*-
from beacontools import parse_packet

# Eddystone UID packet
uid_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x17\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12" \
             b"\x34\x67\x89\x01\x00\x00\x00\x00\x00\x01\x00\x00"
uid_frame = parse_packet(uid_packet)
print("Namespace: %s" % uid_frame.namespace)
print("Instance: %s" % uid_frame.instance)
print("TX Power: %s" % uid_frame.tx_power)

print("-----")

# Eddystone URL packet
url_packet = b"\x03\x03\xAA\xFE\x13\x16\xAA\xFE\x10\xF8\x03github\x00citruz"
url_frame = parse_packet(url_packet)
print("TX Power: %d" % url_frame.tx_power)
print("URL: %s" % url_frame.url)

print("-----")

# Eddystone TLM packet (unencrypted)
tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00" \
             b"\x14\x67\x00\x00\x2a\xc4\xe4"
tlm_frame = parse_packet(tlm_packet)
print("Voltage: %d mV" % tlm_frame.voltage)
print("Temperature: %d °C" % tlm_frame.temperature)
print("Advertising count: %d" % tlm_frame.advertising_count)
print("Seconds since boot: %d" % tlm_frame.seconds_since_boot)

print("-----")

# Eddystone TLM packet (encrypted)
enc_tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x01\x41\x41\x41\x41\x41" \
                 b"\x41\x41\x41\x41\x41\x41\x41\xDE\xAD\xBE\xFF"
enc_tlm_frame = parse_packet(enc_tlm_packet)
print("Data: %s" % enc_tlm_frame.encrypted_data)
print("Salt: %d" % enc_tlm_frame.salt)
print("Mic: %d" % enc_tlm_frame.mic)

print("-----")

# iBeacon Advertisement
ibeacon_packet = b"\x02\x01\x06\x1a\xff\x4c\x00\x02\x15\x41\x41\x41\x41\x41\x41\x41\x41\x41" \
                 b"\x41\x41\x41\x41\x41\x41\x41\x00\x01\x00\x01\xf8"
adv = parse_packet(ibeacon_packet)
print("UUID: %s" % adv.uuid)
print("Major: %d" % adv.major)
print("Minor: %d" % adv.minor)
print("TX Power: %d" % adv.tx_power)

print("-----")
# Cypress iBeacon Sensor
cypress_packet = b"\x02\x01\x04\x1a\xff\x4c\x00\x02\x15\x00\x05\x00\x01\x00\x00\x10\x00\x80" \
                 b"\x00\x00\x80\x5f\x9b\x01\x31\x00\x02\x6c\x66\xc3"
sensor = parse_packet(cypress_packet)
print("UUID: %s" % sensor.uuid)
print("Major: %d" % sensor.major)
print("Temperature: %d °C" % sensor.cypress_temperature)
print("Humidity: %d %%" % sensor.cypress_humidity)
print("TX Power: %d" % sensor.tx_power)
