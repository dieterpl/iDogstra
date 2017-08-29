import time  # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers
import sys
import os
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/motor"))
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/gestures"))
import head
import robot
import screenDog
"""
dont use this, TODO: implement this, currently bei head.py
"""
class Gestures:
    def __enter__(self):
        self.head = head.Head()
        #self.screen = screenDog.ScreenDog()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        return None

if __name__ == '__main__':
    with Gestures() as gs:
        gs.head.headshake(gs.head.MAX_RANGE/4)