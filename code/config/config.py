import os

CAMERA_RESOLUTION = (640, 480)  # the resolution to use for the raspberry pi camera

DETECTION_SIZE_THRESHOLD = .1  # minimum size of a colored object, relative to the total image size

DEBUG_MODE = True  # enable or disable debug mode

GRAPHICAL_OUTPUT = True  # enable or disable graphical output

TRACKING_ALGORITHM = 'TLD'  # algorithm to use for object tracking in images

USE_USB_CAMERA = False
# the paths to relevant directories of the project
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, os.path.pardir))
CODEPATH = os.path.join(ROOT_PATH, "code")
LOGSPATH = os.path.join(ROOT_PATH, 'logs')
DATAPATH = os.path.join(ROOT_PATH, "data")
HAARPATH = os.path.join(DATAPATH, "haarcascades")

BT_TARGET_UUID = "6951e12f049945d2930e1fc462c721c8"

BT_DONGLES = []

