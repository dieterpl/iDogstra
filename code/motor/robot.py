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

    def left_by_angle(self, angle):
        port_A_pos = self.get_motor_encoder(self.PORT_A)
        port_D_pos = self.get_motor_encoder(self.PORT_D)

        offset = 0

        port_A_new_pos = port_A_pos + angle + offset
        port_D_new_pos = port_D_pos - angle - offset

        print("curr portA: %s curr portD: %s" % (port_A_pos, port_D_pos))
        print("next portA: %s next portD: %s" % (port_A_new_pos, port_D_new_pos))

        self.set_motor_position(self.PORT_A, port_A_new_pos)
        self.set_motor_position(self.PORT_D, -port_D_new_pos)
        self.movement_state = 'left'

    def right_by_angle(self, angle):
        port_A_pos = self.get_motor_encoder(self.PORT_A)
        port_D_pos = self.get_motor_encoder(self.PORT_D)

        offset = 0

        port_A_new_pos = port_A_pos - angle - offset
        port_D_new_pos = port_D_pos + angle + offset

        print("curr portA: %s curr portD: %s" % (port_A_pos, port_D_pos))
        print("next portA: %s next portD: %s" % (port_A_new_pos, port_D_new_pos))

        self.set_motor_position(self.PORT_A, port_A_new_pos)
        self.set_motor_position(self.PORT_D, -port_D_new_pos)
        self.movement_state = 'right'

    def get_info():
        port_A_pos = self.get_motor_encoder(self.PORT_A)
        port_D_pos = self.get_motor_encoder(self.PORT_D)

        print("portA position: %s portD position: %s" % (port_A_pos, port_D_pos))

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

    def move_by_angle(self, direction, angle):
        if direction == 'left_by_angle':
            self.left_by_angle(angle)
        elif direction == 'right_by_angle':
            self.right_by_angle(angle)

    def angleToTime(self, degree):
        pass

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
        directions_by_angle = ['left_by_angle', 'right_by_angle']

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
                elif command in directions_by_angle:
                    angle = int(operation[1])
                    self.move_by_angle(command, angle)
                elif command == 'info':
                    self.get_info()

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
