from logic.statemachine import *
import logic.states as states

from sensors.bluetooth import bluetooth
from sensors import pipeline
from sensors.camera import camera
from motor import robot
import config
import logging

class TrackState(State):
    """ Tracks the user with the camera but stays at the current position"""
    def __init__(self):

        State.__init__(self)
        self.robots_control = robot.Robot()
        self.last_dev = 0
        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.ConjunctiveParallelPipeline(
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

    def on_exit(self):
        self.robots_control.stop()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        _, pipeline_result = hist[-1]
        logging.debug("TrackState Pipeline results", hist[-1])
        # unpack results
        camera_result, distance_result = pipeline_result
        cam_ok, dev = camera_result
        bt_ok, distance = distance_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return states.WaitState()
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            return states.SearchState("left" if dev > 0 else "right")
        if cam_ok and not bt_ok:
            return self
        if cam_ok and bt_ok:
            self.last_dev=dev
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
                return states.FollowState()
            return self






