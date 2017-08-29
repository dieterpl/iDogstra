from logic.statemachine import *
from logic.states import follow, search, track
from sensors.bluetooth import bluetooth
from sensors import pipeline
from sensors.camera import camera
from motor import robot
import config
import logging

class WaitState(State):
    """ waits until bt is near or woken up by other sensors"""
    def __init__(self):
        State.__init__(self)

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

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        _, pipeline_result = hist[-1]
        logging.debug("WaitState Pipeline results", hist[-1])
        # unpack results
        camera_result, distance_result = pipeline_result
        cam_ok, dev = camera_result
        bt_ok, distance = distance_result
        # if there are no result values go to wait state
        if not cam_ok and not bt_ok:
            return self
        if not cam_ok and bt_ok:
            # is bt distance far then go in wait state or timeout is reached go in wait state
            if distance == bluetooth.UserDistanceEstimationPipeline.Distance.NEAR:
                return search.SearchState()
            else:
                return self
        if cam_ok and not bt_ok:
            return track.TrackState()
        if cam_ok and bt_ok:
            return follow.FollowState()

