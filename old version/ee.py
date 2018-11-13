import sys
import cv2
import time
import wx
import numpy as np

class Video(object):
    def __init__(self, camera_br = 0):
        self.camera = cv2.VideoCapture(camera_br)        
        self.width = int(round(self.camera.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))
        self.height = int(round(self.camera.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
        self.camera_br=camera_br

    def read(self):
        status, img = self.camera.read()         
        if not status:
            img = np.zeros((self.Height,self.Width,3), np.uint8)
            img[::] = (0,0,0)            
        return img

    @property
    def Width(self):
        return self.width

    @property
    def Height(self):
        return self.height

    @property
    def NumCam(self):
        return self.camera_br

class VideoFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        panel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        panel1= wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.videoPanel = panel

        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        sizer.Add(panel1, 0, wx.EXPAND)
        sizer.Add(self.videoPanel, 1, wx.EXPAND)       
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        
        self.SetDoubleBuffered(True)

        panel1.Layout()        
        
        self.video=Video(0)
        self.get_frame(self.video)        

        self.playTimer = wx.Timer(self)        
        
        self.Bind(wx.EVT_TIMER, self.onOpenVideo, self.playTimer)        
        self.videoPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)              
        self.videoPanel.Bind(wx.EVT_PAINT, self.onPaint)
        
        self.playTimer.Start(1000 / 15)
        
        self.Show(True)

    def onOpenVideo(self,evt):                
        self.get_frame(self.video)

    def updateVideo(self, status, frame):
        if status:
                
            self.imgVideo = np.copy(frame)

            height, width = self.imgVideo.shape[:2]

            displayWidth, displayHeight = self.videoPanel.GetSize()

            aspectRatio = height * 1.0 / width

            areaWidth = displayWidth * int(round(displayWidth * aspectRatio))
            areaHeight = displayHeight * int(round(displayHeight / aspectRatio))

            if (areaWidth >= areaHeight):
                if (int(round(displayWidth * aspectRatio)) <= displayHeight):
                    resizeWidth = displayWidth
                    resizeHeight = int(round(displayWidth * aspectRatio))
                else:
                    resizeHeight = displayHeight
                    resizeWidth = int(round(displayHeight / aspectRatio))
            else:
                if (int(round(displayHeight / aspectRatio)) <= displayWidth):
                    resizeHeight = displayHeight
                    resizeWidth = int(round(displayHeight / aspectRatio))
                else:
                    resizeWidth = displayWidth
                    resizeHeight = int(round(displayWidth * aspectRatio))

            
            self.imgWorking = cv2.resize(self.imgVideo, (resizeWidth, resizeHeight))
            
            
            self.imgWorking = cv2.cvtColor(self.imgWorking, cv2.COLOR_BGR2RGB)

            height, width = self.imgWorking.shape[:2]

            self.bmpVideo = wx.BitmapFromBuffer(width, height, self.imgWorking.tostring())

            self.Refresh()

    def onPaint(self, evt):
        if self.bmpVideo != None:
            dc = wx.BufferedPaintDC(self.videoPanel)
            dc.Clear()
            dc.DrawBitmap(self.bmpVideo,0,0)
        else:
            pass        
