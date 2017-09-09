"""Module that contains visualizer classes."""

import sys
import random
import time

import numpy as np
from PySide import QtCore, QtGui

SAMPLE_MAX = 32767
SAMPLE_RATE = 44100 # [Hz]


class Visualizer(QtGui.QLabel):
    """The base class for visualizers.
    
    When initializing a visualizer, you must provide a get_data function which
    takes no arguments and returns a NumPy array of PCM samples that will be
    called exactly once each time a frame is drawn.
    
    Note: Although this is an abstract class, it cannot have a metaclass of
    abcmeta since it is a child of QObject.
    """
    def __init__(self, get_data, update_interval=33):
        super(Visualizer, self).__init__()
        
        self.get_data = get_data
        self.update_interval = update_interval #33ms ~= 30 fps
        self.sizeHint = lambda: QtCore.QSize(400, 400)
        self.setStyleSheet('background-color: black;');
        self.setWindowTitle('PyVisualizer')
        
    def show(self):
        """Show the label and begin updating the visualization."""
        super(Visualizer, self).show()
        self.refresh()
        
        
    def refresh(self):
        """Generate a frame, display it, and set queue the next frame"""
        data = self.get_data()
        interval = self.update_interval
        if data is not None:
            t1 = time.clock()
            self.setPixmap(QtGui.QPixmap.fromImage(self.generate(data)))
            #decrease the time till next frame by the processing tmie so that the framerate stays consistent
            interval -= 1000 * (time.clock() - t1)
        if self.isVisible():
            QtCore.QTimer.singleShot(self.update_interval, self.refresh)
        
    def generate(self, data):
        """This is the abstract function that child classes will override to
        draw a frame of the visualization.
        
        The function takes an array of data and returns a QImage to display"""
        raise NotImplementedError()
    
    


class Spectrogram(Visualizer):
    def generate(self, data):
        fft = np.absolute(np.fft.rfft(data, n=len(data)))
        freq = np.fft.fftfreq(len(fft), d=1./SAMPLE_RATE)
        max_freq = abs(freq[fft == np.amax(fft)][0]) / 2
        max_amplitude = np.amax(data)
        
        bins = np.zeros(200)
        #indices = (len(fft) - np.logspace(0, np.log10(len(fft)), len(bins), endpoint=False).astype(int))[::-1]
        #for i in xrange(len(bins) - 1):
        #    bins[i] = np.mean(fft[indices[i]:indices[i+1]]).astype(int)
        #bins[-1] = np.mean(fft[indices[-1]:]).astype(int)
        
        step = int(len(fft) / len(bins))
        for i in range(len(bins)):
            bins[i] = np.mean(fft[i:i+step])
            
        img = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_RGB32)
        img.fill(0)
        painter = QtGui.QPainter(img)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255))) #white)
        
        for i, bin in enumerate(bins):
            height = self.height() * bin / float(SAMPLE_MAX) / 10
            width = self.width() / float(len(bins))
            painter.drawRect(i * width, self.height() - height, width, height)
            
        del painter
        
        return img
        
        
