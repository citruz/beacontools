"""All low level structures used for parsing COVID-19 exposure notifications."""
from construct import Array, Byte, Struct

# pylint: disable=invalid-name

# see https://blog.google/documents/70/Exposure_Notification_-_Bluetooth_Specification_v1.2.2.pdf

ExposureNotificationFrame = Struct(
    "identifier" / Array(16, Byte),
    "encrypted_metadata" / Array(4, Byte),
)
