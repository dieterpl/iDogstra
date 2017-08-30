import numpy as np
import pyaudio
import wave

from config.config import *


_device = pyaudio.PyAudio()
_stream = _device.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=AUDIO_CHUNK)


def read(window=np.blackman(AUDIO_CHUNK)):
    data = _stream.read(AUDIO_CHUNK)

    # unpack the data and times by the hamming window
    return np.array(wave.struct.unpack("%dh" % AUDIO_CHUNK, data)) * window


def fft(data):
    w = abs(np.fft.rfft(data))
    freqs = [abs(f * 44100) for f in np.fft.fftfreq(len(data))]

    z = list(zip(w, freqs))
    z.sort(key=lambda i: i[1])
    return z


def freq_value(inp, freq=AUDIO_FREQ):
    prevfreq = -1
    for val, f in inp:
        if prevfreq <= freq <= f:
            return val
        prevfreq = f
    return None



