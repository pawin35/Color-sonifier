#Color-sonifier V 0.1 (for chemical laboratory class at Chulalongkorn University)
#Programmed by Pawin Piemthai
#copyrighted 2016 Pawin.P
#This software is under GPL- new general public licence- version 3.0.

import wx
import pyaudio
import cv2
import numpy as np
import time
from threading import Thread,Event

class ShowCapture (wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		parent.SetSize((1920, 1080))
		self.bmpVideo = wx.BitmapFromBuffer(1920, 1080, np.zeros((1080,1920,3)))
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		
	def OnPaint(self, event):
		print("On Paint")
		dc = wx.BufferedPaintDC(self)
		dc.DrawBitmap(self.bmpVideo, 0, 0)
		
	
	def NextFrame(self, frame):
		print("Next frame")
		print(frame[0])
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		self.bmpVideo.CopyFromBuffer(frame)
		self.Refresh()




class audio(Thread):
	def __init__(self):
		Thread.__init__(self)
		self._stop = Event()
		self.audio = pyaudio.PyAudio()
		self.rate = 44100
		self.stream = self.audio.open(format=pyaudio.paFloat32,                channels=2,                rate=self.rate,                output=True)
	
	def run(self):
		self._stop.clear()
		while not self._stop.is_set():
			self.stream.write(self.data)
			#print(self.data)
			#print("stream in")
	
	def stop(self):
		self._stop.set()
		self.stream.close()
		self.audio.terminate()
	
	def get_data(self, data):
		self.data = data
		#print(data)

		
class Sonifier:
	def __init__(self):
		self.capture = cv2.VideoCapture(0)
		self.audio = audio()
		self.rate = 44100
		self.fps = 25
		self.redavg, self.greenavg, self.blueavg = (0,0,0)
		self.GetFrame()
		self.ypos, self.xpos = round(self.vidwidth/2), round(self.vidhight/2)
		self.ComputeAverage()
		self.DefineFrame()
		self.Sonify()
		#time.sleep(0.1)
		self.audio.start()
	
	def GetFrame(self):
		ret, self.frame = self.capture.read()
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
		cv2.rectangle(self.frame, (self.xpos-5, self.ypos+5), (self.xpos+5, self.ypos-5), (255,255,0), 3)
	
	def Sonify(self):
		red = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.redfreq/self.rate)).astype(np.float32)
		green = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.greenfreq/self.rate)).astype(np.float32)
		blue = (np.sin(2*np.pi*np.arange(self.rate*(1/self.fps))*self.bluefreq/self.rate)).astype(np.float32)
		data = np.empty((red.size + blue.size,), dtype=red.dtype)
		data[0::2] = red + green
		data[1::2] = green + blue
		#print("insert data")
		self.audio.get_data(0*data)
	
	def GetNext(self):
		#print("get next")
		self.GetFrame()
		self.xpos, self.ypos = round(self.vidwidth/2), round(self.vidhight/2)
		self.ComputeAverage()
		self.DefineFrame()
		self.Sonify()
	
	def Destroy(self):
		self.audio.stop()
		self.capture.release()
		
		
class MainApp (wx.Frame):
	def __init__(self,parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		self.parent = parent
		self.initialize()
	
	def initialize(self):
		self.Sonifier = Sonifier()
		self.CreateUi()
		self.Maximize()
		self.Show(True)
		
	def CreateUi(self):
		panel = wx.Panel(self)
		sizer = wx.GridBagSizer(4, 4)
		
		#self.videoPanel = ShowCapture(self)
		self.imgVideo = wx.StaticBitmap(panel)
		text_lr = wx.StaticText(panel, label="Average red:")
		text_lg = wx.StaticText(panel, label="Average green:")
		text_lb = wx.StaticText(panel, label="Average blue:")
		text_fr = wx.StaticText(panel, label="Frequency red:")
		text_fg = wx.StaticText(panel, label="Frequency green:")
		text_fb = wx.StaticText(panel, label="Frequency blue:")
		button_selectcam = wx.Button(panel, label="Select Camera")
		button_setting = wx.Button(panel, label="Setting")
		button_quit = wx.Button(panel, label="Quit")
		self.st_r = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
		self.st_g = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
		self.st_b = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
		self.st_fr = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
		self.st_fg = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
		self.st_fb = wx.TextCtrl(panel, value="0", style=wx.TE_READONLY)
#		sizer.Add(self.videoPanel, pos=(0, 0),span=(5,5))
		#sizer.Add(self.imgVideo, pos=(0, 0),span=(5,5))
		sizer.Add(self.st_r, pos=(5, 1))
		sizer.Add(self.st_g, pos=(6, 1))
		sizer.Add(self.st_b, pos=(7, 1))
		sizer.Add(self.st_fr, pos=(5, 4))
		sizer.Add(self.st_fg, pos=(6, 4))
		sizer.Add(self.st_fb, pos=(7, 4))
		sizer.Add(text_lr, pos=(5, 0))
		sizer.Add(text_lg, pos=(6, 0))
		sizer.Add(text_lb, pos=(7, 0))
		sizer.Add(text_fr, pos=(5, 3))
		sizer.Add(text_fg, pos=(6, 3))
		sizer.Add(text_fb, pos=(7, 3))
		sizer.Add(button_selectcam, pos=(5, 2))
		sizer.Add(button_setting, pos=(6, 2))
		sizer.Add(button_quit, pos=(7, 2))
		
		
		self.Bind(wx.EVT_BUTTON, self.SelectCam, button_selectcam)
		self.Bind(wx.EVT_BUTTON, self.Setting, button_setting)
		self.Bind(wx.EVT_BUTTON, self.Quit, button_quit)
		self.timer = wx.Timer(self, wx.ID_ANY)
		self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)
		self.timer.Start(40)

		panel.SetSizerAndFit(sizer)
	
	def SelectCam(self, event):
		pass
		
	def Setting(self, event):
		pass
	
	def Quit(self, event):
		self.Destroy()
		self.timer.Stop()
		self.Sonifier.Destroy()
	
	def OnUpdate(self, event):
		self.Sonifier.GetNext()
		redavg, greenavg, blueavg, redfreq, greenfreq, bluefreq = self.Sonifier.GetInfo()
		self.st_r.SetValue(str(redavg))
		self.st_g.SetValue(str(greenavg))
		self.st_b.SetValue(str(blueavg))
		self.st_fr.SetValue(str(redfreq))
		self.st_fg.SetValue(str(greenfreq))
		self.st_fb.SetValue(str(bluefreq))
		#self.videoPanel.NextFrame(self.Sonifier.frame)
		frame = self.Sonifier.frame
		hight, width = frame.shape[:2]
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frombuf = wx.BitmapFromBuffer(width, height, frame)
		self.imgVideo.SetBitmap(frombuf)

		
			
		
			

		
		

		
		
		

if __name__ == "__main__":
	app = wx.App()
	frame = MainApp(None, -1, "Color Sonifier V 0.1")
	#Video = ShowCapture(frame)
	app.MainLoop()