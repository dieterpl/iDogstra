import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import math
class Head:
    def __init__(self):
        self.MAX_RANGE = 80
        self.BP = brickpi3.BrickPi3()

    def goToPosition(self,motor, position):
        while self.self.BP.get_motor_encoder(self.BP.PORT_C) not in range(position-8,position+8):
            self.BP.set_motor_position(self.BP.PORT_C, position)
            print (self.BP.get_motor_encoder(self.BP.PORT_C))
        return

    def doFullScan(self):
        self.BP.set_motor_power(self.BP.PORT_C, self.BP.MOTOR_FLOAT)
        self.BP.set_motor_limits(self.BP.PORT_C, 0, 0)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
        self.goToPosition(self.BP.PORT_C,0)
        while True:
            for i in range(0,self.MAX_RANGE,1):
                self.goToPosition(self.BP.PORT_C,i)

            for i in range(self.MAX_RANGE,0,-1):
                self.goToPosition(self.BP.PORT_C,i)

hd = Head()

if __name__ == '__main__':
    try:
       
        while True:
            hd.doFullScan()
            time.sleep(1)
 
        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        hd.BP.reset_all()
        print("Messung vom User gestoppt")
