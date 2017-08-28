import os
import time

import cv2
import numpy as np

import utils.functions
# from typing import Tuple
from config.config import *

if os.uname().machine == 'armv7l':  # probably runnig on RaspPi
    import picamera
    import picamera.array
else:
    picamera = None

last_mouse_state = (0, 0)


def test_camera(show=True):
    video = create_video_device()
    print('Starting camera test')
    try:
        while True:
            start = utils.functions.current_time_millis()
            image, _, _ = get_video_frame(video, color_space='hsv')
            if picamera is None:
                show_pixel_value(image)
            if show:
                cv2.imshow('camtest', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            print('Capture time:', utils.functions.current_time_millis() - start)
    finally:
        print('Exiting...')
        video.release()
        cv2.destroyAllWindows()


def test_person_tracking():
    video = create_video_device()
    # detector = cv2.CascadeClassifier('files/haarcascade_lowerbody.xml')
    detector = cv2.HOGDescriptor()
    detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    try:
        while True:
            print('Is there anybody out there?')
            frame, bbox = detect_person(video, detector)
            print('Found somebody! Tracking the person now...')

            tracker = cv2.Tracker_create("MIL")  # Alternatives: BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN
            tracker.init(frame, bbox)  # Initialize tracker with first frame and bounding box
            if track_bbox(video, tracker) == 'q':
                raise KeyboardInterrupt()
            print('Stopping to track...\n')
    finally:
        print('Exiting...')
        video.release()
        cv2.destroyAllWindows()


def detect_person(video, detector):
    avg_time = None

    while True:
        image, gray = get_video_frame(video, True)

        cv2.imshow('camtest', image)  # Display result
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # persons = detector.detectMultiScale(gray)
        start = utils.functions.current_time_millis()
        persons, _ = detector.detectMultiScale(image)
        delta = utils.functions.current_time_millis() - start
        avg_time = delta if avg_time is None else (avg_time + delta) / 2

        if len(persons) > 0:
            bbox = tuple(persons[0])  # just track the first person found
            print('Average detection time: {}ms'.format(avg_time))
            return image, bbox


def track_bbox(video, tracker, show=True):
    avg_time = None
    while True:
        image, _, _ = get_video_frame(video, with_gray=False, return_original=False)

        start = utils.functions.current_time_millis()
        ok, bbox = tracker.update(image)
        delta = utils.functions.current_time_millis() - start
        avg_time = delta if avg_time is None else (avg_time + delta) / 2

        if ok:  # Draw bounding box
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            if show:
                cv2.rectangle(image, p1, p2, (0, 0, 255))

        if show:
            cv2.imshow('camtest', image)  # Display result
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                print('Average tracking time: {}ms'.format(avg_time))
                return 'q'
            elif key & 0xFF == ord('r'):
                print('Average tracking time: {}ms'.format(avg_time))
                return 'r'


def test_color_detection(obj='orange paper', show=True):
    video = create_video_device()

    while True:
        print('Trying to find an object')
        frame, bbox = detect_object_by_color(video, obj, show)
        print('Found something! Tracking the object now...')

        tracker = cv2.Tracker_create("MIL")  # Alternatives: BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN
        tracker.init(frame, bbox)  # Initialize tracker with first frame and bounding box
        if track_bbox(video, tracker) == 'q':
            raise KeyboardInterrupt()
        print('Stopping to track...\n')


def detect_object_by_color(video, obj='banana', show=True):
    print('Detecting', obj)
    if obj == 'apple':
        lower = np.array([0, 50, 50])
        upper = np.array([10, 255, 255])
    elif obj == 'banana':
        lower = np.array([30, 50, 50])
        upper = np.array([70, 255, 255])
    elif obj == 'orange paper':
        lower = np.array([15, 50, 50])
        upper = np.array([25, 255, 255])
    else:
        print('Unkown object', obj)
        return

    while True:
        hsv_img, _, orig_img = get_video_frame(video, color_space='hsv', return_original=True)

        colmask = cv2.inRange(hsv_img, lower, upper)
        colmask = cv2.erode(colmask, None, iterations=2)
        colmask = cv2.dilate(colmask, None, iterations=2)

        image, cnts, hierachy = cv2.findContours(colmask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            largest_contour = max(cnts, key=cv2.contourArea)
            #rect = cv2.minAreaRect(largest_contour)
            #print(rect)
            #bbox = np.int32(cv2.boxPoints(rect))
            bbox = cv2.boundingRect(largest_contour)
            bbox = tuple(bbox)
            print(bbox)

            if show:
                #cv2.polylines(hsv_img, bbox, True, (0, 0, 255))
                cv2.imshow('camtest', orig_img)
                cv2.imshow('color mask', colmask)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    break

            if cv2.contourArea(largest_contour) > DETECTION_SIZE_THRESHOLD:
                print('Found contour of size', cv2.contourArea(largest_contour))
                return orig_img, bbox


def show_pixel_value(image):
    x, y = last_mouse_state
    height, width, _ = image.shape

    text = ''
    if 0 <= x < width and 0 <= y < height:
        text = str(image[y, x])

    cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 0, 0])
    cv2.putText(image, 'x={}|y={}'.format(x, y), (0, height-5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, .6, [0, 255, 0])


def mouse_callback(event, x, y, flag, *args):
    global last_mouse_state
    last_mouse_state = (x, y)


def get_video_frame(video, with_gray=False, color_space='bgr', return_original=False):
    if picamera is None:
        ok, orig_frame = video.read()
    else:
        start = utils.functions.current_time_millis()
        array = picamera.array.PiRGBArray(video, size=PYCAMERA_RESOLUTION)
        print('  Time to allocate the array', utils.functions.current_time_millis() - start)

        start = utils.functions.current_time_millis()
        video.capture(array, format='bgr', resize=PYCAMERA_RESOLUTION, use_video_port=True)
        ok, orig_frame = True, array.array
        print('  Time to do the capture:', utils.functions.current_time_millis() - start)

    # use the given color space
    start = utils.functions.current_time_millis()
    if color_space == 'hsv':
        result_frame = cv2.cvtColor(orig_frame, cv2.COLOR_BGR2HSV)
    else:
        result_frame = orig_frame
    print('  Time to convert the color space:', utils.functions.current_time_millis() - start)

    if not ok:
        raise IOError('Could not read from device')
    return result_frame, \
        None if not with_gray else cv2.cvtColor(result_frame, cv2.COLOR_BGR2GRAY), \
        orig_frame if return_original else None


def create_video_device():
    if picamera is None:
        return cv2.VideoCapture(0)
    else:
        camera = picamera.PiCamera()
        #camera.resolution = PYCAMERA_RESOLUTION
        camera.framerate = 32
        time.sleep(2)
        return camera


if __name__ == '__main__':
    window = cv2.namedWindow('camtest')
    cv2.setMouseCallback('camtest', mouse_callback)

    test_camera(True)
    # test_person_tracking()
    # test_color_detection('orange paper', show=True)
