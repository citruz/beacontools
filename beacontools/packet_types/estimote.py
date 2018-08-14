from ..utils import data_to_hexstring

class EstimoteTelemetryFrameB(object):
    """Estimote telemetry frame."""

    def __init__(self, data, protocol_version):
        self._protocol_version = protocol_version
        self._identifier = data_to_hexstring(data['identifier'])
        sub = data['sub_frame']
        # magnetic field: convert to tuple and normalize
        self._magnetic_field = tuple([v / 128.0 for v in sub['magnetic_field']])
        # ambient light
        ambient_upper = (sub['ambient_light'] & 0b11110000) >> 4
        ambient_lower = sub['ambient_light'] & 0b00001111
        self._ambient_light = pow(2, ambient_upper) * ambient_lower * 0.72;
        # uptime
        uptime_unit_code = (sub['combined_fields'][1] & 0b00110000) >> 4
        uptime_number = ((sub['combined_fields'][1] & 0b00001111) << 8) | sub['combined_fields'][0]
        if uptime_unit_code ==  1:
            uptime_number *= 60 # minutes
        elif uptime_unit_code == 2:
            uptime_number *= 60 * 60 # hours
        elif uptime_unit_code == 3:
            uptime_number *= 60 * 60 * 24 # days
        else:
            uptime_number = 0
        self._uptime = uptime_number
        # temperature
        temperature = ((sub['combined_fields'][3] & 0b00000011) << 10) |   \
                        (sub['combined_fields'][2]               <<  2) |  \
                        ((sub['combined_fields'][1] & 0b11000000) >>  6)
        temperature = temperature - 4096 if temperature > 2047 else temperature
        self._temperature = temperature / 16.0;
        # battery voltage
        voltage = (sub['combined_fields'][4] << 6) |  \
                    ((sub['combined_fields'][3] & 0b11111100) >> 2)
        self._voltage = None if voltage == 0b11111111111111 else voltage
        if self._protocol_version == 0:
            # errors (only protocol ver 0)
            self._has_firmware_error = (sub['battery_level'] & 0b00000001) == 1
            self._has_clock_error = (sub['battery_level'] & 0b00000010) == 0b10
            self._battery_level = None
        else:
            self._battery_level = None if sub['battery_level'] == 0xFF else sub['battery_level']
            self._has_clock_error = None
            self._has_firmware_error = None


    @property
    def protocol_version(self):
        """Protocol version of the packet."""
        return self._protocol_version

    @property
    def identifier(self):
        """First half of the identifier of the beacon (8 bytes)."""
        return self._identifier

    @property
    def magnetic_field(self):
        """Tuple of magnetic field values for (X, Y, Z) axis. Between -1 and 1."""
        return self._magnetic_field

    @property
    def ambient_light(self):
        """Ambient light in lux."""
        return self._ambient_light

    @property
    def uptime(self):
        """Uptime in seconds."""
        return self._uptime

    @property
    def temperature(self):
        """Ambient temperature in celsius."""
        return self._temperature

    @property
    def has_firmware_error(self):
        """If beacon has a firmware problem. Only available if protocol version is 0, None otherwise."""
        return self._has_firmware_error

    @property
    def has_clock_error(self):
        """If beacon has a clock problem. Only available if protocol version is 0, None otherwise."""
        return self._has_clock_error

    @property
    def battery_level(self):
        """Beacon battery level between 0 and 100. None if protocol version is 0 or not measured yet."""
        return self._battery_level


    def __str__(self):
        return "EstimoteTelemetryFrameB<identifier: %s, protocol_version: %u>" % (self.identifier, self.protocol_version)
