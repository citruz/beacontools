from bluetooth import _bluetooth as bluez

def open_dev(bt_device_id):
    socket = bluez.hci_open_dev(bt_device_id)

    filtr = bluez.hci_filter_new()
    bluez.hci_filter_all_events(filtr)
    bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
    socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filtr)

    return socket

def send_cmd(socket, gf, cf, data):
    return bluez.hci_send_cmd(socket, gf, cf, data)
