"""Test the parser component."""
import unittest

from beacontools import parse_packet, EddystoneUIDFrame, EddystoneURLFrame, \
                        EddystoneEncryptedTLMFrame, EddystoneTLMFrame, EddystoneEIDFrame, \
                        IBeaconAdvertisement

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
        self.assertEqual(frame.properties, {
            "namespace":"12345678901234678901",
            "instance":"000000000001",
        })
        self.assertIsNotNone(str(frame))

    def test_eddystone_url(self):
        """Test URL frame."""
        url_packet = b"\x03\x03\xAA\xFE\x13\x16\xAA\xFE\x10\xF8\x03github\x00citruz"

        frame = parse_packet(url_packet)
        self.assertIsInstance(frame, EddystoneURLFrame)
        self.assertEqual(frame.url, "https://github.com/citruz")
        self.assertEqual(frame.tx_power, -8)
        self.assertIsNotNone(str(frame))

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
        self.assertIsNotNone(str(frame))

    def test_eddystone_tlm_enc(self):
        """Test encrypted TLM frame."""
        enc_tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x01\x41\x41\x41" \
                         b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\xDE\xAD\xBE\xFF"
        frame = parse_packet(enc_tlm_packet)
        self.assertIsInstance(frame, EddystoneEncryptedTLMFrame)
        self.assertEqual(frame.encrypted_data, b'AAAAAAAAAAAA')
        self.assertEqual(frame.salt, 44510)
        self.assertEqual(frame.mic, 65470)
        self.assertIsNotNone(str(frame))

    def test_eddystone_eid(self):
        """Test EID frame."""
        eid_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x0d\x16\xaa\xfe\x30\xe3" \
                     b"\x45\x49\x44\x5f\x74\x65\x73\x74"
        frame = parse_packet(eid_packet)
        self.assertIsInstance(frame, EddystoneEIDFrame)
        self.assertEqual(frame.tx_power, -29)
        self.assertEqual(frame.eid, b'EID_test')
        self.assertIsNotNone(str(frame))

    def test_ibeacon(self):
        """Test iBeacon advertisement."""
        ibeacon_packet = b"\x02\x01\x06\x1a\xff\x4c\x00\x02\x15\x41\x42\x43\x44\x45\x46\x47\x48"\
                         b"\x49\x40\x41\x42\x43\x44\x45\x46\x00\x01\x00\x02\xf8"
        frame = parse_packet(ibeacon_packet)
        self.assertIsInstance(frame, IBeaconAdvertisement)
        self.assertEqual(frame.uuid, "41424344-4546-4748-4940-414243444546")
        self.assertEqual(frame.major, 1)
        self.assertEqual(frame.minor, 2)
        self.assertEqual(frame.tx_power, -8)
        self.assertIsNotNone(str(frame))

    def test_cypress_beacon(self):
        """Test Cypress Cyalkit-E02 Sensor Beacon advertisement."""
        cypress_packet = b"\x02\x01\x04\x1a\xff\x4c\x00\x02\x15\x00\x05\x00\x01\x00\x00\x10\x00"\
                         b"\x80\x00\x00\x80\x5f\x9b\x01\x31\x00\x02\x6c\x66\xc3"
        frame = parse_packet(cypress_packet)
        self.assertIsInstance(frame, IBeaconAdvertisement)
        self.assertEqual(frame.uuid, "00050001-0000-1000-8000-00805f9b0131")
        self.assertEqual(frame.major, 2)
        self.assertEqual(int(frame.cypress_temperature*100), 2316)
        self.assertEqual(int(frame.cypress_humidity*100), 4673)
        self.assertEqual(frame.tx_power, -61)
        self.assertIsNotNone(str(frame))
