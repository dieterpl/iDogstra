import os

CAMERA_RESOLUTION = (640, 480)  # the resolution to use for the raspberry pi camera
SCANLINE_DISTANCE = 5

DETECTION_SIZE_THRESHOLD = .001  # minimum size of a colored object, relative to the total image size

DEBUG_MODE = False  # enable or disable debug mode

GRAPHICAL_OUTPUT = True  # enable or disable graphical output

TRACKING_ALGORITHM = 'TLD'  # algorithm to use for object tracking in images

USE_TRUE_PARALLEL_PIPELINES = True  # use multithreading in parallel pipelines

USE_USB_CAMERA = False
# the paths to relevant directories of the project
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, os.path.pardir))
CODEPATH = os.path.join(ROOT_PATH, "code")
LOGSPATH = os.path.join(ROOT_PATH, 'logs')
DATAPATH = os.path.join(ROOT_PATH, "data")
PICTUREPATH = os.path.join(ROOT_PATH, "assets", "gestures")
SOUNDPATH = os.path.join(ROOT_PATH, "assets", "sounds")
HAARPATH = os.path.join(DATAPATH, "haarcascades")

# MOVEMENT CONFIG

STATE_SWITCH_COOLDOWN = 1000

SEARCH_SPEED = 30

SEARCH_TIMEOUT = 15000

MAX_TURN_SPEED = 30

MIN_TURN_SPEED = 15

MAX_IR_DISTANCE = 60

FORWARD_SPEED_MULT = 1.0

# Bluetooth Config

BT_TARGET_UUID = "6951e12f049945d2930e1fc462c721c8"  # The uuid of the bt beacon
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

IF_US_START_DELAY = 1000

# Ultrasonic Config

US_MAX_VALUE = 300  # Max distance cap

US_TIME_THRESHOLD = 500

US_DISTANCE_THRESHOLD = 75

US_DATA_ACC_THRESHOLD = 1000

# - Hardware pin config

US_GPIO_TRIGGER = 26

US_GPIO_ECHO = 20


# InfraRed

IR_TIME_THRESHOLD = 500

IR_DISTANCE_THRESHOLD = 20

IR_DATA_ACC_THRESHOLD = 1000
