import pyaudio, time
import math, sys, struct, random,argparse
import numpy as np
from itertools import *
def sine_wave(frequency=440.0, framerate=44100, amplitude=0.5):
    if amplitude > 1.0: amplitude = 1.0
    if amplitude < 0.0: amplitude = 0.0
    yield (float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i)/float(framerate))) for i in count(0))
p = pyaudio.PyAudio()
volume = 0.5
duration = 2
fs = 16000
f = 440.0

def callback(in_data, frame_count, time_info, status):
	data = (np.sin(2*np.pi*np.arange(frame_count)*f/fs)).astype(np.float32)
	return (data, pyaudio.paContinue)

stream = p.open(format=pyaudio.paFloat32,                channels=1,                rate=fs,                output=True, frames_per_buffer = 44100,stream_callback=callback)


stream.start_stream()
#while f <= 1000:
	#left = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
	#right = (np.sin(2*np.pi*np.arange(fs*duration)*(f-200)/fs)).astype(np.float32)
	#mid= (np.sin(2*np.pi*np.arange(fs*duration)*(f+400)/fs)).astype(np.float32)
	#samples = np.empty((left.size + right.size,), dtype=left.dtype)
	#samples[0::2] = left+mid
	#samples[1::2] = mid+right
	#f = f+10
	#stream.write(0.3*samples)
time.sleep(5)
stream.stop_stream()

stream.close()

p.terminate()


