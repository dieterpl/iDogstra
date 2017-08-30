import os

CAMERA_RESOLUTION = (640, 480)  # the resolution to use for the raspberry pi camera

DETECTION_SIZE_THRESHOLD = .001  # minimum size of a colored object, relative to the total image size

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

# MOVEMENT CONFIG

STATE_SWITCH_COOLDOWN = 1000

SEARCH_SPEED = 40

SEARCH_TIMEOUT = 10000

MAX_TURN_SPEED = 70

# Bluetooth Config

BT_DONGLE_IDS = list(range(2))  # The device ids of the bt dongles to use

# - Configures how the speed is recommended using bluetooth
BT_MIN_SPEED = 20  # Min speed used during speed recommendation
BT_MOVEMENT_RSSI_THRESHOLD = 65  # Min rssi value needed for speed recommendation
BT_MULTIPLIER = 6.0  # Multiplies the recommended speed

# - Configures the distance estimation thresholds
BT_DISTANCE_THRESHOLDS = {
    "far": 80,
    "medium": 60,
    "near": 0
}
# - Misc
BT_TIME_THRESHOLD = 1800  # The time in ms from which bt data is collected

# Ultrasonic Config

US_MAX_VALUE = 300  # Max distance cap

# - Hardware pin config

US_GPIO_TRIGGER = 26

US_GPIO_ECHO = 20