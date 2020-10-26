"""Custom backend for FreeBSD."""
import os
import socket
import struct
import ctypes

libc = ctypes.cdll.LoadLibrary('libc.so.7')

NG_HCI_EVENT_MASK_LE = 0x2000000000000000
SOL_HCI_RAW = 0x0802
SOL_HCI_RAW_FILTER = 1

class SockaddrHci(ctypes.Structure):
    """Structure representing a hci socket address."""
    _fields_ = [
        ('hci_len', ctypes.c_char),
        ('hci_family', ctypes.c_char),
        ('hci_node', ctypes.c_char * 32),
    ]

class HciRawFilter(ctypes.Structure):
    """Structure specifying filter masks."""
    _fields_ = [
        ('packet_mask', ctypes.c_uint32),
        ('event_mask', ctypes.c_uint64),
    ]

def open_dev(bt_device_id):
    """Open hci device socket."""
    # pylint: disable=no-member
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)

    # Unlike Linux, FreeBSD has separate numbering depending on hardware
    # (ubt - USB bluetooth - is the most common, so convert numbers to that)
    if not isinstance(bt_device_id, str):
        bt_device_id = 'ubt{}hci'.format(bt_device_id)

    # Python's BTPROTO_HCI address parsing is busted: https://bugs.python.org/issue41130
    adr = SockaddrHci(ctypes.sizeof(SockaddrHci), socket.AF_BLUETOOTH, bt_device_id.ljust(32, '\0').encode('utf-8'))
    if libc.bind(sock.fileno(), ctypes.pointer(adr), ctypes.sizeof(SockaddrHci)) != 0:
        raise ConnectionError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
    if libc.connect(sock.fileno(), ctypes.pointer(adr), ctypes.sizeof(SockaddrHci)) != 0:
        raise ConnectionError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
    # pylint: enable=no-member

    fltr = HciRawFilter(0, NG_HCI_EVENT_MASK_LE)
    if libc.setsockopt(sock.fileno(),
                       SOL_HCI_RAW, SOL_HCI_RAW_FILTER,
                       ctypes.pointer(fltr), ctypes.sizeof(HciRawFilter)) != 0:
        raise ConnectionError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))

    return sock

def send_cmd(sock, group_field, command_field, data):
    """Send hci command to device."""
    opcode = (((group_field & 0x3f) << 10) | (command_field & 0x3ff))
    sock.send(struct.pack('<BHB', 1, opcode, len(data)) + data)

def send_req(_socket, _group_field, _command_field, _event, _rlen, _params, _timeout):
    """Support for HCI 5 has not been implemented yet for FreeBSD, pull requests are wellcome"""
    raise NotImplementedError("send_req has not been implemented yet for FreeBSD")
