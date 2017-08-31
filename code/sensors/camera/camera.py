import logging
import sys
import time

import cv2
import numpy as np
import random
from threading import Thread

from config.config import *
from sensors.pipeline import Pipeline
from utils.functions import overrides
from scipy.interpolate import interp1d

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


class ReadCameraPipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

        self.__last_sucess = False
        self.__last_capture = None

        Thread(target=self.__read).start()
        time.sleep(2)
        
    def __read(self):
        while True:
            if picamera is None:
                self.__last_sucess, self.__last_capture = camera.read()
            else:
                array = picamera.array.PiRGBArray(camera, size=CAMERA_RESOLUTION)
                camera.capture(array, format='bgr', resize=CAMERA_RESOLUTION, use_video_port=True)

                self.__last_capture = array.array
                self.__last_sucess = True

    def _execute(self, inp):
        return self.__last_sucess and self.__last_capture is not None, self.__last_capture


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
                self.threshold_lower = np.array([interp1d([0, 360], [0, 180])(300),
                                                 interp1d([0, 100], [0, 255])(10),
                                                 interp1d([0, 100], [0, 255])(10)])
                self.threshold_upper = np.array([interp1d([0, 360], [0, 180])(330),
                                                 interp1d([0, 100], [0, 255])(100),
                                                 interp1d([0, 100], [0, 255])(100)])
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


class HaarcascadePipeline(Pipeline):

    def __init__(self, haarfile):
        Pipeline.__init__(self)
        self.detector = cv2.CascadeClassifier(haarfile)

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, self.detector.detectMultiScale(inp)


class FindLegsPipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        result = np.zeros(inp.shape)

        height, width = inp.shape
        segment_towers = []
        last_segments = []
        this_segments = []
        for y in range(int(height/3), height, 10):
            edge_points = []
            last_segments, this_segments = this_segments, []

            for x in range(0, width):
                if inp[y, x] > 0:
                    edge_points.append(x)

            for i in range(1, len(edge_points)):
                x1, x2 = edge_points[i-1], edge_points[i]

                if 40 < x2 - x1 < 100:
                    this_tower_idx = None

                    found_upper = False
                    for ly, lx1, lx2, tower_idx in last_segments:
                        ix1, ix2 = max(x1, lx1), min(x2, lx2)
                        if ix2 <= ix1:
                            continue  # empty intersection
                        elif ix2 - ix1 > 0.75 * x2 - x1:
                            segment_towers[tower_idx].append((y, x1, x2))
                            this_tower_idx = tower_idx
                            found_upper = True

                    if not found_upper:
                        this_tower_idx = len(segment_towers)
                        segment_towers.append([(y, x1, x2)])

                    this_segments.append((y, x1, x2, this_tower_idx))

        leg_candidates = []
        for tower in segment_towers:
            if len(tower) > 1:
                (top_y, top_x1, top_x2), (bot_y, bot_x1, bot_x2) = tower[0], tower[-1]
                leg_candidates.append([(int(top_x1 + (top_x2-top_x1)/2), top_y),
                                       (int(bot_x1 + (bot_x2 - bot_x1)/1), bot_y)])

                for y, x1, x2 in tower:
                    for x in range(x1, x2):
                        result[y, x] = 255
                    for yy in range(max(0, y-10), min(height-1, y+10)):
                        result[yy, x1] = 255
                        result[yy, x2] = 255

        return True, (result, leg_candidates)
