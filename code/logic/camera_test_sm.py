import cv2
import numpy as np
import sys
import logging

from config.config import *
from logic.statemachine import *
from sensors.camera import camera, camera_pipelines


class CameraTestSM(StateMachine):

    def __init__(self, testmode="show-image"):
        StateMachine.__init__(self)

        if testmode == "show-image":
            self._current_state.first_state = ShowImageState()
        elif testmode == "threshold":
            self._current_state.first_state = FindThresholdState()
        elif testmode == "deviation":
            self._current_state.first_state = TestYDeviationState()
        elif testmode == "edges":
            self._current_state.first_state = ShowEdgesState()
        elif testmode == "find-color":
            self._current_state.first_state = FindColorState()
        elif testmode == "track-color":
            self._current_state.first_state = FindColorStateToTrack()
        elif testmode == "detect-person":
            self._current_state.first_state = DetectPersonState()
        elif testmode == "find-legs":
            self._current_state.first_state = FindLegsState()
        elif testmode == "show-steps":
            self._current_state.first_state = ShowColorTrackingPipelineStepsState()
        else:
            logging.warning("Unkown testmode '{}'. Falling back to show-image".format(testmode))
            self._current_state.first_state = ShowImageState()


class FindLegsState(State):
    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.find_legs_pipeline()

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                image = self.pipeline["image"].output
                edges = self.pipeline["edges"].output
                legs, candidates = self.pipeline["legs"].output

                for leg in candidates:
                    print(leg[0], leg[1])
                    cv2.line(image, leg[0], leg[1], (0, 0, 255))

                cv2.imshow("camera", image)
                cv2.imshow("edges", edges)
                cv2.imshow("legs", legs)

                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camera", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("edges", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("legs", cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self


class TrackObjectState(State):
    def __init__(self, frame, bbox):
        State.__init__(self)

        self.__pipeline = camera_pipelines.box_tracking_pipeline(frame, bbox)

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                _, _, (bbox_ok, bbox) = self.pipeline[1][0].results
                _, (image_ok, image), _, (dev_ok, dev) = self.pipeline.results

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

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow('camtest', cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self


class DetectPersonState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.haarcascade_pipeline(
            haarfile=os.path.join(HAARPATH, "lowerbody.xml"))

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                bboxes = self.pipeline["cascades"].output
                image = self.pipeline["image"].output

                # draw bounding box
                for bbox in bboxes:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(image, p1, p2, (0, 0, 255))

                cv2.imshow("camtest", image)
                if cv2.waitKey(1) & 0xff == ord("q"):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camtest", cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self


class FindColorStateToTrack(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.color_tracking_pipeline()

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                bbox_ok, bbox = self.pipeline["contour_bbox"].result
                image = self.pipeline["image"].output
                dev_ok, dev = self.pipeline["y_deviation"].result

                # draw bounding box
                if bbox_ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(image, p1, p2, (0, 0, 255))

                # add deviation as text
                if dev_ok:
                    cv2.putText(image, str(dev), (0, image.shape[0] - 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

                cv2.imshow("camtest", image)
                if cv2.waitKey(1) & 0xff == ord("q"):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camtest", cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        _, _, _, _, (bbox_ok, bbox) = self.pipeline[1][0].results
        _, (_, image), _, _ = self.pipeline.results

        if bbox_ok:
            return TrackObjectState(image, bbox)
        else:
            return self


class ShowColorTrackingPipelineStepsState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.color_tracking_pipeline()

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                bbox_ok, bbox = self.pipeline["contour_bbox"].result
                image = self.pipeline["image"].output
                hsv_image = self.pipeline["hsv_image"].output
                threshold = self.pipeline["threshold"].output
                filtered = self.pipeline["filtered"].output
                dev_ok, dev = self.pipeline["y_deviation"].result
                raw_dev_ok, raw_dev = self.pipeline["raw_y_deviation"].result

                # draw bounding box
                bbox_image = image.copy()
                if bbox_ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(bbox_image, p1, p2, (0, 0, 255))

                # add deviation as text
                if dev_ok:
                    cv2.putText(bbox_image, str(dev), (0, image.shape[0] - 5),
                                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])
                if raw_dev_ok:
                    cv2.putText(bbox_image, str(raw_dev), (image.shape[1] - 50, image.shape[0] - 5),
                                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

                cv2.imshow("image", image)
                cv2.imshow("hsv_image", hsv_image)
                cv2.imshow("threshold", threshold)
                cv2.imshow("filtered", filtered)
                cv2.imshow("bbox", bbox_image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("hsv_image", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("threshold", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("filtered", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("bbox", cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self


class FindColorState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.color_tracking_pipeline()
        # self.__pipeline = camera_pipelines.color_tracking_dbscan_pipeline()
        # self.__pipeline = camera_pipelines.fast_color_tracking_pipeline("magenta")

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                bbox_ok, bbox = self.pipeline["contour_bbox"].result
                image = self.pipeline["image"].output
                dev_ok, dev = self.pipeline["y_deviation"].result

                # draw bounding box
                if bbox_ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(image, p1, p2, (0, 0, 255))

                # add deviation as text
                if dev_ok:
                    cv2.putText(image, str(dev), (0, image.shape[0] - 5),
                                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

                cv2.imshow('camtest', image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow('camtest', cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self


class ShowImageState(State):

    def __init__(self):
        State.__init__(self)
        self.__pipeline = camera.READ_CAMERA_PIPELINE

        if GRAPHICAL_OUTPUT:
            def show_result(_, image):
                if image is not None:
                    cv2.imshow("camera", image)
                    if cv2.waitKey(1) & 0xff == ord('q'):
                        sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    @property
    def pipeline(self):
        return self.__pipeline

    @overrides(State)
    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camera")

    @overrides(State)
    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @overrides(State)
    def on_update(self, hist):
        return self


class ShowEdgesState(State):

    def __init__(self):
        State.__init__(self)
        self.__pipeline = camera_pipelines.edge_detection_pipeline(100, 200)

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                image = self.pipeline["image"].output
                edges = self.pipeline["edges"].output
                
                cv2.imshow("camera", image)
                cv2.imshow("edges", edges)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    @property
    def pipeline(self):
        return self.__pipeline

    @overrides(State)
    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camera")
            cv2.namedWindow("edges")

    @overrides(State)
    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @overrides(State)
    def on_update(self, hist):
        return self


class FindThresholdState(State):

    def __init__(self):
        State.__init__(self)

        lower = np.array([150, 20, 120])
        upper = np.array([180, 255, 255])
        self.__pipeline = camera_pipelines.color_filter_pipeline(color=(lower, upper))

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                _, (image_ok, image), _, _, (threshold_ok, threshold) = self.pipeline.results

                cv2.imshow("camtest", cv2.bitwise_and(image, image, mask=threshold))
                cv2.imshow("original", image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    @overrides(State)
    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow("camtest")
            cv2.namedWindow("original")
            cv2.namedWindow("control")

            def check_positions(*_):
                hu = cv2.getTrackbarPos("H+", "control")
                hl = cv2.getTrackbarPos("H-", "control")
                su = cv2.getTrackbarPos("S+", "control")
                sl = cv2.getTrackbarPos("S-", "control")
                vu = cv2.getTrackbarPos("V+", "control")
                vl = cv2.getTrackbarPos("V-", "control")

                cv2.setTrackbarPos("H+", "control", max(hu, hl))
                cv2.setTrackbarPos("S+", "control", max(su, sl))
                cv2.setTrackbarPos("V+", "control", max(vu, vl))

            cv2.createTrackbar("H+", "control", 180, 180, check_positions)
            cv2.createTrackbar("H-", "control", 150, 180, check_positions)
            cv2.createTrackbar("S+", "control", 255, 255, check_positions)
            cv2.createTrackbar("S-", "control", 20, 255, check_positions)
            cv2.createTrackbar("V+", "control", 255, 255, check_positions)
            cv2.createTrackbar("V-", "control", 180, 255, check_positions)

    @overrides(State)
    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        if GRAPHICAL_OUTPUT:
            self.pipeline[2].threshold_lower = np.array([
                cv2.getTrackbarPos("H-", "control"),
                cv2.getTrackbarPos("S-", "control"),
                cv2.getTrackbarPos("V-", "control")])
            self.pipeline[2].threshold_upper = np.array([
                cv2.getTrackbarPos("H+", "control"),
                cv2.getTrackbarPos("S+", "control"),
                cv2.getTrackbarPos("V+", "control")])

        return self


class TestYDeviationState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = camera_pipelines.color_tracking_pipeline("magenta")

        if GRAPHICAL_OUTPUT:
            def show_result(*_):
                bbox_ok, bbox = self.pipeline["contour_bbox"].result
                image = self.pipeline["image"].output
                dev_ok, dev = self.pipeline["y_deviation"].result

                # draw bounding box
                if bbox_ok:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(image, p1, p2, (0, 0, 255))

                # add deviation as text
                if dev_ok:
                    cv2.putText(image, str(dev), (0, image.shape[0] - 5),
                                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])

                cv2.imshow('camtest', image)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    sys.exit()

            self.pipeline.execute_callbacks = [show_result]

    def on_enter(self):
        if GRAPHICAL_OUTPUT:
            cv2.namedWindow('camtest', cv2.WINDOW_AUTOSIZE)

    def on_exit(self):
        if GRAPHICAL_OUTPUT:
            cv2.destroyAllWindows()

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self






