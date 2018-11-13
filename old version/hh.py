import pyaudio
import numpy as np

def gensin(frequency, duration, sampRate):

    """ Frequency in Hz, duration in seconds and sampleRate
        in Hz"""

    cycles = np.linspace(0,duration*2*np.pi,num=duration*sampRate)
    wave = np.sin(cycles*frequency,dtype='float16')
    t = np.divide(cycles,2*np.pi)

    return t, wave

frequency=800 #in Hz
duration=10 #in seconds
sampRate=44100 #in Hz

t, sinWav = gensin(frequency,duration,sampRate)

p = pyaudio.PyAudio()

stream = p.open(format = pyaudio.paInt16, 
                channels = 1, 
                rate = sampRate, 
                output = True)

stream.start_stream()

stream.write(sinWav)