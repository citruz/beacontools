"""Packet classes for Estimote beacons."""
from ..utils import data_to_hexstring

class EstimoteTelemetryFrameA(object):
    """Estimote telemetry subframe A."""

    def __init__(self, data, protocol_version):
        self._protocol_version = protocol_version
        self._identifier = data_to_hexstring(data['identifier'])
        sub = data['sub_frame']
        # acceleration: convert to tuple and normalize
        self._acceleration = tuple([v * 2 / 127.0 for v in sub['acceleration']])
        # motion states
        self._previous_motion_state = self.parse_motion_state(sub['previous_motion'])
        self._current_motion_state = self.parse_motion_state(sub['current_motion'])
        self._is_moving = (sub['combined_fields'][0] & 0b00000011) == 1
        # gpio
        states = []
        for i in range(4):
            states.append((sub['combined_fields'][0] & (1 << (4+i))) != 0)
        self._gpio_states = tuple(states)
        # error codes
        if self.protocol_version == 2:
            self._has_firmware_error = ((sub['combined_fields'][0] & 0b00000100) >> 2) == 1
            self._has_clock_error = ((sub['combined_fields'][0] & 0b00001000) >> 3) == 1
        elif self.protocol_version == 1:
            self._has_firmware_error = (sub['combined_fields'][1] & 0b00000001) == 1
            self._has_clock_error = ((sub['combined_fields'][1] & 0b00000010) >> 1) == 1
        else:
            self._has_firmware_error = None
            self._has_clock_error = None
        # pressure
        if self.protocol_version == 2:
            self._pressure = sub['combined_fields'][1] | \
                                sub['combined_fields'][2] << 8 | \
                                sub['combined_fields'][3] << 16 | \
                                sub['combined_fields'][4] << 24
            if self._pressure == 0xffffffff:
                self._pressure = None
            else:
                self._pressure /= 256.0
        else:
            self._pressure = None

    @staticmethod
    def parse_motion_state(val):
        """Convert motion state byte to seconds."""
        number = val & 0b00111111
        unit = (val & 0b11000000) >> 6
        if unit == 1:
            number *= 60 # minutes
        elif unit == 2:
            number *= 60 * 60 # hours
        elif unit == 3 and number < 32:
            number *= 60 * 60 * 24 # days
        elif unit == 3:
            number -= 32
            number *= 60 * 60 * 24 * 7 # weeks
        return number

    @property
    def protocol_version(self):
        """Protocol version of the packet."""
        return self._protocol_version

    @property
    def identifier(self):
        """First half of the identifier of the beacon (8 bytes)."""
        return self._identifier

    @property
    def acceleration(self):
        """Tuple of acceleration values for (X, Y, Z) axis, in g."""
        return self._acceleration

    @property
    def is_moving(self):
        """Whether the beacon is in motion at the moment (Bool)"""
        return self._is_moving

    @property
    def current_motion_state(self):
        """Duration of current motion state in seconds.
        E.g., if is_moving is True, this states how long the beacon is beeing moved already and
        previous_motion_state will tell how long it has been still before."""
        return self._current_motion_state


    @property
    def previous_motion_state(self):
        """Duration of previous motion state in seconds (see current_motion_state)."""
        return self._previous_motion_state

    @property
    def gpio_states(self):
        """Tuple with state of the GPIO pins 0-3 (True is high, False is low)."""
        return self._gpio_states

    @property
    def has_firmware_error(self):
        """If beacon has a firmware problem.
        Only available if protocol version > 0, None otherwise."""
        return self._has_firmware_error

    @property
    def has_clock_error(self):
        """If beacon has a clock problem. Only available if protocol version > 0, None otherwise."""
        return self._has_clock_error

    @property
    def pressure(self):
        """Atmosperic pressure in Pascal. None if all bits are set.
        Only available if protocol version is 2, None otherwise ."""
        return self._pressure

    @property
    def properties(self):
        """Get beacon properties."""
        return {'identifier': self.identifier, 'protocol_version': self.protocol_version}

    def __str__(self):
        return "EstimoteTelemetryFrameA<identifier: %s, protocol_version: %u>" \
            % (self.identifier, self.protocol_version)


class EstimoteTelemetryFrameB(object):
    """Estimote telemetry subframe B."""

    def __init__(self, data, protocol_version):
        self._protocol_version = protocol_version
        self._identifier = data_to_hexstring(data['identifier'])
        sub = data['sub_frame']
        # magnetic field: convert to tuple and normalize
        if sub['magnetic_field'] == [-1, -1, -1]:
            self._magnetic_field = None
        else:
            self._magnetic_field = tuple([v / 128.0 for v in sub['magnetic_field']])
        # ambient light
        ambient_upper = (sub['ambient_light'] & 0b11110000) >> 4
        ambient_lower = sub['ambient_light'] & 0b00001111
        if ambient_upper == 0xf and ambient_lower == 0xf:
            self._ambient_light = None
        else:
            self._ambient_light = pow(2, ambient_upper) * ambient_lower * 0.72
        # uptime
        uptime_unit_code = (sub['combined_fields'][1] & 0b00110000) >> 4
        uptime_number = ((sub['combined_fields'][1] & 0b00001111) << 8) | \
                            sub['combined_fields'][0]
        if uptime_unit_code == 1:
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
        self._temperature = temperature / 16.0
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
        """Tuple of magnetic field values for (X, Y, Z) axis.
        Between -1 and 1 or None if all bits are set."""
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
        """Whether beacon has a firmware problem.
        Only available if protocol version is 0, None otherwise."""
        return self._has_firmware_error

    @property
    def has_clock_error(self):
        """Whether beacon has a clock problem.
        Only available if protocol version is 0, None otherwise."""
        return self._has_clock_error

    @property
    def battery_level(self):
        """Beacon battery level between 0 and 100.
        None if protocol version is 0 or not measured yet."""
        return self._battery_level

    @property
    def properties(self):
        """Get beacon properties."""
        return {'identifier': self.identifier, 'protocol_version': self.protocol_version}

    def __str__(self):
        return "EstimoteTelemetryFrameB<identifier: %s, protocol_version: %u>" \
            % (self.identifier, self.protocol_version)


class EstimoteNearable(object):
    """Estimote Nearable advertisement."""

    def __init__(self, data):
        self._identifier = data_to_hexstring(data['identifier'])
        self._hardware_version = data['hardware_version']
        self._firmware_version = data['firmware_version']

        # byte 13 and the first 4 bits of byte 14 is the temperature in signed,
        temperature_raw_value = (data['temperature'] & 0x0fff)
        if temperature_raw_value > 2047:
            # convert a 12-bit unsigned integer to a signed one
            temperature_raw_value = temperature_raw_value - 4096
        temperature = temperature_raw_value / 16.0
        self._temperature = temperature
        self._is_moving = data['is_moving'] & 0b01000000 != 0

    @property
    def identifier(self):
        """The Nearable identifier (8 bytes)."""
        return self._identifier

    @property
    def hardware_version(self):
        """The hardware version of the nearable."""
        return self._hardware_version

    @property
    def firmware_version(self):
        """The firmware version of the nearable."""
        return self._firmware_version

    @property
    def temperature(self):
        """The temperature reading taken by the nearable."""
        return self._temperature

    @property
    def is_moving(self):
        """Whether the beacon is in motion at the moment."""
        return self._is_moving

    @property
    def properties(self):
        """Get beacon properties."""
        return {'identifier': self.identifier, 'temperature': self.temperature,
                'is_moving': self._is_moving}

    def __str__(self):
        return "EstimoteNearable<identifier: %s>" \
               % self.identifier
