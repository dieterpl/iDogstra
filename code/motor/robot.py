import time
import brickpi3
import getch
import sys


class Robot (brickpi3.BrickPi3):
    def __init__(self, speed=100):
        super(Robot, self).__init__()

        self.movement_state = 'stop'
        self.default_speed = speed
        self.current_speed = 0

    def forward(self, speed=None):
        if speed is None:
            print('using default speed')
            speed = self.default_speed

        self.set_motor_power(self.PORT_A + self.PORT_D, speed)
        self.current_speed = speed
        self.movement_state = 'forward'

    def backward(self, speed=None):
        if speed is None:
            print('using default speed')
            speed = self.default_speed

        self.set_motor_power(self.PORT_A + self.PORT_D, -speed)
        self.current_speed = speed
        self.movement_state = 'backward'

    def left(self, speed=None):
        if speed is None:
            print('using default speed')
            speed = self.default_speed

        self.set_motor_power(self.PORT_A, speed)
        self.set_motor_power(self.PORT_D, -speed)
        self.current_speed = speed
        self.movement_state = 'left'

    def right(self, speed=None):
        if speed is None:
            print('using default speed')
            speed = self.default_speed

        self.set_motor_power(self.PORT_A, -speed)
        self.set_motor_power(self.PORT_D, speed)
        self.current_speed = speed
        self.movement_state = 'right'

    def stop(self):
        while(self.current_speed > 0):
            self.current_speed -= 1

            if self.movement_state == 'forward':
                self.forward(self.current_speed)
            elif self.movement_state == 'backward':
                self.backward(self.current_speed)
            elif self.movement_state == 'left':
                self.left(self.current_speed)
            elif self.movement_state == 'right':
                self.right(self.current_speed)

            time.sleep(0.01)

        self.movement_state = 'stop'

    def move_by_bpdegree(self, direction, bpdegree):
        BP.set_motor_limits(BP.PORT_A + BP.PORT_D, 50, 200)

        self.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
        self.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D))

        port_A_pos = self.get_motor_encoder(self.PORT_A)
        port_D_pos = self.get_motor_encoder(self.PORT_D)

        port_A_new_pos = port_A_pos + bpdegree
        port_D_new_pos = port_D_pos + bpdegree

        print("curr portA: %s curr portD: %s" % (port_A_pos, port_D_pos))
        print("next portA: %s next portD: %s" % (port_A_new_pos, port_D_new_pos))

        if direction == 'left':
            self.set_motor_position(self.PORT_A, port_A_new_pos)
            self.set_motor_position(self.PORT_D, -port_D_new_pos)
            self.movement_state = 'left'
        elif direction == 'right':
            self.set_motor_position(self.PORT_A, -port_A_new_pos)
            self.set_motor_position(self.PORT_D, port_D_new_pos)
            self.movement_state = 'right'

    def __move_for_duration(self, move_func, duration, speed=None):
        if speed is None:
            speed = self.default_speed

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

    def move_by_degree(self, direction, degree):
        bpdegree = self.degree_to_bpdegree(degree)

        if direction == 'left_by_degree':
            self.move_by_bpdegree('left', bpdegree)
        elif direction == 'right_by_degree':
            self.move_by_bpdegree('right', bpdegree)

    def bpdegree_to_degree(self, bpdegree):
        return (bpdegree * 1.66) / 10

    def degree_to_bpdegree(self, degree):
        return (degree * 0.6) * 10

    def __move_with_key(self, key):
        if key == '' and self.movement_state != 'stop':
            self.stop()
        elif key == 'w':
            self.forward()
        elif key == 'a':
            self.left()
        elif key == 'd':
            self.right()
        elif key == 's':
            if self.movement_state == 'stop':
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
        directions_by_degree = ['left_by_degree', 'right_by_degree']

        try:
            while True:
                left_motor = self.get_motor_encoder(self.PORT_A)
                right_motor = self.get_motor_encoder(self.PORT_D)
                print("Left motor: %6d - Right motor: %6d" % (left_motor, right_motor))
                inp = input("> ")

                operation = inp.split(' ')
                command = operation[0]

                if command in directions:
                    speed = int(operation[1])
                    duration = float(operation[2])
                    self.move(command, speed, duration)
                elif command in directions_by_degree:
                    degree = int(operation[1])
                    self.move_by_degree(command, degree)
                elif command == 'info':
                    self.get_info()

                else:
                    print('No such action')

        except KeyboardInterrupt:
            self.reset_all()


"""
call this module with >  python3 robot.py speed  to drive the
brickpi with WASD and a specific speed
otherwise >  python3 robot.py  will open the command line interface:

commands:
left speed duration
right speed duration
forward speed duration
backward speed duration

left_by_degree degree
right_by_degree degree
"""
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
