# -*- coding: utf-8 -*-
from binascii import hexlify

from ..const import URL_SCHEMES, TLD_ENCODINGS

class EddystoneUIDFrame:
    def __init__(self, data):
        self._tx_power = data['tx_power']
        self._namespace = hexlify(bytes(data['namespace'])).decode('ascii')
        self._instance = hexlify(bytes(data['instance'])).decode('ascii')

    @property
    def tx_power(self):
        return self._tx_power

    @property
    def namespace(self):
        return self._namespace

    @property
    def instance(self):
        return self._instance

    def __str__(self):
        return "EddystoneUIDFrame<tx_power: %d, namespace: %s, instance: %s>" \
               % (self.tx_power, self.namespace, self.instance)


class EddystoneURLFrame:
    def __init__(self, data):
        self._tx_power = data['tx_power']
        url_scheme = URL_SCHEMES[data['url_scheme']]
        url = data['url']

        # Replace url encodings with their expanded version
        for enc, tld in TLD_ENCODINGS.items():
            url = url.replace(chr(enc), tld)

        self._url = url_scheme + url

    @property
    def tx_power(self):
        return self._tx_power

    @property
    def url(self):
        return self._url

    def __str__(self):
        return "EddystoneURLFrame<tx_power: %d, url: %s>" \
               % (self.tx_power, self.url)


class EddystoneEncryptedTLMFrame:
    def __init__(self, data):
        self._encrypted_data = bytes(data['encrypted_data'])
        self._salt = data['salt']
        self._mic = data['mic']

    @property
    def encrypted_data(self):
        return self._encrypted_data

    @property
    def salt(self):
        return self._salt    

    @property
    def mic(self):
        return self._mic

    def __str__(self):
        return "EddystoneEncryptedTLMFrame<encrypted_data: %s, salt: %d, mic: %d>" \
               % (self.encrypted_data, self.salt, self.mic)

class EddystoneTLMFrame:
    def __init__(self, data):
        self._voltage = data['voltage']
        self._temperature = data['temperature']
        self._advertising_count = data['advertising_count']
        self._seconds_since_boot = data['seconds_since_boot']

    @property
    def voltage(self):
        return self._voltage

    @property
    def temperature(self):
        return self._temperature    

    @property
    def advertising_count(self):
        return self._advertising_count

    @property
    def seconds_since_boot(self):
        return self._seconds_since_boot

    def __str__(self):
        return "EddystoneTLMFrame<voltage: %d mV, temperature: %d °C, advertising count: %d, " \
               "seconds since boot: %d>" % (self.voltage, self.temperature, \
                self.advertising_count, self.seconds_since_boot)
    