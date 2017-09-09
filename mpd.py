#!/usr/bin/python
import sys
import numpy as np
from PySide import QtCore, QtGui
from visualizer import *
app = QtGui.QApplication(sys.argv)


def record_pyaudio():
    FIFO='/tmp/mpd.fifo'
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
        if len(data):
            return data
    return read_data


read_data = record_pyaudio()

window = Spectrogram(read_data)
window.show()
app.exec_()
