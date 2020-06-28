"""Packet classes for Eddystone beacons."""
from binascii import hexlify
from ..const import EDDYSTONE_URL_SCHEMES, EDDYSTONE_TLD_ENCODINGS
from ..utils import data_to_hexstring, data_to_binstring

class ExposureNotificationFrame(object):
    """COVID-19 Exposure Notification frame."""

    def __init__(self, data):
        self._identifier = data_to_hexstring(data['identifier'])
        self._metadata = data['metadata']

    @property
    def identifier(self):
        """16 byte Rolling Proximity Identifier"""
        return self._identifier

    @property
    def properties(self):
        """Get beacon properties."""
        return {'identifier': self.identifier}

    def __str__(self):
        return "ExposureNotificationFrame<identifier: %s>" \
               % (self.identifier)

