import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import math
#TODO WORK IN PROGRESS
class Head:

    def __enter__(self):
        self.MAX_RANGE = 70
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_C
        self.BP.set_motor_power(self.PORT, self.BP.MOTOR_FLOAT)
        # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
        self.BP.set_motor_limits(self.PORT, 0, 20)
        return self



    def goToPosition(self,motor, position):
        while self.BP.get_motor_encoder(self.PORT) not in range(position-8,position+8):
            self.BP.set_motor_position(self.PORT, position)
            print (self.BP.get_motor_encoder(self.PORT))
        return

    def doFullScan(self):
        self.goToPosition(self.BP.PORT,0)
        while True:
            for i in range(0,self.MAX_RANGE,1):
                self.goToPosition(self.PORT,i)
            for i in range(self.MAX_RANGE,0,-1):
                self.goToPosition(self.PORT,i)

    def headshake(self, speed):
        """
        rotates the head of the robot between (-80,80)<-Degrees of Head Movement possible
        :param speed: set up how fast the robot turns in degrees per 1s
        :return: -
        """
        self.goToPosition(self.PORT, self.MAX_RANGE)
        self.goToPosition(self.PORT, -self.MAX_RANGE)

    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        self.BP.set_motor_power(self.PORT, 0)
        return None

if __name__ == '__main__':
    with Head() as hd:

        #examples
        #Robot looks around carefully
        hd.headshake(hd.MAX_RANGE/4)

        time.sleep(2)

        #visual presentation of "No"
        hd.headshake(hd.MAX_RANGE)


