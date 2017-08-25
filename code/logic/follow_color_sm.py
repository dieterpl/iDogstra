from logic.statemachine import *
from sensors.pipeline import create_parallel_pipeline, create_sequential_pipeline
from sensors.camera import camera
from motor import movement
import cv2
from utils.config import *
from sensors.bluetooth.bluetooth import BTDongle


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
                        camera.DetectColoredObjectPipeline(color='magenta')
                    ]),
                    camera.GetImageDimensionsPipeline()
                ]),
                camera.FindYDeviationPipeline()
            ])

        if DEBUG_MODE:
            def show_result(*_):
                _, _, (bbox_ok, bbox) = self.__pipeline.steps[1].pipelines[0].step_results
                _, (image_ok, image), _, (dev_ok, dev) = self.__pipeline.step_results

                # draw bounding box
                if bbox_ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(image, p1, p2, (0, 0, 255))

                # add deviation as text
                if dev_ok:
                    cv2.putText(image, str(dev), (0, image.shape[0] - 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

                cv2.imshow('camtest', image)
                cv2.waitKey(1)

            self.__pipeline.execute_callbacks = [show_result]

        # todo port to pipelines
        uuid = '6951e12f049945d2930e1fc462c721c8'
        self.btdongles = [BTDongle(i, uuid) for i in range(2)]
        for dongle in self.btdongles:
            dongle.start()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        dev_ok, dev = hist[-1]

        _sum = sum(dongle.snapshot_data().avg() for dongle in self.btdongles)
        _avg = _sum / len(self.btdongles)
        if _avg < 60:
            speed = 0
        else:
            speed = round(min(100.0, 15 + 4 * (_avg - 60)))

        if dev_ok:
            if dev < -0.6:
                movement.right(50)
            elif dev < -0.3:
                movement.right(30)
            elif dev < -0.2:
                movement.right(10)
            elif dev > 0.6:
                movement.left(50)
            elif dev > 0.3:
                movement.left(30)
            elif dev > 0.2:
                movement.left(10)
            else:
                movement.forward(speed)
        else:
            movement.stop()

        return self

    def on_exit(self):
        movement.stop()

if __name__ == '__main__':
    cv2.namedWindow('camtest')

    FollowColorSM().run()


