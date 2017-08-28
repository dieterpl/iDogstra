import time  # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers


class InfraRed:
    def __enter__(self):
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
        return self

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

    def get_distance(self):
        """
        return the distance to the object in cm by avg the last 5 values
        :return: distance in cm
        """
        mean = 0
        mean_counter = 0
        value = None
        for var in range(0, 5):
            try:
                value = self.BP.get_sensor(self.PORT)
            except brickpi3.SensorError as error:
                value = None
            if value is not None:
                mean += value
                mean_counter += 1
        if mean_counter != 0:
            return mean / mean_counter
        return -1

    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        return None

if __name__ == '__main__':
    with InfraRed() as ir:
        for i in range(0,100):
            print ("Gemessene Entfernung = %.1f cm" % ir.get_distance())
            time.sleep(0.1)
