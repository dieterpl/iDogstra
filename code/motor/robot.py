import time
import brickpi3
import getch
import sys


class Robot (brickpi3.BrickPi3):

    def __init__(self, speed=100):
        super(Robot, self)
        self.movement_state = 'stop'
        self.speed = 100

    def forward(self, speed):
        self.set_motor_power(self.PORT_A + self.PORT_D, speed)

    def backward(self, speed):
        self.set_motor_power(self.PORT_A + self.PORT_D, -speed)

    def left(self, speed):
        self.set_motor_power(self.PORT_A, -speed)
        self.set_motor_power(self.PORT_D, speed)

    def right(self, speed):
        self.set_motor_power(self.PORT_A, speed)
        self.set_motor_power(self.PORT_D, -speed)

    def stop(self):
        self.set_motor_power(self.PORT_A + self.PORT_D, 0)

    def left_by_angle(self, angle):
        pass  # todo

    def right_by_angle(self, angle):
        pass  # todo

    def move_for_duration(self, move_func, speed=DEFAULT_SPEED, duration):
        move_func(speed)
        time.sleep(duration)
        stop()

    def move_in_direction(self, direction, speed, duration):
        if direction == 'left':
            move_for_duration(left, speed, duration)
        elif direction == 'right':
            move_for_duration(right, speed, duration)
        elif direction == 'forward':
            move_for_duration(forward, speed, duration)
        elif direction == 'backward':
            move_for_duration(backward, speed, duration)

    def angleToTime(self, degree):
        pass

    def __move_with_key(self, key):
        global state

        if key == '' and self.state != 'stop':
            self.stop()
            self.state = 'stop'
        elif key == 'w':
            self.forward(DEFAULT_SPEED)
            self.state = 'forward'
        elif key == 'a':
            self.left(DEFAULT_SPEED)
            self.state = 'left'
        elif key == 'd':
            self.right(DEFAULT_SPEED)
            self.state = 'right'
        elif key == 's':
            if self.state == 'stop':
                self.backward(DEFAULT_SPEED)
                self.state = 'backward'
            else:
                self.stop()
                self.state = 'stop'

    def __drive_with_keys(self):
        try:
            while True:
                char = getch.getch()
                self.__move_with_key(char)
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.reset_all()

    def __cli(self):
        directions = ['left', 'right', 'forward', 'backward']
        try:
            while True:
                left_motor = self.get_motor_encoder(self.PORT_A)
                right_motor = self.get_motor_encoder(self.PORT_D)
                print("Left motor: %6d - Right motor: %6d", % (left_motor, right_motor))
                inp = raw_input("> ")

                operation = inp.split(' ')
                command = operation[0]
                speed = operation[1]
                duration = operation[2]

                if command in directions:
                    move(command, speed, duration)
                else:
                    print('No such action')

        except KeyboardInterrupt:
            self.reset_all()


if __name__ == '__main__':
    args = sys.argv

    if len(args) >= 2:
        speed = int(args[1])
        BP = Robot(speed)
        BP.__drive_with_keys()

    else:
        speed = DEFAULT_SPEED
        BP = Robot(speed)
        BP.__cli()
