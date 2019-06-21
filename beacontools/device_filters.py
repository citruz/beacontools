"""Filters passed to the BeaconScanner to filter results."""

from .utils import is_valid_mac


class DeviceFilter(object):
    """Base class for all device filters. Should not be used by itself."""

    def __init__(self):
        """Initialize filter."""
        self.properties = {}

    def matches(self, filter_props):
        """Check if the filter matches the supplied properties."""
        if filter_props is None:
            return False

        found_one = True
        for key, value in filter_props.items():
            if key in self.properties and value != self.properties[key]:
                return False

        return found_one

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["=".join((k, str(v),)) for k, v in self.properties.items()]))


class IBeaconFilter(DeviceFilter):
    """Filter for iBeacon."""

    def __init__(self, uuid=None, major=None, minor=None):
        """Initialize filter."""
        super(IBeaconFilter, self).__init__()
        if uuid is not None:
            self.properties['uuid'] = uuid
        if major is not None:
            self.properties['major'] = major
        if minor is not None:
            self.properties['minor'] = minor


class EddystoneFilter(DeviceFilter):
    """Filter for Eddystone beacons."""

    def __init__(self, namespace=None, instance=None):
        """Initialize filter."""
        super(EddystoneFilter, self).__init__()
        if namespace is not None:
            self.properties['namespace'] = namespace
        if instance is not None:
            self.properties['instance'] = instance


class EstimoteFilter(DeviceFilter):
    """Filter for Estimote beacons."""

    def __init__(self, identifier=None, protocol_version=None):
        """Initialize filter."""
        super(EstimoteFilter, self).__init__()
        if identifier is not None:
            self.properties['identifier'] = identifier
        if protocol_version is not None:
            self.properties['protocol_version'] = protocol_version


class BtAddrFilter(DeviceFilter):
    """Filter by bluetooth address."""

    def __init__(self, bt_addr=None):
        """Initialize filter."""
        super(BtAddrFilter, self).__init__()
        if bt_addr is not None:
			try:
				bt_addr = bt_addr.lower()
			except AttributeError:
				raise ValueError("bt_addr({}) wasn't a string".format(bt_addr))
			if not is_valid_mac(bt_addr):
				raise ValueError("Invalid bluetooth MAC address given,"
								 " format should match aa:bb:cc:dd:ee:ff")
			self.properties['bt_addr'] = bt_addr
