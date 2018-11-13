from picamera.array import PiRGBArray
from picamera import PiCamera
from pyo import *
import cv2, time
import math
import numpy

class sonifier:
	def __init__(self):
		self.s = Server(duplex=0).boot()
		self.frequency = 0
		self.volume = 1
		self.a = Sine(freq=self.frequency, mul=self.volume).out()

	def play(self):
		self.s.start()

	def stop(self):
		self.s.stop()

	def change_freq(self, freq=None, vol=None):
		if freq != self.frequency or vol != self.volume:
			if freq == None:
				freq_change_factor = 0
			else:
				freq_change_factor = (freq-self.frequency)/80
			if vol == None:
				vol_change_factor = 0
			else:
				vol_change_factor = (vol-self.volume)/80
			for i in range(1,80):
				self.set_frequency(self.frequency+(i*freq_change_factor))
				self.set_volume(self.volume+(i*vol_change_factor))
				time.sleep(0.001)
		else:
			return
		if freq != None:
			self.set_frequency(freq)
			self.frequency = freq
		if vol != None:
			self.set_volume(vol)
			self.volume = vol

	def set_frequency(self,freq):
		self.a.setFreq(freq)

	def set_volume(self,vol):
		self.a.mul = vol
		print(self.a.mul)






s = sonifier()
s.play()
camera = PiCamera()
camera.exposure_mode = 'auto'
camera.awb_mode = 'auto'
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera)
time.sleep(0.5)
prior_h = 0
prior_s = 0
while(True):
	camera.capture(rawCapture, format="bgr")
	image = rawCapture.array
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	h_avg = numpy.average(hsv[220:260, 300:340, 0])
	s_avg = numpy.average(hsv[220:260, 300:340, 1])
	freq = 100+(abs(h_avg-90)*10)
	vol = 0.1 + ((s_avg/255)*0.8)
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