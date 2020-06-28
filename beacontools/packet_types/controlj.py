"""Packet classes for Control-J Monitors."""
from ..utils import mulaw_to_value, data_to_binstring
from ..const import MANUFACTURER_SPECIFIC_DATA_TYPE, CJ_TEMPHUM_TYPE, COMPLETE_LOCALE_NAME_DATA_TYPE

class CJMonitorAdvertisement(object):
    """CJ Monitor advertisement."""

    def __init__(self, frame):

        for ltv in frame:
            if ltv['type'] == MANUFACTURER_SPECIFIC_DATA_TYPE:
                msd = ltv['value']
                self._company_id = msd['company_identifier']
                self._beacon_type = msd['data']['beacon_type']
                if self._beacon_type == CJ_TEMPHUM_TYPE:
                    data = msd['data']['data']
                    self._temperature = data['temperature'] / 100.0
                    self._humidity = data['humidity']
                    self._light = mulaw_to_value(data['light']) / 10.0
            elif ltv['type'] == COMPLETE_LOCALE_NAME_DATA_TYPE:
                self._name = data_to_binstring(ltv['value']).decode("ascii")

    @property
    def name(self):
        """device name"""
        return self._name

    @property
    def humidity(self):
        """humidity in %"""
        return self._humidity

    @property
    def company_id(self):
        """company ID"""
        return self._company_id

    @property
    def beacon_type(self):
        """type of this beacon"""
        return self._beacon_type

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
        return {'name': self.name,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'light': self.light,
                'company_id': self.company_id,
                'beacon_type': self.beacon_type}

    def __str__(self):
        return "CJMonitorAdvertisement<name: {name}, temp: {temperature:.1f}," \
               "humidity: {humidity:d}, light: {light:.0f}>".format(
                   name=self.name, temperature=self.temperature,
                   humidity=self.humidity, light=self.light)
