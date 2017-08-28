import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import math
#TODO WORK IN PROGRESS
class Head:

    def __enter__(self):
        self.MAX_RANGE = 80
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_C
        return self



    def goToPosition(self,motor, position):
        while self.BP.get_motor_encoder(self.PORT) not in range(position-8,position+8):
            self.BP.set_motor_position(self.PORT, position)
            print (self.BP.get_motor_encoder(self.PORT))
        return

    def doFullScan(self):
        self.BP.set_motor_power(self.PORT, self.BP.MOTOR_FLOAT)
        self.BP.set_motor_limits(self.PORT, 0, 0)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
        self.goToPosition(self.BP.PORT,0)
        while True:
            for i in range(0,self.MAX_RANGE,1):
                self.goToPosition(self.PORT,i)
            for i in range(self.MAX_RANGE,0,-1):
                self.goToPosition(self.PORT,i)

    def headshake(self):
        self.goToPosition(self.PORT, self.MAX_RANGE)
        self.goToPosition(self.PORT, -self.MAX_RANGE)

    def __exit__(self, exc_type, exc_value, traceback):
        # self.BP.reset_all() Kills BrickPi
        self.BP.set_motor_power(self.PORT, 0)
        return None

if __name__ == '__main__':
    with Head() as hd:

        #hd.doFullScan()
        hd.headshake()
 
