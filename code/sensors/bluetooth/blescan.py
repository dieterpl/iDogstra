# BLE Scanner based on https://github.com/switchdoclabs/iBeacon-Scanner-/blob/master/blescan.py

# THIS FILE IS DEPRECATED
# USE bluetooth.py instead!

import os
import sys
import struct
import bluetooth._bluetooth as bluez
import math
import time

from collections import deque
from collections import namedtuple
from threading import Thread

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04


class FindResult:
    def __init__(self, uuid, mac, rssi):
        self.uuid = uuid
        self.mac = mac
        self.rssi = rssi


def returnstringpacket(pkt):
    myString = ""
    for c in pkt:
        myString += "%02x" % c
    return myString


def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)


def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01


def parse_events(sock, target_uuid, loop_count=100):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    result = None
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI or \
                event == bluez.EVT_NUM_COMP_PKTS or \
                event == bluez.EVT_DISCONN_COMPLETE:
            i = 0
        elif event == LE_META_EVENT:
            subevent = pkt[3]
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = pkt[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    uuid = returnstringpacket(
                        pkt[report_pkt_offset - 22: report_pkt_offset - 6])
                    mac = packed_bdaddr_to_string(
                        pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                    rssi = struct.unpack("b", pkt[report_pkt_offset - 1:])[0]
                    if uuid == target_uuid:
                        result = FindResult(uuid, mac, rssi)
                        break
                else:
                    continue
                break
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return result


def current_milli_time() -> int:
    """ Returns the current milli seconds as int"""
    return int(round(time.time() * 1000))


DEFAULT_OLD_DATA_THRESHOLD = 10000
DEFAULT_AVG_THRESHOLD = 2000


class BTDongle:
    DataTuple = namedtuple("DataTuple", "time strength")

    def __init__(self, dev_id, target):
        self.dev_id = dev_id
        self.target = target

        self.sock = None
        self.data = deque()
        self.current = 0
        self.thread = Thread(target=self.scanLoop)
        self.offset = 0

    def start(self):
        """Initializes the bluetooth socket, and starts reading rssi values
        in a new thread"""

        self.sock = bluez.hci_open_dev(self.dev_id)
        hci_le_set_scan_parameters(self.sock)
        hci_enable_le_scan(self.sock)
        self.thread.start()

    def removeOldData(self, threshold=DEFAULT_OLD_DATA_THRESHOLD):
        """Removes data tuples from the queue that are older
        than threshold milliseconds"""

        threshold = current_milli_time() - threshold
        while(len(self.data) > 0 and self.data[0].time < threshold):
            self.data.popleft()

    def addData(self, rssi):
        # Positive rssi values are very rare, and indicate a very
        # good connection. We simplify this by setting the value to
        # 0, which indicates the best possible strength in our terms.
        if rssi > 0:
            rssi = 0

        # Remove old entries from the queue that are older than 10 sec
        self.removeOldData()
        self.data.append(self.DataTuple(
            current_milli_time(), abs(rssi) + self.offset))

    def scan(self):
        result = parse_events(self.sock, self.target, loop_count=10)
        if result != None:
            self.addData(result.rssi)

    def scanLoop(self):
        while True:
            self.scan()

    def recentData(self, threshold):
        """Returns a generator object that yields data tuples of the last
        threshold milliseconds"""

        threshold = current_milli_time() - threshold
        for t in reversed(self.data):
            # Stop when data is too old
            if t.time < threshold:
                break
            yield t

    def datacount(self, threshold=DEFAULT_AVG_THRESHOLD):
        """Returns the amount of data that has been collected in the last
        threshold milliseconds"""

        return sum(1 for _ in self.recentData(threshold))

    def avg(self, threshold=DEFAULT_AVG_THRESHOLD):
        s, count = 0, 0
        for _, strength in self.recentData(threshold):
            s += strength
            count += 1
        return s / count if count > 0 else 0

    def variance(self, threshold=DEFAULT_AVG_THRESHOLD):
        s, count = 0, 0
        avg = self.avg(threshold)
        for _, strength in self.recentData(threshold):
            s += (strength - avg)**2
            count += 1
        return s / count if count > 0 else 0

    def standardDeviation(self, threshold=DEFAULT_AVG_THRESHOLD):
        return math.sqrt(self.variance(threshold))
