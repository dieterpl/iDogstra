import numpy as np
import pyaudio
import wave
from sensors.pipeline import Pipeline
from utils.functions import overrides

from config.config import *


_pyaudio = pyaudio.PyAudio()


class ReadMicrophonePipeline(Pipeline):

    def __init__(self, device, window=np.blackman(AUDIO_CHUNK)):
        Pipeline.__init__(self)

        self.stream = _pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                    input=True, frames_per_buffer=AUDIO_CHUNK, input_device_index=device)
        self.window = window

    @overrides(Pipeline)
    def _execute(self, _):
        data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
        return True, np.array(wave.struct.unpack("%dh" % AUDIO_CHUNK, data)) * self.window


class FFTPipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

    def _execute(self, inp):
        w = abs(np.fft.rfft(inp))
        freqs = [abs(f * AUDIO_RATE) for f in np.fft.fftfreq(len(inp))]

        z = list(zip(w, freqs))
        z.sort(key=lambda i: i[1])
        return True, z


class FilterFrequencyPipeline(Pipeline):

    def __init__(self, freq):
        Pipeline.__init__(self)

        self.__freq = freq

    def _execute(self, inp):
        prevfreq = -1
        for val, f in inp:
            if prevfreq <= self.__freq <= f:
                return True, val

        return False, None


class SignalStartEndPipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

        self.__prev_found = False

    def _execute(self, inp):
        if inp >= AUDIO_THRESHOLD:
            out = 1 if not self.__prev_found else 0
            self.__prev_found = True
            return True, out
        else:
            out = -1 if self.__prev_found else 0
            self.__prev_found = False
            return True, out




