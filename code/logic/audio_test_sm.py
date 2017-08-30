import cv2
import numpy as np
import sys
import logging
import time

from config.config import *
from logic.statemachine import *
from sensors.audio import microphone


class AudioTestSM(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)

        self._current_state.first_state = CheckFrequencyState()


class CheckFrequencyState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = pipeline.PipelineSequence(
            microphone.ReadMicrophonePipeline(device=4),
            microphone.FFTPipeline(),
            microphone.FilterFrequencyPipeline(freq=14079),
            microphone.SignalStartEndPipeline()
        )

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        sig = self.pipeline.output

        if sig > 0:
            print("Signal started!")
        elif sig < 0:
            print("Signal ended!")

        return self

