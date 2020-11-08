"""Test the scanner component."""
import sys
import unittest

from beacontools.const import CJ_TEMPHUM_TYPE, CJ_MANUFACTURER_ID

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from beacontools import BeaconScanner, EddystoneFilter, EddystoneTLMFrame, EddystoneUIDFrame, \
                        BtAddrFilter, IBeaconFilter, IBeaconAdvertisement, EstimoteFilter, \
                        EstimoteTelemetryFrameB, EstimoteTelemetryFrameA, CJMonitorFilter, CJMonitorAdvertisement, \
                        ExposureNotificationFilter, ExposureNotificationFrame

class TestScanner(unittest.TestCase):
    """Test the BeaconScanner."""

    def setUp(self):
        # mock import so that tests can run without PyBluez installed
        sys.modules['bluetooth'] = MagicMock()
        sys.platform = "linux"

    def test_invalid_device_filters(self):
        """Test creation of device filters without arguments"""
        filters = [EddystoneFilter, IBeaconFilter, EstimoteFilter]
        for filter in filters:
            with self.assertRaises(ValueError):
                filter()

    def test_bad_arguments(self):
        """Test if wrong filters result in ValueError."""
        tests = [
            ([{"namespace" : "ABC"}], None),
            (None, EddystoneFilter(namespace="abc")),
            (None, [EddystoneFilter(namespace="abc")]),
            (EddystoneTLMFrame, []),
            ([EddystoneTLMFrame], None),
            ([EddystoneTLMFrame], [EddystoneFilter(namespace="abc")]),
        ]

        for dev_filter, pkt_filter in tests:
            with self.assertRaises(ValueError):
                BeaconScanner(None, 0, dev_filter, pkt_filter)
        with self.assertRaises(ValueError):
            CJMonitorFilter(company_id=None, beacon_type=None)

    def test_good_arguments(self):
        """Test if correct filters result in no exception."""
        tests = [
            (None, None),
            ([], []),
            ([EddystoneFilter(namespace="abc")], None),
            (EddystoneFilter(namespace="abc"), None),
            (None, EddystoneTLMFrame),
            (None, [EddystoneTLMFrame]),
            (EddystoneFilter(namespace="abc"), [EddystoneTLMFrame]),
        ]

        for dev_filter, pkt_filter in tests:
            self.assertIsNotNone(BeaconScanner(None, 0, dev_filter, pkt_filter))

    def test_process_packet(self):
        """Test processing of a packet and callback execution."""
        callback = MagicMock()
        scanner = BeaconScanner(callback)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -28)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -28)
        self.assertIsInstance(args[2], EddystoneTLMFrame)
        self.assertEqual(args[3], None)

    def test_process_packet_dev_filter(self):
        """Test processing of a packet and callback execution with device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EddystoneFilter(instance="000000000001"))
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EddystoneUIDFrame)
        self.assertEqual(args[3], {
            "namespace":"12345678901234678901",
            "instance":"000000000001"
        })

    def test_process_packet_dev_filter2(self):
        """Test processing of a packet and callback execution."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EddystoneFilter(instance="000000000001"))
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        callback.assert_not_called()

    def test_process_packet_dev_filter3(self):
        """Test processing of a packet and callback execution with ibeacon device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=IBeaconFilter(major=1))
        pkt = b"\x02\x01\x06\x1a\xff\x4c"\
              b"\x00\x02\x15\x41\x42\x43\x44\x45\x46\x47\x48\x49\x40\x41\x42\x43\x44\x45\x46\x00"\
              b"\x01\x00\x02\xf8\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], IBeaconAdvertisement)
        self.assertEqual(args[3], {
            "uuid":"41424344-4546-4748-4940-414243444546",
            "major":1,
            "minor":2
        })

    def test_process_packet_dev_filter4(self):
        """Test processing of a packet and callback execution with cj Monitor device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=CJMonitorFilter())
        pkt = b"\x02\x01\x06\x05\x02\x1a\x18\x00\x18" \
              b"\x09\xff\x72\x04\xfe\x10\xbc\x0c\x37\x59" \
              b"\x09\x09\x4d\x6f\x6e\x20\x35\x36\x34\x33\xaa"
        scanner._mon.process_packet(pkt, "00:0b:57:5b:56:43", -86)
        self.assertEqual(1, callback.call_count)
        args = callback.call_args[0]
        self.assertEqual("00:0b:57:5b:56:43", args[0])
        self.assertEqual(-86, args[1])
        self.assertIsInstance(args[2], CJMonitorAdvertisement)
        self.assertEqual('CJMonitorAdvertisement<name: Mon 5643, temp: 32.6,humidity: 55, light: 160>',
                         str(args[2]))
        self.assertEqual(
            {"beacon_type": CJ_TEMPHUM_TYPE,
             "company_id": CJ_MANUFACTURER_ID,
             'name': 'Mon 5643',
             'light': 159.9,
             "temperature": 32.6,
             "humidity": 55},
            args[3])
        # Test same packet with different beacon type, should be ignored.
        scanner = BeaconScanner(callback, device_filter=CJMonitorFilter(beacon_type=4351))
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(1, callback.call_count)

    def test_process_packet_dev_packet(self):
        """Test processing of a packet and callback execution with device and packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=EddystoneFilter(namespace="12345678901234678901"),
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EddystoneUIDFrame)
        self.assertEqual(args[3], {
            "namespace":"12345678901234678901",
            "instance":"000000000001"
        })

    def test_process_packet_filter(self):
        """Test processing of a packet and callback execution with packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EddystoneUIDFrame)
        self.assertEqual(args[3], {
            "namespace":"12345678901234678901",
            "instance":"000000000001"
        })

    def test_process_packet_filter_bad(self):
        """Test processing of a packet and callback execution with packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            packet_filter=EddystoneTLMFrame
        )
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        callback.assert_not_called()

    def test_repr_filter(self):
        self.assertEqual(BtAddrFilter("aa:bb:cc:dd:ee:ff").__repr__(), "BtAddrFilter(bt_addr=aa:bb:cc:dd:ee:ff)")

    def test_wrong_btaddr(self):
        self.assertRaises(ValueError, BtAddrFilter, "az")
        self.assertRaises(ValueError, BtAddrFilter, None)
        self.assertRaises(ValueError, BtAddrFilter, "aa-bb-cc-dd-ee-fg")
        self.assertRaises(ValueError, BtAddrFilter, "aa-bb-cc-dd-ee-ff")
        self.assertRaises(ValueError, BtAddrFilter, "aabb.ccdd.eeff")
        self.assertRaises(ValueError, BtAddrFilter, "aa:bb:cc:dd:ee:")

    def test_process_packet_btaddr(self):
        """Test processing of a packet and callback execution with bt addr filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=BtAddrFilter("1c:d6:cd:ef:94:35")
        )
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EddystoneUIDFrame)
        self.assertEqual(args[3], {
            "namespace":"12345678901234678901",
            "instance":"000000000001"
        })

    def test_process_packet_bad_packet(self):
        """Test processing of a packet and callback execution with a bad packet."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=EddystoneFilter(namespace="12345678901234678901"),
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x41\x3e\x41\x02\x01\x03"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        callback.assert_not_called()

    def test_process_packet_bad_packet2(self):
        """Test processing of a packet and callback execution with a bad packet."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=EddystoneFilter(namespace="12345678901234678901"),
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x02\x01\x06\x03\x03\xaa\xfe"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        callback.assert_not_called()

    def test_process_packet_estimote_a(self):
        """Test processing of a estimote telemetry a packet and callback execution with packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, packet_filter=[EstimoteTelemetryFrameB, EstimoteTelemetryFrameA])
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x12\x47\xa0\x38\xd5\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47"\
              b"\xf0\x01\x00\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EstimoteTelemetryFrameA)
        self.assertEqual(args[3], {
            "identifier": "47a038d5eb032640",
            "protocol_version": 1
        })

    def test_process_packet_estimote_b(self):
        """Test processing of a estimote telemetry b packet and callback execution with packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, packet_filter=[EstimoteTelemetryFrameB, EstimoteTelemetryFrameA])
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5\xeb\x03\x26\x40\x01\xff\xff\xff\xff\x49"\
              b"\x25\x66\xbc\x2e\x50\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EstimoteTelemetryFrameB)
        self.assertEqual(args[3], {
            "identifier": "47a038d5eb032640",
            "protocol_version": 2
        })

    def test_process_packet_estimote_device_filter(self):
        """Test processing of a estimote packet and callback execution with device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EstimoteFilter(protocol_version=2))
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5\xeb\x03\x26\x40\x01\xff\xff\xff\xff\x49"\
              b"\x25\x66\xbc\x2e\x50\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertEqual(args[1], -35)
        self.assertIsInstance(args[2], EstimoteTelemetryFrameB)
        self.assertEqual(args[3], {
            "identifier": "47a038d5eb032640",
            "protocol_version": 2
        })

    def test_process_packet_exposure_notification_filter(self):
        """Test processing of a exposure notification with device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=ExposureNotificationFilter(identifier="0d3b4f65584c582160571dd19010d41c")
        )
        # correct identifier
        pkt = b"\x02\x01\x1a\x03\x03\x6f" \
              b"\xfd\x17\x16\x6f\xfd\x0d\x3b\x4f\x65\x58\x4c\x58\x21\x60\x57\x1d\xd1\x90\x10\xd4" \
              b"\x1c\x26\x60\xee\x34\xd1"
        # different identifier
        pkt2 = b"\x02\x01\x1a\x03\x03\x6f" \
               b"\xfd\x17\x16\x6f\xfd\x0d\x3b\x40\x65\x58\x4c\x58\x21\x60\x57\x1d\xd1\x90\x10\xd4" \
               b"\x1c\x26\x60\xee\x34\xd1"
        scanner._mon.process_packet(pkt, "0d:ea:3d:ca:ac:e1", -47)
        scanner._mon.process_packet(pkt2, "0d:ea:3d:ca:ac:e1", -47)
        self.assertEqual(callback.call_count, 1)
        args = callback.call_args[0]
        self.assertEqual(args[0], "0d:ea:3d:ca:ac:e1")
        self.assertEqual(args[1], -47)
        self.assertIsInstance(args[2], ExposureNotificationFrame)
        self.assertEqual(args[3], {
            "identifier": "0d3b4f65584c582160571dd19010d41c",
            "encrypted_metadata": b"\x26\x60\xee\x34"
        })

    def test_invalid_bt_filter(self):
        """Test passing of an invalid bluetooth address as filter."""
        callback = MagicMock()
        with self.assertRaises(ValueError):
            BeaconScanner(callback, device_filter=BtAddrFilter("this is crap"))

    def test_multiple_filters(self):
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EstimoteFilter(protocol_version=2), packet_filter=EstimoteTelemetryFrameB)
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5\xeb\x03\x26\x40\x01\xff\xff\xff\xff\x49"\
              b"\x25\x66\xbc\x2e\x50\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x12\x47\xa0\x38\xd5\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47"\
              b"\xf0\x01\x00\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 1)

    def test_multiple_filters2(self):
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=[EstimoteFilter(identifier="47a038d5eb032640", protocol_version=2), EddystoneFilter(instance="000000000001")],
            packet_filter=[EstimoteTelemetryFrameB, EddystoneUIDFrame])
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5\xeb\x03\x26\x40\x01\xff\xff\xff\xff\x49"\
              b"\x25\x66\xbc\x2e\x50\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x04\x03\x03\x9a"\
              b"\xfe\x17\x16\x9a\xfe\x12\x47\xa0\x38\xd5\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47"\
              b"\xf0\x01\x00\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x02\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        pkt = b"\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 3)

    def test_exposure_notification(self):
        callback = MagicMock()
        scanner = BeaconScanner(callback, packet_filter=[ExposureNotificationFrame])
        # Android and iOS seem to use slightly different packets
        android_pkt = b"\x03\x03\x6F\xFD\x17\x16"\
                      b"\x6F\xFD\x2C\xFB\x0D\xE0\x2B\x33\xD2\x0C\x5C\x27\x61\x12\x38\xE2\xD1\x07\x42\xB5"\
                      b"\x6E\xE5\xB8"
        scanner._mon.process_packet(android_pkt, "1c:d6:cd:ef:94:35", -35)
        ios_pkt = b"\x02\x01\x1A\x03\x03\x6F"\
                  b"\xFD\x17\x16\x6F\xFD\xE9\x32\xE8\xB0\x68\x8D\xFA\xEC\x00\x62\xB7\xD6\xD3\x5E\xEF"\
                  b"\xB5\xEE\xAA\x91\xAC\xBA"
        scanner._mon.process_packet(ios_pkt, "1c:d6:cd:ef:94:35", -35)
        self.assertEqual(callback.call_count, 2)

if __name__ == "__main__":
    unittest.main()
