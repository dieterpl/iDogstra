import cv2
import numpy as np
import sys

from config.config import *
from logic.statemachine import *
from sensors.camera import camera, camera_pipelines


class CameraTestSM(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)

        self._current_state.first_state = FindThresholdState()


class FindThresholdState(State):

    def __init__(self):
        State.__init__(self)

        lower = np.array([150, 20, 120])
        upper = np.array([180, 255, 255])
        self.__pipeline = camera_pipelines.color_filter_pipeline(color=(lower, upper))

        if DEBUG_MODE:
            def show_result(*_):
                _, (image_ok, image), _, _, (threshold_ok, threshold) = self.pipeline.step_results

                cv2.imshow("camtest", cv2.bitwise_and(image, image, mask=threshold))
                cv2.imshow("original", image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    @overrides(State)
    def on_enter(self):
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

    @overrides(State)
    def on_exit(self):
        cv2.destroyAllWindows()

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


class TestYDeviationState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.color_tracking_pipeline()

    def on_enter(self):
        cv2.namedWindow('camtest', cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):

        def show_result(*_):
            _, _, _, _, (bbox_ok, bbox) = self.pipeline.steps[1].pipelines[0].step_results
            _, (image_ok, image), _, (dev_ok, dev) = self.pipeline.step_results

            # draw bounding box
            if bbox_ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(image, p1, p2, (0, 0, 255))

            # add deviation as text
            if dev_ok:
                cv2.putText(image, str(dev), (0, image.shape[0] - 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

            cv2.imshow('camtest', image)
            if cv2.waitKey(1) & 0xff == ord('q'):
                sys.exit()

        self.pipeline.execute_callbacks = [show_result]




