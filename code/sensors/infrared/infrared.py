import time  # import the time library for the sleep function
from collections import deque, namedtuple
from threading import Thread
from utils.functions import current_time_millis, overrides
from sensors.pipeline import Pipeline

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
                self.data_deque.append(DataTuple(current_time_millis(), value))
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

    def start_thread(self):
          if_t = Thread(target=self.accumulate_distance)
          if_t.start()

    def __len__(self):
        """Returns the amount of data that is present in the queue"""
        # As old data is only removed when new data is added, we have to
        # ensure that old data is being deleted before counting the elements
        # in the queue
        self.remove_old_data()
        return len(self.data_deque)

    def get_avg_value(self):
        """ Returns the average of the measured data"""
        if len(self.data_deque) == 0:
            return None
        return sum(self.data_deque) / len(self.data_deque)

    def check_if_sensor_data_changed(self, time_threshold=500, distance_threshold=10):
        """ Return true if data changed by more than distance threshold in time_threshold"""
        if len(self.data_deque) == 0:
            return None
        upper_threshold = current_time_millis() - time_threshold
        under_threshold = current_time_millis() - time_threshold*2
        upper_avg = []
        under_avg = []
        for i in reversed(self.data_deque):
            if i.time > upper_threshold:
                upper_avg.append(i.distance)
            if under_threshold < i.time < upper_threshold:
                under_avg.append(i.distance)

        if len(upper_avg) == 0 or len(under_avg) == 0:
            return False
        upper_avg = sum(upper_avg) / len(upper_avg)
        under_avg = sum(under_avg) / len(under_avg)

        if abs(upper_avg - under_avg) > distance_threshold:
            return True
        return False



class IRGetDistancePipeline(Pipeline):
    """A pipeline that returns the distance measured by the US sensors"""

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        """Takes an UltraSonic object and returns the average value."""
        if len(inp) == 0:
            return False, None
        return True, inp.get_avg_value()


class IRGetMovementPipeline(Pipeline):
    """A pipeline that returns the distance measured by the US sensors"""

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        """Takes an UltraSonic object and returns the average value."""
        result = inp.check_if_sensor_data_changed()
        if not result:
            return False, None
        return True, result

#if __name__ == '__main__':
#    with InfraRed() as ir:
#        for i in range(0,100):
#            print ("Gemessene Entfernung = %.1f cm" % ir.get_distance())
#            time.sleep(0.1)
