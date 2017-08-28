import time
try:
    import brickpi3
    BP = brickpi3.BrickPi3()
except ModuleNotFoundError:
    print("WARNING: Could not import module brickpi3 (not running on a raspberry pi?). Movement module will not "
          "be available.")
    brickpi3, BP = None, None

import sys

DEFAULT_SPEED = 100

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
    args = sys.argv
    setSpeed = int(args[1])

    rightspin(setSpeed, 1)


    # while True:
    #     char = getch.getch()
    #     keyMapping(char)
    #     time.sleep(0.01)