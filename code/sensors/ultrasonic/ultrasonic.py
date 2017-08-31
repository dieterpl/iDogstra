# Bibliotheken einbinden
import time
from collections import deque, namedtuple
from threading import Thread, Lock

import config
from sensors.pipeline import Pipeline
from utils.functions import current_time_millis, overrides

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("WARNING: Could not import module RaspberryPI (not running on a "
          "raspberry pi?). S module will not be available.")
    GPIO = None

DataTuple = namedtuple("DataTuple", "time distance")

class UltraSonic:


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

        self.lock = Lock()
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

            timeout = current_time_millis()

            # speichere Startzeit
            while GPIO.input(config.US_GPIO_ECHO) == 0 and current_time_millis()-timeout<100:
                StartZeit = time.time()

            timeout = current_time_millis()

            # speichere Ankunftszeit
            while GPIO.input(config.US_GPIO_ECHO) == 1  and current_time_millis()-timeout<100:
                StopZeit = time.time()

            # Zeit Differenz zwischen Start und Ankunft
            TimeElapsed = StopZeit - StartZeit
            # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
            # und durch 2 teilen, da hin und zurueck
            distance = (TimeElapsed * 34300) / 2

            try:
                self.lock.acquire()
                self.data_deque.append(DataTuple(current_time_millis(), max(0.0, min(distance, config.US_MAX_VALUE))))
            finally:
                self.lock.release()
            self.remove_old_data()

    def remove_old_data(self, threshold=config.US_DATA_ACC_THRESHOLD):
        """Removes data tuples from the queue that are older
        than threshold milliseconds"""

        threshold = current_time_millis() - threshold

        try:
            self.lock.acquire()
            while len(self.data_deque) > 0 and self.data_deque[0].time < threshold:
                self.data_deque.popleft()
        finally:
            self.lock.release()

    def get_avg_value(self):
        """ Returns the average of the measured data"""
        try:
            self.lock.acquire()
            if len(self.data_deque) == 0:
                return None
            return sum(r[1] for r in self.data_deque) / len(self.data_deque)
        finally:
            self.lock.release()

    def check_us_sensor_data_changed(self, time_threshold=config.US_TIME_THRESHOLD, distance_threshold=config.US_DISTANCE_THRESHOLD):
        """ Return true if data changed by more than distance threshold in time_threshold"""
        upper_threshold = current_time_millis() - time_threshold
        under_threshold = current_time_millis() - time_threshold*2
        upper_avg = []
        under_avg = []

        try:
            self.lock.acquire()
            if len(self.data_deque) == 0:
                return None
            for i in reversed(self.data_deque):
                if i.time > upper_threshold:
                    upper_avg.append(i.distance)
                if under_threshold < i.time < upper_threshold:
                    under_avg.append(i.distance)
        finally:
            self.lock.release()

        if len(upper_avg) == 0 or len(under_avg) == 0:
            return False
        upper_avg = sum(upper_avg) / len(upper_avg)
        under_avg = sum(under_avg) / len(under_avg)
        print(upper_avg, under_avg)
        if abs(upper_avg - under_avg) > distance_threshold:
            return True
        return False

    def __len__(self):
        """Returns the amount of data that is present in the queue"""
        # As old data is only removed when new data is added, we have to
        # ensure that old data is being deleted before counting the elements
        # in the queue
        self.remove_old_data()
        try:
            self.lock.acquire()
            return len(self.data_deque)
        finally:
            self.lock.release()

    def clean_up(self):
        GPIO.cleanup()

    def start_thread(self):
        us_t = Thread(target=self.accumulate_distance)
        us_t.start()


class USGetDistancePipeline(Pipeline):
    """A pipeline that returns the distance measured by the US sensors"""

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        """Takes an UltraSonic object and returns the average value."""
        if len(inp) == 0:
            return False, None
        return True, inp.get_avg_value()


class USGetMovementPipeline(Pipeline):
    """A pipeline that returns the distance measured by the US sensors"""

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        """Takes an UltraSonic object and returns the average value."""
        result = inp.check_us_sensor_data_changed()
        if not result:
            return False, None
        return True, result
