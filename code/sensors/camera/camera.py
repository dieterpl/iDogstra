import logging
import sys
import time

import cv2
import numpy as np

from config.config import *
from sensors.pipeline import Pipeline
from utils.functions import overrides

if os.uname().machine == 'armv7l':  # probably runnig on RaspPi
    import picamera
    import picamera.array
else:
    picamera = None

# create and setup the camera object
if picamera is None or USE_USB_CAMERA:
    camera = cv2.VideoCapture(0 if picamera is None else 0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
    # camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    # camera.set(cv2.CAP_PROP_EXPOSURE, .0001)
    # camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    # camera.set(cv2.CAP_PROP_GAIN, 1)
    # camera.set(cv2.CAP_PROP_BACKLIGHT, 100)
    # camera.set(cv2.CAP_PROP_SETTINGS, 1)

    picamera = None
else:
    camera = picamera.PiCamera()
    # camera.resolution = PYCAMERA_RESOLUTION
    camera.framerate = 32
    camera.exposure_mode = "antishake"
    time.sleep(2)


def read():
    """ Returns a camera image as an array of bgr-values """

    if picamera is None:
        return camera.read()[1]
    else:
        array = picamera.array.PiRGBArray(camera, size=CAMERA_RESOLUTION)
        camera.capture(array, format='bgr', resize=CAMERA_RESOLUTION, use_video_port=True)
        return array.array


class ReadCameraPipeline(Pipeline):

    def _execute(self, inp):
        if picamera is None:
            return camera.read()
        else:
            array = picamera.array.PiRGBArray(camera, size=CAMERA_RESOLUTION)
            camera.capture(array, format='bgr', resize=CAMERA_RESOLUTION, use_video_port=True)
            return True, array.array


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
                self.threshold_lower = np.array([150, 20, 50])
                self.threshold_upper = np.array([175, 255, 255])
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


class ErodeDilatePipeline(Pipeline):

    @overrides(Pipeline)
    def _execute(self, inp):
        x = cv2.erode(inp, None, iterations=2)
        x = cv2.dilate(x, None, iterations=2)
        return True, x


class GetLargestContourPipeline(Pipeline):

    def __init__(self, min_contour_size=DETECTION_SIZE_THRESHOLD):
        Pipeline.__init__(self)

        self.__min_contour_size = min_contour_size

    @overrides(Pipeline)
    def _execute(self, inp):
        _, cnts, _ = cv2.findContours(inp.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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


class EdgeDetectionPipeline(Pipeline):

    def __init__(self, threshold_lower=100, threshold_upper=200):
        Pipeline.__init__(self)

        self.threshold_lower = threshold_lower
        self.threshold_upper = threshold_upper

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, cv2.Canny(inp, self.threshold_lower, self.threshold_upper)

