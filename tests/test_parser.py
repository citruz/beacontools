"""Test the parser component."""
import unittest

from beacontools import parse_packet, EddystoneUIDFrame, EddystoneURLFrame, \
                        EddystoneEncryptedTLMFrame, EddystoneTLMFrame

class TestParser(unittest.TestCase):
    """Test the parser."""

    def test_bad_packets(self):
        """Test if random data results in a None result."""
        tests = [
            b"0000000",
            b"",
            b"\x02\x01\x06\x03\x03",
            b"\x02\x01\x06\x03\x03\xab\xfe\x17\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90" \
            b"\x12\x34\x67\x89\x01\x00\x00\x00\x00\x00\x01\x00\x00",
            b"\x02\x01\x06\x03\x03\xaa\xfe\x17\x16\xaa\xfe\x01\xe3\x12\x34\x56\x78\x90" \
            b"\x12\x34\x67\x89\x01\x00\x00\x00\x00\x00\x01\x00\x00"
        ]

        for test in tests:
            frame = parse_packet(test)
            self.assertIsNone(frame)


    def test_eddystone_uid(self):
        """Test UID frame."""
        uid_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x17\x16\xaa\xfe\x00\xe3\x12\x34\x56\x78\x90" \
                     b"\x12\x34\x67\x89\x01\x00\x00\x00\x00\x00\x01\x00\x00"

        frame = parse_packet(uid_packet)
        self.assertIsInstance(frame, EddystoneUIDFrame)
        self.assertEqual(frame.namespace, "12345678901234678901")
        self.assertEqual(frame.instance, "000000000001")
        self.assertEqual(frame.tx_power, -29)

    def test_eddystone_url(self):
        """Test URL frame."""
        url_packet = b"\x03\x03\xAA\xFE\x13\x16\xAA\xFE\x10\xF8\x03github\x00citruz"

        frame = parse_packet(url_packet)
        self.assertIsInstance(frame, EddystoneURLFrame)
        self.assertEqual(frame.url, "https://github.com/citruz")
        self.assertEqual(frame.tx_power, -8)

    def test_eddystone_tlm(self):
        """Test TLM frame."""
        tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x13\x00\x00" \
                     b"\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        frame = parse_packet(tlm_packet)
        self.assertIsInstance(frame, EddystoneTLMFrame)
        self.assertEqual(frame.voltage, 2840)
        self.assertEqual(frame.temperature, 19)
        self.assertEqual(frame.advertising_count, 5223)
        self.assertEqual(frame.seconds_since_boot, 10948)

    def test_eddystone_tlm_enc(self):
        """Test encrypted TLM frame."""
        enc_tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x01\x41\x41\x41" \
                         b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\xDE\xAD\xBE\xFF"
        frame = parse_packet(enc_tlm_packet)
        self.assertIsInstance(frame, EddystoneEncryptedTLMFrame)
        self.assertEqual(frame.encrypted_data, b'AAAAAAAAAAAA')
        self.assertEqual(frame.salt, 44510)
        self.assertEqual(frame.mic, 65470)
