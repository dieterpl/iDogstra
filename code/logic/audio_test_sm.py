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
        #self._current_state.first_state = PrintFrequencyState()


class CheckFrequencyState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = pipeline.PipelineSequence(
            pipeline.ConjunctiveParallelPipeline(
                *[
                    pipeline.RepeatPipeline(
                        pipeline.PipelineSequence(
                            microphone.ReadMicrophonePipeline(device=d["index"]),
                            microphone.FFTPipeline(),
                            microphone.FilterFrequencyPipeline(freq=AUDIO_FREQ),
                            microphone.SignalStartPipeline(threshold=d["threshold"])
                        )
                    ) for d in AUDIO_DEVICES
                ]),
            microphone.ComputeDeltaTimePipeline()
        )

        # self.__pipeline = pipeline.PipelineSequence(
        #     pipeline.ConjunctiveParallelPipeline(
        #         *[microphone.FindSignalTimePipeline(
        #             device=d["index"], freq=AUDIO_FREQ, threshold=d["threshold"]) for d in AUDIO_DEVICES]
        #     ),
        #     microphone.ComputeDeltaTimePipeline()
        # )

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        #print(self.pipeline.output)
        return self


class PrintFrequencyState(State):

    def __init__(self):
        State.__init__(self)

        self.__pipeline = pipeline.PipelineSequence(
            microphone.ReadMicrophonePipeline(device=0),
            microphone.FFTPipeline(),
            microphone.FilterFrequencyPipeline(freq=AUDIO_FREQ),
        )

    @property
    def pipeline(self):
        return self.__pipeline

    def on_update(self, hist):
        return self

