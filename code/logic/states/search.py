from logic.statemachine import *
from logic.states import follow,wait
from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth
from sensors import pipeline
from sensors.camera import camera
import logging
class SearchState(State):
    """ Abstract superclass for all state machine states """
    def __init__(self):
        self.start_time = None
        self.__btdongles = bluetooth.btdongles

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            pipeline.create_parallel_pipeline([
                # Camera inputs
                pipeline.create_sequential_pipeline([
                    lambda inp: camera.read(),
                    pipeline.create_parallel_pipeline([
                        pipeline.create_sequential_pipeline([
                            camera.ConvertColorspacePipeline(to='hsv'),
                            camera.DetectColoredObjectPipeline(color='magenta')
                        ]),
                        camera.GetImageDimensionsPipeline()
                    ]),
                    camera.FindYDeviationPipeline()
                ]),
                # Bluetooth inputs
                pipeline.create_sequential_pipeline([
                    pipeline.ConstantPipeline(self.__btdongles),
                    bluetooth.SnapshotBTDataPipeline(),
                    bluetooth.UserDistanceEstimationPipeline()
                ])
            ])


    def on_enter(self):
        self.start_time = current_time_millis()


    def on_exit(self):
        """ Called when this state is exited"""
        pass

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        camera_dev_result, distance_result = hist[-1]
        logging.debug("SearchState Pipeline results", hist[-1])

        if True:
            return follow.FollowState()
        else:
            return self

        if current_time_millis()-self.start_time>30000:
            return WaitState()


