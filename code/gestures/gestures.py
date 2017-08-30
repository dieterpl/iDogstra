import os
import time  # import the time library for the sleep function
import config
from threading import Thread, Condition, Lock
from screen import Screen


class Gesture(Thread):

    PICTURES = {
        "default": "default.gif",
        "wait": [0, 1],
        "follow": [0, 1, 2, 3, 4, 3, 2, 1, 0, 5, 6, 7, 8, 7, 6, 5],
        "track": [0, 1, 2, 1],
        "search": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        "dodge": [0, 1],
    }

    def __init__(self):
        Thread.__init__(self)
        self.paused = False
        self.pause_condition = Condition(Lock())

        self.current_gesture = "default"
        self.current_frame = 0
        # set picture delay to add up to exactly 1s for each picture sequence
        self.picture_delay = 1 / len(Gesture.PICTURES["default"])
        self.screen = Screen()
        self.gesture_running = False

        # show default picture after initialization
        self.screen.change_picture(self.__get_picture("default.gif"))

    def __next_picture(self):
        picture_frames = Gesture.PICTURES[self.current_gesture]
        picture_number = picture_frame[self.current_frame]
        picture_name = ("%s_%d.gif" % (self.current_gesture, picture_number))
        print(picture_name)

        return self.__get_picture(picture_name)

    def __get_picture(self, name):
        return os.path.join(config.PICTUREPATH, name)

    def change_gesture(self, gesture):
        if gesture in Gesture.PICTURES.keys():
            self.current_gesture = gesture
            self.current_frame = 0
            self.picture_delay = 1 / len(Gesture.PICTURES[gesture])

    def run(self):
        print("Gestures running")
        while True:
            with self.pause_condition:
                while self.paused:
                    self.pause_condition.wait()

                picture_path = self.__next_picture()
                self.screen.change_picture(picture_path)
                self.current_frame += 1

                time.sleep(self.picture_delay)
            time.sleep(5)

        print("Gestures stopping")

    def pause(self):
        self.paused = True
        self.pause_condition.acquire()

    def resume(self):
        self.paused = False
        self.pause_condition.notify()
        self.pause_condition.release()


if __name__ == '__main__':
    gesture = Gesture()
    gesture.start()
    time.sleep(5)
    gesture.change_gesture("search")
