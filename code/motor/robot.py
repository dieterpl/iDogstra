import time
import brickpi3
import getch
import sys


class Robot (brickpi3.BrickPi3):

    def __init__(self, speed=100):
        super(Robot, self).__init__()
        self.movement_state = 'stop'
        self.speed = 100

    def forward(self, speed=None):
        if speed is None:
            speed = self.speed
        self.set_motor_power(self.PORT_A + self.PORT_D, speed)
        self.state = 'forward'

    def backward(self, speed=None):
        if speed is None:
            speed = self.speed
        self.set_motor_power(self.PORT_A + self.PORT_D, -speed)
        self.state = 'backward'

    def left(self, speed=None):
        if speed is None:
            speed = self.speed
        self.set_motor_power(self.PORT_A, speed)
        self.set_motor_power(self.PORT_D, -speed)
        self.state = 'left'

    def right(self, speed=None):
        if speed is None:
            speed = self.speed
        self.set_motor_power(self.PORT_A, -speed)
        self.set_motor_power(self.PORT_D, speed)
        self.state = 'right'

    def stop(self):
        self.set_motor_power(self.PORT_A + self.PORT_D, 0)
        self.state = 'stop'

    def left_by_angle(self, angle):
        pass  # todo

    def right_by_angle(self, angle):
        pass  # todo

    def __move_for_duration(self, move_func, duration, speed=None):
        if speed is None:
            speed = self.speed
        move_func(speed)
        time.sleep(duration)
        self.stop()

    def move(self, direction, speed, duration):
        if direction == 'left':
            self.__move_for_duration(self.left, duration, speed)
        elif direction == 'right':
            self.__move_for_duration(self.right, duration, speed)
        elif direction == 'forward':
            self.__move_for_duration(self.forward, duration, speed)
        elif direction == 'backward':
            self.__move_for_duration(self.backward, duration, speed)

    def angleToTime(self, degree):
        pass

    def __move_with_key(self, key):
        global state

        if key == '' and self.state != 'stop':
            self.stop()
        elif key == 'w':
            self.forward()
        elif key == 'a':
            self.left()
        elif key == 'd':
            self.right()
        elif key == 's':
            if self.state == 'stop':
                self.backward()
            else:
                self.stop()

    def drive_with_keys(self):
        try:
            while True:
                char = getch.getch()
                self.__move_with_key(char)
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.reset_all()

    def cli(self):
        directions = ['left', 'right', 'forward', 'backward']
        try:
            while True:
                left_motor = self.get_motor_encoder(self.PORT_A)
                right_motor = self.get_motor_encoder(self.PORT_D)
                print("Left motor: %6d - Right motor: %6d" % (left_motor, right_motor))
                inp = input("> ")

                operation = inp.split(' ')
                command = operation[0]
                speed = int(operation[1])
                duration = float(operation[2])

                if command in directions:
                    self.move(command, speed, duration)
                else:
                    print('No such action')

        except KeyboardInterrupt:
            self.reset_all()


if __name__ == '__main__':
    args = sys.argv

    if len(args) >= 2:
        speed = int(args[1])
        BP = Robot(speed)
        BP.drive_with_keys()

    else:
        speed = 80
        BP = Robot(speed)
        BP.cli()
