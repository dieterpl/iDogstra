import logging
import sys
import time

import cv2
import numpy as np

from config.config import *
from sensors.pipeline import Pipeline, PipelineSequence, ParallelPipeline
from utils.functions import overrides

if os.uname().machine == 'armv7l':  # probably runnig on RaspPi
    import picamera
    import picamera.array
else:
    picamera = None

# create and setup the camera object
if picamera is None or USE_USB_CAMERA:
    camera = cv2.VideoCapture(1 if picamera is None else 0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
else:
    camera = picamera.PiCamera()
    #camera.resolution = PYCAMERA_RESOLUTION
    camera.framerate = 32
    time.sleep(2)


def read():
    """ Returns a camera image as an array of bgr-values """

    if picamera is None:
        return camera.read()[1]
    else:
        array = picamera.array.PiRGBArray(camera, size=CAMERA_RESOLUTION)
        camera.capture(array, format='bgr', resize=CAMERA_RESOLUTION, use_video_port=True)
        return array.array


class ConvertColorspacePipeline(Pipeline):

    def __init__(self, to='hsv'):
        Pipeline.__init__(self)

        self.__target_colorspace = to

    @overrides(Pipeline)
    def _execute(self, inp):
        if self.__target_colorspace == "hsv":
            return True, cv2.cvtColor(inp, cv2.COLOR_BGR2HSV)
        elif self.__target_colorspace == "grayscale":
            return True, cv2.cvtColor(inp, cv2.COLOR_BGR2GRAY)
        else:
            logging.warning('Unsupported color space', self.__target_colorspace)
            return False, None


class ColorThresholdPipeline(Pipeline):

    def __init__(self, color):
        Pipeline.__init__(self)

        if type(color) == str:
            if color == 'red':
                self.threshold_lower = np.array([140, 50, 50])
                self.threshold_upper = np.array([160, 255, 255])
            elif color == 'yellow':
                self.threshold_lower = np.array([30, 50, 50])
                self.threshold_upper = np.array([70, 255, 255])
            elif color == 'orange':
                self.threshold_lower = np.array([15, 50, 50])
                self.threshold_upper = np.array([25, 255, 255])
            elif color == 'magenta':
                self.threshold_lower = np.array([150, 50, 20])
                self.threshold_upper = np.array([170, 255, 255])
            else:
                raise ValueError('Unsupported color', color)
        elif type(color) == tuple:
            self.threshold_lower, self.threshold_upper = color
        else:
            raise ValueError('Unsupported argument type', type(color), '(must be str or tuple)')

    @overrides(Pipeline)
    def _execute(self, inp):
        colmask = cv2.inRange(inp, self.threshold_lower, self.threshold_upper)
        return True, colmask


class DetectColoredObjectPipeline(Pipeline):

    def __init__(self, color, min_contour_size=DETECTION_SIZE_THRESHOLD, post_process=True):
        Pipeline.__init__(self)

        if type(color) == str:
            if color == 'red':
                self.__threshold_lower = np.array([140, 50, 50])
                self.__threshold_upper = np.array([160, 255, 255])
            elif color == 'yellow':
                self.__threshold_lower = np.array([30, 50, 50])
                self.__threshold_upper = np.array([70, 255, 255])
            elif color == 'orange':
                self.__threshold_lower = np.array([15, 50, 50])
                self.__threshold_upper = np.array([25, 255, 255])
            elif color == 'magenta':
                self.__threshold_lower = np.array([150, 50, 20])
                self.__threshold_upper = np.array([170, 255, 255])
            else:
                raise ValueError('Unsupported color', color)
        elif type(color) == tuple:
            self.__threshold_lower, self.__threshold_upper = color
        else:
            raise ValueError('Unsupported argument type', type(color), '(must be str or tuple)')

        self.__post_process = post_process
        self.__min_contour_size = min_contour_size

    @overrides(Pipeline)
    def _execute(self, inp):
        colmask = cv2.inRange(inp, self.__threshold_lower, self.__threshold_upper)

        if self.__post_process:
            colmask = cv2.erode(colmask, None, iterations=2)
            colmask = cv2.dilate(colmask, None, iterations=2)

        _, cnts, _ = cv2.findContours(colmask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            largest_contour = max(cnts, key=cv2.contourArea)

            if cv2.contourArea(largest_contour) > inp.shape[0] * inp.shape[1] * self.__min_contour_size:
                bbox = tuple(cv2.boundingRect(largest_contour))
                return True, bbox

        return False, None


class TrackBBOXPipeline(Pipeline):
    supported_tracking_algorithms = ['MIL', 'BOOSTING', 'KCF', 'TLC', 'MEDIANFLOW', 'GOTURN']

    def __init__(self, initial_frame, initial_bbox, tracking_algorithm='MIL'):
        Pipeline.__init__(self)

        if tracking_algorithm not in TrackBBOXPipeline.supported_tracking_algorithms:
            raise ValueError('Invalid tracking algorithm', tracking_algorithm)

        self.__tracker = cv2.Tracker_create(tracking_algorithm)
        self.__tracker.init(initial_frame, initial_bbox)

    @overrides(Pipeline)
    def _execute(self, inp):
        return self.__tracker.update(inp)


class FindYDeviationPipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        (left_x, _, width, _), (_, image_width, _) = inp
        mid_x = image_width / 2
        max_dev = mid_x

        left_x -= mid_x
        dev = (left_x + width/2) / max_dev
        return True, dev


class GetImageDimensionsPipeline(Pipeline):

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, inp.shape


def test():
    # test a default pipeline
    camera_pipeline = \
        PipelineSequence(
            lambda inp: read(),
            ParallelPipeline(
                PipelineSequence(
                    ConvertColorspacePipeline(to='hsv'),
                    DetectColoredObjectPipeline(color='red')
                ),
                GetImageDimensionsPipeline()
            ),
            FindYDeviationPipeline()
        )

    def show_result(*_):
        _, _, (bbox_ok, bbox) = camera_pipeline.steps[1].pipelines[0].step_results
        _, (image_ok, image), _, (dev_ok, dev) = camera_pipeline.step_results

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

    def switch_detect_to_track(*_):
        _, (image_ok, image), _, (bbox_ok, bbox), _ = camera_pipeline.step_results

        if bbox_ok:
            print('Switching detection step with tracking step')
            camera_pipeline.steps[2] = TrackBBOXPipeline(image, bbox, tracking_algorithm=TRACKING_ALGORITHM)
            camera_pipeline.execute_callbacks.remove(switch_detect_to_track)

    cv2.namedWindow('camtest', cv2.WINDOW_AUTOSIZE)
    camera_pipeline.execute_callbacks = [show_result]
    while True:
        camera_pipeline.run_pipeline(None)  # first input is irrelevant


if __name__ == '__main__':
    test()

