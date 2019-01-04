BeaconTools - Universal beacon scanning
=======================================
|PyPI Package| |Build Status| |Coverage Status| |Requirements Status|

A Python library for working with various types of Bluetooth LE Beacons.

Currently supported types are:

* `Eddystone Beacons <https://github.com/google/eddystone/>`__
* `iBeacons <https://developer.apple.com/ibeacon/>`__ (Apple and Cypress CYALKIT-E02)
* `Estimote Beacons (Telemetry only) <https://github.com/estimote/estimote-specs>`__

The BeaconTools library has two main components:

* a parser to extract information from raw binary beacon advertisements
* a scanner which scans for Bluetoth LE advertisements using bluez and can be configured to look only for specific beacons or packet types

Installation
------------
If you only want to use the **parser** install the library using pip and you're good to go:

.. code:: bash

    pip install beacontools
    
If you want to perfom beacon **scanning** there are a few more requirement. First of all you need an OS with bluez (most Linux OS; Windows and macOS are also possible but untested, see the "`Build Requirements <https://github.com/karulis/pybluez>`__" section of pybluez for more information).

.. code:: bash

    # install libbluetooth headers and libpcap2
    sudo apt-get install python-dev libbluetooth-dev libcap2-bin
    # grant the python executable permission to access raw socket data
    sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python))
    # install beacontools with scanning support
    pip install beacontools[scan]
    
Usage
-----
See the `examples <https://github.com/citruz/beacontools/tree/master/examples>`__ directory for more usage examples.

Parser
~~~~~~

.. code:: python

    from beacontools import parse_packet
    
    tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00" \
                 b"\x14\x67\x00\x00\x2a\xc4\xe4"
    tlm_frame = parse_packet(tlm_packet)
    print("Voltage: %d mV" % tlm_frame.voltage)
    print("Temperature: %d °C" % tlm_frame.temperature)
    print("Advertising count: %d" % tlm_frame.advertising_count)
    print("Seconds since boot: %d" % tlm_frame.seconds_since_boot)

Scanner
~~~~~~~
.. code:: python

    import time
    from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter

    def callback(bt_addr, rssi, packet, additional_info):
        print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

    # scan for all TLM frames of beacons in the namespace "12345678901234678901"
    scanner = BeaconScanner(callback, 
        device_filter=EddystoneFilter(namespace="12345678901234678901"),
        packet_filter=EddystoneTLMFrame
    )
    scanner.start()

    time.sleep(10)
    scanner.stop()


.. code:: python

    import time
    from beacontools import BeaconScanner, IBeaconFilter

    def callback(bt_addr, rssi, packet, additional_info):
        print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

    # scan for all iBeacon advertisements from beacons with the specified uuid 
    scanner = BeaconScanner(callback, 
        device_filter=IBeaconFilter(uuid="e5b9e3a6-27e2-4c36-a257-7698da5fc140")
    )
    scanner.start()
    time.sleep(5)
    scanner.stop()


Changelog
---------
Beacontools follows the `semantic versioning <https://semver.org/>`__ scheme.

* 1.3.1
    * Multiple fixes and internal refactorings, including support for Raspberry Pi 3B+ (huge thanks to `cereal <https://github.com/cereal>`__)
    * Updated dependencies
* 1.3.0
    * Added support for Estimote Telemetry packets (see examples/parser_example.py)
    * Relaxed parsing constraints for RFU and flags field
    * Added temperature output in 8.8 fixed point decimal format for Eddystone TLM
* 1.2.4
    * Added support for Eddystone packets with Flags Data set to 0x1a (thanks to `AndreasTornes <https://github.com/AndreasTornes>`__)
    * Updated dependencies
* 1.2.3
    * Fixed compatibility with construct >=2.9.41
* 1.2.2
    * Moved import of bluez so that the library can be used in parsing-only mode, without having bluez installed.
* 1.2.1
    * Updated dependencies
* 1.2.0
    * Added support for Cypress iBeacons which transmit temp and humidity embedded in the minor value (thanks to `darkskiez <https://github.com/darkskiez>`__)
    * Updated dependencies
* 1.1.0
    * Added support for Eddystone EID frames (thanks to `miek <https://github.com/miek>`__)
    * Updated dependencies
* 1.0.1
    * Implemented a small tweak which reduces the CPU usage.
* 1.0.0 
    * Implemented iBeacon support
    * Added rssi to callback function.
* 0.1.2 
    * Initial release

.. |PyPI Package| image:: https://badge.fury.io/py/beacontools.svg
  :target: https://pypi.python.org/pypi/beacontools/
.. |Build Status| image:: https://travis-ci.org/citruz/beacontools.svg?branch=master
    :target: https://travis-ci.org/citruz/beacontools
.. |Coverage Status| image:: https://coveralls.io/repos/github/citruz/beacontools/badge.svg?branch=master
  :target: https://coveralls.io/github/citruz/beacontools?branch=master
.. |Requirements Status| image:: https://requires.io/github/citruz/beacontools/requirements.svg?branch=master
  :target: https://requires.io/github/citruz/beacontools/requirements/?branch=master
