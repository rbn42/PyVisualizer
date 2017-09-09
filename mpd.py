#!/usr/bin/python

import sys
import numpy as np
from PySide import QtCore, QtGui
from PySide.QtCore import *
from visualizer import *
app = QtGui.QApplication(sys.argv)


def record_mpd():
    FIFO = '/tmp/mpd.fifo'
    stereo = True
    fps = 25
    # format                  "44100:16:2"
    m_samples = 44100 // fps
    if stereo:
        m_samples *= 2
    f = open(FIFO, 'rb')

    def read_data():
        line = f.read(m_samples)
        data = np.frombuffer(line, 'int16').astype(float)
        return data
    return read_data


read_data = record_mpd()

window = Spectrogram(read_data)
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

import setproctitle
setproctitle.setproctitle("background-visualizer")

while True:
    import os.path
    if os.path.exists('/dev/shm/quit-visualizer'):
        break
    app.processEvents()
import sys
sys.exit()
app.exec_()
