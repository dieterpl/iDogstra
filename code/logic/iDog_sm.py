from logic.statemachine import *
from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth, bluetooth_pipelines
from sensors import pipeline
from sensors.camera import camera, camera_pipelines
from sensors.ultrasonic import ultrasonic_pipelines, ultrasonic
from sensors.infrared import infrared_piplelines, infrared
from motor import robot
from gestures import gestures
import logging
import config
import cv2
import sys
from scipy.interpolate import interp1d
import numpy


class IDog(StateMachine):
    def __init__(self):
        StateMachine.__init__(self)

        # Ultrasonic
        logging.debug("Starting US-Sensor")
        self.ultrasonic = ultrasonic.UltraSonic()
        self.ultrasonic.start_thread()

        # Infrared
        logging.debug("Starting IR-Sensor")
        self.infrared = infrared.InfraRed()
        self.infrared.start_thread()

        # Bluetooth
        logging.debug("Starting BT-Dongles")
        self.bt_dongles = [bluetooth.BTDongle(i, config.BT_TARGET_UUID)
                           for i in config.BT_DONGLE_IDS]
        for dongle in self.bt_dongles:
            dongle.start()

        # RobotControl
        logging.debug("Starting RobotControl")
        self.robots_control = robot.Robot()

        # GestureControl
        logging.debug("Starting GestureControl")
        self.gesture_control = gestures.Gesture()

        self._current_state.first_state = SearchState(self)


class AbstractRobotState(State):
    def __init__(self, state_machine):
        State.__init__(self)
        self.next_state = None
        self.state_switching_timestamp = None
        self.state_machine = state_machine

    def motor_alignment(self, dev):
        if abs(dev) > 0.2:
            value = interp1d([-1, 1], [-config.MAX_TURN_SPEED, config.MAX_TURN_SPEED])(dev)
            logging.debug("Current Turn Speed".format(value))
            self.state_machine.robots_control.rotate(max(config.MIN_TURN_SPEED, abs(value))*numpy.sign(value))

    def show_result(self, *_):
        if config.GRAPHICAL_OUTPUT:
            bbox_ok, bbox = self.pipeline["contour_bbox"].result
            image = self.pipeline["image"].output
            dev_ok, dev = self.pipeline["y_deviation"].result

            # draw bounding box
            if bbox_ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(image, p1, p2, (0, 0, 255))

            # add deviation as text
            if dev_ok:
                cv2.putText(image, str(dev), (0, image.shape[0] - 5),
                            cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6,
                            [0, 255, 0])

            if image is not None:
                cv2.imshow("camtest", image)
            if cv2.waitKey(1) & 0xff == ord("q"):
                sys.exit()

    def queue_next_state(self, next_state):
        if self.next_state != type(next_state):
            self.next_state = type(next_state)
            self.state_switching_timestamp = current_time_millis()
        if current_time_millis() - self.state_switching_timestamp > config.STATE_SWITCH_COOLDOWN:
            return next_state
        else:
            return self

    @property
    def pipeline(self):
        raise NotImplementedError()

    def on_update(self, hist):
        raise NotImplementedError()


class SearchState(AbstractRobotState):
    """Turn robot in circles until the user is found or timeout occurred"""

    def __init__(self, state_machine, start_spin_direction="left"):
        AbstractRobotState.__init__(self, state_machine)
        self.start_time = None
        self.start_spin_direction = start_spin_direction
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline(
                    self.state_machine.bt_dongles)
            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_enter(self):
        self.state_machine.gesture_control.change_gesture("search")

        if self.start_spin_direction == "left":
            self.state_machine.robots_control.left(config.SEARCH_SPEED)
        else:
            self.state_machine.robots_control.right(config.SEARCH_SPEED)
        self.start_time = current_time_millis()

    def on_exit(self):
        self.state_machine.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("SearchState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline["y_deviation"].success_state, \
                        self.pipeline["user_distance"].success_state
        dev, distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            if current_time_millis() - self.start_time > config.SEARCH_TIMEOUT:
                return WaitState(self.state_machine)
            return self
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go
            #  in wait state
            if current_time_millis() - self.start_time > config.SEARCH_TIMEOUT or \
                            distance == bluetooth.UserDistanceEstimationPipeline.Distance.FAR:
                return WaitState(self.state_machine)
            return self
        if cam_ok and not bt_ok:
            return TrackState(self.state_machine)
        if cam_ok and bt_ok:
            return FollowState(self.state_machine)


class FollowState(AbstractRobotState):
    """ Follows the user using the camera and bt by moving the robot"""

    def __init__(self, state_machine):
        AbstractRobotState.__init__(self, state_machine)
        self.last_dev = 0

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.recommended_speed_pipeline(
                    self.state_machine.bt_dongles),
                # InfraRed Input
                infrared_piplelines.get_distance_pipeline(
                    self.state_machine.infrared)

            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_enter(self):
        self.state_machine.gesture_control.change_gesture("follow")

    def on_exit(self):
        self.state_machine.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]

        logging.debug("FollowState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok, ir_ok = self.pipeline["y_deviation"].success_state, \
                        self.pipeline["bt_speed"].success_state, \
                        self.pipeline["ir_distance"].success_state

        logging.debug("FollowState Pipeline results {}".format(cam_ok))
        dev, speed, distance = pipeline_result

        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self.queue_next_state(WaitState(self.state_machine))
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go
            # in wait state
            return self.queue_next_state(SearchState(self.state_machine,
                                                     "left" if self.last_dev > 0 else "right"))
        if cam_ok and not bt_ok:
            return self.queue_next_state(TrackState(self.state_machine))
        if cam_ok and bt_ok:
            self.last_dev = dev
            self.motor_alignment(dev)
            if ir_ok and distance < config.MAX_IR_DISTANCE:
                return self.queue_next_state(TrackState(self.state_machine))
            if abs(dev) < 0.2:
                self.state_machine.robots_control.forward(speed*config.FORWARD_SPEED_MULT)
            return self.queue_next_state(self)


class TrackState(AbstractRobotState):
    """ Tracks the user with the camera but stays at the current position"""

    def __init__(self, state_machine):
        AbstractRobotState.__init__(self, state_machine)
        self.last_dev = 0
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline(
                    self.state_machine.bt_dongles),
                # InfraRed Input
                infrared_piplelines.get_distance_pipeline(
                self.state_machine.infrared)
            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_enter(self):
        self.state_machine.gesture_control.change_gesture("track")

    def on_exit(self):
        self.state_machine.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("TrackState Pipeline results {}".format(hist[-1]))

        # unpack results
        cam_ok, bt_ok, ir_ok = self.pipeline["y_deviation"].success_state, \
                        self.pipeline["user_distance"].success_state, \
                        self.pipeline["ir_distance"].success_state
        dev, bt_distance, ir_distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self.queue_next_state(WaitState(self.state_machine))
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go
            # in wait state
            return self.queue_next_state(SearchState(
                self.state_machine, "left" if self.last_dev > 0 else "right"))
        if cam_ok and not bt_ok:
            self.last_dev = dev
            self.motor_alignment(dev)
            return self
        if cam_ok and bt_ok:
            self.last_dev = dev
            self.motor_alignment(dev)
            if ir_distance > config.MAX_IR_DISTANCE and bt_distance != bluetooth.UserDistanceEstimationPipeline.Distance.NEAR:
                return self.queue_next_state(FollowState(self.state_machine))
            return self.queue_next_state(self)


class WaitState(AbstractRobotState):
    """ waits until bt is near or woken up by other sensors"""

    def __init__(self, state_machine):
        AbstractRobotState.__init__(self, state_machine)
        self.start_time = None
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline(
                    self.state_machine.bt_dongles),
                # Ultrasonic inputs
                ultrasonic_pipelines.get_movement_pipeline(
                    self.state_machine.ultrasonic),
                # Infrared inputs
                infrared_piplelines.get_movement_pipeline(
                    self.state_machine.infrared)

            )

        self.pipeline.execute_callbacks = [self.show_result]

    @property
    def pipeline(self):
        return self.__pipeline

    def on_enter(self):
        self.state_machine.gesture_control.change_gesture("wait")
        self.start_time = current_time_millis()

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("WaitState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok, us_ok, ir_ok = self.pipeline[
                                          "y_deviation"].success_state, \
                                      self.pipeline[
                                          "user_distance"].success_state, \
                                      self.pipeline["us_change"].success_state, \
                                      self.pipeline["ir_change"].success_state

        dev, distance, _, _ = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:

            if (us_ok or ir_ok) and current_time_millis() - self.start_time > config.IF_US_START_DELAY:
                return SearchState(self.state_machine)
            return self
        if not cam_ok and bt_ok:

            # is bt distance far then go in wait state or timeout is reached go
            # in wait state
            if distance == bluetooth.UserDistanceEstimationPipeline.Distance.NEAR \
                    or ((us_ok or ir_ok) and current_time_millis() - self.start_time > config.IF_US_START_DELAY):
                return SearchState(self.state_machine)
            else:
                return self
        if cam_ok and not bt_ok:
            return TrackState(self.state_machine)
        if cam_ok and bt_ok:
            return FollowState(self.state_machine)
