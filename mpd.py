#!/usr/bin/python

import sys
import numpy as np
from PySide import QtCore, QtGui
from PySide.QtCore import *
from visualizer import *


app = QtGui.QApplication(sys.argv)
window = Spectrogram(None)
window.setAttribute(Qt.WA_TranslucentBackground)
window.setWindowFlags(Qt.FramelessWindowHint)
window.show()
from Xlib import X, display, Xutil, protocol
disp = display.Display()
winid = window.winId()
window_xlib = disp.create_resource_object('window', winid)
window_xlib.set_wm_class('qmlterm_background', 'qmlterm_background')
disp.flush()
disp.close()
#import setproctitle
#setproctitle.setproctitle("background-visualizer")


FIFO = '/tmp/mpd.fifo'
stereo = True
fps = 25
m_samples = 44100 // fps
if stereo:
    m_samples *= 2
f = open(FIFO, 'rb')

import os.path
import time
while True:
    time.sleep(1/fps)
    if os.path.exists('/dev/shm/quit-visualizer'):
        break
    line = f.read(m_samples)
    f.flush()
    data = np.frombuffer(line, 'int16').astype(float)
    if data is not None:
        window.refresh(data)
    app.processEvents()
