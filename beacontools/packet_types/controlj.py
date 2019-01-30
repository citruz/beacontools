"""Packet classes for iBeacon beacons."""
from ..utils import mulaw_to_value, data_to_binstring


class CJMonitorAdvertisement(object):
    """CJ Monitor advertisement."""


    def __init__(self, data):
        self._temperature = data['temperature'] / 100.0
        self._humidity = data['humidity']
        self._light = mulaw_to_value(data['light']) / 100.0
        self._name = data_to_binstring(data['name']).decode("utf-8")

    @property
    def name(self):
        """device name"""
        return self._name

    @property
    def humidity(self):
        """humidity in %"""
        return self._humidity

    @property
    def temperature(self):
        """temperature in C."""
        return self._temperature

    @property
    def light(self):
        """light level in lux"""
        return self._light

    @property
    def properties(self):
        """Get Monitor properties."""
        return {'name': self.name, 'temperature': self.temperature, 'humidity': self.humidity, 'light': self.light}

    def __str__(self):
        return f"CJMonitorAdvertisement<name: {self.name}, temp: {self.temperature:.1f}, humidity: {self.humidity:d}, light: {self.light:.0f}>"
