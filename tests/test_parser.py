"""Test the parser component."""
import unittest

from beacontools import parse_packet, EddystoneUIDFrame, EddystoneURLFrame, \
                        EddystoneEncryptedTLMFrame, EddystoneTLMFrame, EddystoneEIDFrame, \
                        IBeaconAdvertisement, EstimoteTelemetryFrameA, EstimoteTelemetryFrameB, \
                        ExposureNotificationFrame
from beacontools.packet_types import EstimoteNearable

class TestParser(unittest.TestCase):
    """Test the parser."""

    def test_bad_packets(self):
        """Test if random data results in a None result."""
        tests = [
            b"0000000",
            b"",
            b"\x02\x01\x06\x03\x03",
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

    def test_eddystone_tlm2(self):
        """Test TLM frame."""
        tlm_packet = b"\x02\x01\x06\x03\x03\xaa\xfe\x11\x16\xaa\xfe\x20\x00\x0b\x18\x47\x11\x00" \
                     b"\x00\x14\x67\x00\x00\x2a\xc4\xe4"
        frame = parse_packet(tlm_packet)
        self.assertIsInstance(frame, EddystoneTLMFrame)
        self.assertEqual(frame.voltage, 2840)
        self.assertTrue(abs(frame.temperature_fixed_point - 17.27) < 0.1)
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


    def test_estimote_telemetry_a(self):
        telemetry_a_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47\xfa\xff\xff\xff\xff"
        frame = parse_packet(telemetry_a_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameA)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 2)
        self.assertEqual(frame.acceleration, (0, 2/127.0, 130/127.0))
        self.assertEqual(frame.is_moving, False)
        self.assertEqual(frame.current_motion_state, 420)
        self.assertEqual(frame.previous_motion_state, 240)
        self.assertEqual(frame.gpio_states, (1, 1, 1, 1))
        self.assertEqual(frame.has_firmware_error, False)
        self.assertEqual(frame.has_clock_error, True)
        self.assertEqual(frame.pressure, None)
        self.assertIsNotNone(str(frame))

    def test_estimote_telemetry_a2(self):
        telemetry_a_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x12\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47\xf0\x01\x00\x00\x00"
        frame = parse_packet(telemetry_a_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameA)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 1)
        self.assertEqual(frame.acceleration, (0, 2/127.0, 130/127.0))
        self.assertEqual(frame.is_moving, False)
        self.assertEqual(frame.current_motion_state, 420)
        self.assertEqual(frame.previous_motion_state, 240)
        self.assertEqual(frame.gpio_states, (1, 1, 1, 1))
        self.assertEqual(frame.has_firmware_error, True)
        self.assertEqual(frame.has_clock_error, False)
        self.assertEqual(frame.pressure, None)
        self.assertIsNotNone(str(frame))

    def test_estimote_telemetry_a3(self):
        telemetry_a_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x02\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x00\x00\x01\x41\x44\x47\xf0\x01\x00\x00\x00"
        frame = parse_packet(telemetry_a_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameA)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 0)
        self.assertEqual(frame.acceleration, (0, 2/127.0, 130/127.0))
        self.assertEqual(frame.is_moving, False)
        self.assertEqual(frame.current_motion_state, 420)
        self.assertEqual(frame.previous_motion_state, 240)
        self.assertEqual(frame.gpio_states, (1, 1, 1, 1))
        self.assertEqual(frame.has_firmware_error, None)
        self.assertEqual(frame.has_clock_error, None)
        self.assertEqual(frame.pressure, None)
        self.assertIsNotNone(str(frame))

    def test_estimote_telemetry_b(self):
        telemetry_b_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x01\xff\xff\xff\xff\x49\x25\x66\xbc\x2e\x50"
        frame = parse_packet(telemetry_b_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameB)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 2)
        self.assertEqual(frame.magnetic_field, None)
        self.assertEqual(frame.ambient_light, None)
        self.assertEqual(frame.uptime, 4870800)
        self.assertEqual(frame.temperature, 25.5)
        self.assertEqual(frame.has_firmware_error, None)
        self.assertEqual(frame.has_clock_error, None)
        self.assertEqual(frame.battery_level, 80)
        self.assertIsNotNone(str(frame))

    def test_estimote_telemetry_b2(self):
        telemetry_b_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x22\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x01\xd8\x42\xed\x73\x49\x25\x66\xbc\x2e\x50"
        frame = parse_packet(telemetry_b_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameB)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 2)
        self.assertEqual(frame.magnetic_field, (-0.3125, 0.515625, -0.1484375))
        self.assertEqual(frame.ambient_light, 276.48)
        self.assertEqual(frame.uptime, 4870800)
        self.assertEqual(frame.temperature, 25.5)
        self.assertEqual(frame.has_firmware_error, None)
        self.assertEqual(frame.has_clock_error, None)
        self.assertEqual(frame.battery_level, 80)
        self.assertIsNotNone(str(frame))

    def test_estimote_telemetry_b3(self):
        telemetry_b_packet = b"\x02\x01\x04\x03\x03\x9a\xfe\x17\x16\x9a\xfe\x02\x47\xa0\x38\xd5"\
                             b"\xeb\x03\x26\x40\x01\xd8\x42\xed\x73\x49\x25\x66\xbc\x2e\x53"
        frame = parse_packet(telemetry_b_packet)
        self.assertIsInstance(frame, EstimoteTelemetryFrameB)
        self.assertEqual(frame.identifier, "47a038d5eb032640")
        self.assertEqual(frame.protocol_version, 0)
        self.assertEqual(frame.magnetic_field, (-0.3125, 0.515625, -0.1484375))
        self.assertEqual(frame.ambient_light, 276.48)
        self.assertEqual(frame.uptime, 4870800)
        self.assertEqual(frame.temperature, 25.5)
        self.assertEqual(frame.has_firmware_error, True)
        self.assertEqual(frame.has_clock_error, True)
        self.assertEqual(frame.battery_level, None)
        self.assertIsNotNone(str(frame))

    def test_estimote_nearable(self):
        nearable_packet = b"\x02\x01\x04\x03\x03\x0f" \
                          b"\x18\x17\xff\x5d\x01\x01\x1e\xfe\x42\x7e" \
                          b"\xb6\xf4\xbc\x2f\x04\x01\x68\xa1\xaa\xfe" \
                          b"\x05\xc1\x45\x25\x53"
        frame = parse_packet(nearable_packet)
        self.assertIsInstance(frame, EstimoteNearable)
        self.assertEqual("1efe427eb6f4bc2f", frame.identifier)
        self.assertEqual(22.5, frame.temperature)
        self.assertEqual(1, frame.firmware_version)
        self.assertEqual(4, frame.hardware_version)
        self.assertFalse(frame.is_moving)

    def test_exposure_notification(self):
        exposure_packet = b"\x02\x01\x1a\x03\x03\x6f\xfd\x17\x16\x6f\xfd\x0d\x3b\x4f" \
                          b"\x65\x58\x4c\x58\x21\x60\x57\x1d\xd1\x90\x10\xd4\x1c\x26" \
                          b"\x60\xee\x34\xd1"
        frame = parse_packet(exposure_packet)
        self.assertIsInstance(frame, ExposureNotificationFrame)
        self.assertEqual("0d3b4f65584c582160571dd19010d41c", frame.identifier)
        self.assertEqual(b"\x26\x60\xee\x34", frame.encrypted_metadata)


if __name__ == "__main__":
    unittest.main()
