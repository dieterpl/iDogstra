import time  # import the time library for the sleep function
from threading import Thread
from gestures import screenDog


class Gesture(Thread):

    GESTURE_PICTURES = {
        "default": [],
        "wait": [],
        "follow": [],
        "track": [],
        "search": [],
        "collision": [],
    }

    # GESTURE_DELAY = 0.5

    def __init__(self):
        self.current_gesture = "default"
        self.picture_delay = 1 / len(GESTURE_PICTURES["default"])
        self.screen = screenDog.ScreenDog()
        self.gesture_running = False
        pass

    def run():
        print("Gestures running")
        doEmotion()
        print("Gestures stopping")

    def doEmotion(self):
        while True:
            for picture in GESTURE_PICTURES.get(self.current_gesture):
                self.screen.change_gesture(picture)
                time.sleep(self.picture_delay)
            # time.sleep(GESTURE_DELAY)

    def change_gesture(self, gesture):
        if gesture in GESTURE_PICTURES.keys():
            self.current_gesture = gesture
            self.picture_delay = 1 / len(GESTURE_PICTURES[gesture])

        """
        Does an Emotion, general Method for alle EMOTIONS
        :param breakflag: breaks if statement is TRUE
        :param emotionArray: see Gesture Enum:= Array of pictures to iterate
        :return:
        """


if __name__ == '__main__':
    gesture = Gesture()
    gesture.start()
    gesture.doEmotion(flag, gesture.screen.Gesture.searchArray)
