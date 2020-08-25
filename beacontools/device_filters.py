"""Filters passed to the BeaconScanner to filter results."""
from .const import CJ_MANUFACTURER_ID, CJ_TEMPHUM_TYPE
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

        found_one = False
        for key, value in filter_props.items():
            if key in self.properties and value != self.properties[key]:
                return False
            elif key in self.properties and value == self.properties[key]:
                found_one = True

        return found_one

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["=".join((k, str(v),)) for k, v in self.properties.items()]))


class CJMonitorFilter(DeviceFilter):
    """Filter for CJ Monitor."""

    def __init__(self, company_id=CJ_MANUFACTURER_ID, beacon_type=CJ_TEMPHUM_TYPE):
        """Initialize filter."""
        super().__init__()
        if company_id is None and beacon_type is None:
            raise ValueError("CJMonitorFilter needs at least one argument set")
        if company_id is not None:
            self.properties['company_id'] = company_id
        if beacon_type is not None:
            self.properties['beacon_type'] = beacon_type

class IBeaconFilter(DeviceFilter):
    """Filter for iBeacon."""

    def __init__(self, uuid=None, major=None, minor=None):
        """Initialize filter."""
        super().__init__()
        if uuid is None and major is None and minor is None:
            raise ValueError("IBeaconFilter needs at least one argument set")
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
        super().__init__()
        if namespace is None and instance is None:
            raise ValueError("EddystoneFilter needs at least one argument set")
        if namespace is not None:
            self.properties['namespace'] = namespace
        if instance is not None:
            self.properties['instance'] = instance


class EstimoteFilter(DeviceFilter):
    """Filter for Estimote beacons."""

    def __init__(self, identifier=None, protocol_version=None):
        """Initialize filter."""
        super().__init__()
        if identifier is None and protocol_version is None:
            raise ValueError("EstimoteFilter needs at least one argument set")
        if identifier is not None:
            self.properties['identifier'] = identifier
        if protocol_version is not None:
            self.properties['protocol_version'] = protocol_version


class ExposureNotificationFilter(DeviceFilter):
    """Filter for specific exposure notification identifier."""

    def __init__(self, identifier):
        """Initialize filter."""
        super().__init__()
        if identifier is None:
            raise ValueError("ExposureNotificationFilter needs identifier to be set")
        self.properties['identifier'] = identifier


class BtAddrFilter(DeviceFilter):
    """Filter by bluetooth address."""

    def __init__(self, bt_addr):
        """Initialize filter."""
        super().__init__()
        try:
            bt_addr = bt_addr.lower()
        except AttributeError as exc:
            raise ValueError("bt_addr({}) wasn't a string".format(bt_addr)) from exc
        if not is_valid_mac(bt_addr):
            raise ValueError("Invalid bluetooth MAC address given,"
                             " format should match aa:bb:cc:dd:ee:ff")
        self.properties['bt_addr'] = bt_addr
