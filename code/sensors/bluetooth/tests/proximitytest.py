#!/usr/bin/python3

import sys
import time

from sensors.bluetooth.bluetooth import BTDongle, SnapshotBTDataPipeline, \
    RecommendedSpeedPipeline
from sensors.pipeline import create_sequential_pipeline, ConstantPipeline
from motor import robot


DEV_COUNT = 2
robot_control = robot.Robot()


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
        ConstantPipeline(dongles),
        SnapshotBTDataPipeline(),
        RecommendedSpeedPipeline(threshold=50)
    ])

    while True:
        succ, speed = pipeline.run_pipeline(None)
        print(succ, speed)
        if speed == 0:
            robot.stop()
        else:
            robot.forward(speed)
        time.sleep(0.4)

if __name__ == "__main__":
    main()
