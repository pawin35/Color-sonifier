#Color-sonifier V 0.1 (for chemical laboratory class at Chulalongkorn University)
#Programmed by Pawin Piemthai
#copyrighted 2016 Pawin.P
#This software is under GPL- new general public licence- version 3.0.

from picamera.array import PiRGBArray
from picamera import PiCamera
import pyaudio
import cv2
import numpy as np
import time


class audio:
	def __init__(self):
		self.audio = pyaudio.PyAudio()
		self.rate = 44100
		self.stream = self.audio.open(format=pyaudio.paFloat32,                channels=2,                rate=self.rate,                output=True)
	
	def run(self):
		self.stream.write(self.data)
			#print(self.data)
			#print("stream in")
	
	def stop(self):
		self.stream.close()
		self.audio.terminate()
	
	def get_data(self, data):
		self.data = data
		#print(data)

		
class Sonifier:
	def __init__(self):
		self.camera = PiCamera()
		self.camera.resolution = (640, 480)
		self.camera.framerate = 32
		self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
		time.sleep(0.5)
		self.audio = audio()
		self.rate = 44100
		self.fps = 32
		self.redavg, self.greenavg, self.blueavg = (0,0,0)
		self.xpos, self.ypos = round(640/2), round(480/2)
		#self.ComputeAverage()
		#self.DefineFrame()
		#self.Sonify()
		#time.sleep(0.1)
		#self.audio.start()
	
	def GetFrame(self, frame):
		self.frame = frame
		#print(self.frame[1])
		self.vidhight, self.vidwidth = self.frame.shape[:2]
	
	def ComputeAverage(self, radius=2, tor=3):
		newredavg = round(np.average(self.frame[self.xpos-radius:self.xpos+radius, self.ypos-radius:self.ypos+radius, 2]))
		newgreenavg = round(np.average(self.frame[self.xpos-radius:self.xpos+radius, self.ypos-radius:self.ypos+radius, 1]))
		newblueavg = round(np.average(self.frame[self.xpos-radius:self.xpos+radius, self.ypos-radius:self.ypos+radius, 0]))
		if abs(self.redavg-newredavg) > tor:
			self.redavg = newredavg
		if abs(self.greenavg-newgreenavg) > tor:
			self.greenavg = newgreenavg
		if abs(self.blueavg-newblueavg) > tor:
			self.blueavg = newblueavg
		self.redfreq = (self.redavg/10)*100
		self.greenfreq = (self.greenavg/10)*100
		self.bluefreq = (self.blueavg/10)*100
	
	def GetInfo(self):
		return (self.redavg, self.greenavg, self.blueavg, self.redfreq, self.greenfreq, self.bluefreq)
	
	def DefineFrame(self):
		#print((self.xpos,self.ypos))
		cv2.rectangle(self.frame, (self.xpos-5, self.ypos+5), (self.xpos+5, self.ypos-5), (255,255,0), 3)
	
	def Sonify(self):
		red = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.redfreq/self.rate)).astype(np.float32)
		green = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.greenfreq/self.rate)).astype(np.float32)
		blue = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.bluefreq/self.rate)).astype(np.float32)
		data = np.empty((red.size + blue.size,), dtype=red.dtype)
		data[0::2] = red + green
		data[1::2] = green + blue
		#print("insert data")
		self.audio.get_data(0.3*data)
	
	def GetNext(self):
		#print("get next")
		self.xpos, self.ypos = round(self.vidwidth/2), round(self.vidhight/2)
		self.ComputeAverage()
		self.DefineFrame()
		self.Sonify()
	
	def Destroy(self):
		self.audio.stop()
		self.capture.release()
		
Sonifier = Sonifier()
for frame in Sonifier.camera.capture_continuous(Sonifier.rawCapture, format="bgr", use_video_port=True):
	Sonifier.GetFrame(frame.array)
	Sonifier.GetNext()
	Sonifier.rawCapture.truncate(0)