import time  # import the time library for the sleep function
from collections import deque, namedtuple
from threading import Thread
from utils.functions import current_time_millis

try:
    import brickpi3
    BP = brickpi3.BrickPi3()
except ModuleNotFoundError:
    print("WARNING: Could not import module brickpi3 (not running on a raspberry pi?). Movement module will not "
          "be available.")
    brickpi3 = None

DataTuple = namedtuple("DataTuple", "time distance")

class InfraRed:
    def __init__(self):
        """
        setting up pi and brickpi for ir sensor
        :return: -
        """
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_1
        # Configure for an EV3 color sensor.
        # BP.set_sensor_type configures the BrickPi3 for a specific sensor.
        # BP.PORT_1 specifies that the sensor will be on sensor port 1.
        # BP.Sensor_TYPE.EV3_INFRARED_PROXIMITY specifies that the sensor will be an EV3 infrared sensor.
        self.BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)
        self.init_sensor()

        self.data_deque = deque()

    def accumulate_distance(self):
        """
        returns the distance in cm max value means object ist too far or too close
        :return:
        """

        while True:
            try:
                value = self.BP.get_sensor(self.PORT)
            except brickpi3.SensorError as error:
                value = None
            if value:
                self.data_deque.append(self.DataTuple(current_time_millis(), value))
                self.remove_old_data()


    def remove_old_data(self, threshold=1000):
        """Removes data tuples from the queue that are older
        than threshold milliseconds"""

        threshold = current_time_millis() - threshold

        while len(self.data_deque) > 0 and self.data_deque[0].time < threshold:
            self.data_deque.popleft()

    def init_sensor(self):
        """
        initalizing sensor because it need 2 seconds to boot up
        :return: -
        """
        value = None
        for var in range(0, 20):
            try:
                self.BP.get_sensor(self.PORT)
            except brickpi3.SensorError as error:
                time.sleep(0.1)
            if value is not None:
                break

    def get_avg_value(self):
        if len(self.data_deque) == 0:
            return None
        return sum(self.data_deque) / len(self.data_deque)

    def start_thread(self):
          if_t = Thread(target=self.accumulate_distance)
          if_t.start()

#if __name__ == '__main__':
#    with InfraRed() as ir:
#        for i in range(0,100):
#            print ("Gemessene Entfernung = %.1f cm" % ir.get_distance())
#            time.sleep(0.1)
