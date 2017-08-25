from logic.statemachine import *
from sensors.pipeline import create_parallel_pipeline, create_sequential_pipeline
from sensors.camera import camera
from motor import movement


class FollowColorSM(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)

        self._current_state.first_state = FollowState()


class FollowState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = \
            create_sequential_pipeline([
                lambda inp: camera.read(),
                create_parallel_pipeline([
                    create_sequential_pipeline([
                        camera.ConvertColorspacePipeline(to='hsv'),
                        camera.DetectColoredObjectPipeline(color='orange')
                    ]),
                    camera.GetImageDimensionsPipeline()
                ]),
                camera.FindYDeviationPipeline()
            ])

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        dev_ok, dev = hist[-1]

        if dev_ok:
            if dev > 0.2:
                movement.right(255)
            elif dev < -0.2:
                movement.left(255)
            else:
                movement.forward(255)

        return self

if __name__ == '__main__':
    FollowColorSM().run()


