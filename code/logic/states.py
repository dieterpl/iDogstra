from logic.statemachine import *
from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth, bluetooth_pipelines
from sensors import pipeline
from sensors.camera import camera, camera_pipelines
from motor import robot
import logging
import config
import cv2
import sys
from scipy.interpolate import interp1d


class AbstractRobotState(State):
    def __init__(self):
        State.__init__(self)
        self.robots_control = robot.Robot()
        self.next_state = None
        self.state_switching_timestamp = None

    def motor_alignment(self, dev):
        dev *= -1
        if abs(dev) > 0.2:
            self.robots_control.rotate(interp1d([-1, 1], [-config.MAX_TURN_SPEED, config.MAX_TURN_SPEED])(dev))

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
                cv2.putText(image, str(dev), (0, image.shape[0] - 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6,
                            [0, 255, 0])

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


class SearchState(AbstractRobotState):
    """Turn robot in circles until the user is found or timeout occurred"""

    def __init__(self, start_spin_direction="left"):
        AbstractRobotState.__init__(self)
        self.start_time = None
        self.start_spin_direction = start_spin_direction
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        print(type(pipeline), pipeline)
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline()
            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_enter(self):
        if self.start_spin_direction == "left":
            self.robots_control.left(config.SEARCH_SPEED)
        else:
            self.robots_control.right(config.SEARCH_SPEED)
        self.start_time = current_time_millis()

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("SearchState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline["y_deviation"].success_state, self.pipeline["user_distance"].success_state
        dev, distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            if current_time_millis() - self.start_time > config.SEARCH_TIMEOUT or distance == bluetooth.UserDistanceEstimationPipeline.Distance.FAR:
                return WaitState()
            return self
        if cam_ok and not bt_ok:
            return TrackState()
        if cam_ok and bt_ok:
            return FollowState()


class FollowState(AbstractRobotState):
    """ Follows the user using the camera and bt by moving the robot"""

    def __init__(self):
        AbstractRobotState.__init__(self)
        self.robots_control = robot.Robot()
        self.last_dev = 0

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                ("test1", camera_pipelines.color_tracking_pipeline()),
                # Bluetooth inputs
                bluetooth_pipelines.recommended_speed_pipeline()
            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("FollowState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline["test1"].success_state, self.pipeline["bt_speed"].success_state
        logging.debug("FollowState Pipeline results {}".format(cam_ok))
        dev, speed = pipeline_result

        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self.queue_next_state(WaitState())
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            return self.queue_next_state(SearchState("left" if self.last_dev > 0 else "right"))
        if cam_ok and not bt_ok:
            return self.queue_next_state(TrackState())
        if cam_ok and bt_ok:
            self.last_dev = dev
            self.motor_alignment(dev)
        else:
            self.robots_control.forward(speed)
        return self.queue_next_state(self)


class TrackState(AbstractRobotState):
    """ Tracks the user with the camera but stays at the current position"""

    def __init__(self):
        AbstractRobotState.__init__(self)
        self.robots_control = robot.Robot()
        self.last_dev = 0
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline()
            )

        self.pipeline.execute_callbacks = [self.show_result]

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("TrackState Pipeline results {}".format(hist[-1]))

        # unpack results
        cam_ok, bt_ok = self.pipeline["y_deviation"].success_state, self.pipeline["user_distance"].success_state
        dev, distance = pipeline_result
        dev *= -1
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self.queue_next_state(WaitState())
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            return self.queue_next_state(SearchState("left" if dev > 0 else "right"))
        if cam_ok and not bt_ok:
            self.last_dev = dev
            self.motor_aligment(dev)
            return self
        if cam_ok and bt_ok:
            self.last_dev = dev
            self.motor_aligment(dev)
            if distance != bluetooth.UserDistanceEstimationPipeline.Distance.NEAR:
                return self.queue_next_state(FollowState())
            return self.queue_next_state(self)


class WaitState(AbstractRobotState):
    """ waits until bt is near or woken up by other sensors"""

    def __init__(self):
        AbstractRobotState.__init__(self)

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                bluetooth_pipelines.user_distance_estimation_pipeline()
            )

        self.pipeline.execute_callbacks = [self.show_result]

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("WaitState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline["y_deviation"].success_state, self.pipeline["user_distance"].success_state
        dev, distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            if distance == bluetooth.UserDistanceEstimationPipeline.Distance.NEAR:
                return SearchState()
            else:
                return self
        if cam_ok and not bt_ok:
            return TrackState()
        if cam_ok and bt_ok:
            return FollowState()
