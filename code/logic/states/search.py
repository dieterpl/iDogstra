from logic.statemachine import *
from logic.states import FollowState, WaitState
from utils.functions import current_time_millis
from sensors.bluetooth import *

class SearchState(State):
    """ Abstract superclass for all state machine states """
    def __init__(self):
        self.start_time = None
        self.__btdongles = btdongles

        # Create a pipeline that reads both camara and bluetooth inputs
        # parallel and processes them sequentially
        self.__pipeline = \
            create_parallel_pipeline([
                # Camera inputs
                create_sequential_pipeline([
                    lambda inp: camera.read(),
                    create_parallel_pipeline([
                        create_sequential_pipeline([
                            camera.ConvertColorspacePipeline(to='hsv'),
                            camera.DetectColoredObjectPipeline(color='magenta')
                        ]),
                        camera.GetImageDimensionsPipeline()
                    ]),
                    camera.FindYDeviationPipeline()
                ]),
                # Bluetooth inputs
                create_sequential_pipeline([
                    ConstantPipeline(self.__btdongles),
                    SnapshotBTDataPipeline(),
                    RecommendedSpeedPipeline()
                ])
            ])


    def on_enter(self):
        self.start_time = current_time_millis()


    def on_exit(self):
        """ Called when this state is exited"""
        pass

    @property
    def pipeline(self):
        raise NotImplementedError()

    def on_update(self, hist):
        if True:
            return FollowState()
        else:
            return self

        if current_time_millis()-self.start_time>30000:
            return WaitState()


