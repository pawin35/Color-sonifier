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
		self.table = [math.sin(i/1000) for i in range(0,6284)]
		self.table[1571] = 1.0
		self.table[3142] = 0
		self.table[4712] = -1.0
		self.table[6283] = 0

	def play(self):
		self.sound.play(-1)

	def stop(self):
		self.sound.stop()

	def change_freq(self, freq=None, vol=None):
		if freq != self.frequency or vol != self.volume:
			if freq == None:
				freq_change_factor = 0
			else:
				freq_change_factor = (freq-self.frequency)/50
			if vol == None:
				vol_change_factor = 0
			else:
				vol_change_factor = (vol-self.volume)/50
			for i in range(1,50):
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
		delta = round(((2*math.pi*freq*(1/self.sample_rate)) % (2*math.pi))*1000)
		phase_accumulator = 0
		pre_compute = []
		s = 1
		while (True):
			pre_compute.append(round(self.max_sample*self.table[phase_accumulator]))
			phase_accumulator += delta
			if phase_accumulator >= 6283:
				phase_accumulator %= 6283
			s += 1
			if phase_accumulator == 0 or phase_accumulator == 1:
				self.buf = numpy.array(pre_compute, dtype=numpy.int16)
				self.sound.stop()
				self.sound = pygame.sndarray.make_sound(self.buf)
				self.sound.play(-1)
				break


s = sonifier()
s.play()