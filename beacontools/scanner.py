"""Classes responsible for Beacon scanning."""
import logging
import sys

from .device_filters import DeviceFilter
from .utils import is_packet_type


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class BeaconScanner(object):
    """Scan for Beacon advertisements."""

    def __init__(self, callback, bt_device_id=0, device_filter=None, packet_filter=None, scan_parameters=None):
        """Initialize scanner."""
        # check if device filters are valid
        if device_filter is not None:
            if not isinstance(device_filter, list):
                device_filter = [device_filter]
            if len(device_filter) > 0:
                for filtr in device_filter:
                    if not isinstance(filtr, DeviceFilter):
                        raise ValueError("Device filters must be instances of DeviceFilter")
            else:
                device_filter = None

        # check if packet filters are valid
        if packet_filter is not None:
            if not isinstance(packet_filter, list):
                packet_filter = [packet_filter]
            if len(packet_filter) > 0:
                for filtr in packet_filter:
                    if not is_packet_type(filtr):
                        raise ValueError("Packet filters must be one of the packet types")
            else:
                packet_filter = None

        if scan_parameters is None:
            scan_parameters = {}

        if sys.platform == "darwin":
            from .monitor_macos import MonitorMacOS
            self._mon = MonitorMacOS(callback, device_filter, packet_filter, scan_parameters)
        else:
            from .monitor_hci import MonitorHci
            self._mon = MonitorHci(callback, bt_device_id, device_filter, packet_filter, scan_parameters)

    def start(self):
        """Start beacon scanning."""
        self._mon.start()

    def stop(self):
        """Stop beacon scanning."""
        self._mon.terminate()
