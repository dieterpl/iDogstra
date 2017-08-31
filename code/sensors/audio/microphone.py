import numpy as np
import pyaudio
import wave
from sensors.pipeline import Pipeline
from utils.functions import overrides, current_time_micros

from config.config import *
from threading import Thread

_pyaudio = pyaudio.PyAudio()


class ReadMicrophonePipeline(Pipeline):

    def __init__(self, device, window=np.blackman(AUDIO_CHUNK)):
        Pipeline.__init__(self)

        self.stream = _pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                    input=True, frames_per_buffer=AUDIO_CHUNK, input_device_index=device)
        self.window = window

        self.__last_frame = None
        #Thread(target=self.__read).run()

    def __read(self):
        while True:
            data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
            self.__last_frame = np.array(wave.struct.unpack("%dh" % AUDIO_CHUNK, data)) * self.window

    @overrides(Pipeline)
    def _execute(self, _):
        data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
        self.__last_frame = np.array(wave.struct.unpack("%dh" % AUDIO_CHUNK, data)) * self.window
        return self.__last_frame is None, self.__last_frame


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
        for i, (val, f) in enumerate(inp):
            if prevfreq <= self.__freq <= f:
                print(val)
                return True, val

        return False, None


class FindSignalTimePipeline(Pipeline):

    def __init__(self, device, freq, threshold):
        Pipeline.__init__(self)

        self.freq = freq
        self.threshold = threshold
        self.stream = _pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                    input=True, frames_per_buffer=AUDIO_CHUNK, input_device_index=device)

    @overrides(Pipeline)
    def _execute(self, _):
        window = np.blackman(AUDIO_CHUNK)

        while True:
            time = current_time_micros()
            data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
            data = np.array(wave.struct.unpack("%dh" % AUDIO_CHUNK, data)) * window

            w = abs(np.fft.rfft(data))
            freqs = [abs(f * AUDIO_RATE) for f in np.fft.fftfreq(len(data))]

            z = list(zip(w, freqs))
            z.sort(key=lambda f: f[1])

            prevfreq = -1
            for i, (val, f) in enumerate(z):
                if prevfreq <= self.freq <= f:
                    freqval = val
            print(freqval)
            if freqval > self.threshold:
                return True, time


class SignalStartPipeline(Pipeline):

    def __init__(self, threshold):
        Pipeline.__init__(self)

        self.__threshold = threshold
        self.__prev_found = False

    @overrides(Pipeline)
    def _execute(self, inp):
        if inp >= self.__threshold and not self.__prev_found:
            self.__prev_found = True
            return True, True
        else:
            self.__prev_found = inp >= self.__threshold
            return True, False


class ComputeDeltaTimePipeline(Pipeline):

    def __init__(self):
        Pipeline.__init__(self)

    @overrides(Pipeline)
    def _execute(self, inp):
        t1, t2 = inp
        return True, t1 - t2




