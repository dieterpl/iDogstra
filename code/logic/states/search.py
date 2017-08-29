from logic.statemachine import *
import logic.states as states

from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth
from sensors import pipeline
from sensors.camera import camera
from motor import robot

import logging
import config

class SearchState(State):
    """Turn robot in circles until the user is found or timeout occurred"""
    def __init__(self, start_spin_direction = "left"):
        State.__init__(self)
        self.start_time = None
        self.robots_control = robot.Robot()
        self.start_spin_direction = start_spin_direction
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.DisjunctiveParallelPipeline(
                # Camera inputs
                pipeline.PipelineSequence(
                    lambda inp: camera.read(),
                    pipeline.ConjunctiveParallelPipeline(
                        pipeline.PipelineSequence(
                            camera.ConvertColorspacePipeline(to='hsv'),
                            camera.DetectColoredObjectPipeline(color='magenta')
                        ),
                        camera.GetImageDimensionsPipeline()
                    ),
                    camera.FindYDeviationPipeline()
                ),
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
        _, pipeline_result = hist[-1]
        logging.debug("SearchState Pipeline results", hist[-1])
        # unpack results
        camera_result, distance_result = pipeline_result
        cam_ok, dev = camera_result
        bt_ok, distance = distance_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return states.WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            if current_time_millis() - self.start_time > 30000 or distance == bluetooth.UserDistanceEstimationPipeline.Distance.FAR:
                return states.WaitState()
            return self
        if cam_ok and not bt_ok:
            return states.TrackState()
        if cam_ok and bt_ok:
            return states.FollowState()
