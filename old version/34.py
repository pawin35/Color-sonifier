from picamera.array import PiRGBArray
from picamera import PiCamera
from pygame.locals import *
import cv2, time
import pygame
import math
import numpy

class sonifier:
	def __init__(self):
		self.size = (1280, 720)
		self.bits = 16
		pygame.mixer.pre_init(22050, -self.bits, 1)
		pygame.init()
		self._display_surf = pygame.display.set_mode(self.size)#, pygame.HWSURFACE | pygame.DOUBLEBUF)
		self.duration = 0.1
		self.sample_rate = 22050
		self.n_samples = int(round(self.duration*self.sample_rate))
		self.frequency = 0
		self.volume = 0.5
		self.buf = numpy.zeros(self.n_samples, dtype = numpy.int16)
		self.max_sample = 2**(self.bits - 1) - 1
		self.sound = pygame.sndarray.make_sound(self.buf)
		self.sam = pygame.sndarray.samples(self.sound)
		self.table = [math.sin(i/100) for i in range(0,629)]
		self.table[157] = 1.0
		self.table[314] = 0
		self.table[471] = -1.0
		self.table[628] = 0

	def play(self):
		self.sound.play(-1)

	def stop(self):
		self.sound.stop()

	def change_freq(self, freq=None, vol=None):
		if freq != self.frequency or vol != self.volume:
			if freq == None:
				freq_change_factor = 0
			else:
				freq_change_factor = (freq-self.frequency)/30
			if vol == None:
				vol_change_factor = 0
			else:
				vol_change_factor = (vol-self.volume)/30
			for i in range(1,30):
				self.set_frequency(self.frequency+(i*freq_change_factor))
				self.sound.set_volume(self.volume+(i*vol_change_factor))
				#pygame.time.delay(1)
		else:
			return
		if freq != None:
			self.set_frequency(freq)
			self.frequency = freq
		if vol != None:
			self.sound.set_volume(vol)
			self.volume = vol

	def set_frequency(self,freq):
		delta = int(round(((2*math.pi*freq*(1/self.sample_rate)) % (2*math.pi))*100))
		phase_accumulator = 0
		pre_compute = []
		s = 1
		while (True):
			pre_compute.append(round(self.max_sample*self.table[phase_accumulator]))
			phase_accumulator += delta
			if phase_accumulator >= 628:
				phase_accumulator %= 628
			s += 1
			if phase_accumulator == 0 or phase_accumulator == 1:
				self.buf = numpy.array(pre_compute, dtype=numpy.int16)
				self.sound.stop()
				self.sound = pygame.sndarray.make_sound(self.buf)
				self.sound.play(-1)
				break


s = sonifier()
s.play()
camera = PiCamera()
camera.exposure_mode = 'auto'
camera.awb_mode = 'auto'
camera.resolution = (640, 480)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)
prior_h = 0
prior_s = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	h_avg = numpy.average(hsv[220:260, 300:340, 0])
	s_avg = numpy.average(hsv[220:260, 300:340, 1])
	freq = 100+(abs(h_avg-90)*10)
	vol = 0.2 + ((s_avg/255)*0.8)
	if abs(prior_h - h_avg) > 1 and abs(prior_s - s_avg) > 5:
		s.change_freq(freq=freq, vol=vol)
		prior_h = h_avg
		prior_s = s_avg
	elif abs(prior_h - h_avg) > 1 and abs(prior_s - s_avg) <= 5:
		s.change_freq(freq=freq)
		prior_h = h_avg
	elif abs(prior_h - h_avg) <= 1 and abs(prior_s - s_avg) > 5:
		s.change_freq(vol=vol)
		prior_s = s_avg
	else:
		pass
	v_avg = numpy.average(hsv[220:260, 300:340, 2])
	rawCapture.truncate(0)