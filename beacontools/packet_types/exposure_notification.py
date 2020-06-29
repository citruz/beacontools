"""Packet classes for Eddystone beacons."""
from ..utils import data_to_hexstring, data_to_binstring

class ExposureNotificationFrame(object):
    """COVID-19 Exposure Notification frame."""

    def __init__(self, data):
        self._identifier = data_to_hexstring(data['identifier'])
        self._encrypted_metadata = data_to_binstring(data['encrypted_metadata'])

    @property
    def identifier(self):
        """16 byte Rolling Proximity Identifier"""
        return self._identifier

    @property
    def encrypted_metadata(self):
        """4 byte encrypted data containing version info and transmission power"""
        return self._encrypted_metadata

    @property
    def properties(self):
        """Get beacon properties."""
        return {'identifier': self.identifier, 'encrypted_metadata' : self.encrypted_metadata}

    def __str__(self):
        return "ExposureNotificationFrame<identifier: %s>" % (self.identifier)
