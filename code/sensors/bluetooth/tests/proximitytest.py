#!/usr/bin/python3

import sys
import time

from sensors.bluetooth.bluetooth import BTDongle, SnapshotBTDataPipeline, \
        RecommendedSpeedPipeline
from sensors.pipeline import create_sequential_pipeline
from motor import movement


DEV_COUNT = 2


def avg(dongles):
    return sum(dongle.snapshot_data().avg() for dongle in dongles) / len(dongles)


def stddev(dongles):
    return sum(dongle.snapshot_data().standard_deviation() for dongle in dongles) / len(dongles)


def main():
    if len(sys.argv) != 1 + DEV_COUNT:
        print("Usage:", sys.argv[0], "<dev_id_1> <dev_id_2>")
        sys.exit(1)

    target = "6951e12f049945d2930e1fc462c721c8"

    ids = []
    for i in range(DEV_COUNT):
        ids.append(int(sys.argv[i + 1]))
    dongles = [BTDongle(id, target) for id in ids]
    for dongle in dongles:
        dongle.start()

    pipeline = create_sequential_pipeline([
            SnapshotBTDataPipeline(),
            RecommendedSpeedPipeline(threshold=50)
        ])


    while True:
        succ, speed = pipeline.run_pipeline(dongles)
        print(succ, speed)
        if speed == 0:
            movement.stop()
        else:
            movement.forward(speed)
        time.sleep(0.4)

    while True:
        # for dongle in dongles:
        #    print("%02.2f %d " % (dongle.avg(), dongle.datacount()), end="")
        a = avg(dongles)
        s = stddev(dongles)
        if a < 40:
            print("direkt dran")
        elif a < 50:
            print("nah dran")
        elif a < 60:
            print("nicht so ganz nah, aber auch nicht wirklich weit")
        elif a < 70:
            print("ca. 1 m")
        elif a < 80:
            print("einige Meter")
        else:
            print("weit entfernt")
        print("%02.2f %02.2f" % (a, s))
        time.sleep(1)


if __name__ == "__main__":
    main()
