"""Packet classes for iBeacon beacons."""
from ..utils import data_to_uuid

class IBeaconAdvertisement(object):
    """iBeacon advertisement."""

    def __init__(self, data):
        self._uuid = data_to_uuid(data['uuid'])
        self._major = data['major']
        self._minor = data['minor']
        self._tx_power = data['tx_power']

    @property
    def tx_power(self):
        """Calibrated Tx power at 0 m."""
        return self._tx_power

    @property
    def uuid(self):
        """16-byte uuid."""
        return self._uuid

    @property
    def major(self):
        """2-byte major identifier."""
        return self._major

    @property
    def minor(self):
        """2-byte minor identifier."""
        return self._minor

    @property
    def properties(self):
        """Get beacon properties."""
        return {'uuid': self.uuid, 'major': self.major, 'minor': self.minor}

    def __str__(self):
        return "IBeaconAdvertisement<tx_power: %d, uuid: %s, major: %d, minor: %d>" \
               % (self.tx_power, self.uuid, self.major, self.minor)
