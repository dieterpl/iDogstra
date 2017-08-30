import time  # import the time library for the sleep function
from threading import Thread
import gestures.screenDog

"""
dont use this, TODO: implement this, currently bei head.py
"""
class Gesture(Thread):

    def __init__(self):
        self.screen = screenDog.ScreenDog()
        pass

    def run():
        pass

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


if __name__ == '__main__':
    gesture = Gesture()
    gesture.doEmotion(True, gesture.screen.Gesture.followArray)

