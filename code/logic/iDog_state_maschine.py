import cv2

from config.config import *

from motor import movement
from sensors.bluetooth.bluetooth import BTDongle
from sensors.camera import camera
from sensors.pipeline import create_parallel_pipeline, create_sequential_pipeline
from logic.statemachine import *
from logic.states import *




class IDog(StateMachine):


    def __init__(self):
        StateMachine.__init__(self)
        self._current_state.first_state = SearchState()





