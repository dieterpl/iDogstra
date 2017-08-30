# Bibliotheken einbinden
import time
import config
from collections import deque, namedtuple
from threading import Thread
from utils.functions import current_time_millis
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("WARNING: Could not import module RaspberryPI (not running on a raspberry pi?). S module will not "
          "be available.")
    GPIO = None


class UltraSonic:
    DataTuple = namedtuple("DataTuple", "time distance")

    def __init__(self):
        """
        sets GPIO ports and max distance value also setting up pi for us sensor
        :return:
        """
        GPIO.cleanup()

        # GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(config.US_GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(config.US_GPIO_ECHO, GPIO.IN)

        self.data_deque = deque()

    def accumulate_distance(self):
        """
        returns the distance in cm max value means object ist too far or too close
        :return:
        """

        while True:
            # setze Trigger auf HIGH
            GPIO.output(config.US_GPIO_TRIGGER, True)

            # setze Trigger nach 0.01ms aus LOW
            time.sleep(0.01)
            GPIO.output(config.US_GPIO_TRIGGER, False)

            StartZeit = time.time()
            StopZeit = time.time()

            # speichere Startzeit
            while GPIO.input(config.US_GPIO_ECHO) == 0:
                StartZeit = time.time()

            # speichere Ankunftszeit
            while GPIO.input(config.US_GPIO_ECHO) == 1:
                StopZeit = time.time()

            # Zeit Differenz zwischen Start und Ankunft
            TimeElapsed = StopZeit - StartZeit
            # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
            # und durch 2 teilen, da hin und zurueck
            distance = (TimeElapsed * 34300) / 2

            self.data_deque.append(self.DataTuple(current_time_millis(),min(distance, config.US_MAX_VALUE)))
            self.remove_old_data()

    def remove_old_data(self, threshold=1000):
        """Removes data tuples from the queue that are older
        than threshold milliseconds"""

        threshold = current_time_millis() - threshold

        while len(self.data_deque) > 0 and self.data_deque[0].time < threshold:
            self.data_deque.popleft()

    def get_avg_value(self):
        if len(self.data_deque) == 0:
            return None
        return sum(self.data_deque) / len(self.data_deque)


    def clean_up(self):
        GPIO.cleanup()

    def start_thread(self):
        us_t = Thread(target=self.accumulate_distance)
        us_t.start()

# if __name__ == '__main__':
#    with UltraSonic() as us:
#        print ("Gemessene Entfernung = %.1f cm" % us.get_distance())
