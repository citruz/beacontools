"""Test the scanner component."""
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from beacontools import BeaconScanner, EddystoneFilter, EddystoneTLMFrame, EddystoneUIDFrame, \
                        BtAddrFilter

class TestScanner(unittest.TestCase):
    """Test the BeaconScanner."""

    def test_bad_arguments(self):
        """Test if wrong filters result in ValueError."""
        tests = [
            ([{"namespace" : "ABC"}], None),
            (None, EddystoneFilter()),
            (None, [EddystoneFilter()]),
            (EddystoneTLMFrame, []),
            ([EddystoneTLMFrame], None),
            ([EddystoneTLMFrame], [EddystoneFilter()]),
        ]

        for dev_filter, pkt_filter in tests:
            with self.assertRaises(ValueError):
                BeaconScanner(None, 0, dev_filter, pkt_filter)

    def test_good_arguments(self):
        """Test if correct filters result in no exception."""
        tests = [
            (None, None),
            ([], []),
            ([EddystoneFilter()], None),
            (EddystoneFilter(), None),
            (None, EddystoneTLMFrame),
            (None, [EddystoneTLMFrame]),
            (EddystoneFilter(), [EddystoneTLMFrame]),
        ]

        for dev_filter, pkt_filter in tests:
            self.assertIsNotNone(BeaconScanner(None, 0, dev_filter, pkt_filter))

    def test_process_packet(self):
        """Test processing of a packet and callback execution."""
        callback = MagicMock()
        scanner = BeaconScanner(callback)
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        scanner._mon.process_packet(pkt)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertIsInstance(args[1], EddystoneTLMFrame)
        self.assertEqual(args[2], None)

    def test_process_packet_dev_filter(self):
        """Test processing of a packet and callback execution with device filter."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EddystoneFilter(instance="000000000001"))
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertIsInstance(args[1], EddystoneUIDFrame)
        self.assertEqual(args[2], {
            "namespace":"12345678901234678901",
            "instance":"000000000001"
        })

    def test_process_packet_dev_filter2(self):
        """Test processing of a packet and callback execution."""
        callback = MagicMock()
        scanner = BeaconScanner(callback, device_filter=EddystoneFilter(instance="000000000001"))
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        scanner._mon.process_packet(pkt)
        callback.assert_not_called()

    def test_process_packet_dev_packet(self):
        """Test processing of a packet and callback execution with device and packet filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=EddystoneFilter(namespace="12345678901234678901"),
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertIsInstance(args[1], EddystoneUIDFrame)
        self.assertEqual(args[2], {
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
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertIsInstance(args[1], EddystoneUIDFrame)
        self.assertEqual(args[2], {
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
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt)
        callback.assert_not_called()

    def test_process_packet_btaddr(self):
        """Test processing of a packet and callback execution with bt addr filter."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=BtAddrFilter("1c:d6:cd:ef:94:35")
        )
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe\x11\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90\x12\x34\x67\x89\x01\x00\x00\x00"\
              b"\x00\x00\x01\x00\x00\xdd"
        scanner._mon.process_packet(pkt)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertEqual(args[0], "1c:d6:cd:ef:94:35")
        self.assertIsInstance(args[1], EddystoneUIDFrame)
        self.assertEqual(args[2], {
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
        scanner._mon.process_packet(pkt)
        callback.assert_not_called()

    def test_process_packet_bad_packet2(self):
        """Test processing of a packet and callback execution with a bad packet."""
        callback = MagicMock()
        scanner = BeaconScanner(
            callback,
            device_filter=EddystoneFilter(namespace="12345678901234678901"),
            packet_filter=EddystoneUIDFrame
        )
        pkt = b"\x41\x3e\x41\x02\x01\x03\x01\x35\x94\xef\xcd\xd6\x1c\x19\x02\x01\x06\x03\x03\xaa"\
              b"\xfe"
        scanner._mon.process_packet(pkt)
        callback.assert_not_called()
