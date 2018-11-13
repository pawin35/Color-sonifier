import time
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
				freq_change_factor = (freq-self.frequency)/20
			if vol == None:
				vol_change_factor = 0
			else:
				vol_change_factor = (vol-self.volume)/20
			for i in range(1,20):
				self.set_frequency(self.frequency+(i*freq_change_factor))
				self.sound.set_volume(self.volume+(i*vol_change_factor))
				pygame.time.delay(200)
		else:
			return
		if freq != None:
			self.set_frequency(freq)
			self.frequency = freq
		if vol != None:
			self.sound.set_volume(vol)
			self.volume = vol

	def set_frequency(self,freq):
		for s in range(self.n_samples):
			t = float(s)/self.sample_rate
			self.sam[s] = round(self.max_sample*math.sin(2*math.pi*freq*t))

s = sonifier()
s.play()