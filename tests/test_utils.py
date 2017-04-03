"""Test the utilities component."""
import unittest

from beacontools.utils import data_to_hexstring, data_to_binstring, bt_addr_to_string, \
                              is_one_of, is_packet_type, to_int, bin_to_int, data_to_uuid
from beacontools import EddystoneUIDFrame, EddystoneURLFrame, \
                        EddystoneEncryptedTLMFrame, EddystoneTLMFrame

class TestUtils(unittest.TestCase):
    """Test the utilities."""

    def test_data_to_hexstring(self):
        """Verify that data is converted correctly."""
        tests = [
            ([0x41, 0x42, 0x43], "414243"),
            ([], "")
        ]

        for data, hexstring in tests:
            self.assertEqual(data_to_hexstring(data), hexstring)

    def test_data_to_uuid(self):
        """Verify that data is converted correctly."""
        data = b"\x41\x42\x43\x44\x45\x46\x47\x48\x49\x40\x41\x42\x43\x44\x45\x46"
        uuid = "41424344-4546-4748-4940-414243444546"
        self.assertEqual(data_to_uuid(data), uuid)

    def test_data_to_binstring(self):
        """Verify that data is converted correctly."""
        tests = [
            ([0x41, 0x42, 0x43], b"\x41\x42\x43"),
            ([], b"")
        ]

        for data, hexstring in tests:
            self.assertEqual(data_to_binstring(data), hexstring)

    def test_is_one_of(self):
        """Test is_one_of method."""
        tests = [
            ("Test", [str, list, int], True),
            ("Test", [int], False),
            (1, [int], True),
            (1, [str, list], False),
        ]

        for obj, types, expected in tests:
            self.assertEqual(is_one_of(obj, types), expected)

    def test_is_packet_type(self):
        """Check if class is one the packet types."""
        tests = [
            (EddystoneTLMFrame, True),
            (EddystoneURLFrame, True),
            (EddystoneUIDFrame, True),
            (EddystoneEncryptedTLMFrame, True),
            (str, False),
            (list, False),
            (int, False),
        ]
        for clazz, expected in tests:
            self.assertEqual(is_packet_type(clazz), expected)

    def test_to_int(self):
        """Test byte string to int conversion."""
        tests = [
            ("\x41", 0x41),
            (0x41, 0x41),
        ]
        for string, expected in tests:
            self.assertEqual(to_int(string), expected)

    def bin_to_int(self):
        """Test byte string to int conversion."""
        tests = [
            ("\xF8", -8),
            (0xF8, -8),
        ]
        for string, expected in tests:
            self.assertEqual(bin_to_int(string), expected)
