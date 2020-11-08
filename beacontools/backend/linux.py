"""Backend for Linux using bluez"""
from bluetooth import _bluetooth as bluez

# pylint: disable=c-extension-no-member

def open_dev(bt_device_id):
    """Open hci device socket."""
    socket = bluez.hci_open_dev(bt_device_id)

    filtr = bluez.hci_filter_new()
    bluez.hci_filter_all_events(filtr)
    bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
    socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filtr)

    return socket

def send_cmd(socket, group_field, command_field, data):
    """Send hci command to device."""
    return bluez.hci_send_cmd(socket, group_field, command_field, data)

def send_req(socket, group_field, command_field, event, rlen, params, timeout):
    """Send hci request to device."""
    return bluez.hci_send_req(socket, group_field, command_field, event, rlen, params, timeout)
