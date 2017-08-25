#!/usr/bin/python3

"""This module opens multiple bluetooth dongles and provides access to the RSSI values"""

import sys
import time

from blescan import BTDongle

def main():
    if len(sys.argv) != 5:
        print("Usage:", sys.argv[0], "<front> <back> <left> <right>")
        sys.exit(1)

    # Arduino
    #target = "74278bdab64445208f0c720eaf059935"
    # Lukas handy
    target = "6951e12f049945d2930e1fc462c721c8"

    ids = []
    for i in range(4):
        ids.append(int(sys.argv[i + 1]))

    dongles = [BTDongle(id, target) for id in ids]
    front, back, left, right = dongles[0], dongles[1], dongles[2], dongles[3]

    #right.offset = -10

    # Start scanning in seperate threads
    for dongle in dongles:
        dongle.start()

    state = None

    while True:
        favg = front.avg()
        bavg = back.avg()
        lavg = left.avg()
        ravg = right.avg()
        xdiff = bavg - favg
        ydiff = ravg - lavg

        print("xdiff: %02.2f ydiff: %02.2f" % (xdiff, ydiff))
        print("front: " + str(xdiff > 0) + " left: " + (str(ydiff > 0)))
        print("front: %02.2f back: %02.2f left: %02.2f right: %02.2f" %
              (favg, bavg, lavg, ravg))
        #print("%02.2f" % ((favg + bavg + lavg + ravg) / len(dongles)))
        time.sleep(1)
        continue

        diff = abs(lavg - ravg)
        stddeviation = (left.standardDeviation() +
                        right.standardDeviation()) / len(dongles)
        if stddeviation < 6:
            if lavg > ravg:
                state = Direction.RIGHT
            else:
                state = Direction.LEFT
            pct = 100 * min(10, diff) / 10
            print(state.name, pct, "%")
        else:
            print("object probably moving")
        # print("lavg: %02.2f ravg: %02.2f stddev: %02.2f" %
        #       (lavg, ravg, stddeviation), state.name)
        # print()


if __name__ == "__main__":
    main()
