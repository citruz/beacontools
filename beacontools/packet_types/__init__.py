"""Packets supported by the parser."""
from .eddystone import EddystoneUIDFrame, EddystoneURLFrame, EddystoneEncryptedTLMFrame, \
                       EddystoneTLMFrame, EddystoneEIDFrame
from .ibeacon import IBeaconAdvertisement
