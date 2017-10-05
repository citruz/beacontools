"""Packet classes for Eddystone beacons."""
from binascii import hexlify
from ..const import EDDYSTONE_URL_SCHEMES, EDDYSTONE_TLD_ENCODINGS
from ..utils import data_to_hexstring, data_to_binstring

class EddystoneUIDFrame(object):
    """Eddystone UID frame."""

    def __init__(self, data):
        self._tx_power = data['tx_power']
        self._namespace = data_to_hexstring(data['namespace'])
        self._instance = data_to_hexstring(data['instance'])

    @property
    def tx_power(self):
        """Calibrated Tx power at 0 m."""
        return self._tx_power

    @property
    def namespace(self):
        """10-byte namespace identifier."""
        return self._namespace

    @property
    def instance(self):
        """6-byte instance identifier."""
        return self._instance

    @property
    def properties(self):
        """Get beacon properties."""
        return {'namespace': self.namespace, 'instance': self.instance}

    def __str__(self):
        return "EddystoneUIDFrame<tx_power: %d, namespace: %s, instance: %s>" \
               % (self.tx_power, self.namespace, self.instance)


class EddystoneURLFrame(object):
    """Eddystone URL frame."""

    def __init__(self, data):
        self._tx_power = data['tx_power']
        url_scheme = EDDYSTONE_URL_SCHEMES[data['url_scheme']]
        url = data['url']

        # Replace url encodings with their expanded version
        for enc, tld in EDDYSTONE_TLD_ENCODINGS.items():
            url = url.replace(chr(enc), tld)

        self._url = url_scheme + url

    @property
    def tx_power(self):
        """Calibrated Tx power at 0 m."""
        return self._tx_power

    @property
    def url(self):
        """Transmitted URL."""
        return self._url

    def __str__(self):
        return "EddystoneURLFrame<tx_power: %d, url: %s>" \
               % (self.tx_power, self.url)


class EddystoneEncryptedTLMFrame(object):
    """Eddystone encrypted TLM frame."""

    def __init__(self, data):
        self._encrypted_data = data_to_binstring(data['encrypted_data'])
        self._salt = data['salt']
        self._mic = data['mic']

    @property
    def encrypted_data(self):
        """Encrypted TLM data."""
        return self._encrypted_data

    @property
    def salt(self):
        """16-bit salt."""
        return self._salt

    @property
    def mic(self):
        """16-bit message integrity check."""
        return self._mic

    def __str__(self):
        return "EddystoneEncryptedTLMFrame<encrypted_data: %s, salt: %d, mic: %d>" \
               % (hexlify(self.encrypted_data), self.salt, self.mic)


class EddystoneTLMFrame(object):
    """Eddystone TLM frame."""

    def __init__(self, data):
        self._voltage = data['voltage']
        self._temperature = data['temperature']
        self._advertising_count = data['advertising_count']
        self._seconds_since_boot = data['seconds_since_boot']

    @property
    def voltage(self):
        """Battery voltage measured in mV."""
        return self._voltage

    @property
    def temperature(self):
        """Temperature in degree Celsius."""
        return self._temperature

    @property
    def advertising_count(self):
        """Advertising PDU count."""
        return self._advertising_count

    @property
    def seconds_since_boot(self):
        """Time since power-on or reboot."""
        return self._seconds_since_boot

    def __str__(self):
        return "EddystoneTLMFrame<voltage: %d mV, temperature: %d Celsius, advertising count: %d,"\
               " seconds since boot: %d>" % (self.voltage, self.temperature, \
                self.advertising_count, self.seconds_since_boot)

class EddystoneEIDFrame(object):
    """Eddystone EID frame."""

    def __init__(self, data):
        self._tx_power = data['tx_power']
        self._eid = data_to_binstring(data['eid'])

    @property
    def tx_power(self):
        """Calibrated Tx power at 0 m."""
        return self._tx_power

    @property
    def eid(self):
        """8-byte Ephemeral Identifier."""
        return self._eid

    def __str__(self):
        return "EddystoneEIDFrame<tx_power: %d, eid: %s>" \
               % (self.tx_power, hexlify(self.eid))
