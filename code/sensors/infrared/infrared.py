import time  # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers


class InfraRed:
    def __enter__(self):
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_1
        self.TIME = 0.5
        # Configure for an EV3 color sensor.
        # BP.set_sensor_type configures the BrickPi3 for a specific sensor.
        # BP.PORT_1 specifies that the sensor will be on sensor port 1.
        # BP.Sensor_TYPE.EV3_INFRARED_PROXIMITY specifies that the sensor will be an EV3 infrared sensor.
        self.BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)
        return self

    def get_distance(self):
        mean = 0
        mean_counter = 0
        value = None
        for var in range(0, 4):
            try:
                value = self.BP.get_sensor(self.PORT)
            except brickpi3.SensorError as error:
                value = None
            if value is not None:
                mean += value
                mean_counter += 1
            time.sleep(self.TIME)

        if mean_counter != 0:
            return mean / mean_counter
        return -1


    def __exit__(self, exc_type, exc_value, traceback):
        self.BP.reset_all()


if __name__ == '__main__':
    with InfraRed() as ir:
        print ("Gemessene Entfernung = %.1f cm" % ir.get_distance())
