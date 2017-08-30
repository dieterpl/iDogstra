import time  # import the time library for the sleep function
from threading import Thread
from screen import Screen


class Gesture(Thread):

    PICTURES = {
        "default": "default.gif",
        "wait": [1, 2],
        "follow": [1, 2, 3, 4, 5, 4, 3, 2, 1, 6, 7, 8, 9, 8, 7, 6],
        "track": [1, 2, 3, 2],
        "search": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "dodge": [1, 2],
    }

    def __init__(self):
        self.current_gesture = "default"
        self.picture_delay = 1 / len(Gesture.PICTURES["default"])
        self.screen = Screen()

        self.initial_state()

    def run():
        print("Gestures running")
        doEmotion()
        print("Gestures stopping")

    def initial_state(self):
        self.gesture_running = False

        default_picture = Gesture.PICTURES["default"]
        self.screen.change_gesture(default_picture)

    def doEmotion(self):
        while True:
            for index in Gesture.PICTURES[self.current_gesture]:
                picture = self.get_picture(index)
                self.screen.change_gesture(picture)
                time.sleep(self.picture_delay)

    def get_picture(self, framenumber):
        picture_frames = Gesture.PICTURES[self.current_gesture]
        picture_number = picture_frames[framenumber]

        return "./pics/%s_%d.gif" % (self.current_gesture, picture_number)

    def change_gesture(self, gesture):
        if gesture in GesturePICTURES.keys():
            self.current_gesture = gesture
            self.picture_delay = 1 / len(Gesture.PICTURES[gesture])


if __name__ == '__main__':
    gesture = Gesture()
    gesture.start()
    time.sleep(5)
    gesture.change_gesture("search")
