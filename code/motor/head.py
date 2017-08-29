import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import math
#TODO WORK IN PROGRESS
class Head:

    def __init__(self):
        self.MAX_RANGE = 80
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_C
        self.BP.set_motor_power(self.PORT, self.BP.MOTOR_FLOAT)
        # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
        self.BP.set_motor_limits(self.PORT, 0, 0)

    def __enter__(self):
        self.MAX_RANGE = 80
        self.BP = brickpi3.BrickPi3()
        self.PORT = self.BP.PORT_C
        self.BP.set_motor_power(self.PORT, self.BP.MOTOR_FLOAT)
        # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
        self.BP.set_motor_limits(self.PORT, 0, 0)
        return self

    def goToPosition(self, motor, position, degree):
        self.BP.set_motor_limits(self.PORT, 0, degree)
        time.sleep(0.1)

        oldValue = 99999
        while self.BP.get_motor_encoder(self.PORT) != oldValue:
        #while self.BP.get_motor_encoder(self.PORT) not in range(position-10,position+10):
            oldValue = self.BP.get_motor_encoder(self.PORT)
            self.BP.set_motor_position(self.PORT, position)
            if(degree <= self.MAX_RANGE/4):
                time.sleep(1)
            else:
                time.sleep(self.MAX_RANGE/degree)
            #time.sleep(1)
            print (self.BP.get_motor_encoder(self.PORT))
        return

 #   def doFullScan(self):
  #      self.goToPosition(self.BP.PORT,0)
   #     while True:
    #        for i in range(0,self.MAX_RANGE,1):
     #           self.goToPosition(self.PORT,i)
      #      for i in range(self.MAX_RANGE,0,-1):
        #        self.goToPosition(self.PORT,i)

    def headshake(self, degree):
        """
        rotates the head of the robot between (-MAX,MAX)<-Degrees of Head Movement possible
        after that returns to neutral position
        :return: -
        """
        self.goToPosition(self.PORT, self.MAX_RANGE, degree)
        self.goToPosition(self.PORT, -self.MAX_RANGE, degree)
        time.sleep(0.1)
        self.goToPosition(self.PORT, 0, degree)

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
        hd.headshake(hd.MAX_RANGE*5)


