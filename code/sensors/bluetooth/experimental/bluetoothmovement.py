#!/usr/bin/python3

"""This module opens multiple bluetooth dongles and provides access to the RSSI values"""

import blescan
import sys
import time
import math
import movement

import bluetooth._bluetooth as bluez

from enum import Enum
from collections import deque
from collections import namedtuple


def current_milli_time() -> int:
    """ Returns the current milli seconds as int"""
    return int(round(time.time() * 1000))


DEFAULT_OLD_DATA_THRESHOLD = 10000
DEFAULT_AVG_THRESHOLD = 3000


class Direction(Enum):
    FRONT = 0
    LEFT = 1
    RIGHT = 2


class BTDongle:
    DataTuple = namedtuple("DataTuple", "time strength")

    def __init__(self, dev_id):
        self.dev_id = dev_id
        self.sock = None
        self.data = deque()
        self.current = 0

    def open(self):
        self.sock = bluez.hci_open_dev(self.dev_id)
        blescan.hci_le_set_scan_parameters(self.sock)
        blescan.hci_enable_le_scan(self.sock)

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
        self.data.append(self.DataTuple(current_milli_time(), abs(rssi)))

    def recentData(self, threshold):
        """Returns a generator object that yields data tuples of the last
        threshold milliseconds"""

        threshold = current_milli_time() - threshold
        for t in reversed(self.data):
            # Stop when data is too old
            if t.time < threshold:
                break
            yield t

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


def main():
    if len(sys.argv) != 3:
        print("Usage:", sys.argv[0], "<left> <right>")
        sys.exit(1)

    ids = int(sys.argv[1]), int(sys.argv[2])
    dongles = [BTDongle(id) for id in ids]
    left, right = dongles[0], dongles[1]

    for dongle in dongles:
        dongle.open()

    # Lukas Smartphone
    # target = "6951e12f049945d2930e1fc462c721c8"
    target = "6546bc8087e44c42a2c3a386d0ea1864"
    state = None
    lastmove =0

    while True:
        for dongle in dongles:
            result = blescan.parse_events(dongle.sock, target, loop_count=10)
            if result != None:
                dongle.addData(result.rssi)
            # print("%02.2f %02.2f | " %
            #       (dongle.avg(), dongle.standardDeviation()), end="")
        # print()
        lavg = left.avg()
        ravg = right.avg()
        diff = abs(lavg - ravg)
        stddeviation = (left.standardDeviation() +
                        right.standardDeviation()) / len(dongles)

        avg = (lavg + ravg) / len(dongles)

        print("%02.2f" % avg)

        # The following code moves the robot as long as the rssi value
        # is too high

        #if avg >= 60:
        #    movement.forward(min(100, 15 + 6 * (avg - 60)))
        #else:
        #    movement.stop()
        #continue



        # The following code rotates the robot based on the beacon
        # location

        if stddeviation < 6:
            if lavg > ravg:
                state = Direction.RIGHT
            else:
                state = Direction.LEFT
            pct = 100 * min(10, diff) / 10
            print("%02.2f %02.2f" % (lavg, ravg), state.name, pct, "%")

            if pct > 40 and (current_milli_time() - lastmove) > 3000:
                if state == Direction.RIGHT:
                    movement.rightspin(30, 1)
                else:
                    movement.leftspin(30, 1)
                #movement.forward(40)
                #time.sleep(2)
                #movement.stop()
                lastmove = current_milli_time()
        else:
            print("object probably moving")
        # print("lavg: %02.2f ravg: %02.2f stddev: %02.2f" %
        #       (lavg, ravg, stddeviation), state.name)
        # print()


if __name__ == "__main__":
    main()
