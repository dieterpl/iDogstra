import time
import brickpi3
import getch
import sys


BP = brickpi3.BrickPi3()
DEFAULT_SPEED = 20

state = 'stop'


def forward(speed):
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, speed)


def backward(speed):
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, -speed)


def left(speed):
    BP.set_motor_power(BP.PORT_A, -speed)
    BP.set_motor_power(BP.PORT_D, speed)


def right(speed):
    BP.set_motor_power(BP.PORT_A, speed)
    BP.set_motor_power(BP.PORT_D, -speed)


def stop():
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, 0)


def leftspin(speed, duration):
    left(speed)
    time.sleep(duration)
    stop()


def rightspin(speed, duration):
    right(speed)
    time.sleep(duration)
    stop()


def keyMapping(key):
    global state

    if key == 'w':
        forward(DEFAULT_SPEED)
        state = 'forward'
    elif key == 'a':
        left(DEFAULT_SPEED)
        state = 'left'
    elif key == 's':
        if state == 'stop':
            backward(DEFAULT_SPEED)
            state = 'backward'
        else:
            stop()
            state = 'stop'
    elif key == 'd':
        right(DEFAULT_SPEED)
        state = 'right'


if __name__ == '__main__':
   while True:
      char = getch.getch()
      keyMapping(char)
      time.sleep(0.01)
