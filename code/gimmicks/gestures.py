import time  # import the time library for the sleep function
import sys
import os
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/motor"))
sys.path.append(os.path.abspath("/home/pi/An/iDogstra/code/gestures"))
import screenDog
from threading import Thread


"""
dont use this, TODO: implement this, currently bei head.py
"""
class Gestures():
    def __enter__(self):
        #self.head = head.Head()
        self.screen = screenDog.ScreenDog()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        return None

    def search(self, breakflag):
        """
        Displays the dog searching through monitor 0
        :param breakflag: Stops this emotion if breakflag is true
        :return:
        """
       # t = Thread(target=startHeadshaking(breakflag))
       # t.start()
        while not breakflag:
            for element in gs.screen.Gesture.searchArray:
                if not breakflag:
                    gs.screen.change_gesture(element)
                    time.sleep(0.2)

    def idle(self, breakflag):
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


    def doEmotion(self, breakflag, emotionArray):
        """
        Does an Emotion, general Method for alle EMOTIONS
        :param breakflag: breaks if statement is TRUE
        :param emotionArray: see Gesture Enum:= Array of pictures to iterate
        :return:
        """
        while not breakflag:
            for element in emotionArray:
                if not breakflag:
                    gs.screen.change_gesture(element)
                    time.sleep(1/len(emotionArray))

def swap(flag, t):
    time.sleep(t)
    flag = False;
    print("now breaking")


if __name__ == '__main__':
    with Gestures() as gs:
        flag = False
        t1 = Thread(target=swap(flag,5))
        t1.start()

        #gs.doEmotion(flag, gs.screen.Gesture.sleepArray)

        gs.doEmotion(flag, gs.screen.Gesture.searchArray)

