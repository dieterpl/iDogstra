import os

CAMERA_RESOLUTION = (640, 480)  # the resolution to use for the raspberry pi camera

DETECTION_SIZE_THRESHOLD = .01  # minimum size of a colored object, relative to the total image size

DEBUG_MODE = True  # enable or disable debug mode

TRACKING_ALGORITHM = 'MIL'  # algorithm to use for object tracking in images

USE_USB_CAMERA = True

# the paths to relevant directories of the project
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
LOGSPATH = os.path.join(ROOT_PATH, 'logs')

BT_TARGET_UUID = "6951e12f049945d2930e1fc462c721c8"

BT_DONGLES = []