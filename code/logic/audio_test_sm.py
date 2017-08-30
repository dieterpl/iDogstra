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
            lambda _: microphone.read(),
            microphone.fft,
            microphone.freq_value
        )

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        _, _, _, (_, v) = self.pipeline.results
        if v > 5000:
            print("Tone!")
        else:
            print("No Tone!")
        return self

