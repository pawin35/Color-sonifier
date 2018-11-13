import wx
import cv2

class Camera:
	def __init__(self):
		self.capture = cv2.VideoCapture(0)
		self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
		self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
	
	def GetFrame(self):
		r,f = self.capture.read()
		return f
	

class ShowCapture(wx.Panel):
	def __init__(self, parent, capture, fps=15):
		wx.Panel.__init__(self, parent)

		self.capture = capture
		frame = self.capture.GetFrame()
		self.SetDoubleBuffered(True)
		height, width = frame.shape[:2]
		parent.SetSize((width, height))
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		self.bmp = wx.BitmapFromBuffer(width, height, frame)

		self.timer = wx.Timer(self)
		self.timer.Start(1000./fps)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_TIMER, self.NextFrame)


	def OnPaint(self, evt):
		dc = wx.BufferedPaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0)
	def NextFrame(self, event):
		frame = self.capture.GetFrame()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		self.bmp.CopyFromBuffer(frame)
		self.Refresh()



capture = Camera()
app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()


 
