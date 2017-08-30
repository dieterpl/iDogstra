import os

CAMERA_RESOLUTION = (640, 480)  # the resolution to use for the raspberry pi camera

DETECTION_SIZE_THRESHOLD = .1  # minimum size of a colored object, relative to the total image size

DEBUG_MODE = False  # enable or disable debug mode

GRAPHICAL_OUTPUT = True  # enable or disable graphical output

TRACKING_ALGORITHM = 'TLD'  # algorithm to use for object tracking in images

AUDIO_CHUNK = 2048
AUDIO_FREQ = 15 #14079
AUDIO_RATE = 44100
AUDIO_THRESHOLD = 5000
AUDIO_INPUT_IDXS = [4, 6]

USE_USB_CAMERA = False
# the paths to relevant directories of the project
ROOTPATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, os.path.pardir))
CODEPATH = os.path.join(ROOTPATH, "code")
LOGSPATH = os.path.join(ROOTPATH, 'logs')
DATAPATH = os.path.join(ROOTPATH, "data")
HAARPATH = os.path.join(DATAPATH, "haarcascades")

BT_TARGET_UUID = "6951e12f049945d2930e1fc462c721c8"

BT_DONGLES = []

