# BLE Scanner based on https://github.com/switchdoclabs/iBeacon-Scanner-/blob/master/blescan.py
# BLE = Bluetooth Low Energy

import os
import sys
import struct
import bluetooth._bluetooth as bluez
import math
import time

from collections import deque
from collections import namedtuple
from threading import Thread
from utils.functions import current_time_millis


OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C

LE_META_EVENT = 0x3e
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02


# Named tuple that represents the data that the ble scan returns
FindResult = namedtuple("FindResult", "uuid rssi")


def returnstringpacket(pkt):
    """Returns a packet as hex string"""

    myString = ""
    for c in pkt:
        myString += "%02x" % c
    return myString


def parse_events(sock, target_uuid, loop_count=100):
    """Parses the events that the bluetooth socket recieves"""
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    result = None
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == LE_META_EVENT:
            subevent = pkt[3]
            pkt = pkt[4:]
            if subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = pkt[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    uuid = returnstringpacket(
                        pkt[report_pkt_offset - 22: report_pkt_offset - 6])
                    rssi = struct.unpack("b", pkt[report_pkt_offset - 1:])[0]
                    if uuid == target_uuid:
                        result = FindResult(uuid, rssi)
                        break
                else:
                    continue
                break
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return result


DEFAULT_OLD_DATA_THRESHOLD = 10000
DEFAULT_AVG_THRESHOLD = 2000


# A named tuple that defines how the received rssi values are stored.
# Note that the rssi value is negative, whereas the data in this
# tuple will be positive.
DataTuple = namedtuple("DataTuple", "time strength")


class DataList:
    """This is a snapshot of the bt dongle data. It contains multiple
    values in a list and provides convenience methods to analyse the data"""

    def __init__(self, threshold, data_list):
        """threshold is the amount of time this snapshot is representing.
        data_list is the list of DataTuple's"""
        self.threshold = threshold
        self.data_list = data_list

    def __len__(self):
        """Returns the amount of data this snapshot contains"""
        return len(self.data_list)

    def avg(self):
        """Returns the average of all values"""

        s = 0
        for _, strength in self.data_list
            s += strength
        count = len(self)
        return s / count if count > 0 else 0

    def variance(self):
        """Returns the variance of all values"""

        s = 0
        avg = self.avg()
        for _, strength in self.data_list
            s += (strength - avg)**2
        count = len(self)
        return s / count if count > 0 else 0

    def standard_deviation(self):
        """Returns the standard deviation of all values. Equivalent to
        math.sqrt(self.variance())"""

        return math.sqrt(self.variance())


class BTDongle:
    """Manages a single bluetooth dongle and stores the received data.
    The data is stored in a double ended queue (deque) which allows
    accessing the newest and oldest data in a very efficient way. For
    performance reasons older data is being deleted, each time, new data
    is inserted."""

    def __init__(self, dev_id, target):
        self.dev_id = dev_id
        self.target = target

        self.sock = None
        self.data = deque()
        self.current = 0
        self.thread = Thread(target=self.scan_loop)
        self.offset = 0

    def start(self):
        """Initializes the bluetooth socket, and starts reading rssi values
        in a new thread"""

        # Open the bt socket
        self.sock = bluez.hci_open_dev(self.dev_id)
        # Enable ble scan
        bluez.hci_send_cmd(
            sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, struct.pack("<BB", enable, 0x00))
        # Start scanning in a new thread
        self.thread.start()

    def remove_old_data(self, threshold=DEFAULT_OLD_DATA_THRESHOLD):
        """Removes data tuples from the queue that are older
        than threshold milliseconds"""

        threshold = current_time_millis() - threshold
        while(len(self.data) > 0 and self.data[0].time < threshold):
            self.data.popleft()

    def add_data(self, rssi):
        """Adds a new rssi value. This also calls self.remove_old_data()"""

        # Positive rssi values are very rare, and indicate a very
        # good connection. We simplify this by setting the value to
        # 0, which indicates the best possible strength in our terms.
        if rssi > 0:
            rssi = 0

        # Remove old entries from the queue that are older than 10 sec
        self.remove_old_data()
        # Add the new rssi value to the data queue
        self.data.append(self.DataTuple(
            current_time_millis(), abs(rssi) + self.offset))

    def scan(self):
        """Scans a single time for ble beacons"""

        result = parse_events(self.sock, self.target, loop_count=10)
        if result != None:
            self.addData(result.rssi)

    def scan_loop(self):
        """Scans in a loop for ble beacons. Simply calls self.scan() in a
        while True loop"""

        while True:
            self.scan()

    def snapshot_data(self, threshold):
        """Returns a snapshot of the data in form of a DataList object.
        This contains all data that has been collected in the last threshold
        milliseconds"""
        threshold = current_time_millis() - threshold

        data_list = []
        for t in reversed(self.data):
            # Stop when data is too old
            if t.time < threshold:
                break
            data_list.append(t)
        return DataList(threshold, data_list)
