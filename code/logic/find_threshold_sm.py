import cv2
import numpy as np
import sys

from config.config import *
from logic.statemachine import *
from sensors.camera import camera
from sensors.pipeline import PipelineSequence


class FindThresholdSM(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)

        if DEBUG_MODE:
            cv2.namedWindow("camtest")
            cv2.namedWindow("original")

            def check_positions(*_):
                hu = cv2.getTrackbarPos("H+", "camtest")
                hl = cv2.getTrackbarPos("H-", "camtest")
                su = cv2.getTrackbarPos("S+", "camtest")
                sl = cv2.getTrackbarPos("S-", "camtest")
                vu = cv2.getTrackbarPos("V+", "camtest")
                vl = cv2.getTrackbarPos("V-", "camtest")

                cv2.setTrackbarPos("H+", "camtest", max(hu, hl))
                cv2.setTrackbarPos("S+", "camtest", max(su, sl))
                cv2.setTrackbarPos("V+", "camtest", max(vu, vl))

            cv2.createTrackbar("H+", "camtest", 180, 180, check_positions)
            cv2.createTrackbar("H-", "camtest", 150, 180, check_positions)
            cv2.createTrackbar("S+", "camtest", 255, 255, check_positions)
            cv2.createTrackbar("S-", "camtest", 20, 255, check_positions)
            cv2.createTrackbar("V+", "camtest", 255, 255, check_positions)
            cv2.createTrackbar("V-", "camtest", 180, 255, check_positions)

        self._current_state.first_state = FindThresholdState()


class FindThresholdState(State):

    def __init__(self):
        State.__init__(self)

        lower = np.array([150, 20, 120])
        upper = np.array([180, 255, 255])

        self.__pipeline = \
            PipelineSequence(
                lambda inp: camera.read(),
                camera.ConvertColorspacePipeline(to='hsv'),
                camera.ColorThresholdPipeline(color=(lower, upper)),
                camera.ErodeDilatePipeline()
            )

        if DEBUG_MODE:
            def show_result(*_):
                _, (image_ok, image), _, _, (threshold_ok, threshold) = self.pipeline.step_results

                cv2.imshow("camtest", cv2.bitwise_and(image, image, mask=threshold))
                cv2.imshow("original", image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        self.pipeline.steps[2].threshold_lower = np.array([
            cv2.getTrackbarPos("H-", "camtest"),
            cv2.getTrackbarPos("S-", "camtest"),
            cv2.getTrackbarPos("V-", "camtest")])
        self.pipeline.steps[2].threshold_upper = np.array([
            cv2.getTrackbarPos("H+", "camtest"),
            cv2.getTrackbarPos("S+", "camtest"),
            cv2.getTrackbarPos("V+", "camtest")])

        return self


if __name__ == "__main__":
    FindThresholdSM().run()


