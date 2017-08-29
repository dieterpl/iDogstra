import time  # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers
import sys
import os
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/motor"))
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/gestures"))
import head
import robot
import screenDog
from threading import Thread
"""
dont use this, TODO: implement this, currently bei head.py
"""
class Gestures:
    def __enter__(self):
        self.head = head.Head()
        self.screen = screenDog.ScreenDog()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        return None

    def idle(self, breakflag):
        """
        Displays the dog searching through monitor 0
        :param breakflag: Stops this emotion if breakflag is true
        :return:
        """
        while not breakflag:
            for element in gs.screen.Gesture.searchArray:
                if not breakflag:
                    gs.screen.change_gesture(element)
                    time.sleep(0.2)

    def search(self, breakflag):
        """
        Displays the dog sleeping through monitor 0
        :param breakflag: Stops this emotion if breakflag is true
        :return:
        """
        while not breakflag:
            for element in gs.screen.Gesture.sleepArray:
                if not breakflag:
                    gs.screen.change_gesture(element)
                    time.sleep(0.5)

def startHeadshaking():
    gs.head.headshake(gs.head.MAX_RANGE / 4)


if __name__ == '__main__':
    with Gestures() as gs:
        t = Thread(target=startHeadshaking)
        t.start()

        #time.sleep(1)
        #gs.head.headshake(gs.head.MAX_RANGE*3)

        #gs.idle(False)
        gs.search(False)