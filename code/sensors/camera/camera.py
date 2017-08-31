import logging
import sys
import time
import sklearn.cluster

import cv2
import numpy as np
import itertools
import random
from threading import Thread

from config.config import *
from sensors.pipeline import Pipeline
from utils.functions import overrides, get_class_name, current_time_millis, deprecated
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


class _ReadCameraPipeline(Pipeline):

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
    """ Converts an image to a target colorspace. The input image is assumed to be in BGR. """

    def __init__(self, to='hsv'):
        Pipeline.__init__(self)

        self.__target_colorspace = to

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: BGR-image (np.array)
        :return: image in the target color space (np.array)
        """
        if self.__target_colorspace == "hsv":
            return True, cv2.cvtColor(inp, cv2.COLOR_BGR2HSV)
        elif self.__target_colorspace == "grayscale":
            return True, cv2.cvtColor(inp, cv2.COLOR_BGR2GRAY)
        else:
            logging.warning('Unsupported color space', self.__target_colorspace)
            return False, None


class ColorThresholdPipeline(Pipeline):
    """ Creates a binary image where white pixels are in the given color threshold  """

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
        """
        :param inp: An image (np.array)
        :return: A binary image (np.array)
        """
        colmask = cv2.inRange(inp, self.threshold_lower, self.threshold_upper)
        return True, colmask


class ErodeDilatePipeline(Pipeline):
    """ Applies an erode and dilate filter on an image """

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: an image (np.array)
        :return: the filtered image (np.array)
        """
        x = cv2.erode(inp, None, iterations=2)
        x = cv2.dilate(x, None, iterations=2)
        return True, x


class GetLargestContourPipeline(Pipeline):
    """ Finds the largest contour in the image and returns its bounding box"""

    def __init__(self, min_contour_size=DETECTION_SIZE_THRESHOLD):
        Pipeline.__init__(self)

        self.__min_contour_size = min_contour_size

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: a binary image (np.array)
        :return: a bounding box (tuple (x, y, w, h) )
        """
        _, cnts, _ = cv2.findContours(inp, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            largest_contour = max(cnts, key=cv2.contourArea)

            if cv2.contourArea(largest_contour) > inp.shape[0] * inp.shape[1] * self.__min_contour_size:
                bbox = tuple(cv2.boundingRect(largest_contour))
                return True, bbox

        return False, None


class FastColorDetectionPipeline(Pipeline):
    """ A heuristical color detection approach. Not actually fast. """

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

    def _execute(self, inp):
        height, width = inp.shape

        startt = current_time_millis()
        horizontal_segments = []
        for y in range(0, height, SCANLINE_DISTANCE):
            start = None
            for x in range(0, width):
                if self.__pixel_in_range(inp[y, x]):
                    if start is None:
                        start = x
                elif start is not None and x - start > SCANLINE_DISTANCE:
                    horizontal_segments.append((y, start, x))
                    start = None
        print("HSCAN", current_time_millis() - startt)

        startt = current_time_millis()
        vertical_segments = []
        for x in range(0, width, SCANLINE_DISTANCE):
            start = None
            for y in range(0, height):
                if self.__pixel_in_range(inp[y, x]):
                    if start is None:
                        start = y
                elif start is not None and y - start > SCANLINE_DISTANCE:
                    vertical_segments.append((x, start, y))
                    start = None
        print("VSCAN", current_time_millis() - startt)

        startt = current_time_millis()
        largest_bbox = None
        largest_area = 0
        for (hy, hx1, hx2), (vx, vy1, vy2) in itertools.product(horizontal_segments, vertical_segments):
            if vy1 <= hy <= vy2 and hx1 <= vx <= hx2:
                w, h = hx2 - hx1, vy2 - vy1
                if w*h > largest_area:
                    largest_bbox = (hx1, vy1, w, h)
        print("BBOX", current_time_millis() - startt)

        return largest_bbox is None, largest_bbox

    def __pixel_in_range(self, pixel):
        return pixel > 0
        #return np.all(pixel >= self.threshold_lower) and np.all(pixel <= self.threshold_upper)


class TrackBBOXPipeline(Pipeline):
    """ Tracks an initial bbox over several frames. """
    supported_tracking_algorithms = ['MIL', 'BOOSTING', 'KCF', 'TLC', 'MEDIANFLOW', 'GOTURN']

    def __init__(self, initial_frame, initial_bbox, tracking_algorithm='MIL'):
        Pipeline.__init__(self)

        if tracking_algorithm not in TrackBBOXPipeline.supported_tracking_algorithms:
            raise ValueError('Invalid tracking algorithm', tracking_algorithm)

        self.__tracker = cv2.Tracker_create(tracking_algorithm)
        self.__tracker.init(initial_frame, initial_bbox)

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: an image (np.array)
        :return: the bounding box as it was tracked in the image ( tuple (x, y, w, h) )
        """
        return self.__tracker.update(inp)


class FindYDeviationPipeline(Pipeline):
    """ Finds the deviation of a bounding box on the x-axis"""

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: a bounding box and the image coordinates (tuple)
        :return: the deviation of the bounding box along the x axis (float in [-1, 1])
        """
        (left_x, _, width, _), (_, image_width, _) = inp
        mid_x = image_width / 2
        max_dev = mid_x

        left_x -= mid_x
        dev = (left_x + width/2) / max_dev
        return True, dev


class GetImageDimensionsPipeline(Pipeline):
    """ Returns the dimensions of the image """

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: an image (np.array)
        :return: the dimensions of the image ( tuple (h, w) )
        """
        return True, inp.shape


class EdgeDetectionPipeline(Pipeline):
    """ Applies canny edge detection on an image """

    def __init__(self, threshold_lower=100, threshold_upper=200):
        Pipeline.__init__(self)

        self.threshold_lower = threshold_lower
        self.threshold_upper = threshold_upper

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: an image (np.array)
        :return: an image containing the edges of the input image (np.array)
        """
        return True, cv2.Canny(inp, self.threshold_lower, self.threshold_upper)


class HaarcascadePipeline(Pipeline):
    """ Applies HAAR Cascade detection on an input image """

    def __init__(self, haarfile):
        Pipeline.__init__(self)
        self.detector = cv2.CascadeClassifier(haarfile)

    @overrides(Pipeline)
    def _execute(self, inp):
        """
        :param inp: an image (np.array)
        :return: a list of bounding boxes for the found object (list)
        """
        return True, self.detector.detectMultiScale(inp)


@deprecated
class DBSCANPipeline(Pipeline):

    def __init__(self, eps, min_neighs):
        Pipeline.__init__(self)

        self.__eps = eps
        self.__min_neighs = min_neighs

    @overrides(Pipeline)
    def _execute(self, inp):
        points = []
        height, width = inp.shape
        for y in range(0, height):
            for x in range(0, width):
                points.append(np.array([x, y]))
        points = np.array(points)

        dbscan = sklearn.cluster.DBSCAN(eps=self.__eps, min_samples=self.__min_neighs)
        labels = dbscan.fit_predict(points)

        unique, counts = np.unique(labels, return_counts=True)
        l_max = unique[np.argmax(counts)]

        largest_cluster = [p for i, p in enumerate(points) if labels[i] == l_max]

        min_x = min(largest_cluster, key=lambda p: p[0])
        max_x = min(largest_cluster, key=lambda p: p[0])
        min_y = min(largest_cluster, key=lambda p: p[1])
        max_y = min(largest_cluster, key=lambda p: p[1])

        return True, (min_x, min_y, max_x-min_x, max_y-min_y)


@deprecated
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


class KalmanFilterPipeline(Pipeline):
    """ Applies a Kalman Filter on an input signal"""

    def __init__(self, process_noise=.001, sensor_noise=.4):
        Pipeline.__init__(self)

        self.__state = 0
        self.__error = 1
        self.__process_noise = process_noise
        self.__sensor_noise = sensor_noise
        self.__kalman_gain = 1

    def _execute(self, inp):
        """
        :param inp: a signal (float)
        :return: the filtered signal (float)
        """
        
        # predict
        self.__error = self.__error + self.__process_noise

        # update
        self.__kalman_gain = self.__error / (self.__error + self.__process_noise)
        self.__state = self.__state + self.__kalman_gain * (inp - self.__state)
        self.__error = (1 - self.__kalman_gain) * self.__process_noise

        return True, self.__state


READ_CAMERA_PIPELINE = _ReadCameraPipeline()

