"""Filters passed to the BeaconScanner to filter results."""

class DeviceFilter(object):
    """Base class for all device filters. Should not be used by itself."""

    def __init__(self):
        """Initialize filter."""
        self.properties = {}

    def matches(self, filter_props):
        """Check if the filter matches the supplied properties."""
        if filter_props is None:
            return False

        found_one = False
        for key, value in filter_props.items():
            if key in self.properties and value != self.properties[key]:
                return False
            elif key in self.properties and value == self.properties[key]:
                found_one = True

        return found_one

class IBeaconFilter(DeviceFilter):
    """Filter for iBeacon."""

    def __init__(self, uuid=None, major=None, minor=None):
        """Initialize filter."""
        super(IBeaconFilter, self).__init__()
        # TODO validate arguments
        if uuid:
            self.properties['uuid'] = uuid
        if major:
            self.properties['major'] = major
        if minor:
            self.properties['minor'] = minor

class EddystoneFilter(DeviceFilter):
    """Filter for Eddystone beacons."""

    def __init__(self, namespace=None, instance=None):
        """Initialize filter."""
        super(EddystoneFilter, self).__init__()
        # TODO validate arguments
        if namespace:
            self.properties['namespace'] = namespace
        if instance:
            self.properties['instance'] = instance

class BtAddrFilter(DeviceFilter):
    """Filter by bluetooth address."""

    def __init__(self, bt_addr):
        """Initialize filter."""
        super(BtAddrFilter, self).__init__()
        # TODO validate arguments
        self.properties['bt_addr'] = bt_addr
