from logic.statemachine import *
from utils.functions import current_time_millis
from sensors.bluetooth import bluetooth, bluetooth_pipelines
from sensors import pipeline
from sensors.camera import camera, camera_pipelines
from sensors.ultrasonic import ultrasonic_pipelines, ultrasonic
from sensors.infrared import infrared_piplelines, infrared
from motor import robot
import logging
import config
import sys
from scipy.interpolate import interp1d
import numpy

class BTTestSM(StateMachine):

    def __init__(self, testmode="show-image"):
        StateMachine.__init__(self)

        # Bluetooth
        logging.debug("Starting BT-Dongles")
        self.bt_dongles = [bluetooth.BTDongle(i, config.BT_TARGET_UUID)
                           for i in config.BT_DONGLE_IDS]
        for dongle in self.bt_dongles:
            dongle.start()
        self._current_state.first_state = BTTestState()


class BTTestState(State):
    def __init__(self):
        State.__init__(self)

        self.__pipeline = bluetooth_pipelines.user_distance_estimation_pipeline()



    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        print (hist[:1])
        return self
