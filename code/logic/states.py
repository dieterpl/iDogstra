from logic.statemachine import *
from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth
from sensors import pipeline
from sensors.camera import camera, camera_pipelines
from motor import robot
import logging
import config


class SearchState(State):
    """Turn robot in circles until the user is found or timeout occurred"""

    def __init__(self, start_spin_direction="left"):
        State.__init__(self)
        self.start_time = None
        self.robots_control = robot.Robot()
        self.start_spin_direction = start_spin_direction
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                pipeline.PipelineSequence(
                    pipeline.ConstantPipeline(config.BT_DONGLES),
                    bluetooth.SnapshotBTDataPipeline(),
                    bluetooth.UserDistanceEstimationPipeline()
                )
            )

    def on_enter(self):
        if self.start_spin_direction == "left":
            self.robots_control.left(25)
        else:
            self.robots_control.right(25)
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
        cam_ok, bt_ok = self.pipeline[0].success_state, self.pipeline[1].success_state
        dev, distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            if current_time_millis() - self.start_time > 30000 or distance == bluetooth.UserDistanceEstimationPipeline.Distance.FAR:
                return WaitState()
            return self
        if cam_ok and not bt_ok:
            return TrackState()
        if cam_ok and bt_ok:
            return FollowState()


class FollowState(State):
    """ Follows the user using the camera and bt by moving the robot"""

    def __init__(self):
        State.__init__(self)
        self.robots_control = robot.Robot()
        self.last_dev = 0
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                pipeline.PipelineSequence(
                    pipeline.ConstantPipeline(config.BT_DONGLES),
                    bluetooth.SnapshotBTDataPipeline(),
                    bluetooth.RecommendedSpeedPipeline()
                )
            )

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("FollowState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline[0].success_state, self.pipeline[1].success_state
        print(cam_ok, bt_ok)
        dev, speed = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            return SearchState("left" if self.last_dev > 0 else "right")
        if cam_ok and not bt_ok:
            return TrackState()
        if cam_ok and bt_ok:
            self.last_dev = dev
            if dev < -0.6:
                self.robots_control.right(50)
            elif dev < -0.3:
                self.robots_control.right(30)
            elif dev < -0.2:
                self.robots_control.right(10)
            elif dev > 0.6:
                self.robots_control.left(50)
            elif dev > 0.3:
                self.robots_control.left(30)
            elif dev > 0.2:
                self.robots_control.left(10)
            else:
                self.robots_control.forward(speed)
            return self


class TrackState(State):
    """ Tracks the user with the camera but stays at the current position"""

    def __init__(self):

        State.__init__(self)
        self.robots_control = robot.Robot()
        self.last_dev = 0
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                pipeline.PipelineSequence(
                    pipeline.ConstantPipeline(config.BT_DONGLES),
                    bluetooth.SnapshotBTDataPipeline(),
                    bluetooth.UserDistanceEstimationPipeline()
                )
            )

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("TrackState Pipeline results {}".format(hist[-1]))

        # unpack results
        cam_ok, bt_ok = self.pipeline[0].success_state, self.pipeline[1].success_state
        logging.debug("Values {}{}".format(cam_ok, bt_ok))
        dev, distance = pipeline_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            return SearchState("left" if dev > 0 else "right")
        if cam_ok and not bt_ok:
            return self
        if cam_ok and bt_ok:
            self.last_dev = dev
            if dev < -0.6:
                self.robots_control.right(50)
            elif dev < -0.3:
                self.robots_control.right(30)
            elif dev < -0.2:
                self.robots_control.right(10)
            elif dev > 0.6:
                self.robots_control.left(50)
            elif dev > 0.3:
                self.robots_control.left(30)
            elif dev > 0.2:
                self.robots_control.left(10)
            if distance != bluetooth.UserDistanceEstimationPipeline.Distance.NEAR:
                return FollowState()
            return self


class WaitState(State):
    """ waits until bt is near or woken up by other sensors"""

    def __init__(self):
        State.__init__(self)

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                camera_pipelines.color_tracking_pipeline(),
                # Bluetooth inputs
                pipeline.PipelineSequence(
                    pipeline.ConstantPipeline(config.BT_DONGLES),
                    bluetooth.SnapshotBTDataPipeline(),
                    bluetooth.UserDistanceEstimationPipeline()
                )
            )

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        pipeline_result = hist[-1]
        logging.debug("WaitState Pipeline results {}".format(hist[-1]))
        # unpack results
        cam_ok, bt_ok = self.pipeline[0].success_state, self.pipeline[1].success_state
        logging.debug("Values {}{}".format(cam_ok,bt_ok))
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
