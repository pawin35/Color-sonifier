from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2, time
import pygame
from pygame.locals import *
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

	def play(self):
		self.sound.play(-1)

	def stop(self):
		self.sound.stop()

	def change_freq(self, freq=None, vol=None):
		if freq != self.frequency or vol != self.volume:
			if freq == None:
				freq_change_factor = 0
			else:
				freq_change_factor = (freq-self.frequency)/15
			if vol == None:
				vol_change_factor = 0
			else:
				vol_change_factor = (vol-self.frequency)/15
			for i in range(1,15):
				self.set_frequency(freq=self.frequency+(i*freq_change_factor), vol=self.volume+(i*vol_change_factor))
				pygame.time.delay(2)
			self.set_frequency(freq=freq, vol=vol)
		else:
			return
		if freq != None:
			self.frequency = freq
		if vol != None:
			self.volume = vol

	def set_frequency(self,freq=None, vol=None):
		if freq == None and vol == None:
			return
		if freq == None:
			freq = self.frequency
		if vol == None:
			vol = self.volume
		for s in range(self.n_samples):
			t = float(s)/self.sample_rate
			self.sam[s] = round(self.max_sample*vol*math.sin(2*math.pi*freq*t))

s = sonifier()
s.play()


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)